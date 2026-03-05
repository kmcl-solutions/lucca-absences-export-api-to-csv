# 📅 lucca-absences-export-api-to-csv

Application web développée en **Python + Streamlit** permettant
d'interroger l'API **Lucca** afin d'extraire les absences des
collaborateurs et de générer un **export CSV propre et exploitable**.

L'objectif est de simplifier l'accès aux données d'absences pour des
usages RH, reporting ou intégration dans d'autres systèmes.

------------------------------------------------------------------------

# ✨ Fonctionnalités

-   🖥 **Interface graphique simple**
    -   Application web basée sur **Streamlit**
    -   Accessible directement depuis un navigateur
-   📆 **Filtrage par période**
    -   Sélection de date de début et de fin d'export
-   🏢 **Filtrage par entité légale**
    -   Chargement automatique des entités via l'API Lucca
    -   Inclusion ou exclusion possible
-   🔄 **Regroupement intelligent des absences**
    -   Fusion automatique des demi-journées contiguës
    -   Production de périodes d'absence cohérentes
-   📄 **Export CSV prêt à l'emploi**
    -   Format simple et lisible
    -   Téléchargement en un clic

------------------------------------------------------------------------

# 🧩 Cas d'usage

Cet outil peut être utilisé pour :

-   extraire les absences pour un **reporting RH**
-   alimenter un **outil de paie**
-   générer des **exports personnalisés**
-   auditer les données d'absences d'une instance Lucca

------------------------------------------------------------------------

# 🛠️ Prérequis

-   **Python 3.8+**
-   Une **clé API Lucca**

Permissions nécessaires :

### Socle RH

-   Consulter les collaborateurs
-   Lire les entités légales

### Figgo / Absences

-   Consulter les absences

Sans ces permissions l'API renverra une erreur :

401 Unauthorized

------------------------------------------------------------------------

# 🚀 Installation

Clonez le dépôt :

git clone
https://github.com/simongrossi/lucca-absences-export-api-to-csv.git cd
lucca-absences-export-api-to-csv

Créer un environnement virtuel (recommandé) :

python -m venv venv

Activation :

Mac / Linux

source venv/bin/activate

Windows

venv`\Scripts`{=tex}`\activate`{=tex}

Installer les dépendances :

pip install -r requirements.txt

------------------------------------------------------------------------

# 💻 Utilisation

Lancer l'application :

streamlit run app.py

L'application sera accessible à l'adresse :

http://localhost:8501

Dans l'interface :

1.  Entrer le **nom de l'instance Lucca**
2.  Entrer la **clé API**
3.  Choisir la **période d'export**
4.  Sélectionner les **entités légales**
5.  Télécharger le **CSV généré**

------------------------------------------------------------------------

# 📡 APIs Lucca utilisées

Documentation officielle :

https://developers.lucca.fr/

### API Absences (Timmi)

GET /api/v3/leaves

Permet de récupérer les absences approuvées sur une période.

------------------------------------------------------------------------

### API Directory (Collaborateurs)

GET /api/v3/users

Permet d'obtenir la liste des collaborateurs : - actifs - anciens -
matricules - rattachement organisationnel

------------------------------------------------------------------------

### API Organization (Structure)

GET /organization/structure/api/legal-units

Permet de récupérer la liste des entités légales.

------------------------------------------------------------------------

# 📦 Structure du projet

lucca-absences-export-api-to-csv │ ├── app.py ├── requirements.txt ├──
README.md │ └── utils ├── api.py ├── processing.py └── export.py

------------------------------------------------------------------------

# 📜 Licence

Projet open source sous licence **MIT**.

------------------------------------------------------------------------

# 👨‍💻 Auteur

Projet développé par **Simon Grossi**

Consultant technique solutions\
Spécialiste **Lucca / SIRH**
