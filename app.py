import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlencode

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Générateur d'Import Absences Lucca",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction de log globale
def add_log(msg):
    if 'app_logs' not in st.session_state:
        st.session_state.app_logs = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.append(f"[{timestamp}] {msg}")

st.title("📅 Générateur d'Import Absences")
st.markdown("""
Cet outil interroge les API Lucca pour générer un fichier CSV d'import d'absences.
Il regroupe automatiquement les demi-journées en périodes continues.
""")

# ==========================================
# FONCTIONS D'APPEL API
# ==========================================
def get_headers(key):
    return {'Authorization': f'lucca application={key}', 'Accept': 'application/json'}

def clean_domain(tenant):
    t = tenant.strip().lower().rstrip('/')
    t = t.removeprefix('https://').removeprefix('http://')
    return f"https://{t}" if '.' in t else f"https://{t}.ilucca.net"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reference_data(domain, api_key):
    """Récupère et met en cache les entités et utilisateurs (Actifs + Anciens)."""
    headers = get_headers(api_key)
    
    # Entités légales
    res_lu = requests.get(f"{domain}/organization/structure/api/legal-units", headers=headers)
    res_lu.raise_for_status()
    legal_units = {item['id']: item.get('code', '') for item in res_lu.json().get('items', [])}

    # Utilisateurs
    res_users = requests.get(
        f"{domain}/api/v3/users?fields=id,firstName,lastName,employeeNumber,legalEntity&formerEmployees=true&paging=0,2000",
        headers=headers
    )
    res_users.raise_for_status()
    users_cache = {u['id']: u for u in res_users.json().get('data', {}).get('items', [])}
    
    return legal_units, users_cache

def fetch_leaves_for_owners(domain, headers, start_str, end_str, owner_ids):
    leaves = []
    BATCH = 200
    for i in range(0, len(owner_ids), BATCH):
        batch = owner_ids[i:i + BATCH]
        qs = urlencode({
            "date": f"between,{start_str},{end_str}",
            "leavePeriod.ownerId": ",".join(str(uid) for uid in batch),
            "fields": "id,date,isAm,leaveAccountId,leavePeriodId,leavePeriod[id,ownerId]",
            "paging": "0,5000",
        })
        res = requests.get(f"{domain}/api/v3/leaves?{qs}", headers=headers)
        res.raise_for_status()
        leaves.extend(res.json().get('data', {}).get('items', []))
    return leaves

def get_is_am(leave):
    return leave.get('isAm', leave.get('isAM', True))

# ==========================================
# BARRE LATÉRALE (CONNEXION)
# ==========================================
with st.sidebar:
    st.header("⚙️ Configuration API")
    tenant = st.text_input("Instance Lucca", value="kmcl", help="'kmcl' ou URL complète")
    api_key = st.text_input("Clé API", type="password")

    domain_url = clean_domain(tenant) if tenant else ""
    
    if st.button("🔌 Connecter & Charger", use_container_width=True, type="primary"):
        if api_key and domain_url:
            with st.spinner("Synchronisation avec Lucca..."):
                try:
                    add_log("Début du chargement des données de référence...")
                    lu, uc = fetch_reference_data(domain_url, api_key)
                    st.session_state.legal_units = lu
                    st.session_state.users_cache = uc
                    st.session_state.domain_url = domain_url
                    st.session_state.api_key = api_key
                    add_log(f"Succès : {len(uc)} collaborateurs et {len(lu)} entités chargés.")
                    st.success("Données de référence chargées avec succès !")
                except requests.exceptions.RequestException as e:
                    add_log(f"Erreur API lors de la connexion : {e}")
                    st.error(f"Erreur de connexion : {e}")
        else:
            st.warning("Veuillez renseigner les identifiants.")

