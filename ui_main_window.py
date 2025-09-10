from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableView, QPushButton, QMessageBox, QHeaderView,
    QTabWidget, QGroupBox, QFormLayout, QLineEdit,
    QSpinBox, QComboBox, QLabel, QToolBar, QStatusBar,
    QSplitter, QGridLayout, QFrame, QSizePolicy, QApplication,
    QFileDialog, QScrollArea, QScrollBar, QSizeGrip, QAbstractItemView
)
from PySide6.QtCore import Qt, QAbstractTableModel, Signal, QSettings, QSize, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QColor, QPalette, QFont, QFontDatabase
import os
import sys
from database import Database
from models import Student
from ui_student_dialog import StudentDialog
from ui_faculty_dialog import FacultyDialog
from ui_department_dialog import DepartmentDialog
from ui_promotion_dialog import PromotionDialog
from pdf_generator import PDFGenerator
from image_utils import ImageUtils

class ModernScrollBar(QScrollBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)


class StudentsTableModel(QAbstractTableModel):
    def __init__(self, students):
        super().__init__()
        self.students = students
        self.headers = ["ID", "Photo", "Nom", "Postnom", "Prénom", "Email", "Téléphone", "Matricule", "Promotion", "Faculté", "Département"]

    def rowCount(self, parent):
        return len(self.students)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return None
            
        student = self.students[index.row()]
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return student['id']
            elif index.column() == 2:
                return student['last_name']
            elif index.column() == 3:
                return student['postnom']
            elif index.column() == 4:
                return student['first_name']
            elif index.column() == 5:
                return student['email'] or ""
            elif index.column() == 6:
                return student['phone'] or ""
            elif index.column() == 7:
                return student['registration_number']
            elif index.column() == 8:
                return student['promotion_name']
            elif index.column() == 9:
                return student['faculty_name']
            elif index.column() == 10:
                return student['department_name']
        
        elif role == Qt.DecorationRole and index.column() == 1:
            return ImageUtils.load_image(student['photo_path'], (40, 40))
        
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter if index.column() in [0, 1, 6, 7] else Qt.AlignLeft | Qt.AlignVCenter
            
        elif role == Qt.ToolTipRole:
            if index.column() == 5 and student['email']:
                return student['email']
            elif index.column() == 6 and student['phone']:
                return student['phone']
                
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        elif role == Qt.FontRole and orientation == Qt.Horizontal:
            font = QFont()
            font.setBold(True)
            return font
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None


