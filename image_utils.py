import os
from PIL import Image
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import shutil

class ImageUtils:
    @staticmethod
    def select_image(parent, current_path=None):
        file_path, _ = QFileDialog.getOpenFileName(
            parent, 
            "Sélectionner une photo", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Créer le dossier de destination s'il n'existe pas
            dest_dir = "data/images/students"
            os.makedirs(dest_dir, exist_ok=True)
            
            # Générer un nom de fichier unique
            filename = f"student_{os.path.splitext(os.path.basename(file_path))[0]}_{os.urandom(4).hex()}{os.path.splitext(file_path)[1]}"
            dest_path = os.path.join(dest_dir, filename)
            
            try:
                # Redimensionner et sauvegarder l'image
                with Image.open(file_path) as img:
                    img.thumbnail((300, 300))  # Redimensionner tout en gardant les proportions
                    img.save(dest_path)
                
                return dest_path
            except Exception as e:
                QMessageBox.warning(parent, "Erreur", f"Impossible de traiter l'image: {str(e)}")
                return current_path
        
        return current_path

    @staticmethod
    def load_image(image_path, size=(150, 150)):
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return pixmap
        else:
            # Retourner une image par défaut si aucune image n'est disponible
            pixmap = QPixmap(size[0], size[1])
            pixmap.fill(Qt.lightGray)
            return pixmap
