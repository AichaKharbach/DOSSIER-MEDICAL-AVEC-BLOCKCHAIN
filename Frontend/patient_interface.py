import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QTextEdit, QComboBox, QGroupBox
)
from contract_patient_interaction import *
from ipfs_utils import *

class PatientInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interface Patient - Gestion Dossier Médical")
        self.setGeometry(200, 200, 600, 500)

        self.apply_medical_theme()

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        self.label_welcome = QLabel("Bienvenue ! Veuillez entrer votre adresse Ethereum pour accéder à vos données.")
        self.layout.addWidget(self.label_welcome)

        self.input_patient_address = QLineEdit(self)
        self.input_patient_address.setPlaceholderText("Adresse Ethereum du Patient")
        self.layout.addWidget(self.input_patient_address)

        self.btn_login = QPushButton("🔑 Connexion")
        self.btn_login.clicked.connect(self.login)
        self.layout.addWidget(self.btn_login)

        self.group_box_patient_info = QGroupBox("📝 Informations du Patient")
        self.group_box_patient_info.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #1c4966;
                border: 2px solid #4da8da;
                border-radius: 10px;
                padding: 10px;
                background-color: #f0f5f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        self.group_box_layout = QVBoxLayout()

        self.output_patient_info = QTextEdit()
        self.output_patient_info.setReadOnly(True)
        self.output_patient_info.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #4da8da;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                color: #333333;
            }
        """)
        self.group_box_layout.addWidget(self.output_patient_info)

        self.btn_download_decrypt = QPushButton("📥 Télécharger et Déchiffrer le Fichier Médical")
        self.btn_download_decrypt.clicked.connect(self.download_and_decrypt_file)
        self.group_box_layout.addWidget(self.btn_download_decrypt)

        self.group_box_patient_info.setLayout(self.group_box_layout)
        self.group_box_patient_info.hide()

        self.layout.addWidget(self.group_box_patient_info)

        self.label_doctor_list = QLabel("\nListe des Médecins")
        self.layout.addWidget(self.label_doctor_list)
        self.label_doctor_list.hide()

        self.dropdown_doctors = QComboBox(self)
        self.layout.addWidget(self.dropdown_doctors)
        self.dropdown_doctors.hide()

        self.btn_grant_access = QPushButton("✅ Donner l'accès")
        self.btn_grant_access.clicked.connect(self.grant_access)
        self.layout.addWidget(self.btn_grant_access)
        self.btn_grant_access.hide()

        self.btn_revoke_access = QPushButton("❌ Révoquer l'accès")
        self.btn_revoke_access.clicked.connect(self.revoke_access)
        self.layout.addWidget(self.btn_revoke_access)
        self.btn_revoke_access.hide()

        self.btn_logout = QPushButton("🚪 Déconnexion")
        self.btn_logout.clicked.connect(self.logout)
        self.layout.addWidget(self.btn_logout)
        self.btn_logout.hide()

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def login(self):
        patient_address = self.input_patient_address.text()

        if not patient_address:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une adresse Ethereum.")
            return

        try:
            patient_info = get_patient(patient_address)
            self.patient_address = patient_address

            self.private_key = self.retrieve_patient_private_key(patient_address)

            formatted_info = (
                f"Adresse : {patient_info['address']}\n"
                f"Nom : {patient_info['name']}\n"
                f"Date de naissance : {patient_info['dateOfBirth']}"
            )
            self.output_patient_info.setText(formatted_info)

            QMessageBox.information(self, "Succès", "Connexion réussie !")
            self.show_patient_interface()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def retrieve_patient_private_key(self, patient_address):
        """
        Récupérer automatiquement la clé privée du patient depuis le backend.
        :param patient_address: Adresse Ethereum du patient.
        :return: Clé privée RSA.
        """
        try:
            key_path = f"keys/{patient_address}_private.pem"
            if os.path.exists(key_path):
                with open(key_path, "r") as file:
                    return file.read()
            else:
                raise Exception("Clé privée non trouvée.")
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération de la clé privée : {str(e)}")


    def download_and_decrypt_file(self):
        """
        Télécharger et déchiffrer automatiquement le fichier médical depuis IPFS.
        """
        try:
            patient_info = get_patient(self.patient_address)
            ipfs_hash = patient_info.get("ipfsHash", "")

            if not ipfs_hash:
                QMessageBox.warning(self, "Erreur", "Aucun fichier n'est associé à ce patient.")
                return

            encrypted_data = download_from_pinata(ipfs_hash, PINATA_JWT_TOKEN)

            private_key = self.retrieve_patient_private_key(self.patient_address)

            decrypted_data = decrypt_file(encrypted_data, private_key)

            save_path = os.path.join(os.getcwd(), "fichier_medical_dechiffre.txt")
            with open(save_path, "w") as file:
                file.write(decrypted_data)

            QMessageBox.information(self, "Succès", f"Fichier déchiffré avec succès et sauvegardé à :\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du téléchargement/déchiffrement : {str(e)}")


    def show_patient_interface(self):
        self.label_welcome.hide()
        self.input_patient_address.hide()
        self.btn_login.hide()

        self.group_box_patient_info.show()

        self.label_doctor_list.show()
        self.dropdown_doctors.show()
        self.btn_grant_access.show()
        self.btn_revoke_access.show()
        self.btn_logout.show()

        self.load_doctor_list()


    def load_doctor_list(self):
        try:
            doctors = get_all_doctors()  
            self.dropdown_doctors.clear()
            if not doctors:
                QMessageBox.information(self, "Information", "Aucun médecin enregistré trouvé.")
            else:
                for doctor in doctors:
                    name_specialty = f"{doctor[1]} ({doctor[2]})"  # Exemple : Dr. Adam (Cardiologue)
                    ethereum_address = doctor[0]  # Adresse Ethereum
                    # Ajouter le nom à afficher et associer l'adresse en tant que donnée cachée
                    self.dropdown_doctors.addItem(name_specialty, ethereum_address)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des docteurs : {e}")


    def grant_access(self):
        selected_index = self.dropdown_doctors.currentIndex()
        if selected_index < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un médecin.")
            return

        try:
            doctor_address = self.dropdown_doctors.itemData(selected_index)
            if not doctor_address:
                QMessageBox.warning(self, "Erreur", "Impossible de récupérer l'adresse du médecin.")
                return

            grant_permission(self.patient_address, doctor_address)
            QMessageBox.information(self, "Succès", "Accès accordé avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'attribution de la permission : {str(e)}")

    def revoke_access(self):
        selected_index = self.dropdown_doctors.currentIndex()
        if selected_index < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un médecin.")
            return

        try:
            doctor_address = self.dropdown_doctors.itemData(selected_index)
            if not doctor_address:
                QMessageBox.warning(self, "Erreur", "Impossible de récupérer l'adresse du médecin.")
                return

            revoke_permission(self.patient_address, doctor_address)
            QMessageBox.information(self, "Succès", f"Accès révoqué pour le médecin sélectionné.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la révocation de l'accès : {str(e)}")


    def logout(self):
        self.patient_address = None
        self.output_patient_info.clear()

        self.group_box_patient_info.hide()
        self.label_doctor_list.hide()
        self.dropdown_doctors.hide()
        self.btn_grant_access.hide()
        self.btn_revoke_access.hide()
        self.btn_logout.hide()

        self.label_welcome.show()
        self.input_patient_address.clear()  
        self.input_patient_address.show()
        self.btn_login.show()

        # Message de confirmation
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
            QLineEdit, QComboBox {
                border: 2px solid #4da8da;
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
                color: #000000; /* Texte en noir */
            }
            QComboBox:hover {
                border: 2px solid #2e86c1;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #4da8da;
                selection-background-color: #e9f5fc;
                selection-color: #000000; /* Texte sélectionné en noir */
                background-color: white;
                color: #000000; /* Texte normal en noir */
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
            }
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4da8da, stop:1 #2e86c1
                );
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                margin-top: 10px;
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
