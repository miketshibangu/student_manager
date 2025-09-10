import sys
import os
from PySide6.QtWidgets import QApplication
from ui_main_window import MainWindow

# Créer les dossiers nécessaires
os.makedirs("data/images/students", exist_ok=True)

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
