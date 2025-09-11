import sys
import os
import platform
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui_main_window import MainWindow

# Créer les dossiers nécessaires
os.makedirs("data/images/students", exist_ok=True)

def get_icon_path():
    """Retourne le chemin de l'icône selon le système d'exploitation"""
    base_dir = Path(__file__).parent
    system = platform.system()
    
    if system == "Windows":
        return str(base_dir / "assets" / "icons" / "app_icon.ico")
    elif system == "Darwin":  # macOS
        return str(base_dir / "assets" / "icons" / "app_icon.icns")
    else:  # Linux et autres
        return str(base_dir / "assets" / "icons" / "app_icon.png")

def main():
    app = QApplication(sys.argv)
    
    # Définir l'icône de l'application
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        print(f"Icône chargée depuis : {icon_path}")
    else:
        print(f"Attention : fichier d'icône introuvable à {icon_path}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
