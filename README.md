# 📅 lucca-absences-export-api-to-csv

Une application web interactive développée en Python (Streamlit) pour interroger l'API Lucca, récupérer les absences des collaborateurs et générer un fichier CSV formaté et prêt à l'emploi.

## ✨ Fonctionnalités

- **Interface Graphique Intuitive :** Propulsée par Streamlit pour une utilisation simple par les équipes RH ou IT.
- **Sélection de Période :** Filtrage facile des dates de début et de fin d'export.
- **Filtrage par Entité Légale :** Possibilité d'inclure ou d'exclure certaines entités (récupérées dynamiquement via l'API).
- **Regroupement Intelligent :** Consolide automatiquement les demi-journées d'absence contiguës en périodes complètes.
- **Export CSV :** Génère un fichier propre avec le bon formatage de colonnes, prêt à être téléchargé d'un simple clic.

## 🛠️ Prérequis

- **Python 3.8+**
- **Une clé API Lucca** ayant les permissions suivantes :
  - *Socle RH* : "Consulter les collaborateurs" et "Lire les entités légales" (indispensable pour éviter l'erreur `401 Unauthorized`).
  - *Figgo / Absences* : "Consulter les absences".

## 🚀 Installation

1. Clonez ce dépôt sur votre machine locale :
   ```bash
   git clone [https://github.com/votre-nom-utilisateur/lucca-absences-export-api-to-csv.git](https://github.com/votre-nom-utilisateur/lucca-absences-export-api-to-csv.git)
   cd lucca-absences-export-api-to-csv
