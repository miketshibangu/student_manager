# 🎓 Student Manager

**Student Manager** est une application desktop développée en **Python 3.12.3** avec **PySide6** (Qt pour Python).  
Elle permet de gérer efficacement les étudiants, facultés, départements et promotions, avec la possibilité de générer des PDF et d’utiliser des images liées aux étudiants.

L’application est livrée avec **SQLite** comme base de données par défaut, mais peut être configurée pour utiliser **PostgreSQL** grâce à un simple paramètre dans le fichier `.env`.

---

## 🚀 Fonctionnalités principales
- Interface graphique moderne avec **PySide6**
- Gestion des étudiants, facultés, départements et promotions
- Stockage des images associées aux étudiants
- Génération de documents PDF
- Base de données flexible :
  - **SQLite (par défaut)** pour une utilisation locale rapide
  - **PostgreSQL** si `DB_ENGINE=postgresql` est défini dans `.env`
- Build multi-plateforme (Linux, Windows, macOS) via **GitHub Actions**

---

## 📂 Structure du projet

```text
student_manager/
├── main.py                  # Point d’entrée de l’application
├── database.py              # Gestion de la base de données (SQLite/PostgreSQL)
├── models.py                # Modèles de données
├── ui_main_window.py        # Interface principale
├── ui_student_dialog.py     # Dialogues de gestion des étudiants
├── ui_faculty_dialog.py     # Dialogues de gestion des facultés
├── ui_department_dialog.py  # Dialogues de gestion des départements
├── ui_promotion_dialog.py   # Dialogues de gestion des promotions
├── pdf_generator.py         # Génération de PDF
├── image_utils.py           # Outils pour les images
├── .env                     # Variables d’environnement (choix DB_ENGINE, etc.)
├── requirements.txt         # Dépendances Python
├── data/
│   └── images/
│       └── students/        # Images des étudiants
├── .github/
│   └── workflows/
│       └── build.yml        # Workflow GitHub Actions pour compiler l’app
└── README.md