# ==========================================
# VUE PRINCIPALE (ONGLETS)
# ==========================================
if 'users_cache' in st.session_state:
    tab_gen, tab_logs = st.tabs(["🚀 Génération de l'Export", "📝 Console & Logs"])

    with tab_gen:
        st.subheader("Filtres & Période")
        col_dates, col_entities = st.columns([1, 2])
        
        with col_dates:
            # Période par défaut : les 30 derniers jours
            default_start = datetime.today() - timedelta(days=30)
            date_range = st.date_input(
                "Période d'export (Début - Fin)", 
                value=(default_start, datetime.today())
            )
            
        with col_entities:
            lu_options = {eid: f"{code} (ID: {eid})" for eid, code in st.session_state.legal_units.items()}
            selected_entity_ids = st.multiselect(
                "Entités Légales à inclure", 
                options=list(lu_options.keys()), 
                format_func=lambda x: lu_options[x],
                default=list(lu_options.keys())
            )

        st.divider()

        # Contrôle des filtres avant génération
        if len(date_range) != 2:
            st.info("Veuillez sélectionner une date de début ET une date de fin.")
        elif not selected_entity_ids:
            st.warning("Veuillez sélectionner au moins une entité légale.")
        else:
            # Calcul des collaborateurs impactés par les filtres
            filtered_user_ids = []
            for uid, u in st.session_state.users_cache.items():
                le_id = u.get('legalEntityId', u.get('legalEntity', {}).get('id'))
                if str(le_id) in map(str, selected_entity_ids):
                    filtered_user_ids.append(uid)
            
            st.caption(f"👥 **{len(filtered_user_ids)}** collaborateur(s) dans le périmètre sélectionné.")

            if st.button("⚡ Lancer la récupération et générer l'import", type="primary", use_container_width=True):
                start_str, end_str = date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d")
                headers = get_headers(st.session_state.api_key)
                domain_url = st.session_state.domain_url
                users_cache = st.session_state.users_cache
                legal_units = st.session_state.legal_units
                
                with st.status("Génération en cours...", expanded=True) as status:
                    try:
                        st.write("Interrogation de l'API Lucca...")
                        add_log(f"Requête des absences du {start_str} au {end_str} pour {len(filtered_user_ids)} utilisateurs.")
                        leaves = fetch_leaves_for_owners(domain_url, headers, start_str, end_str, filtered_user_ids)
                        add_log(f"{len(leaves)} lignes brutes récupérées.")
                        
                        st.write("Regroupement des demi-journées...")
                        periods = defaultdict(list)
                        for leave in leaves:
                            pid = leave.get('leavePeriodId', leave.get('leavePeriod', {}).get('id'))
                            if pid:
                                periods[pid].append(leave)
                            else:
                                add_log(f"⚠️ Absence {leave.get('id')} sans leavePeriodId, ignorée.")

                        st.write("Formatage du fichier d'export...")
                        csv_data = []
                        missing = []

                        for period_id, period_leaves in periods.items():
                            sorted_leaves = sorted(period_leaves, key=lambda x: (x.get('date', ''), not get_is_am(x)))
                            first_leave = sorted_leaves[0]
                            last_leave = sorted_leaves[-1]
                            
                            owner_id = (first_leave.get('leavePeriod') or {}).get('ownerId')
                            
                            if owner_id is None:
                                missing.append(f"Période #{period_id} ignorée : ownerId absent.")
                                continue

                            user = users_cache.get(owner_id, users_cache.get(int(owner_id) if owner_id else None))
                            if not user:
                                missing.append(f"Période #{period_id} ignorée : Utilisateur {owner_id} introuvable en cache.")
                                continue

                            le_id = user.get('legalEntityId', user.get('legalEntity', {}).get('id'))
                            le_code = legal_units.get(le_id, f"ID:{le_id}")
                            
                            csv_data.append({
                                "legalEntityCode": le_code,
                                "employeeNumber": user.get('employeeNumber', ''),
                                "lastName": user.get('lastName', ''),
                                "firstName": user.get('firstName', ''),
                                "accountId": first_leave.get('leaveAccountId', ''),
                                "startDate": datetime.strptime(first_leave['date'][:10], '%Y-%m-%d').strftime('%d/%m/%Y'),
                                "flagStartDate": "AM" if get_is_am(first_leave) else "PM",
                                "endDate": datetime.strptime(last_leave['date'][:10], '%Y-%m-%d').strftime('%d/%m/%Y'),
                                "flagEndDate": "AM" if get_is_am(last_leave) else "PM",
                                "nbHours": "",
                                "isApproved": "Oui"
                            })
                            
                        # Sauvegarde en session
                        st.session_state.last_results = {
                            "df": pd.DataFrame(csv_data),
                            "missing": missing,
                            "filename": f"import_absences_{date_range[0].strftime('%Y%m%d')}_{date_range[1].strftime('%Y%m%d')}.csv"
                        }
                        add_log(f"Traitement terminé : {len(csv_data)} périodes formatées. {len(missing)} ignorées.")
                        status.update(label="✅ Traitement terminé !", state="complete", expanded=False)
                        
                    except Exception as e:
                        add_log(f"ERREUR CRITIQUE : {str(e)}")
                        status.update(label="Erreur lors de la génération", state="error")
                        st.error(f"Une erreur est survenue : {e}")

        # Affichage des résultats s'ils existent (persistant après rerun)
        if 'last_results' in st.session_state:
            st.divider()
            df = st.session_state.last_results["df"]
            missing = st.session_state.last_results["missing"]
            
            st.subheader("📊 Résultats de l'export")
            
            # Affichage des KPIs
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Lignes d'export générées", len(df))
            kpi2.metric("Collaborateurs en absence", df['employeeNumber'].nunique() if not df.empty else 0)
            kpi3.metric("Entités impactées", df['legalEntityCode'].nunique() if not df.empty else 0)
            
            if missing:
                with st.expander(f"⚠️ {len(missing)} période(s) n'ont pas pu être traitées (voir détails)", expanded=False):
                    for m in missing:
                        st.write(f"- {m}")

            st.dataframe(df, use_container_width=True)
            
            # Bouton de téléchargement
            if not df.empty:
                st.download_button(
                    label="📥 Télécharger le fichier CSV",
                    data=df.to_csv(index=False, sep=';').encode('utf-8-sig'),
                    file_name=st.session_state.last_results["filename"],
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("Aucune absence trouvée pour cette sélection.")

    with tab_logs:
        st.write("Historique technique (pratique pour débugger) :")
        if 'app_logs' in st.session_state and st.session_state.app_logs:
            st.code("\n".join(st.session_state.app_logs[::-1]), language="text")
            if st.button("🗑️ Vider les logs"):
                st.session_state.app_logs = []
                st.rerun()
        else:
            st.info("Aucun log disponible pour le moment.")
else:
    st.info("👈 Veuillez vous connecter via le panneau latéral pour commencer l'extraction.")