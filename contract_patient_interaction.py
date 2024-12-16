import os
import json
import re
from web3 import Web3
from contract_patient_interaction import *  

with open("deployed_contracts.json", "r") as f:
    deployed_contracts = json.load(f)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  
w3.eth.default_account = w3.eth.accounts[0]  

CONTRACT_PATIENT_ADDRESS = deployed_contracts["addresses"]["ContractPatient"]
CONTRACT_PATIENT_ABI = deployed_contracts["abis"]["ContractPatient"]

contract = w3.eth.contract(address=CONTRACT_PATIENT_ADDRESS, abi=CONTRACT_PATIENT_ABI)

CONTRACT_DOCTOR_ADDRESS = deployed_contracts["addresses"]["ContractDoctor"]
CONTRACT_DOCTOR_ABI = deployed_contracts["abis"]["ContractDoctor"]

contract_doctor = w3.eth.contract(address=CONTRACT_DOCTOR_ADDRESS, abi=CONTRACT_DOCTOR_ABI)


def create_ethereum_account():
    account = w3.eth.account.create()
    print(f"Compte Ethereum créé :")
    print(f"Adresse : {account.address}")
    print(f"Clé privée : {account.privateKey.hex()}")
    return account.address, account.privateKey.hex()


def register_patient(patient_address, name, dob, ipfs_hash):
    """
    Appelle la fonction 'registerPatient' du smart contract.
    """
    try:
        tx = contract.functions.registerPatient(
            patient_address, 
            name, 
            dob, 
            ipfs_hash
        ).transact({'from': w3.eth.defaultAccount})
        w3.eth.wait_for_transaction_receipt(tx)
        print("Patient enregistré avec succès dans la blockchain.")
    except Exception as e:
        raise Exception(f"Erreur lors de l'enregistrement du patient : {str(e)}")


def update_patient_record(patient_address, ipfs_hash):
    try:
        tx_hash = contract.functions.updatePatientRecord(patient_address, ipfs_hash).transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Dossier médical mis à jour avec succès : {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour du dossier : {e}")


def grant_permission(patient_address, doctor_address):
    try:
        tx_hash = contract.functions.grantPermission(doctor_address).transact({"from": patient_address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Permission accordée au médecin : {doctor_address}")  
    except Exception as e:
        print(f"Erreur lors de l'attribution de la permission : {e}")


def revoke_permission(patient_address, doctor_address):
    try:
        tx_hash = contract.functions.revokePermission(doctor_address).transact({"from": patient_address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Permission révoquée pour le médecin : {doctor_address}")
    except Exception as e:
        print(f"Erreur lors de la révocation de la permission : {e}")


def update_patient_record_by_doctor(doctor_address, patient_address, name, date_of_birth, ipfs_hash):
    try:
        tx_hash = contract.functions.updatePatientRecordByDoctor(
            patient_address,
            name,
            date_of_birth,
            ipfs_hash
        ).transact({"from": doctor_address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Dossier médical mis à jour avec succès : {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")


def get_patient(patient_address):
    try:
        patient = contract.functions.getPatient(patient_address).call()
        if not patient[0]:
            raise ValueError("Adresse Ethereum du patient non trouvée")
        print("Informations du patient :")
        print(f"Adresse : {patient[0]}")
        print(f"Nom : {patient[1]}")
        print(f"Date de naissance : {patient[2]}")
        print(f"Hash IPFS : {patient[3]}")
        return {
            "address": patient[0],
            "name": patient[1],
            "dateOfBirth": patient[2],
            "ipfsHash": patient[3]
        }
    except Exception as e:
        print(f"Erreur lors de la récupération des informations : {e}")
        raise e


def check_permission(patient_address, doctor_address):
    try:
        is_granted = contract.functions.checkPermission(patient_address, doctor_address).call()
        print(f"Permission accordée pour le médecin ({doctor_address}) : {is_granted}")
        return is_granted
    except Exception as e:
        print(f"Erreur lors de la vérification de la permission : {e}")


def get_all_patients():
    try:
        return contract.functions.getAllPatients().call()
    except Exception as e:
        print(f"Erreur lors de la récupération des patients : {e}")
        return []

def get_list_patients():
    """
    Récupère la liste complète des patients depuis le contrat intelligent.
    Retourne une liste de dictionnaires contenant : adresse, nom, date de naissance, hash du fichier.
    """
    try:
        patients = contract.functions.getAllPatientDetails().call()

        patient_list = []
        for patient in patients:
            patient_list.append({
                "address": patient[0],  
                "name": patient[1],      
                "dob": patient[2],       
                "hash": patient[3]       
            })

        return patient_list
    except Exception as e:
        print(f"Erreur lors de la récupération des patients : {e}")
        return []


def get_all_doctors():
    try:
        doctors = contract_doctor.functions.getAllDoctorsDetails().call()

        return [(doctor[0], doctor[1], doctor[2]) for doctor in doctors]
    except Exception as e:
        print(f"Erreur lors de la récupération des docteurs : {e}")
        return []


def update_patient_record_by_doctor(doctor_address, patient_address, name, date_of_birth, ipfs_hash):
    try:
        tx_hash = contract.functions.updatePatientRecordByDoctor(
            patient_address, name, date_of_birth, ipfs_hash
        ).transact({"from": doctor_address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Dossier médical mis à jour avec succès : {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour du dossier par le médecin : {e}")


def save_private_key_backend(patient_address, private_key):
    """
    Sauvegarder la clé privée du patient de manière sécurisée dans un backend.
    :param patient_address: Adresse Ethereum du patient.
    :param private_key: Clé privée RSA du patient.
    """
    try:
        key_directory = "keys"
        if not os.path.exists(key_directory):  
            os.makedirs(key_directory)  

        key_path = os.path.join(key_directory, f"{patient_address}_private.pem")
        
        with open(key_path, "w") as file:
            file.write(private_key)
    except Exception as e:
        raise Exception(f"Erreur lors de la sauvegarde de la clé privée : {str(e)}")


def delete_patient(patient_address, admin_address):
    """
    Supprime un patient par son adresse Ethereum.
    :param patient_address: Adresse Ethereum du patient à supprimer.
    :param admin_address: Adresse Ethereum de l'admin qui effectue la transaction.
    """
    try:
        tx_hash = contract.functions.deletePatient(patient_address).transact({'from': admin_address})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression du patient : {e}")
        return False
