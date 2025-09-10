from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QPushButton, QMessageBox, QTableView,
                               QHeaderView, QGroupBox, QComboBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from database import Database

class DepartmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Gestion des Départements")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Formulaire d'ajout
        form_group = QGroupBox("Ajouter un département")
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.code_edit = QLineEdit()
        self.faculty_combo = QComboBox()
        self.add_button = QPushButton("Ajouter")

        form_layout.addRow("Nom:", self.name_edit)
        form_layout.addRow("Code:", self.code_edit)
        form_layout.addRow("Faculté:", self.faculty_combo)
        form_layout.addRow(self.add_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Table des départements
        self.departments_table = QTableView()
        layout.addWidget(self.departments_table)

        # Boutons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Supprimer")
        self.close_button = QPushButton("Fermer")

        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connexions
        self.add_button.clicked.connect(self.add_department)
        self.delete_button.clicked.connect(self.delete_department)
        self.close_button.clicked.connect(self.accept)

        # Charger les facultés
        self.load_faculties()

    def load_faculties(self):
        faculties = self.db.execute_query("SELECT id, name FROM faculties ORDER BY name")
        self.faculty_combo.clear()
        for faculty in faculties:
            self.faculty_combo.addItem(faculty['name'], faculty['id'])

    def load_data(self):
        departments = self.db.execute_query("""
            SELECT d.id, d.name, d.code, f.name as faculty_name 
            FROM departments d 
            JOIN faculties f ON d.faculty_id = f.id 
            ORDER BY f.name, d.name
        """)
        self.model = DepartmentsTableModel(departments)
        self.departments_table.setModel(self.model)
        self.departments_table.resizeColumnsToContents()

    def add_department(self):
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()
        faculty_id = self.faculty_combo.currentData()

        if not name or not code or not faculty_id:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            self.db.execute_query(
                "INSERT INTO departments (name, code, faculty_id) VALUES (%s, %s, %s)",
                (name, code, faculty_id)
            )
            self.load_data()
            self.name_edit.clear()
            self.code_edit.clear()
            QMessageBox.information(self, "Succès", "Département ajouté avec succès!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout: {str(e)}")

    def delete_department(self):
        selected = self.departments_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un département.")
            return

        department_id = self.model.departments[selected[0].row()]['id']
        reply = QMessageBox.question(self, "Confirmation", 
                                   "Êtes-vous sûr de vouloir supprimer ce département?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM departments WHERE id = %s", (department_id,))
                self.load_data()
                QMessageBox.information(self, "Succès", "Département supprimé avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

class DepartmentsTableModel(QAbstractTableModel):
    def __init__(self, departments):
        super().__init__()
        self.departments = departments
        self.headers = ["ID", "Nom", "Code", "Faculté"]

    def rowCount(self, parent):
        return len(self.departments)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            department = self.departments[index.row()]
            if index.column() == 0:
                return department['id']
            elif index.column() == 1:
                return department['name']
            elif index.column() == 2:
                return department['code']
            elif index.column() == 3:
                return department['faculty_name']

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
