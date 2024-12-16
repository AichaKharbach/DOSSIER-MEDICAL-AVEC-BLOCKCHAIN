import json
import os
from web3 import Web3
from solcx import compile_files, install_solc

install_solc("0.8.0")

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  
w3.eth.default_account = w3.eth.accounts[0]  

CONTRACTS_FOLDER = os.path.abspath("./contracts")  


def compile_contracts():
    print("Compilation des contrats Solidity...")
    if not os.path.exists(CONTRACTS_FOLDER):
        raise FileNotFoundError(f"Dossier des contrats non trouvé : {CONTRACTS_FOLDER}")

    contracts_path = [os.path.join(CONTRACTS_FOLDER, f) for f in os.listdir(CONTRACTS_FOLDER) if f.endswith(".sol")]
    if not contracts_path:
        raise FileNotFoundError(f"Aucun fichier Solidity trouvé dans le dossier : {CONTRACTS_FOLDER}")

    compiled = compile_files(contracts_path, solc_version="0.8.0")

    print("Clés des contrats compilés :", compiled.keys())
    return compiled


def deploy_contract(contract_interface, contract_name, constructor_args=None):
    print(f"Déploiement du contrat : {contract_name}...")

    bytecode = contract_interface["bin"]
    abi = contract_interface["abi"]

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    if constructor_args:
        tx_hash = Contract.constructor(*constructor_args).transact()
    else:
        tx_hash = Contract.constructor().transact()

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Contrat {contract_name} déployé à l'adresse : {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress, abi


def main():
    try:
        compiled_contracts = compile_contracts()

        keys = {key.split(":")[-1]: key for key in compiled_contracts.keys()}
        print("Correspondance des noms des contrats :", keys)

        required_contracts = ["ContractAudit", "ContractPatient", "ContractDoctor"]
        for contract in required_contracts:
            if contract not in keys:
                raise KeyError(f"Le contrat {contract} n'a pas été trouvé dans les fichiers compilés.")

        addresses = {}
        abis = {}

        # Déploiement de ContractAudit
        print("\n--- Déploiement de ContractAudit ---")
        contract_key_audit = keys["ContractAudit"]
        contract_audit_interface = compiled_contracts[contract_key_audit]
        audit_address, audit_abi = deploy_contract(contract_audit_interface, "ContractAudit")
        addresses["ContractAudit"] = audit_address
        abis["ContractAudit"] = audit_abi

        # Déploiement de ContractPatient avec l'adresse de ContractAudit
        print("\n--- Déploiement de ContractPatient ---")
        contract_key_patient = keys["ContractPatient"]
        contract_patient_interface = compiled_contracts[contract_key_patient]
        patient_address, patient_abi = deploy_contract(
            contract_patient_interface, "ContractPatient", constructor_args=[audit_address]
        )
        addresses["ContractPatient"] = patient_address
        abis["ContractPatient"] = patient_abi

        # Déploiement de ContractDoctor avec les adresses de ContractPatient et ContractAudit
        print("\n--- Déploiement de ContractDoctor ---")
        contract_key_doctor = keys["ContractDoctor"]
        contract_doctor_interface = compiled_contracts[contract_key_doctor]
        doctor_address, doctor_abi = deploy_contract(
            contract_doctor_interface, "ContractDoctor", constructor_args=[patient_address, audit_address]
        )
        addresses["ContractDoctor"] = doctor_address
        abis["ContractDoctor"] = doctor_abi

        deployed_data = {"addresses": addresses, "abis": abis}
        with open("deployed_contracts.json", "w") as file:
            json.dump(deployed_data, file, indent=4)

        print("\nAdresses des contrats déployés et ABIs sauvegardées dans 'deployed_contracts.json'.")
        print(f"Adresse administrateur (déployeur) : {w3.eth.default_account}")

    except Exception as e:
        print(f"Erreur lors du déploiement des contrats : {e}")


if __name__ == "__main__":
    main()