class MainWindow(QMainWindow):
    theme_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.pdf_generator = PDFGenerator()
        self.loading_data = False
        self.current_student_id = None
        self.settings = QSettings("UniversiteUNIKIN", "GestionEtudiants")
        self.setup_ui()
        self.load_settings()
        self.load_data()
        self.setup_theme_handler()

    def setup_ui(self):
        self.setWindowTitle("🎓 Gestion des Étudiants - Université UNIKIN")
        self.setMinimumSize(1200, 700)  # Taille minimale réduite
        self.resize(1400, 800)  # Taille initiale raisonnable
        
        # Configuration de la police
        self.setFont(QFont("Segoe UI", 10))
        
        # Widget central avec layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Configuration de la barre d'outils
        self.setup_toolbar()
        
        # Configuration de la barre de statut
        self.setup_statusbar()
        
        # Configuration des filtres
        self.setup_filters(main_layout)
        
        # Configuration du séparateur principal
        self.setup_main_splitter(main_layout)
        
        # Configuration des boutons d'action
        self.setup_action_buttons(main_layout)
        
        # Configuration du menu
        self.setup_menu()
        
        # Appliquer le style initial
        self.apply_styles()

    def setup_toolbar(self):
        toolbar = QToolBar("Barre d'outils principale")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 5px;
                padding: 5px;
                background: palette(button);
                border-bottom: 1px solid palette(mid);
            }
            QToolButton {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self.addToolBar(toolbar)
        
        # Actions de la barre d'outils
        actions = [
            ("➕ Ajouter", "add_student", self.add_student, "Ctrl+N"),
            ("👀 Détails", "view_student", self.view_student_details, "Ctrl+D"),
            ("✏️ Modifier", "edit_student", self.edit_student, "Ctrl+E"),
            ("🗑️ Supprimer", "delete_student", self.delete_student, "Del"),
            ("🖨️ Imprimer", "print_list", self.print_students_list, "Ctrl+P"),
            ("🔄 Actualiser", "refresh", self.load_data, "F5"),
        ]
        
        for text, icon_name, callback, shortcut in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            action.setShortcut(shortcut)
            toolbar.addAction(action)
            
        toolbar.addSeparator()
        
        # Sélecteur de thème
        theme_action = QAction("🎨 Thème", self)
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)

    def setup_statusbar(self):
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background: palette(button);
                border-top: 1px solid palette(mid);
                padding: 3px;
            }
        """)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")

    def setup_filters(self, parent_layout):
        filter_group = QGroupBox("🔍 Filtres de Recherche")
        filter_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        filter_layout = QGridLayout(filter_group)
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(15, 20, 15, 15)

        # Création des filtres
        self.faculty_filter = QComboBox()
        self.department_filter = QComboBox()
        self.promotion_filter = QComboBox()
        
        # Filtres avec labels
        filters = [
            ("🏛️ Faculté:", self.faculty_filter, self.on_filter_changed),
            ("📚 Département:", self.department_filter, self.on_filter_changed),
            ("🎓 Promotion:", self.promotion_filter, self.on_filter_changed),
        ]
        
        for col, (label_text, widget, callback) in enumerate(filters):
            label = QLabel(label_text)
            widget.setMinimumWidth(180)
            widget.currentIndexChanged.connect(callback)
            
            filter_layout.addWidget(label, 0, col * 2)
            filter_layout.addWidget(widget, 0, col * 2 + 1)
        
        # Bouton de réinitialisation des filtres
        reset_btn = QPushButton("🗑️ Réinitialiser")
        reset_btn.clicked.connect(self.reset_filters)
        reset_btn.setFixedWidth(120)
        filter_layout.addWidget(reset_btn, 0, 6, 1, 2)
        
        parent_layout.addWidget(filter_group)

    def setup_main_splitter(self, parent_layout):
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: palette(mid);
                width: 4px;
            }
            QSplitter::handle:hover {
                background: palette(highlight);
            }
        """)
        
        # Table des étudiants
        self.setup_students_table()
        splitter.addWidget(self.students_table)
        
        # Détails de l'étudiant
        self.setup_student_details()
        splitter.addWidget(self.details_scroll)
        
        # Configuration du splitter
        splitter.setSizes([700, 400])
        splitter.setChildrenCollapsible(False)
        
        parent_layout.addWidget(splitter, 1)

    def setup_students_table(self):
        self.students_table = QTableView()
        self.students_table.setSelectionBehavior(QTableView.SelectRows)
        self.students_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSortingEnabled(True)
        self.students_table.verticalHeader().setDefaultSectionSize(60)
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.students_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.students_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.students_table.doubleClicked.connect(self.view_student_details)
        self.students_table.clicked.connect(self.on_student_selected)
        
        # Configuration des colonnes
        self.students_table.horizontalHeader().setStretchLastSection(True)

    def setup_student_details(self):
        # Zone de défilement pour les détails
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setVerticalScrollBar(ModernScrollBar())
        self.details_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.details_scroll.setMinimumWidth(350)
        
        # Widget de contenu
        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)
        self.details_layout.setSpacing(15)
        self.details_layout.setContentsMargins(15, 15, 15, 15)
        
        # Photo et informations de base
        self.setup_basic_info()
        
        # Informations supplémentaires
        self.setup_additional_info()
        
        # Boutons d'action
        self.setup_detail_buttons()
        
        self.details_scroll.setWidget(details_widget)

    def setup_basic_info(self):
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(15)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        # Photo de l'étudiant
        self.student_photo = QLabel()
        self.student_photo.setAlignment(Qt.AlignCenter)
        self.student_photo.setFixedSize(120, 120)
        self.student_photo.setStyleSheet("""
            QLabel {
                border: 2px solid palette(mid);
                border-radius: 8px;
                background: palette(window);
            }
        """)
        self.student_photo.setScaledContents(True)
        self.student_photo.setText("Aucune photo")
        
        # Informations de base
        basic_info_widget = QWidget()
        basic_info_layout = QFormLayout(basic_info_widget)
        basic_info_layout.setSpacing(8)
        basic_info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.student_name = QLabel("Non sélectionné")
        self.student_registration = QLabel("-")
        self.student_email = QLabel("-")
        self.student_phone = QLabel("-")
        
        # Style des labels d'information
        for label in [self.student_name, self.student_registration, self.student_email, self.student_phone]:
            label.setWordWrap(True)
            label.setStyleSheet("""
                QLabel {
                    padding: 4px;
                    background: palette(base);
                    border-radius: 4px;
                    border: 1px solid palette(mid);
                }
            """)
        
        basic_info_layout.addRow("👤 Nom:", self.student_name)
        basic_info_layout.addRow("🔢 Matricule:", self.student_registration)
        basic_info_layout.addRow("📧 Email:", self.student_email)
        basic_info_layout.addRow("📞 Téléphone:", self.student_phone)
        
        info_layout.addWidget(self.student_photo)
        info_layout.addWidget(basic_info_widget)
        
        self.details_layout.addWidget(info_frame)

    def setup_additional_info(self):
        additional_frame = QFrame()
        additional_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        additional_layout = QFormLayout(additional_frame)
        additional_layout.setSpacing(8)
        additional_layout.setContentsMargins(15, 15, 15, 15)
        
        self.student_address = QLabel("-")
        self.student_emergency_contact = QLabel("-")
        self.student_emergency_phone = QLabel("-")
        self.student_faculty = QLabel("-")
        self.student_department = QLabel("-")
        self.student_promotion = QLabel("-")
        
        # Style des labels d'information
        info_labels = [
            self.student_address, self.student_emergency_contact,
            self.student_emergency_phone, self.student_faculty,
            self.student_department, self.student_promotion
        ]
        
        for label in info_labels:
            label.setWordWrap(True)
            label.setStyleSheet("""
                QLabel {
                    padding: 4px;
                    background: palette(base);
                    border-radius: 4px;
                    border: 1px solid palette(mid);
                    min-height: 20px;
                }
            """)
        
        additional_layout.addRow("🏠 Adresse:", self.student_address)
        additional_layout.addRow("🆘 Contact d'urgence:", self.student_emergency_contact)
        additional_layout.addRow("📞 Téléphone d'urgence:", self.student_emergency_phone)
        additional_layout.addRow("🏛️ Faculté:", self.student_faculty)
        additional_layout.addRow("📚 Département:", self.student_department)
        additional_layout.addRow("🎓 Promotion:", self.student_promotion)
        
        self.details_layout.addWidget(additional_frame)

    def setup_detail_buttons(self):
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        buttons = [
            ("👀 Détails", self.view_student_details, "primary"),
            ("✏️ Modifier", self.edit_student, "secondary"),
            ("🗑️ Supprimer", self.delete_student, "danger"),
            ("📊 Rapport", self.generate_student_report, "success"),
        ]
        
        for text, callback, style in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setProperty("class", style)
            btn.setMinimumHeight(35)
            action_layout.addWidget(btn)
        
        self.details_layout.addLayout(action_layout)

    def setup_action_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        buttons = [
            ("➕ Ajouter", self.add_student, "primary"),
            ("✏️ Modifier", self.edit_student, "secondary"),
            ("🗑️ Supprimer", self.delete_student, "danger"),
            ("🔄 Actualiser", self.load_data, "default"),
            ("🖨️ Imprimer PDF", self.print_students_list, "success"),
        ]
        
        for text, callback, style in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setProperty("class", style)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(120)
            buttons_layout.addWidget(btn)
        
        parent_layout.addLayout(buttons_layout)

    def setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: palette(button);
                border-bottom: 1px solid palette(mid);
                padding: 4px;
            }
            QMenuBar::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        
        # Menu Fichier
        file_menu = menubar.addMenu("📁 Fichier")
        exit_action = QAction("🚪 Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu("✏️ Édition")
        edit_menu.addAction("➕ Ajouter étudiant", self.add_student)
        edit_menu.addAction("✏️ Modifier étudiant", self.edit_student)
        edit_menu.addAction("🗑️ Supprimer étudiant", self.delete_student)
        
        # Menu Gestion
        manage_menu = menubar.addMenu("⚙️ Gestion")
        manage_menu.addAction("🏛️ Gérer les facultés", self.manage_faculties)
        manage_menu.addAction("📚 Gérer les départements", self.manage_departments)
        manage_menu.addAction("🎓 Gérer les promotions", self.manage_promotions)
        
        # Menu Affichage
        view_menu = menubar.addMenu("👀 Affichage")
        view_menu.addAction("🎨 Changer le thème", self.toggle_theme)
        
        # Menu Aide
        help_menu = menubar.addMenu("❓ Aide")
        help_menu.addAction("ℹ️ À propos", self.show_about)

    def setup_theme_handler(self):
        # Détecter le thème du système
        palette = QApplication.palette()
        is_dark = palette.window().color().lightness() < 128
        initial_theme = "dark" if is_dark else "light"
        
        # Appliquer le thème sauvegardé ou le thème système
        saved_theme = self.settings.value("theme", initial_theme)
        self.apply_theme(saved_theme)
        
        # Connecter le signal de changement de thème
        self.theme_changed.connect(self.apply_theme)

    def apply_styles(self):
        # Style de base qui s'adaptera au thème
        base_style = """
            QMainWindow, QDialog {
                background: palette(window);
                color: palette(window-text);
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid palette(mid);
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background: palette(base);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: palette(window-text);
                font-weight: bold;
            }
            QTableView {
                gridline-color: palette(mid);
                alternate-background-color: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid palette(mid);
            }
            QTableView::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QHeaderView::section {
                background: palette(button);
                color: palette(button-text);
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton[class="primary"] {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton[class="secondary"] {
                background: #6c757d;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton[class="success"] {
                background: #28a745;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton[class="danger"] {
                background: #dc3545;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton[class="default"] {
                background: palette(button);
                color: palette(button-text);
                border: 1px solid palette(mid);
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                opacity: 0.8;
                transform: translateY(1px);
            }
            QFrame {
                background: palette(base);
                border-radius: 8px;
                border: 1px solid palette(mid);
            }
            QScrollArea {
                border: 1px solid palette(mid);
                border-radius: 8px;
                background: palette(base);
            }
            QComboBox, QLineEdit, QSpinBox {
                padding: 10px;
                border: 2px solid palette(mid);
                border-radius: 6px;
                background: palette(base);
                font-size: 11px;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
                border-color: palette(highlight);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QLabel {
                color: palette(window-text);
                font-size: 11px;
            }
            QToolBar {
                spacing: 5px;
                padding: 5px;
                background: palette(button);
                border-bottom: 1px solid palette(mid);
            }
            QStatusBar {
                background: palette(button);
                border-top: 1px solid palette(mid);
                padding: 5px;
            }
        """
        self.setStyleSheet(base_style)

    def apply_theme(self, theme_name):
        """Applique un thème light ou dark à l'application"""
        palette = QPalette()
        
        if theme_name == "dark":
            # Palette pour le thème sombre
            palette.setColor(QPalette.Window, QColor(45, 45, 48))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(30, 30, 30))
            palette.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
            palette.setColor(QPalette.ToolTipBase, QColor(40, 40, 40))
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(60, 60, 60))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(150, 150, 150))
            palette.setColor(QPalette.Mid, QColor(80, 80, 80))
        else:
            # Palette pour le thème clair
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(0, 0, 255))
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))
            palette.setColor(QPalette.Mid, QColor(200, 200, 200))
        
        QApplication.setPalette(palette)
        self.settings.setValue("theme", theme_name)
        
        # Recharger les styles pour s'assurer qu'ils s'adaptent au nouveau thème
        QTimer.singleShot(100, self.apply_styles)

    def toggle_theme(self):
        current_theme = self.settings.value("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.theme_changed.emit(new_theme)

    def load_settings(self):
        # Restaurer la géométrie de la fenêtre
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState"):
            self.restoreState(self.settings.value("windowState"))

    def closeEvent(self, event):
        # Sauvegarder la géométrie de la fenêtre
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        event.accept()

    # Les autres méthodes restent inchangées...
    def load_data(self):
        if self.loading_data:
            return
            
        self.loading_data = True
        self.statusBar.showMessage("Chargement des données...")
        
        try:
            # Charger les filtres
            self.load_filters()

            # Charger les étudiants avec les filtres actuels
            query = """
                SELECT s.*, p.name as promotion_name, d.name as department_name, 
                       f.name as faculty_name, p.year as promotion_year
                FROM students s
                JOIN promotions p ON s.promotion_id = p.id
                JOIN departments d ON p.department_id = d.id
                JOIN faculties f ON d.faculty_id = f.id
                WHERE 1=1
            """
            params = []
            
            faculty_id = self.faculty_filter.currentData()
            if faculty_id and faculty_id != -1:
                query += " AND f.id = %s"
                params.append(faculty_id)

            department_id = self.department_filter.currentData()
            if department_id and department_id != -1:
                query += " AND d.id = %s"
                params.append(department_id)
            
            promotion_id = self.promotion_filter.currentData()
            if promotion_id and promotion_id != -1:
                query += " AND p.id = %s"
                params.append(promotion_id)
            
            query += " ORDER BY s.last_name, s.first_name"
            
            students = self.db.execute_query(query, params)
            self.model = StudentsTableModel(students)
            self.students_table.setModel(self.model)
            
            # Ajuster la largeur des colonnes
            for column in range(self.model.columnCount(None)):
                if column == 1:  # Colonne photo
                    self.students_table.setColumnWidth(column, 60)
                else:
                    self.students_table.resizeColumnToContents(column)

            # Mettre à jour le statut
            self.statusBar.showMessage(f"✅ {len(students)} étudiant(s) trouvé(s)")
        
        except Exception as e:
            self.statusBar.showMessage(f"❌ Erreur lors du chargement: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données: {str(e)}")
        finally:
            self.loading_data = False

    def load_filters(self):
        # Bloquer les signaux pendant le chargement des filtres
        self.faculty_filter.blockSignals(True)
        self.department_filter.blockSignals(True)
        self.promotion_filter.blockSignals(True)
        
        try:
            # Charger les facultés
            faculties = self.db.execute_query("SELECT id, name FROM faculties ORDER BY name")
            self.faculty_filter.clear() 
            self.faculty_filter.addItem("🏛️ Toutes les facultés", -1)
            for faculty in faculties:
                self.faculty_filter.addItem(f"🏛️ {faculty['name']}", faculty['id'])
            
            # Charger les départements
            departments = self.db.execute_query("SELECT id, name FROM departments ORDER BY name")
            self.department_filter.clear()
            self.department_filter.addItem("📚 Tous les départements", -1)
            for dept in departments:
                self.department_filter.addItem(f"📚 {dept['name']}", dept['id'])
            
            # Charger les promotions
            promotions = self.db.execute_query("SELECT id, name, year FROM promotions ORDER BY year DESC, name")
            self.promotion_filter.clear()
            self.promotion_filter.addItem("🎓 Toutes les promotions", -1)
            for promo in promotions:
                self.promotion_filter.addItem(f"🎓 {promo['name']} ({promo['year']})", promo['id'])
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des filtres: {str(e)}")
        finally:
            # Réactiver les signaux
            self.faculty_filter.blockSignals(False)
            self.department_filter.blockSignals(False)
            self.promotion_filter.blockSignals(False)

    def reset_filters(self):
        self.faculty_filter.setCurrentIndex(0)
        self.department_filter.setCurrentIndex(0)
        self.promotion_filter.setCurrentIndex(0)
        self.load_data()

    def on_filter_changed(self):
        if not self.loading_data:
            self.load_data()

    def on_student_selected(self, index):
        if not index.isValid():
            return
            
        row = index.row()
        if 0 <= row < len(self.model.students):
            student = self.model.students[row]
            self.current_student_id = student['id']
            self.display_student_details(student)

    def display_student_details(self, student):
        # Afficher la photo
        pixmap = ImageUtils.load_image(student['photo_path'], (120, 120))
        if not pixmap.isNull():
            self.student_photo.setPixmap(pixmap)
            self.student_photo.setText("")
        else:
            self.student_photo.clear()
            self.student_photo.setText("❌ Photo non disponible")
        
        # Informations de base
        self.student_name.setText(f"{student['last_name']} {student['postnom']} {student['first_name']}")
        self.student_registration.setText(student['registration_number'])
        self.student_email.setText(student['email'] or "❌ Non renseigné")
        self.student_phone.setText(student['phone'] or "❌ Non renseigné")
        
        # Informations supplémentaires
        self.student_address.setText(student['address'] or "❌ Non renseigné")
        self.student_emergency_contact.setText(student['emergency_contact'] or "❌ Non renseigné")
        self.student_emergency_phone.setText(student['emergency_phone'] or "❌ Non renseigné")
        self.student_faculty.setText(student['faculty_name'])
        self.student_department.setText(student['department_name'])
        self.student_promotion.setText(f"{student['promotion_name']} ({student['promotion_year']})")

    def add_student(self):
        dialog = StudentDialog(self)
        dialog.resize(600, 700)  # Taille fixe pour le dialogue
        if dialog.exec():
            try:
                data = dialog.get_data()
                result = self.db.execute_query("""
                    INSERT INTO students (last_name, postnom, first_name, email, phone, address, 
                                        emergency_contact, emergency_phone, registration_number, 
                                        photo_path, promotion_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    data['last_name'], data['postnom'], data['first_name'], 
                    data['email'], data['phone'], data['address'],
                    data['emergency_contact'], data['emergency_phone'],
                    data['registration_number'], data['photo_path'],
                    data['promotion_id']
                ))
                
                if result:
                    QMessageBox.information(self, "Succès", "✅ Étudiant ajouté avec succès!")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Erreur", "❌ Échec de l'ajout de l'étudiant")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout: {str(e)}")

    def edit_student(self):
        if not self.current_student_id:
            QMessageBox.warning(self, "Avertissement", "⚠️ Veuillez sélectionner un étudiant à modifier")
            return
            
        try:
            # Récupérer les données actuelles de l'étudiant
            student = self.db.execute_query("""
                SELECT * FROM students WHERE id = %s
            """, (self.current_student_id,))
            
            if not student:
                QMessageBox.warning(self, "Erreur", "❌ Étudiant non trouvé")
                return
                
            student = student[0]
            dialog = StudentDialog(self, student)
            dialog.resize(600, 700)  # Taille fixe pour le dialogue
            
            if dialog.exec():
                data = dialog.get_data()
                self.db.execute_query("""
                    UPDATE students 
                    SET last_name = %s, postnom = %s, first_name = %s, 
                        email = %s, phone = %s, address = %s,
                        emergency_contact = %s, emergency_phone = %s,
                        registration_number = %s, photo_path = %s,
                        promotion_id = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    data['last_name'], data['postnom'], data['first_name'], 
                    data['email'], data['phone'], data['address'],
                    data['emergency_contact'], data['emergency_phone'],
                    data['registration_number'], data['photo_path'],
                    data['promotion_id'], self.current_student_id
                ))
                
                QMessageBox.information(self, "Succès", "✅ Étudiant modifié avec succès!")
                self.load_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification: {str(e)}")

    def delete_student(self):
        if not self.current_student_id:
            QMessageBox.warning(self, "Avertissement", "⚠️ Veuillez sélectionner un étudiant à supprimer")
            return
            
        reply = QMessageBox.question(
            self, "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cet étudiant ?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM students WHERE id = %s", (self.current_student_id,))
                QMessageBox.information(self, "Succès", "✅ Étudiant supprimé avec succès!")
                self.current_student_id = None
                self.clear_student_details()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

    def view_student_details(self):
        if not self.current_student_id:
            QMessageBox.warning(self, "Avertissement", "⚠️ Veuillez sélectionner un étudiant")
            return
            
        try:
            student = self.db.execute_query("""
                SELECT s.*, p.name as promotion_name, d.name as department_name, 
                       f.name as faculty_name, p.year as promotion_year
                FROM students s
                JOIN promotions p ON s.promotion_id = p.id
                JOIN departments d ON p.department_id = d.id
                JOIN faculties f ON d.faculty_id = f.id
                WHERE s.id = %s
            """, (self.current_student_id,))
            
            if student:
                self.display_student_details(student[0])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des détails: {str(e)}")

    def clear_student_details(self):
        self.student_photo.clear()
        self.student_photo.setText("Aucune photo sélectionnée")
        self.student_name.setText("Non sélectionné")
        self.student_registration.setText("-")
        self.student_email.setText("-")
        self.student_phone.setText("-")
        self.student_address.setText("-")
        self.student_emergency_contact.setText("-")
        self.student_emergency_phone.setText("-")
        self.student_faculty.setText("-")
        self.student_department.setText("-")
        self.student_promotion.setText("-")

    def print_students_list(self):
        try:
            # Récupérer tous les étudiants avec leurs informations complètes
            students = self.db.execute_query("""
                SELECT s.*, p.name as promotion_name, d.name as department_name, 
                       f.name as faculty_name, p.year as promotion_year
                FROM students s
                JOIN promotions p ON s.promotion_id = p.id
                JOIN departments d ON p.department_id = d.id
                JOIN faculties f ON d.faculty_id = f.id
                ORDER BY f.name, d.name, p.name, s.last_name, s.first_name
            """)
            
            if not students:
                QMessageBox.information(self, "Information", "Aucun étudiant à imprimer")
                return
                
            # Demander où sauvegarder le PDF
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le PDF", 
                f"liste_etudiants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                self.pdf_generator.generate_students_list(students, file_path)
                QMessageBox.information(self, "Succès", f"✅ PDF généré avec succès!\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du PDF: {str(e)}")

    def generate_student_report(self):
        if not self.current_student_id:
            QMessageBox.warning(self, "Avertissement", "⚠️ Veuillez sélectionner un étudiant")
            return
            
        try:
            student = self.db.execute_query("""
                SELECT s.*, p.name as promotion_name, d.name as department_name, 
                       f.name as faculty_name, p.year as promotion_year
                FROM students s
                JOIN promotions p ON s.promotion_id = p.id
                JOIN departments d ON p.department_id = d.id
                JOIN faculties f ON d.faculty_id = f.id
                WHERE s.id = %s
            """, (self.current_student_id,))
            
            if student:
                # Demander où sauvegarder le PDF
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Enregistrer le rapport", 
                    f"rapport_{student[0]['registration_number']}.pdf",
                    "PDF Files (*.pdf)"
                )
                
                if file_path:
                    self.pdf_generator.generate_student_report(student[0], file_path)
                    QMessageBox.information(self, "Succès", f"✅ Rapport généré avec succès!\n{file_path}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du rapport: {str(e)}")

    def manage_faculties(self):
        dialog = FacultyDialog(self)
        dialog.exec()
        self.load_filters()

    def manage_departments(self):
        dialog = DepartmentDialog(self)
        dialog.exec()
        self.load_filters()

    def manage_promotions(self):
        dialog = PromotionDialog(self)
        dialog.exec()
        self.load_filters()

    def show_about(self):
        QMessageBox.about(self, "À propos", 
            "🎓 Gestion des Étudiants - Université UNIKIN\n\n"
            "Version 2.0\n"
            "Application de gestion des étudiants avec interface moderne\n\n"
            "Fonctionnalités:\n"
            "• Gestion complète des étudiants\n"
            "• Filtres avancés par faculté/département/promotion\n"
            "• Génération de rapports PDF\n"
            "• Interface adaptative light/dark\n"
            "• Gestion des photos d'étudiants\n\n"
            "© 2024 Université UNIKIN"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Gestion des Étudiants - UNIKIN")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("UniversiteUNIKIN")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
