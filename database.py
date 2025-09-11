import os
import sqlite3
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import re

load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.db_engine = os.getenv("DB_ENGINE", "sqlite").lower()
        self.connect()

    def get_param_style(self):
        """Retourne le style de paramètre selon le moteur de base de données"""
        return "%s" if self.db_engine == "postgresql" else "?"

    def connect(self):
        try:
            if self.db_engine == "postgresql":
                self.connection = psycopg2.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    database=os.getenv("DB_NAME", "university_db"),
                    user=os.getenv("DB_USER", "postgres"),
                    password=os.getenv("DB_PASSWORD", ""),
                    port=os.getenv("DB_PORT", "5432")
                )
                # Configuration pour PostgreSQL
                self.connection.autocommit = False
            else:  # SQLite par défaut
                db_path = os.getenv("SQLITE_PATH", "./data/student_manager.db")
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                self.connection = sqlite3.connect(db_path)
                self.connection.row_factory = sqlite3.Row  # dict-like results
                # Configuration pour SQLite
                self.connection.isolation_level = None  # Auto-commit désactivé

            self.create_tables()
            self.insert_default_data()
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données: {e}")
            raise

    def create_tables(self):
        cursor = None
        try:
            cursor = self.connection.cursor()

            # Différence SERIAL vs AUTOINCREMENT
            auto_inc = "SERIAL PRIMARY KEY" if self.db_engine == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"

            # Création des tables
            tables = [
                f"""
                CREATE TABLE IF NOT EXISTS faculties (
                    id {auto_inc},
                    name VARCHAR(100) NOT NULL UNIQUE,
                    code VARCHAR(10) NOT NULL UNIQUE,
                    description TEXT
                )
                """,
                f"""
                CREATE TABLE IF NOT EXISTS departments (
                    id {auto_inc},
                    name VARCHAR(100) NOT NULL,
                    code VARCHAR(10) NOT NULL,
                    faculty_id INTEGER REFERENCES faculties(id),
                    UNIQUE(name, faculty_id)
                )
                """,
                f"""
                CREATE TABLE IF NOT EXISTS promotions (
                    id {auto_inc},
                    name VARCHAR(100) NOT NULL,
                    year INTEGER NOT NULL,
                    department_id INTEGER REFERENCES departments(id),
                    UNIQUE(name, department_id, year)
                )
                """,
                f"""
                CREATE TABLE IF NOT EXISTS students (
                    id {auto_inc},
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    postnom VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE,
                    phone VARCHAR(20),
                    address TEXT,
                    emergency_contact VARCHAR(100),
                    emergency_phone VARCHAR(20),
                    registration_number VARCHAR(20) UNIQUE NOT NULL,
                    photo_path VARCHAR(255),
                    promotion_id INTEGER REFERENCES promotions(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ]

            for table_sql in tables:
                cursor.execute(table_sql)

            self.connection.commit()
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def insert_default_data(self):
        """Insère les données par défaut de l'UNIKIN si elles n'existent pas"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            
            # Vérifier si des données existent déjà
            cursor.execute("SELECT COUNT(*) FROM faculties")
            faculty_count = cursor.fetchone()[0]
            
            if faculty_count == 0:
                print("📦 Insertion des données par défaut de l'UNIKIN...")
                
                # Insertion des facultés de l'UNIKIN
                faculties = [
                    ("Droit", "DROIT", "Faculté de Droit"),
                    ("Sciences Économiques et de Gestion", "ECO-GEST", "Faculté des Sciences Économiques et de Gestion"),
                    ("Lettres et Sciences Humaines", "LET-SH", "Faculté des Lettres et Sciences Humaines"),
                    ("Médecine", "MED", "Faculté de Médecine"),
                    ("Médecine Vétérinaire", "MED-VET", "Faculté de Médecine Vétérinaire"),
                    ("Pétrole, Gaz et Énergies Nouvelles", "PÉTROLE", "Faculté de Pétrole, Gaz et Énergies Nouvelles"),
                    ("Polytechnique", "POLY", "Faculté Polytechnique"),
                    ("Psychologie et Sciences de l'Éducation", "PSY-EDU", "Faculté de Psychologie et des Sciences de l'Éducation"),
                    ("Sciences", "SCI", "Faculté des Sciences"),
                    ("Sciences Agronomiques", "AGRO", "Faculté des Sciences Agronomiques"),
                    ("Sciences Pharmaceutiques", "PHARMA", "Faculté des Sciences Pharmaceutiques"),
                    ("Sciences Sociales, Administratives et Politiques", "SOCIO", "Faculté des Sciences Sociales, Administratives et Politiques"),
                    ("Médecine Dentaire", "MED-DENT", "Faculté de Médecine Dentaire")
                ]
                
                faculty_ids = {}
                param_style = self.get_param_style()
                
                for name, code, description in faculties:
                    query = f"INSERT INTO faculties (name, code, description) VALUES ({param_style}, {param_style}, {param_style})"
                    if self.db_engine == "postgresql":
                        query += " RETURNING id"
                    
                    cursor.execute(query, (name, code, description))
                    
                    if self.db_engine == "postgresql":
                        faculty_id = cursor.fetchone()[0]
                    else:
                        faculty_id = cursor.lastrowid
                    faculty_ids[name] = faculty_id
                
                # Insertion des départements
                departments = [
                    # Droit
                    ("Droit privé et judiciaire", "D-PRIV", "Droit"),
                    ("Droit pénal et criminologie", "D-PENAL", "Droit"),
                    ("Droit international public", "D-INT", "Droit"),
                    ("Droits de l'Homme", "D-DH", "Droit"),
                    ("Droit économique et social", "D-ECO", "Droit"),
                    ("Droit public interne", "D-PUB", "Droit"),
                    ("Droit de l'environnement", "D-ENV", "Droit"),
                    
                    # Sciences Économiques et de Gestion
                    ("Économie politique", "ECO-POL", "Sciences Économiques et de Gestion"),
                    ("Gestion des entreprises", "GEST-ENT", "Sciences Économiques et de Gestion"),
                    ("Sciences commerciales et financières", "SCI-COM", "Sciences Économiques et de Gestion"),
                    ("Informatique de Gestion et Anglais des Affaires (IGAF)", "IGAF", "Sciences Économiques et de Gestion"),
                    ("Gestion et Anglais de Affaires (GAF)", "GAF", "Sciences Économiques et de Gestion"),
                    
                    # Lettres et Sciences Humaines
                    ("Lettres", "LETTRES", "Lettres et Sciences Humaines"),
                    ("Langues", "LANGUES", "Lettres et Sciences Humaines"),
                    ("Histoire", "HIST", "Lettres et Sciences Humaines"),
                    ("Philosophie", "PHILO", "Lettres et Sciences Humaines"),
                    ("Anglais et Informatique des Affaires (AIA)", "AIA", "Lettres et Sciences Humaines"),
                    
                    # Médecine
                    ("Médecine générale", "MED-G", "Médecine"),
                    ("Chirurgie", "CHIR", "Médecine"),
                    ("Pédiatrie", "PED", "Médecine"),
                    ("Gynécologie-obstétrique", "GYN-OBS", "Médecine"),
                    ("Médecine interne", "MED-INT", "Médecine"),
                    ("Biologie clinique", "BIO-CLIN", "Médecine"),
                    
                    # Médecine Vétérinaire
                    ("Santé animale", "SANTE-ANIM", "Médecine Vétérinaire"),
                    ("Production animale", "PROD-ANIM", "Médecine Vétérinaire"),
                    ("Pathologie vétérinaire", "PATHO-VET", "Médecine Vétérinaire"),
                    
                    # Pétrole, Gaz et Énergies Nouvelles
                    ("Ingénierie pétrolière", "ING-PET", "Pétrole, Gaz et Énergies Nouvelles"),
                    ("Gaz et énergies renouvelables", "GAZ-ENER", "Pétrole, Gaz et Énergies Nouvelles"),
                    ("Gestion des ressources énergétiques", "GEST-ENER", "Pétrole, Gaz et Énergies Nouvelles"),
                    
                    # Polytechnique
                    ("Génie civil", "GC", "Polytechnique"),
                    ("Génie électrique", "GE", "Polytechnique"),
                    ("Génie mécanique", "GM", "Polytechnique"),
                    ("Génie informatique et technologique", "GI", "Polytechnique"),
                    
                    # Psychologie et Sciences de l'Éducation
                    ("Psychologie clinique", "PSY-CLIN", "Psychologie et Sciences de l'Éducation"),
                    ("Sciences de l'éducation", "SCI-EDU", "Psychologie et Sciences de l'Éducation"),
                    ("Gestion des entreprises et organisation du travail", "GEST-ORG", "Psychologie et Sciences de l'Éducation"),
                    
                    # Sciences
                    ("Mathématiques, Statistique et Informatique", "MSI", "Sciences"),
                    ("Physique et Technologie", "PHY-TECH", "Sciences"),
                    ("Chimie et Industries", "CHIM-IND", "Sciences"),
                    ("Sciences de la Vie et Environnement", "SVE", "Sciences"),
                    ("Géosciences (Géologie et Géographie)", "GEO", "Sciences"),
                    ("Sciences et Gestion de l'Environnement", "SGE", "Sciences"),
                    
                    # Sciences Agronomiques
                    ("Phytotechnie", "PHYTO", "Sciences Agronomiques"),
                    ("Zootechnie", "ZOO", "Sciences Agronomiques"),
                    ("Économie agricole", "ECO-AGRI", "Sciences Agronomiques"),
                    ("Agroécologie", "AGRO-ECO", "Sciences Agronomiques"),
                    ("Gestion des ressources naturelles", "GEST-RN", "Sciences Agronomiques"),
                    
                    # Sciences Pharmaceutiques
                    ("Pharmacie clinique", "PHAR-CLIN", "Sciences Pharmaceutiques"),
                    ("Pharmacologie", "PHARMA", "Sciences Pharmaceutiques"),
                    ("Chimie pharmaceutique", "CHIM-PHAR", "Sciences Pharmaceutiques"),
                    
                    # Sciences Sociales, Administratives et Politiques
                    ("Sociologie", "SOCIO", "Sciences Sociales, Administratives et Politiques"),
                    ("Anthropologie", "ANTHRO", "Sciences Sociales, Administratives et Politiques"),
                    ("Administration publique", "ADM-PUB", "Sciences Sociales, Administratives et Politiques"),
                    ("Sciences politiques", "SCI-POL", "Sciences Sociales, Administratives et Politiques"),
                    
                    # Médecine Dentaire
                    ("Odontologie conservatrice", "ODON-CONS", "Médecine Dentaire"),
                    ("Chirurgie buccale", "CHIR-BUC", "Médecine Dentaire"),
                    ("Orthodontie", "ORTHO", "Médecine Dentaire")
                ]
                
                department_ids = {}
                for name, code, faculty_name in departments:
                    faculty_id = faculty_ids[faculty_name]
                    query = f"INSERT INTO departments (name, code, faculty_id) VALUES ({param_style}, {param_style}, {param_style})"
                    if self.db_engine == "postgresql":
                        query += " RETURNING id"
                    
                    cursor.execute(query, (name, code, faculty_id))
                    
                    if self.db_engine == "postgresql":
                        department_id = cursor.fetchone()[0]
                    else:
                        department_id = cursor.lastrowid
                    department_ids[name] = department_id
                
                # Insertion des promotions LMD pour l'année en cours
                from datetime import datetime
                current_year = datetime.now().year
                
                for department_name in department_ids:
                    department_id = department_ids[department_name]
                    
                    # Niveaux LMD
                    lmd_levels = [
                        "Licence 1", "Licence 2", "Licence 3",
                        "Master 1", "Master 2", 
                        "Doctorat 1", "Doctorat 2", "Doctorat 3"
                    ]
                    
                    for level in lmd_levels:
                        query = f"INSERT INTO promotions (name, year, department_id) VALUES ({param_style}, {param_style}, {param_style})"
                        cursor.execute(query, (f"{level} - {department_name}", current_year, department_id))
                
                self.connection.commit()
                print("✅ Données par défaut de l'UNIKIN insérées avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion des données par défaut: {e}")
            if self.connection:
                self.connection.rollback()
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query, params=None, return_id=False):
        """Exécute une requête SQL avec gestion propre des transactions"""
        cursor = None
        try:
            # Conversion des paramètres pour SQLite
            if self.db_engine != "postgresql":
                query = query.replace('%s', '?')
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            # Pour les requêtes SELECT, retourner les résultats
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                if self.db_engine == "postgresql":
                    columns = [desc[0] for desc in cursor.description]
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = [dict(row) for row in rows]
                return result

            # Commit pour les autres types de requêtes
            self.connection.commit()

            # Pour les INSERT avec retour d'ID
            if return_id:
                if self.db_engine == "postgresql":
                    cursor.execute("SELECT LASTVAL()")
                    result = cursor.fetchone()[0]
                else:
                    result = cursor.lastrowid
                return result

            # Pour UPDATE/DELETE, retourner le nombre de lignes affectées
            return cursor.rowcount
            
        except Exception as e:
            # Rollback en cas d'erreur
            if self.connection:
                self.connection.rollback()
            print(f"❌ Erreur lors de l'exécution de la requête: {e}")
            print(f"📋 Requête: {query}")
            print(f"🔧 Paramètres: {params}")
            raise
        finally:
            # Toujours fermer le curseur
            if cursor:
                cursor.close()

    def execute_query_with_transaction(self, query, params=None, return_id=False):
        """Version alternative avec gestion explicite des transactions"""
        cursor = None
        try:
            # Début de transaction explicite pour SQLite
            if self.db_engine != "postgresql":
                self.connection.execute("BEGIN TRANSACTION")
            
            # Conversion des paramètres pour SQLite
            if self.db_engine != "postgresql":
                query = query.replace('%s', '?')
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            # Pour les requêtes SELECT, retourner les résultats
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                if self.db_engine == "postgresql":
                    columns = [desc[0] for desc in cursor.description]
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = [dict(row) for row in rows]
                return result

            # Commit de la transaction
            self.connection.commit()

            # Pour les INSERT avec retour d'ID
            if return_id:
                if self.db_engine == "postgresql":
                    cursor.execute("SELECT LASTVAL()")
                    result = cursor.fetchone()[0]
                else:
                    result = cursor.lastrowid
                return result

            return cursor.rowcount
            
        except Exception as e:
            # Rollback en cas d'erreur
            if self.connection:
                self.connection.rollback()
            print(f"❌ Erreur lors de l'exécution de la requête: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            try:
                self.connection.close()
                print("✅ Connexion à la base de données fermée")
            except Exception as e:
                print(f"❌ Erreur lors de la fermeture de la connexion: {e}")

    def __del__(self):
        """Destructeur pour fermer la connexion"""
        self.close()
