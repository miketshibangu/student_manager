from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from database import Database

class PDFGenerator:
    def __init__(self):
        self.db = Database()
        self.styles = getSampleStyleSheet()

        if 'Title' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Title',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centered
            ))

        if 'Header' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Header',
                parent=self.styles['Normal'],
                fontSize=12,
                spaceAfter=6,
                alignment=1
            ))

        if 'Footer' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                alignment=1
            ))

    def generate_student_report(self, student_data, output_path):
        """Génère un rapport PDF pour un étudiant spécifique"""
        try:
            # Créer le document PDF
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            elements = []
            
            # Titre
            elements.append(Paragraph("FICHE ÉTUDIANT - UNIVERSITÉ UNIKIN", self.styles['Title']))
            elements.append(Spacer(1, 20))
            
            # Table des informations de l'étudiant
            student_info = [
                ["Matricule:", student_data['registration_number']],
                ["Nom complet:", f"{student_data['last_name']} {student_data['postnom']} {student_data['first_name']}"],
                ["Email:", student_data['email'] or "Non renseigné"],
                ["Téléphone:", student_data['phone'] or "Non renseigné"],
                ["Adresse:", student_data['address'] or "Non renseigné"],
                ["Contact d'urgence:", student_data['emergency_contact'] or "Non renseigné"],
                ["Téléphone d'urgence:", student_data['emergency_phone'] or "Non renseigné"],
                ["Faculté:", student_data['faculty_name']],
                ["Département:", student_data['department_name']],
                ["Promotion:", f"{student_data['promotion_name']} ({student_data['promotion_year']})"],
                ["Date d'inscription:", student_data['created_at'].strftime("%d/%m/%Y") if hasattr(student_data['created_at'], 'strftime') else str(student_data['created_at'])]
            ]
            
            student_table = Table(student_info, colWidths=[2*inch, 3*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(student_table)
            
            # Ajouter la photo si elle existe
            if student_data.get('photo_path') and os.path.exists(student_data['photo_path']):
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Photo:", self.styles['Header']))
                try:
                    img = Image(student_data['photo_path'], width=2*inch, height=2*inch)
                    elements.append(img)
                except:
                    elements.append(Paragraph("Photo non disponible", self.styles['Normal']))
            
            # Pied de page
            elements.append(Spacer(1, 40))
            elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", self.styles['Footer']))
            
            # Générer le PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération du rapport: {e}")
            return False

    def generate_students_list(self, students, output_path):
        """Génère une liste PDF de tous les étudiants"""
        try:
            # Créer le document PDF
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            elements = []
            
            # Titre
            title = "LISTE DES ÉTUDIANTS - UNIVERSITÉ UNIKIN"
            elements.append(Paragraph(title, self.styles['Title']))
            elements.append(Spacer(1, 20))
            
            # En-tête du tableau
            if students:
                data = [["Matricule", "Nom", "Postnom", "Prénom", "Email", "Téléphone", "Promotion"]]
                
                for student in students:
                    data.append([
                        student['registration_number'],
                        student['last_name'],
                        student['postnom'],
                        student['first_name'],
                        student['email'] or "",
                        student['phone'] or "",
                        student['promotion_name']
                    ])
                
                table = Table(data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch, 1.2*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                elements.append(table)
            else:
                elements.append(Paragraph("Aucun étudiant trouvé.", self.styles['Normal']))
            
            # Pied de page
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Total: {len(students)} étudiant(s)", self.styles['Normal']))
            elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", self.styles['Footer']))
            
            # Générer le PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération de la liste: {e}")
            return False
