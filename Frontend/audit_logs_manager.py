from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QMessageBox
)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from contract_audit_interaction import get_log_count, get_log


class AuditLogsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs d'Audit Blockchain")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        audit_group = QGroupBox("Logs d'Audit")
        audit_layout = QVBoxLayout()

        logs_btn = QPushButton("Afficher Logs d'Audit")
        logs_btn.clicked.connect(self.list_all_logs_ui)
        audit_layout.addWidget(logs_btn)

        audit_group.setLayout(audit_layout)
        layout.addWidget(audit_group)
        self.setLayout(layout)

    def show_message(self, title, message, error=False):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
        msg_box.exec_()

    def list_all_logs_ui(self):
        try:
            count = get_log_count()
            if count == 0:
                self.show_message("Logs d'Audit", "Aucune action enregistrée.")
            else:
                result = "Logs d'Audit :\n\n"
                for i in range(count):
                    log = get_log(i)
                    result += (
                        f"Utilisateur : {log[0]}\n"
                        f"Action     : {log[1]}\n"
                        f"Détails    : {log[2]}\n"
                        f"Timestamp  : {log[3]}\n\n"
                    )
                self.show_message("Logs d'Audit", result)
        except Exception as e:
            self.show_message("Erreur", f"Erreur lors de la récupération des logs : {str(e)}", error=True)
