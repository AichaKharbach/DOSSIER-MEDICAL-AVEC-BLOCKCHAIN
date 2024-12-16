import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from admin_interface import AdminInterface
from patient_interface import PatientInterface
from doctor_interface import DoctorInterface


class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion Dossier Médical - Accueil")
        self.setGeometry(300, 150, 500, 300)
        self.setStyleSheet(self.apply_medical_theme())

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Gestion des Dossiers Médicaux")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        button_size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        btn_admin = QPushButton("Administrateur")
        btn_admin.setFont(QFont("Arial", 10))
        btn_admin.setFixedSize(200, 35)
        btn_admin.setSizePolicy(button_size_policy)
        btn_admin.clicked.connect(self.show_admin_interface)
        layout.addWidget(btn_admin, alignment=Qt.AlignCenter)

        btn_patient = QPushButton("Patient")
        btn_patient.setFont(QFont("Arial", 10))
        btn_patient.setFixedSize(200, 35)
        btn_patient.setSizePolicy(button_size_policy)
        btn_patient.clicked.connect(self.show_patient_interface)
        layout.addWidget(btn_patient, alignment=Qt.AlignCenter)

        btn_doctor = QPushButton("Docteur")
        btn_doctor.setFont(QFont("Arial", 10))
        btn_doctor.setFixedSize(200, 35)
        btn_doctor.setSizePolicy(button_size_policy)
        btn_doctor.clicked.connect(self.show_doctor_interface)
        layout.addWidget(btn_doctor, alignment=Qt.AlignCenter)

        self.main_widget.setLayout(layout)
        self.stack.addWidget(self.main_widget)

        self.admin_interface = AdminInterface()
        self.patient_interface = PatientInterface()
        self.doctor_interface = DoctorInterface()

        self.stack.addWidget(self.admin_interface)
        self.stack.addWidget(self.patient_interface)
        self.stack.addWidget(self.doctor_interface)

    def show_admin_interface(self):
        """Afficher l'interface administrateur."""
        self.stack.setCurrentWidget(self.admin_interface)

    def show_patient_interface(self):
        """Afficher l'interface patient."""
        self.stack.setCurrentWidget(self.patient_interface)

    def show_doctor_interface(self):
        """Afficher l'interface docteur."""
        self.stack.setCurrentWidget(self.doctor_interface)

    def apply_medical_theme(self):
        """Appliquer un thème médical."""
        return """
            QMainWindow {
                background-color: #f0f5f9;
            }
            QLabel {
                color: #1c4966;
            }
            QPushButton {
                background-color: #4da8da;
                color: white;
                border-radius: 8px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e86c1;
            }
            QPushButton:pressed {
                background-color: #1c4966;
            }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainInterface()
    window.show()
    sys.exit(app.exec_())
