import os
import json
from web3 import Web3
from contract_patient_interaction import *  

with open("deployed_contracts.json", "r") as f:
    deployed_contracts = json.load(f)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.default_account = w3.eth.accounts[0]  

CONTRACT_DOCTOR_ADDRESS = deployed_contracts["addresses"]["ContractDoctor"]
CONTRACT_DOCTOR_ABI = deployed_contracts["abis"]["ContractDoctor"]

contract_doctor = w3.eth.contract(address=CONTRACT_DOCTOR_ADDRESS, abi=CONTRACT_DOCTOR_ABI)


def register_doctor(doctor_address, name, specialty):
    try:
        tx_hash = contract_doctor.functions.registerDoctor(doctor_address, name, specialty).transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Docteur enregistré avec succès : {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du docteur : {e}")


def get_doctor_info(doctor_address):
    try:
        name, specialty, is_registered = contract_doctor.functions.getDoctorInfo(doctor_address).call()
        return {"name": name, "specialty": specialty, "isRegistered": is_registered}
    except Exception as e:
        print(f"Erreur lors de la récupération des informations du docteur : {e}")
        return None

def check_access(patient_address, doctor_address, access_type):
    try:
        return contract_doctor.functions.checkAccess(patient_address, doctor_address, access_type).call()
    except Exception as e:
        print(f"Erreur lors de la vérification des permissions : {e}")
        return False

def get_patients_for_doctor(doctor_address):
    patients_with_access = []
    try:
        patient_addresses = get_all_patients()

        for patient_address in patient_addresses:
            is_granted = check_permission(patient_address, doctor_address)
            if is_granted:
                patient_info = get_patient(patient_address)
                if patient_info:
                    patients_with_access.append(patient_info)

        return patients_with_access
    except Exception as e:
        print(f"Erreur lors de la récupération des patients : {e}")
        return []


def get_all_doctors():
    try:
        return contract_doctor.functions.getAllDoctors().call()
    except Exception as e:
        print(f"Erreur lors de la récupération des docteurs : {e}")
        return []
    
def get_list_doctors():
    """
    Récupère la liste complète des docteurs : adresse, nom, spécialité.
    """
    try:
        addresses, names, specialties = contract_doctor.functions.getlistDoctors().call()
        
        doctors = [
            {"address": addr, "name": name, "specialty": specialty}
            for addr, name, specialty in zip(addresses, names, specialties)
        ]
        return doctors
    except Exception as e:
        print(f"Erreur lors de la récupération des médecins : {e}")
        return []


def delete_doctor(doctor_address, admin_address):
    """
    Supprime un médecin par son adresse Ethereum.
    :param doctor_address: Adresse Ethereum du médecin à supprimer.
    :param admin_address: Adresse Ethereum de l'admin effectuant l'action.
    :return: True si la suppression réussit, False sinon.
    """
    try:
        tx_hash = contract_doctor.functions.deleteDoctor(doctor_address).transact({'from': admin_address})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression du médecin : {e}")
        return False
