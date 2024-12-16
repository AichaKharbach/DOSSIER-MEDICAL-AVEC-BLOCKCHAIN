import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from web3 import Web3
from datetime import datetime
from contract_patient_interaction import *  
from contract_doctor_interaction import *  
from contract_audit_interaction import get_all_audit_logs  
from ipfs_utils import *

# Initialisation de Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  

class AdminInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interface Admin - Gestion Blockchain")
        self.setGeometry(200, 200, 800, 700)

        self.apply_medical_theme()

        self.admin_account = None
        self.file_path = None

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        self.btn_back = QPushButton("🔙 Retour")
        self.btn_back.clicked.connect(self.show_main_menu)

        self.setup_login_section()
        self.setup_patient_management()
        self.setup_doctor_management()
        self.setup_audit_logs()

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def setup_login_section(self):
        self.clear_layout()  
        
        self.label_welcome = QLabel("Bienvenue, Admin ! Entrez votre adresse Ethereum pour vous connecter.")
        self.layout.addWidget(self.label_welcome)

        self.input_admin_address = QLineEdit(self)
        self.input_admin_address.setPlaceholderText("Adresse Ethereum")
        self.layout.addWidget(self.input_admin_address)

        self.btn_login = QPushButton("🔑 Connexion")
        self.btn_login.clicked.connect(self.admin_login)
        self.layout.addWidget(self.btn_login)

    # --- MENU PRINCIPAL ---
    def show_main_menu(self):
        self.clear_layout()
        self.label_menu = QLabel(f"Vous êtes connecté(e) en tant qu'administrateur.")
        self.layout.addWidget(self.label_menu)

        self.btn_manage_patients = QPushButton("👨‍💼 Gestion des Patients")
        self.btn_manage_patients.clicked.connect(self.show_patient_form)
        self.layout.addWidget(self.btn_manage_patients)

        self.btn_manage_doctors = QPushButton("🩺 Gestion des Médecins")
        self.btn_manage_doctors.clicked.connect(self.show_doctor_form)
        self.layout.addWidget(self.btn_manage_doctors)

        self.btn_audit_logs = QPushButton("📜 Accéder aux Historiques")
        self.btn_audit_logs.clicked.connect(self.show_logs_table)
        self.layout.addWidget(self.btn_audit_logs)

        self.btn_logout = QPushButton("🚪 Déconnexion")
        self.btn_logout.clicked.connect(self.logout)
        self.layout.addWidget(self.btn_logout)

    # --- FORMULAIRE GESTION DES PATIENTS ---
    def setup_patient_management(self):
        
        self.group_patient = QGroupBox("📝 Création d'un Patient")
        self.group_patient.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #1c4966;
                border: 2px solid #4da8da;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        self.input_patient_address = QLineEdit()
        self.input_patient_address.setPlaceholderText("Adresse Ethereum du Patient")

        self.input_patient_name = QLineEdit()
        self.input_patient_name.setPlaceholderText("Nom complet du Patient")

        self.input_patient_dob = QLineEdit()
        self.input_patient_dob.setPlaceholderText("Date de naissance (JJ-MM-AAAA)")

        self.input_patient_file = QLineEdit()
        self.input_patient_file.setPlaceholderText("Sélectionner un fichier médical")
        self.input_patient_file.setReadOnly(True)

        self.btn_browse_file = QPushButton("📂 Parcourir")
        self.btn_browse_file.clicked.connect(self.browse_file)

        self.btn_create_patient = QPushButton("✅ Créer le Patient")
        self.btn_create_patient.clicked.connect(self.create_patient)

        self.btn_list_patients = QPushButton("📋 Lister Tous les Patients")
        self.btn_list_patients.clicked.connect(self.list_all_patients)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Adresse Ethereum du Patient :"))
        form_layout.addWidget(self.input_patient_address)
        form_layout.addWidget(QLabel("Nom Complet :"))
        form_layout.addWidget(self.input_patient_name)
        form_layout.addWidget(QLabel("Date de Naissance :"))
        form_layout.addWidget(self.input_patient_dob)
        form_layout.addWidget(QLabel("Fichier Médical :"))

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.input_patient_file)
        file_layout.addWidget(self.btn_browse_file)
        form_layout.addLayout(file_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_create_patient)
        btn_layout.addWidget(self.btn_list_patients)
        form_layout.addLayout(btn_layout)

        self.group_patient.setLayout(form_layout)


    def show_patient_form(self):
        self.clear_layout()  
        self.setup_patient_management()  
        self.layout.addWidget(self.group_patient) 
        self.reset_back_button(self.show_main_menu)  
        self.layout.addWidget(self.btn_back)

    def setup_doctor_management(self):
        self.group_doctor = QGroupBox("🩺 Création d'un Médecin")
        self.group_doctor.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #1c4966;
                border: 2px solid #4da8da;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        self.input_doctor_address = QLineEdit()
        self.input_doctor_address.setPlaceholderText("Adresse Ethereum du Médecin")

        self.input_doctor_name = QLineEdit()
        self.input_doctor_name.setPlaceholderText("Nom complet du Médecin")

        self.input_doctor_specialty = QLineEdit()
        self.input_doctor_specialty.setPlaceholderText("Spécialité du Médecin")

        self.btn_create_doctor = QPushButton("✅ Créer le Médecin")
        self.btn_create_doctor.clicked.connect(self.create_doctor)

        self.btn_list_doctors = QPushButton("📋 Lister Tous les Médecins")
        self.btn_list_doctors.clicked.connect(self.show_doctor_list)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Adresse Ethereum du Médecin :"))
        form_layout.addWidget(self.input_doctor_address)
        form_layout.addWidget(QLabel("Nom Complet :"))
        form_layout.addWidget(self.input_doctor_name)
        form_layout.addWidget(QLabel("Spécialité du Médecin :"))
        form_layout.addWidget(self.input_doctor_specialty)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_create_doctor)
        btn_layout.addWidget(self.btn_list_doctors)
        form_layout.addLayout(btn_layout)

        self.group_doctor.setLayout(form_layout)


    def show_doctor_form(self):
        self.clear_layout()
        self.setup_doctor_management()
        self.layout.addWidget(self.group_doctor)
        self.reset_back_button(self.show_main_menu)  
        self.layout.addWidget(self.btn_back)

    # --- TABLE DES LOGS ---
    def setup_audit_logs(self):
        """
        Configure la table des logs avec un design amélioré.
        """
        self.label_logs = QLabel("Historique des Actions (Logs d'Audit)")
        self.label_logs.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333333;")

        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(4)
        self.table_logs.setHorizontalHeaderLabels(["Utilisateur", "Action", "Détails", "Horodatage"])

        self.table_logs.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #4da8da;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

        self.table_logs.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                background-color: #f9f9f9;
                border: 1px solid #b0c4de;
                gridline-color: #b0c4de;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e1f5fe;
            }
        """)

        self.table_logs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_logs.verticalHeader().setDefaultSectionSize(40)  # Hauteur des lignes
        self.table_logs.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Empêcher l'édition des cellules
        self.table_logs.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.btn_refresh_logs = QPushButton("Rafraîchir les Logs")
        self.btn_refresh_logs.setStyleSheet("""
            QPushButton {
                background-color: #4da8da;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e86c1;
            }
        """)
        self.btn_refresh_logs.clicked.connect(self.load_audit_logs)

    def show_logs_table(self):
        """
        Affiche la table des logs dans l'interface avec le design amélioré.
        """
        self.clear_layout()
        self.layout.addWidget(self.label_logs)
        self.layout.addWidget(self.table_logs)
        self.layout.addWidget(self.btn_refresh_logs)
        self.reset_back_button(self.show_main_menu)
        self.layout.addWidget(self.btn_back)

        self.load_audit_logs()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def reset_back_button(self, target_method):
        """
        Réinitialise le bouton Retour pour pointer vers une méthode cible.
        """
        try:
            self.btn_back.clicked.disconnect() 
        except TypeError:
            pass  
        self.btn_back.clicked.connect(target_method)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", "All Files (*)")
        if file_path:
            self.file_path = file_path
            self.input_patient_file.setText(file_path)

    def admin_login(self):
        admin_address = self.input_admin_address.text()
        if not admin_address or not w3.isAddress(admin_address):
            QMessageBox.warning(self, "Erreur", "Adresse Ethereum invalide.")
            return

        self.admin_address = admin_address
        self.admin_account = {"address": admin_address}
        self.show_main_menu()


    def logout(self):
        """
        Déconnecte l'admin et revient à l'écran de connexion.
        """
        QMessageBox.information(self, "Déconnexion", "Vous avez été déconnecté avec succès.")
        self.admin_account = None
        self.setup_login_section()

    def create_patient(self): 
        patient_address = self.input_patient_address.text()
        name = self.input_patient_name.text()
        dob = self.input_patient_dob.text()

        if not patient_address or not name or not dob or not self.file_path:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        try:
            private_key, public_key = generate_key_pair()

            nonce, tag, ciphertext, encrypted_aes_key = encrypt_file(self.file_path, public_key)

            result = upload_encrypted_file_to_pinata(nonce, tag, ciphertext, encrypted_aes_key, PINATA_JWT_TOKEN)
            ipfs_hash = result["IpfsHash"]

            register_patient(patient_address, name, dob, ipfs_hash)

            save_private_key_backend(patient_address, private_key)

            QMessageBox.information(self, "Succès", f"Patient créé avec succès : {patient_address}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création du patient : {str(e)}")

    def create_doctor(self):
        doctor_address = self.input_doctor_address.text()
        name = self.input_doctor_name.text()
        specialty = self.input_doctor_specialty.text()

        if not doctor_address or not name or not specialty:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires pour créer un médecin.")
            return

        try:
            register_doctor(doctor_address, name, specialty)
            QMessageBox.information(self, "Succès", f"Médecin créé avec succès : {name}, Spécialité : {specialty}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


    def load_audit_logs(self):
        self.table_logs.setRowCount(0)
        logs = get_all_audit_logs()
        for row, log in enumerate(logs):
            self.table_logs.insertRow(row)
            self.table_logs.setItem(row, 0, QTableWidgetItem(log["userAddress"]))
            self.table_logs.setItem(row, 1, QTableWidgetItem(log["action"]))
            self.table_logs.setItem(row, 2, QTableWidgetItem(log["details"]))
            timestamp = datetime.fromtimestamp(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            self.table_logs.setItem(row, 3, QTableWidgetItem(timestamp))

    def list_all_patients(self):
        """
        Affiche une table avec les patients, harmonisée avec le design des médecins.
        """
        try:
            patients = get_list_patients()

            self.table_patients = QTableWidget()
            self.table_patients.setColumnCount(5)
            self.table_patients.setHorizontalHeaderLabels([
                "Adresse Ethereum", "Nom Complet", "Date de Naissance", "Hash du Fichier", "Action"
            ])

            self.table_patients.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #4da8da;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 6px;
                    border: none;
                }
            """)
            self.table_patients.setStyleSheet("""
                QTableWidget {
                    font-size: 13px;
                    background-color: #f9f9f9;
                    border: 1px solid #b0c4de;
                }
                QTableWidget::item {
                    padding: 5px;
                }
            """)

            self.table_patients.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_patients.verticalHeader().setDefaultSectionSize(50)  # Hauteur des lignes
            self.table_patients.setEditTriggers(QAbstractItemView.NoEditTriggers)

            self.table_patients.setRowCount(len(patients))
            for row, patient in enumerate(patients):
                self.table_patients.setItem(row, 0, QTableWidgetItem(patient["address"]))
                self.table_patients.setItem(row, 1, QTableWidgetItem(patient["name"]))
                self.table_patients.setItem(row, 2, QTableWidgetItem(patient["dob"]))
                self.table_patients.setItem(row, 3, QTableWidgetItem(patient["hash"]))

                btn_delete = QPushButton("Supprimer")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4d4f;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e63946;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, addr=patient["address"]: self.delete_patient(addr))

                button_container = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(btn_delete)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                button_container.setLayout(layout)
                self.table_patients.setCellWidget(row, 4, button_container)

            self.clear_layout()
            title_label = QLabel("Liste des Patients")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333333;")
            self.layout.addWidget(title_label)
            self.layout.addWidget(self.table_patients)
            self.reset_back_button(self.show_patient_form)
            self.layout.addWidget(self.btn_back)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des patients : {e}")

    def delete_patient(self, patient_address):
        """
        Supprime un patient sélectionné dans la liste après confirmation.
        """
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer le patient avec l'adresse : {patient_address} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                success = delete_patient(patient_address, self.admin_account['address'])
                
                if success:
                    QMessageBox.information(self, "Succès", "Patient supprimé avec succès.")
                    self.list_all_patients()  
                else:
                    QMessageBox.warning(self, "Échec", "La suppression du patient a échoué.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def show_doctor_list(self):
        """
        Affiche la liste des médecins. Si la liste est vide, elle affiche une table vide sans message.
        """
        try:
            doctors = get_list_doctors()

            self.table_doctors = QTableWidget()
            self.table_doctors.setColumnCount(4)  
            self.table_doctors.setHorizontalHeaderLabels([
                "Adresse Ethereum", "Nom", "Spécialité", "Action"
            ])

            self.table_doctors.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #4da8da;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            self.table_doctors.setStyleSheet("""
                QTableWidget {
                    font-size: 12px;
                    background-color: #f9f9f9;
                    border: 1px solid #b0c4de;
                }
            """)
            self.table_doctors.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_doctors.verticalHeader().setDefaultSectionSize(40)
            self.table_doctors.setEditTriggers(QAbstractItemView.NoEditTriggers)
            
            self.table_doctors.setRowCount(len(doctors))
            for row, doctor in enumerate(doctors):
                self.table_doctors.setItem(row, 0, QTableWidgetItem(doctor["address"]))
                self.table_doctors.setItem(row, 1, QTableWidgetItem(doctor["name"]))
                self.table_doctors.setItem(row, 2, QTableWidgetItem(doctor["specialty"]))

                btn_delete = QPushButton("Supprimer")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4d4f;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e63946;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, addr=doctor["address"]: self.delete_doctor(addr))

                button_container = QWidget()
                button_layout = QHBoxLayout()
                button_layout.addWidget(btn_delete)
                button_layout.setAlignment(Qt.AlignCenter)
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_container.setLayout(button_layout)
                self.table_doctors.setCellWidget(row, 3, button_container)

            self.clear_layout()
            title_label = QLabel("Liste des Médecins")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333333;")
            self.layout.addWidget(title_label)
            self.layout.addWidget(self.table_doctors)

            self.reset_back_button(self.show_doctor_form)
            self.layout.addWidget(self.btn_back)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des médecins : {e}")


    def delete_doctor(self, doctor_address):
        """
        Supprime un médecin sélectionné et rafraîchit automatiquement la liste.
        """
        confirmation = QMessageBox.question(
            self, "Confirmation", f"Voulez-vous vraiment supprimer le médecin {doctor_address} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            success = delete_doctor(doctor_address, self.admin_account['address'])
            if success:
                QMessageBox.information(self, "Succès", f"Le médecin {doctor_address} a été supprimé.")
                self.show_doctor_list()  
            else:
                QMessageBox.critical(self, "Erreur", "La suppression du médecin a échoué.")

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
                border: 1px solid #4da8da;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2e86c1;
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

