from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QComboBox, QPushButton, QMessageBox,
                               QLabel, QGroupBox, QTextEdit, QFileDialog, QScrollArea, QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QPalette
from database import Database
from models import Student
from image_utils import ImageUtils

class StudentDialog(QDialog):
    theme_changed = Signal(str)
    
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.db = Database()
        self.photo_path = None
        self.current_theme = "dark"  # Thème par défaut
        self.setup_ui()
        self.load_data()
        
        if self.student:
            self.fill_form()

    def setup_ui(self):
        self.setWindowTitle("➕ Ajouter Étudiant" if not self.student else "✏️ Modifier Étudiant")
        self.setMinimumSize(800, 700)
        self.resize(850, 750)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Zone de défilement pour le formulaire
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Widget conteneur
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        # Photo de l'étudiant
        photo_group = QGroupBox("📸 PHOTO DE PROFIL")
        photo_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        photo_layout = QHBoxLayout(photo_group)
        photo_layout.setSpacing(20)
        photo_layout.setContentsMargins(15, 20, 15, 20)
        
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setProperty("class", "photo-label")
        self.photo_label.setText("Cliquez pour\najouter une photo")
        self.photo_label.setWordWrap(True)
        self.photo_label.mousePressEvent = self.select_photo
        
        photo_button_layout = QVBoxLayout()
        photo_button_layout.setSpacing(15)
        photo_button_layout.setAlignment(Qt.AlignCenter)
        
        self.photo_button = QPushButton("📁 Parcourir les fichiers")
        self.photo_button.clicked.connect(self.select_photo)
        self.photo_button.setFixedSize(180, 40)
        self.photo_button.setProperty("class", "secondary")
        
        photo_button_layout.addWidget(self.photo_button)
        photo_button_layout.addStretch()
        
        photo_layout.addWidget(self.photo_label)
        photo_layout.addLayout(photo_button_layout)
        photo_layout.addStretch()
        
        layout.addWidget(photo_group)

        # Informations personnelles
        personal_group = QGroupBox("👤 INFORMATIONS PERSONNELLES")
        personal_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        personal_layout = QFormLayout(personal_group)
        personal_layout.setSpacing(12)
        personal_layout.setContentsMargins(20, 25, 20, 25)
        personal_layout.setLabelAlignment(Qt.AlignRight)

        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Entrez le nom de famille")
        self.last_name_edit.setClearButtonEnabled(True)
        
        self.postnom_edit = QLineEdit()
        self.postnom_edit.setPlaceholderText("Entrez le postnom")
        self.postnom_edit.setClearButtonEnabled(True)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Entrez le prénom")
        self.first_name_edit.setClearButtonEnabled(True)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("exemple@unikin.ac.cd")
        self.email_edit.setClearButtonEnabled(True)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+243 XXX XXX XXX")
        self.phone_edit.setClearButtonEnabled(True)
        
        self.registration_edit = QLineEdit()
        self.registration_edit.setPlaceholderText("MAT2025001")
        self.registration_edit.setClearButtonEnabled(True)
        
        personal_layout.addRow("Nom *:", self.last_name_edit)
        personal_layout.addRow("Postnom *:", self.postnom_edit)
        personal_layout.addRow("Prénom *:", self.first_name_edit)
        personal_layout.addRow("Email:", self.email_edit)
        personal_layout.addRow("Téléphone:", self.phone_edit)
        personal_layout.addRow("Matricule *:", self.registration_edit)
        
        layout.addWidget(personal_group)

        # Adresse et contacts d'urgence
        contact_group = QGroupBox("🏠 CONTACT & URGENCE")
        contact_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        contact_layout = QFormLayout(contact_group)
        contact_layout.setSpacing(12)
        contact_layout.setContentsMargins(20, 25, 20, 25)
        contact_layout.setLabelAlignment(Qt.AlignRight)

        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        self.address_edit.setPlaceholderText("Adresse complète de résidence")
        
        self.emergency_contact_edit = QLineEdit()
        self.emergency_contact_edit.setPlaceholderText("Nom du contact d'urgence")
        self.emergency_contact_edit.setClearButtonEnabled(True)
        
        self.emergency_phone_edit = QLineEdit()
        self.emergency_phone_edit.setPlaceholderText("Téléphone du contact d'urgence")
        self.emergency_phone_edit.setClearButtonEnabled(True)
        
        contact_layout.addRow("Adresse:", self.address_edit)
        contact_layout.addRow("Contact urgence:", self.emergency_contact_edit)
        contact_layout.addRow("Tél. urgence:", self.emergency_phone_edit)
        
        layout.addWidget(contact_group)

        # Filière académique
        academic_group = QGroupBox("🎓 FILIÈRE ACADÉMIQUE")
        academic_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        academic_layout = QFormLayout(academic_group)
        academic_layout.setSpacing(12)
        academic_layout.setContentsMargins(20, 25, 20, 25)
        academic_layout.setLabelAlignment(Qt.AlignRight)

        self.faculty_combo = QComboBox()
        self.faculty_combo.setMinimumWidth(300)
        self.faculty_combo.setMaximumWidth(400)
        self.faculty_combo.currentIndexChanged.connect(self.load_departments)
        
        self.department_combo = QComboBox()
        self.department_combo.setMinimumWidth(300)
        self.department_combo.setMaximumWidth(400)
        self.department_combo.currentIndexChanged.connect(self.load_promotions)
        
        self.promotion_combo = QComboBox()
        self.promotion_combo.setMinimumWidth(300)
        self.promotion_combo.setMaximumWidth(400)

        academic_layout.addRow("Faculté *:", self.faculty_combo)
        academic_layout.addRow("Département *:", self.department_combo)
        academic_layout.addRow("Promotion *:", self.promotion_combo)
        
        layout.addWidget(academic_group)

        # Définir le widget conteneur dans la zone de défilement
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area, 1)

        # Boutons en bas
        button_widget = QWidget()
        button_widget.setProperty("class", "button-container")
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(20, 15, 20, 15)
        button_layout.setSpacing(20)
        
        self.save_button = QPushButton("💾 Enregistrer")
        self.save_button.setMinimumSize(150, 45)
        self.save_button.setDefault(True)
        self.save_button.setProperty("class", "primary")
        
        self.cancel_button = QPushButton("❌ Annuler")
        self.cancel_button.setMinimumSize(150, 45)
        self.cancel_button.setProperty("class", "danger")

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addWidget(button_widget)
        
        # Appliquer les styles initiaux
        self.apply_theme(self.current_theme)
        
        # Connecter le signal de changement de thème
        self.theme_changed.connect(self.apply_theme)

    def apply_theme(self, theme_name):
        """Applique un thème light ou dark au dialogue"""
        self.current_theme = theme_name
        palette = QPalette()
        
        if theme_name == "dark":
            # Palette pour le thème sombre
            palette.setColor(QPalette.Window, QColor(45, 45, 48))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(30, 30, 30))
            palette.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(60, 60, 60))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, Qt.white)
        else:
            # Palette pour le thème clair
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, Qt.white)
        
        self.setPalette(palette)
        self.apply_styles()

    def apply_styles(self):
        """Applique les styles CSS en fonction du thème actuel"""
        if self.current_theme == "dark":
            style = """
                QDialog {
                    background: #2d2d30;
                    color: #ffffff;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid #3d3d40;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 16px;
                    background: #2d2d30;
                    color: #4e73df;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 16px;
                    padding: 0 10px 0 10px;
                    color: #4e73df;
                    font-size: 13px;
                    font-weight: bold;
                }
                QLineEdit, QTextEdit, QComboBox {
                    padding: 12px;
                    border: 2px solid #3d3d40;
                    border-radius: 8px;
                    background: #1e1e1e;
                    font-size: 13px;
                    color: #ffffff;
                    selection-background-color: #4e73df;
                    selection-color: white;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 2px solid #4e73df;
                }
                QLineEdit:hover, QComboBox:hover {
                    border: 2px solid #5a7cdf;
                }
                QTextEdit {
                    background: #1e1e1e;
                    color: #ffffff;
                }
                QComboBox QAbstractItemView {
                    background: #2d2d30;
                    border: 2px solid #3d3d40;
                    color: #ffffff;
                    selection-background-color: #4e73df;
                }
                QLabel {
                    color: #cccccc;
                    font-size: 13px;
                }
                QLabel[class="photo-label"] {
                    border: 3px dashed #666666;
                    border-radius: 75px;
                    background: #2d2d30;
                    font-size: 12px;
                    color: #cccccc;
                }
                QLabel[class="photo-label"]:hover {
                    border-color: #4e73df;
                    background: #3d3d40;
                }
                QPushButton[class="primary"] {
                    background: #4e73df;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton[class="primary"]:hover {
                    background: #2e59d9;
                }
                QPushButton[class="primary"]:pressed {
                    background: #1a46c4;
                }
                QPushButton[class="secondary"] {
                    background: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton[class="secondary"]:hover {
                    background: #5a6268;
                }
                QPushButton[class="danger"] {
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton[class="danger"]:hover {
                    background: #c82333;
                }
                QWidget[class="button-container"] {
                    background: #2d2d30;
                    border-top: 2px solid #3d3d40;
                    border-radius: 8px;
                }
            """
        else:
            style = """
                QDialog {
                    background: #ffffff;
                    color: #000000;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid #d1d3e2;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 16px;
                    background: #f8f9fc;
                    color: #4e73df;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 16px;
                    padding: 0 10px 0 10px;
                    color: #4e73df;
                    font-size: 13px;
                    font-weight: bold;
                }
                QLineEdit, QTextEdit, QComboBox {
                    padding: 12px;
                    border: 2px solid #d1d3e2;
                    border-radius: 8px;
                    background: #ffffff;
                    font-size: 13px;
                    color: #000000;
                    selection-background-color: #4e73df;
                    selection-color: white;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 2px solid #4e73df;
                }
                QLineEdit:hover, QComboBox:hover {
                    border: 2px solid #bac8f3;
                }
                QTextEdit {
                    background: #ffffff;
                    color: #000000;
                }
                QComboBox QAbstractItemView {
                    background: #ffffff;
                    border: 2px solid #d1d3e2;
                    color: #000000;
                    selection-background-color: #4e73df;
                }
                QLabel {
                    color: #5a5c69;
                    font-size: 13px;
                }
                QLabel[class="photo-label"] {
                    border: 3px dashed #a0a0a0;
                    border-radius: 75px;
                    background: #f8f9fa;
                    font-size: 12px;
                    color: #666666;
                }
                QLabel[class="photo-label"]:hover {
                    border-color: #4e73df;
                    background: #eaecf4;
                }
                QPushButton[class="primary"] {
                    background: #4e73df;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton[class="primary"]:hover {
                    background: #2e59d9;
                }
                QPushButton[class="primary"]:pressed {
                    background: #1a46c4;
                }
                QPushButton[class="secondary"] {
                    background: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton[class="secondary"]:hover {
                    background: #5a6268;
                }
                QPushButton[class="danger"] {
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton[class="danger"]:hover {
                    background: #c82333;
                }
                QWidget[class="button-container"] {
                    background: #f8f9fa;
                    border-top: 2px solid #e3e6f0;
                    border-radius: 8px;
                }
            """
        
        self.setStyleSheet(style)

    def load_data(self):
        try:
            # Charger les facultés
            faculties = self.db.execute_query("SELECT id, name FROM faculties ORDER BY name")
            self.faculty_combo.clear()
            self.faculty_combo.addItem("🏛️ Sélectionnez une faculté", -1)
            for faculty in faculties:
                self.faculty_combo.addItem(f"🏛️ {faculty['name']}", faculty['id'])
            
            # Charger les départements et promotions si un étudiant est fourni
            if self.student:
                self.load_student_academic_data()
            else:
                # Initialiser les combobox vides
                self.department_combo.addItem("📚 Sélectionnez d'abord une faculté", -1)
                self.promotion_combo.addItem("🎓 Sélectionnez d'abord un département", -1)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")

    # Les autres méthodes restent inchangées...
    def load_student_academic_data(self):
        """Charge les données académiques de l'étudiant existant"""
        try:
            promotion_info = self.db.execute_query("""
                SELECT p.id as promotion_id, p.department_id, d.faculty_id 
                FROM promotions p 
                JOIN departments d ON p.department_id = d.id 
                WHERE p.id = %s
            """, (self.student['promotion_id'],))
            
            if promotion_info:
                faculty_id = promotion_info[0]['faculty_id']
                department_id = promotion_info[0]['department_id']
                
                # Charger les départements pour cette faculté
                departments = self.db.execute_query(
                    "SELECT id, name FROM departments WHERE faculty_id = %s ORDER BY name",
                    (faculty_id,)
                )
                
                self.department_combo.clear()
                self.department_combo.addItem("📚 Sélectionnez un département", -1)
                for dept in departments:
                    self.department_combo.addItem(f"📚 {dept['name']}", dept['id'])
                
                # Charger les promotions pour ce département
                promotions = self.db.execute_query(
                    "SELECT id, name, year FROM promotions WHERE department_id = %s ORDER BY year DESC, name",
                    (department_id,)
                )
                
                self.promotion_combo.clear()
                self.promotion_combo.addItem("🎓 Sélectionnez une promotion", -1)
                for promo in promotions:
                    self.promotion_combo.addItem(f"🎓 {promo['name']} ({promo['year']})", promo['id'])
                
                # Sélectionner les valeurs
                faculty_index = self.faculty_combo.findData(faculty_id)
                if faculty_index >= 0:
                    self.faculty_combo.setCurrentIndex(faculty_index)
                
                department_index = self.department_combo.findData(department_id)
                if department_index >= 0:
                    self.department_combo.setCurrentIndex(department_index)
                
                promotion_index = self.promotion_combo.findData(self.student['promotion_id'])
                if promotion_index >= 0:
                    self.promotion_combo.setCurrentIndex(promotion_index)
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur académique: {str(e)}")

    def load_departments(self):
        faculty_id = self.faculty_combo.currentData()
        self.department_combo.clear()
        
        if faculty_id and faculty_id != -1:
            try:
                departments = self.db.execute_query(
                    "SELECT id, name FROM departments WHERE faculty_id = %s ORDER BY name",
                    (faculty_id,)
                )
                self.department_combo.addItem("📚 Sélectionnez un département", -1)
                for dept in departments:
                    self.department_combo.addItem(f"📚 {dept['name']}", dept['id'])
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur départements: {str(e)}")
        else:
            self.department_combo.addItem("📚 Sélectionnez d'abord une faculté", -1)
        
        self.promotion_combo.clear()
        self.promotion_combo.addItem("🎓 Sélectionnez d'abord un département", -1)

    def load_promotions(self):
        department_id = self.department_combo.currentData()
        self.promotion_combo.clear()
        
        if department_id and department_id != -1:
            try:
                promotions = self.db.execute_query(
                    "SELECT id, name, year FROM promotions WHERE department_id = %s ORDER BY year DESC, name",
                    (department_id,)
                )
                self.promotion_combo.addItem("🎓 Sélectionnez une promotion", -1)
                for promo in promotions:
                    self.promotion_combo.addItem(f"🎓 {promo['name']} ({promo['year']})", promo['id'])
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur promotions: {str(e)}")
        else:
            self.promotion_combo.addItem("🎓 Sélectionnez d'abord un département", -1)

    def select_photo(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner une photo", 
            "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                pixmap = ImageUtils.load_image(file_path, (150, 150))
                if not pixmap.isNull():
                    self.photo_label.setPixmap(pixmap)
                    self.photo_path = file_path
                    self.photo_label.setText("")
                else:
                    QMessageBox.warning(self, "Erreur", "Image non valide")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur image: {str(e)}")

    def update_photo_display(self):
        if self.photo_path:
            pixmap = ImageUtils.load_image(self.photo_path, (150, 150))
            self.photo_label.setPixmap(pixmap)
        elif self.student and self.student.get('photo_path'):
            pixmap = ImageUtils.load_image(self.student['photo_path'], (150, 150))
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.clear()
            self.photo_label.setText("Cliquez pour\najouter une photo")

    def fill_form(self):
        if not self.student:
            return
            
        self.last_name_edit.setText(self.student.get('last_name', ''))
        self.postnom_edit.setText(self.student.get('postnom', ''))
        self.first_name_edit.setText(self.student.get('first_name', ''))
        self.email_edit.setText(self.student.get('email', ''))
        self.phone_edit.setText(self.student.get('phone', ''))
        self.registration_edit.setText(self.student.get('registration_number', ''))
        self.address_edit.setPlainText(self.student.get('address', ''))
        self.emergency_contact_edit.setText(self.student.get('emergency_contact', ''))
        self.emergency_phone_edit.setText(self.student.get('emergency_phone', ''))
        
        if self.student.get('photo_path'):
            self.photo_path = self.student['photo_path']
        
        self.update_photo_display()

    def get_data(self):
        return { 
            'last_name': self.last_name_edit.text().strip(),
            'postnom': self.postnom_edit.text().strip(),
            'first_name': self.last_name_edit.text().strip(),
            'email': self.email_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None,
            'address': self.address_edit.toPlainText().strip() or None,
            'emergency_contact': self.emergency_contact_edit.text().strip() or None,
            'emergency_phone': self.emergency_phone_edit.text().strip() or None,
            'registration_number': self.registration_edit.text().strip(),
            'photo_path': self.photo_path,
            'promotion_id': self.promotion_combo.currentData()
        }

    def accept(self):
        data = self.get_data()
        
        # Validation
        errors = []
        
        if not data['last_name']:
            errors.append("Le nom est obligatoire")
        if not data['postnom']:
            errors.append("Le postnom est obligatoire")
        if not data['first_name']:
            errors.append("Le prénom est obligatoire")
        if not data['registration_number']:
            errors.append("Le matricule est obligatoire")
        
        promotion_id = data['promotion_id']
        if not promotion_id or promotion_id == -1:
            errors.append("La promotion est obligatoire")
        
        if data['email'] and '@' not in data['email']:
            errors.append("Email invalide")
        
        if errors:
            QMessageBox.warning(self, "Erreur de validation", 
                               "Veuillez corriger les erreurs suivantes :\n\n• " + "\n• ".join(errors))
            return

        super().accept()
