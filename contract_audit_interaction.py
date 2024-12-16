import json
from web3 import Web3

with open("deployed_contracts.json", "r") as f:
    deployed_contracts = json.load(f)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.default_account = w3.eth.accounts[0]  

CONTRACT_PATIENT_ADDRESS = deployed_contracts["addresses"]["ContractPatient"]
CONTRACT_PATIENT_ABI = deployed_contracts["abis"]["ContractPatient"]

CONTRACT_DOCTOR_ADDRESS = deployed_contracts["addresses"]["ContractDoctor"]
CONTRACT_DOCTOR_ABI = deployed_contracts["abis"]["ContractDoctor"]

CONTRACT_AUDIT_ADDRESS = deployed_contracts["addresses"]["ContractAudit"]
CONTRACT_AUDIT_ABI = deployed_contracts["abis"]["ContractAudit"]


contract_patient = w3.eth.contract(address=CONTRACT_PATIENT_ADDRESS, abi=CONTRACT_PATIENT_ABI)
contract_doctor = w3.eth.contract(address=CONTRACT_DOCTOR_ADDRESS, abi=CONTRACT_DOCTOR_ABI)
contract_audit = w3.eth.contract(address=CONTRACT_AUDIT_ADDRESS, abi=CONTRACT_AUDIT_ABI)


def add_audit_log(user_address, action, details):
    try:
        tx_hash = contract_audit.functions.addLog(user_address, action, details).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Log ajouté avec succès : {action} - {details}")
    except Exception as e:
        print(f"Erreur lors de l'ajout du log : {e}")


def get_all_audit_logs():
    try:
        logs = contract_audit.functions.getAllLogs().call()
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "userAddress": log[0],
                "action": log[1],
                "details": log[2],
                "timestamp": log[3]
            })
        return formatted_logs
    except Exception as e:
        print(f"Erreur lors de la récupération des logs : {e}")
        return []


def register_patient_with_audit(admin_address, patient_address, name, date_of_birth):
    try:
        tx_hash = contract_patient.functions.registerPatient(patient_address, name, date_of_birth).transact({"from": admin_address})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        add_audit_log(admin_address, "RegisterPatient", f"Patient: {name}, Address: {patient_address}")
        print("Patient enregistré avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du patient : {e}")


def register_doctor_with_audit(admin_address, doctor_address, name, specialty):
    try:
        tx_hash = contract_doctor.functions.registerDoctor(doctor_address, name, specialty).transact({"from": admin_address})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        add_audit_log(admin_address, "RegisterDoctor", f"Doctor: {name}, Specialty: {specialty}, Address: {doctor_address}")
        print("Médecin enregistré avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du médecin : {e}")


def update_patient_record_with_audit(doctor_address, patient_address, name, date_of_birth, ipfs_hash):
    try:
        tx_hash = contract_patient.functions.updatePatientRecordByDoctor(patient_address, name, date_of_birth, ipfs_hash).transact({"from": doctor_address})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        add_audit_log(doctor_address, "UpdatePatientRecord", f"Patient: {patient_address}, IPFS: {ipfs_hash}")
        print("Dossier médical mis à jour avec succès.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour du dossier médical : {e}")


def grant_permission_with_audit(patient_address, doctor_address):
    try:
        tx_hash = contract_patient.functions.grantPermission(doctor_address).transact({"from": patient_address})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        add_audit_log(patient_address, "GrantPermission", f"Doctor: {doctor_address}")
        print("Permission accordée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'accord de permission : {e}")
