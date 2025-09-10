from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QPushButton, QMessageBox, QTableView,
                               QHeaderView, QGroupBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from database import Database

class FacultyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Gestion des Facultés")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Formulaire d'ajout
        form_group = QGroupBox("Ajouter une faculté")
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.code_edit = QLineEdit()
        self.add_button = QPushButton("Ajouter")

        form_layout.addRow("Nom:", self.name_edit)
        form_layout.addRow("Code:", self.code_edit)
        form_layout.addRow(self.add_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Table des facultés
        self.faculties_table = QTableView()
        layout.addWidget(self.faculties_table)

        # Boutons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Supprimer")
        self.close_button = QPushButton("Fermer")

        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connexions
        self.add_button.clicked.connect(self.add_faculty)
        self.delete_button.clicked.connect(self.delete_faculty)
        self.close_button.clicked.connect(self.accept)

    def load_data(self):
        faculties = self.db.execute_query("SELECT id, name, code FROM faculties ORDER BY name")
        self.model = FacultiesTableModel(faculties)
        self.faculties_table.setModel(self.model)
        self.faculties_table.resizeColumnsToContents()

    def add_faculty(self):
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()

        if not name or not code:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            self.db.execute_query(
                "INSERT INTO faculties (name, code) VALUES (%s, %s)",
                (name, code)
            )
            self.load_data()
            self.name_edit.clear()
            self.code_edit.clear()
            QMessageBox.information(self, "Succès", "Faculté ajoutée avec succès!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout: {str(e)}")

    def delete_faculty(self):
        selected = self.faculties_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une faculté.")
            return

        faculty_id = self.model.faculties[selected[0].row()]['id']
        reply = QMessageBox.question(self, "Confirmation", 
                                   "Êtes-vous sûr de vouloir supprimer cette faculté?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM faculties WHERE id = %s", (faculty_id,))
                self.load_data()
                QMessageBox.information(self, "Succès", "Faculté supprimée avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

class FacultiesTableModel(QAbstractTableModel):
    def __init__(self, faculties):
        super().__init__()
        self.faculties = faculties
        self.headers = ["ID", "Nom", "Code"]

    def rowCount(self, parent):
        return len(self.faculties)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            faculty = self.faculties[index.row()]
            if index.column() == 0:
                return faculty['id']
            elif index.column() == 1:
                return faculty['name']
            elif index.column() == 2:
                return faculty['code']

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
