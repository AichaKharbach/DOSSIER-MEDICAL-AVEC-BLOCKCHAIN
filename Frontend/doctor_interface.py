import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QFileDialog,QGroupBox,QHeaderView
)

from contract_doctor_interaction import get_doctor_info, get_patients_for_doctor
from contract_patient_interaction import update_patient_record_by_doctor
from ipfs_utils import *


class DoctorInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.apply_medical_theme() 

        self.setWindowTitle("Interface Docteur - Gestion des Patients")
        self.setGeometry(200, 200, 600, 500)

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        self.label_welcome = QLabel("Bienvenue, Docteur ! Veuillez entrer votre adresse Ethereum pour vous connecter.")
        self.layout.addWidget(self.label_welcome)

        self.input_doctor_address = QLineEdit(self)
        self.input_doctor_address.setPlaceholderText("Adresse Ethereum du Docteur")
        self.layout.addWidget(self.input_doctor_address)

        self.btn_login = QPushButton("🔑 Connexion")
        self.btn_login.clicked.connect(self.login)
        self.layout.addWidget(self.btn_login)

        self.group_box_doctor_info = QGroupBox("Informations du Docteur")
        self.group_box_doctor_info.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #1c4966;
                border: 2px solid #4da8da;
                border-radius: 10px;
                padding: 10px;
                background-color: #f0f5f9;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
        """)
        self.group_box_layout = QVBoxLayout()

        self.output_doctor_info = QLabel("")
        self.output_doctor_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #555555;
                padding: 5px;
            }
        """)
        self.group_box_layout.addWidget(self.output_doctor_info)

        self.group_box_doctor_info.setLayout(self.group_box_layout)
        self.layout.addWidget(self.group_box_doctor_info)
        self.group_box_doctor_info.hide()

        self.label_patient_list = QLabel("\nListe des Patients")
        self.layout.addWidget(self.label_patient_list)
        self.label_patient_list.hide()

        self.table_patients = QTableWidget()
        self.table_patients.setColumnCount(4)
        self.table_patients.setHorizontalHeaderLabels(["Nom", "Date de naissance", "Hash IPFS", "Update Dossier"])
        self.layout.addWidget(self.table_patients)
        self.table_patients.hide()

        self.btn_logout = QPushButton("🚪 Déconnexion")
        self.btn_logout.clicked.connect(self.logout)
        self.layout.addWidget(self.btn_logout)
        self.btn_logout.hide()

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        self.doctor_address = None

    def login(self):
        doctor_address = self.input_doctor_address.text()

        if not doctor_address:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une adresse Ethereum.")
            return

        try:
            doctor_info = get_doctor_info(doctor_address)

            if not doctor_info or not doctor_info["isRegistered"]:
                QMessageBox.warning(self, "Erreur", "Docteur non enregistré.")
                return

            self.doctor_address = doctor_address
            self.output_doctor_info.setText(
                f"Nom : {doctor_info['name']}\nSpécialité : {doctor_info['specialty']}\n"
            )

            self.label_welcome.hide()  
            self.input_doctor_address.hide()
            self.btn_login.hide()
            self.show_patient_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite : {e}")


    def show_patient_list(self):
        self.input_doctor_address.hide()
        self.btn_login.hide()

        self.group_box_doctor_info.show()

        self.label_patient_list.show()
        self.table_patients.show()
        self.btn_logout.show()

        self.load_patient_data()

    def load_patient_data(self):
        self.table_patients.setRowCount(0)
        self.table_patients.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #4da8da;
                border-radius: 8px;
                gridline-color: #cce7f0;
                font-size: 12px;
                color: #1c4966;
            }
            QHeaderView::section {
                background-color: #4da8da;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)

        try:
            patients = get_patients_for_doctor(self.doctor_address)

            if not patients:
                QMessageBox.information(self, "Information", "Aucun patient ne vous a accordé d'accès.")
                return

            self.table_patients.setColumnCount(4)
            self.table_patients.setHorizontalHeaderLabels(["Nom", "Date de naissance", "Update Dossier", "Télécharger"])

            self.table_patients.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_patients.verticalHeader().setDefaultSectionSize(60) 

            for row, patient in enumerate(patients):
                self.table_patients.insertRow(row)
                self.table_patients.setItem(row, 0, QTableWidgetItem(patient["name"]))
                self.table_patients.setItem(row, 1, QTableWidgetItem(patient["dateOfBirth"]))

                btn_update = QPushButton("📝 Update")
                btn_update.setStyleSheet("""
                    QPushButton {
                        background-color: #4da8da;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 14px;  /* Taille de l'écriture augmentée */
                    }
                    QPushButton:hover {
                        background-color: #2e86c1;
                    }
                """)
                btn_update.clicked.connect(lambda _, p=patient: self.open_update_form(p))
                self.table_patients.setCellWidget(row, 2, btn_update)

                btn_download = QPushButton("📥 Télécharger")
                btn_download.setStyleSheet("""
                    QPushButton {
                        background-color: #2e86c1;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 14px;  /* Taille de l'écriture augmentée */
                    }
                    QPushButton:hover {
                        background-color: #1c4966;
                    }
                """)
                btn_download.clicked.connect(lambda _, p=patient: self.download_and_decrypt_patient_file(p))
                self.table_patients.setCellWidget(row, 3, btn_download)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des patients : {e}")

    def download_and_decrypt_patient_file(self, patient):
        """
        Télécharger et déchiffrer le fichier médical d'un patient en utilisant la clé privée du médecin.
        """
        try:
            ipfs_hash = patient.get("ipfsHash", "")
            if not ipfs_hash:
                QMessageBox.warning(self, "Erreur", "Aucun fichier n'est associé à ce patient.")
                return

            encrypted_data = download_from_pinata(ipfs_hash, PINATA_JWT_TOKEN)

            private_key_path = f"keys/{self.doctor_address}_private.pem"
            if not os.path.exists(private_key_path):
                QMessageBox.warning(self, "Erreur", "Votre clé privée n'a pas été trouvée.")
                return

            with open(private_key_path, "r") as file:
                private_key = file.read()

            decrypted_data = decrypt_file(encrypted_data, private_key)

            save_path = os.path.join(os.getcwd(), f"fichier_{patient['name']}_dechiffre.txt")
            with open(save_path, "w") as file:
                file.write(decrypted_data)

            QMessageBox.information(
                self, "Succès", f"Fichier déchiffré avec succès et sauvegardé à :\n{save_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors du téléchargement/déchiffrement : {str(e)}"
            )


    def open_update_form(self, patient): 
        """Affiche un formulaire pour mettre à jour les informations du patient."""

        self.table_patients.hide()
        self.label_patient_list.hide()
        self.group_box_doctor_info.hide()  
        self.btn_logout.hide()

        self.update_form_layout = QFormLayout()

        self.name_input = QLineEdit(patient["name"])
        self.dob_input = QLineEdit(patient["dateOfBirth"])

        self.ipfs_label = QLabel(patient["ipfsHash"] if patient["ipfsHash"] else "Aucun fichier sélectionné")
        self.ipfs_label.setVisible(False)  

        self.btn_browse = QPushButton("📁 Parcourir...")
        self.btn_browse.clicked.connect(self.browse_file)

        self.update_form_layout.addRow("Nom :", self.name_input)
        self.update_form_layout.addRow("Date de naissance :", self.dob_input)
        self.update_form_layout.addRow("Fichier :", self.ipfs_label)  
        self.update_form_layout.addRow("", self.btn_browse)

        self.btn_save = QPushButton("✅ Enregistrer")
        self.btn_save.clicked.connect(lambda: self.save_patient_info(patient))
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.clicked.connect(self.cancel_update)

        self.update_form_layout.addRow("", self.btn_save)
        self.update_form_layout.addRow("", self.btn_cancel)

        self.update_form_widget = QWidget()
        self.update_form_widget.setLayout(self.update_form_layout)
        self.layout.addWidget(self.update_form_widget)


    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path:
            self.ipfs_file_path = file_path
            self.ipfs_label.setText(os.path.basename(file_path))

    def save_patient_info(self, patient):
        """Sauvegarde les modifications apportées au dossier du patient."""
        new_name = self.name_input.text()
        new_dob = self.dob_input.text()
        new_ipfs_hash = self.ipfs_label.text()

        try:
            update_patient_record_by_doctor(
                doctor_address=self.doctor_address,
                patient_address=patient["address"],
                name=new_name,
                date_of_birth=new_dob,
                ipfs_hash=new_ipfs_hash
            )
            QMessageBox.information(self, "Succès", "Dossier patient mis à jour avec succès.")
            self.layout.removeWidget(self.update_form_widget)
            self.update_form_widget.deleteLater()
            self.update_form_widget = None
            self.show_patient_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la mise à jour : {e}")

    def cancel_update(self):
        """Annule la mise à jour et revient à la liste des patients."""
        self.layout.removeWidget(self.update_form_widget)
        self.update_form_widget.deleteLater()
        self.update_form_widget = None

        self.group_box_doctor_info.show()
        self.show_patient_list()

    def logout(self):
        """Déconnecte le docteur et réinitialise l'interface."""
 
        self.doctor_address = None
        self.output_doctor_info.clear()
        self.group_box_doctor_info.hide()
        self.label_patient_list.hide()
        self.table_patients.hide()
        self.btn_logout.hide()
        self.label_welcome.show()
        self.input_doctor_address.clear() 
        self.input_doctor_address.show()
        self.btn_login.show()

        QMessageBox.information(self, "Déconnexion", "Vous êtes déconnecté.")

    
    def apply_medical_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5f9;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #1c4966;
            }
            QLineEdit {
                border: 2px solid #4da8da;
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
                color: #000000;
            }
            QTableWidget {
                background-color: white;
                border: 2px solid #4da8da;
                border-radius: 10px;
                font-size: 12px;
                color: #333333;
            }
            QTableWidget QHeaderView::section {
                background-color: #4da8da;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4da8da, stop:1 #2e86c1
                );
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e86c1;
            }
            QPushButton:pressed {
                background-color: #1c4966;
            }
        """)
