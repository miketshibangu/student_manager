from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QPushButton, QMessageBox, QTableView,
                               QHeaderView, QGroupBox, QComboBox, QSpinBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from database import Database

class PromotionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Gestion des Promotions")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Formulaire d'ajout
        form_group = QGroupBox("Ajouter une promotion")
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.year_spin = QSpinBox()
        self.year_spin.setMinimum(2000)
        self.year_spin.setMaximum(2100)
        self.year_spin.setValue(2024)
        self.faculty_combo = QComboBox()
        self.department_combo = QComboBox()
        self.add_button = QPushButton("Ajouter")

        self.faculty_combo.currentIndexChanged.connect(self.load_departments)

        form_layout.addRow("Nom:", self.name_edit)
        form_layout.addRow("Année:", self.year_spin)
        form_layout.addRow("Faculté:", self.faculty_combo)
        form_layout.addRow("Département:", self.department_combo)
        form_layout.addRow(self.add_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Table des promotions
        self.promotions_table = QTableView()
        layout.addWidget(self.promotions_table)

        # Boutons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Supprimer")
        self.close_button = QPushButton("Fermer")

        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connexions
        self.add_button.clicked.connect(self.add_promotion)
        self.delete_button.clicked.connect(self.delete_promotion)
        self.close_button.clicked.connect(self.accept)

        # Charger les facultés
        self.load_faculties()

    def load_faculties(self):
        faculties = self.db.execute_query("SELECT id, name FROM faculties ORDER BY name")
        self.faculty_combo.clear()
        for faculty in faculties:
            self.faculty_combo.addItem(faculty['name'], faculty['id'])

    def load_departments(self):
        faculty_id = self.faculty_combo.currentData()
        self.department_combo.clear()
        
        if faculty_id:
            departments = self.db.execute_query(
                "SELECT id, name FROM departments WHERE faculty_id = %s ORDER BY name",
                (faculty_id,)
            )
            for department in departments:
                self.department_combo.addItem(department['name'], department['id'])

    def load_data(self):
        promotions = self.db.execute_query("""
            SELECT p.id, p.name, p.year, d.name as department_name, f.name as faculty_name 
            FROM promotions p 
            JOIN departments d ON p.department_id = d.id 
            JOIN faculties f ON d.faculty_id = f.id 
            ORDER BY p.year DESC, p.name
        """)
        self.model = PromotionsTableModel(promotions)
        self.promotions_table.setModel(self.model)
        self.promotions_table.resizeColumnsToContents()

    def add_promotion(self):
        name = self.name_edit.text().strip()
        year = self.year_spin.value()
        department_id = self.department_combo.currentData()

        if not name or not department_id:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            self.db.execute_query(
                "INSERT INTO promotions (name, year, department_id) VALUES (%s, %s, %s)",
                (name, year, department_id)
            )
            self.load_data()
            self.name_edit.clear()
            QMessageBox.information(self, "Succès", "Promotion ajoutée avec succès!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout: {str(e)}")

    def delete_promotion(self):
        selected = self.promotions_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une promotion.")
            return

        promotion_id = self.model.promotions[selected[0].row()]['id']
        reply = QMessageBox.question(self, "Confirmation", 
                                   "Êtes-vous sûr de vouloir supprimer cette promotion?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM promotions WHERE id = %s", (promotion_id,))
                self.load_data()
                QMessageBox.information(self, "Succès", "Promotion supprimée avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

class PromotionsTableModel(QAbstractTableModel):
    def __init__(self, promotions):
        super().__init__()
        self.promotions = promotions
        self.headers = ["ID", "Nom", "Année", "Département", "Faculté"]

    def rowCount(self, parent):
        return len(self.promotions)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            promotion = self.promotions[index.row()]
            if index.column() == 0:
                return promotion['id']
            elif index.column() == 1:
                return promotion['name']
            elif index.column() == 2:
                return promotion['year']
            elif index.column() == 3:
                return promotion['department_name']
            elif index.column() == 4:
                return promotion['faculty_name']

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
