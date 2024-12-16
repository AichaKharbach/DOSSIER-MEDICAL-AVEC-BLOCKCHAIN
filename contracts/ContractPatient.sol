// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractAudit.sol";

contract ContractPatient {
    
    ContractAudit public auditContract;

    struct Patient {
        address patientAddress;  
        string name;            
        string dateOfBirth;      
        string ipfsHash;         
    }

    struct Permission {
        bool isGranted; 
    }

    mapping(address => Patient) public patients;

    mapping(address => mapping(address => Permission)) public permissions;

    address[] public patientAddresses;

    address public admin;

    // Événements
    event PatientRegistered(address indexed patientAddress, string name);
    event PatientUpdated(address indexed patientAddress, string ipfsHash);
    event PermissionGranted(address indexed patient, address indexed doctor);
    event PermissionRevoked(address indexed patient, address indexed doctor);
    event PatientDeleted(address patientAddress);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Seul l'admin peut effectuer cette action");
        _;
    }

    constructor(address _auditContractAddress) {
        admin = msg.sender;
        auditContract = ContractAudit(_auditContractAddress);
    }

    function registerPatient(
        address _patientAddress, 
        string memory _name, 
        string memory _dateOfBirth, 
        string memory _ipfsHash
    ) public onlyAdmin {
        require(patients[_patientAddress].patientAddress == address(0), "Le patient est deja enregistre");
        patients[_patientAddress] = Patient(_patientAddress, _name, _dateOfBirth, _ipfsHash);
        patientAddresses.push(_patientAddress); // Ajouter l'adresse du patient au tableau
        
        emit PatientRegistered(_patientAddress, _name);
        auditContract.addLog(msg.sender, "RegisterPatient", string(abi.encodePacked("Patient: ", _name)));
    }


    function updatePatientRecord(address _patientAddress, string memory _ipfsHash) public {
        require(msg.sender == _patientAddress, "Seul le patient peut mettre a jour son dossier");
        require(patients[_patientAddress].patientAddress != address(0), "Patient non enregistre");
        patients[_patientAddress].ipfsHash = _ipfsHash;
        emit PatientUpdated(_patientAddress, _ipfsHash);
    }

    // Utilitaire pour convertir une adresse en chaîne de caractères (hexadécimal)
    function toHexString(address _addr) internal pure returns (string memory) {
        bytes memory data = abi.encodePacked(_addr);
        bytes memory hexChars = "0123456789abcdef";
        bytes memory str = new bytes(2 + data.length * 2);
        str[0] = "0";
        str[1] = "x";
        for (uint i = 0; i < data.length; i++) {
            str[2 + i * 2] = hexChars[uint(uint8(data[i] >> 4))];
            str[3 + i * 2] = hexChars[uint(uint8(data[i] & 0x0f))];
        }
        return string(str);
    }

    function grantPermission(address _doctor) public {
        require(_doctor != address(0), "Adresse du medecin invalide");
        permissions[msg.sender][_doctor] = Permission(true);

        // Ajouter l'adresse du patient dans la liste globale s'il n'y est pas déjà
        bool exists = false;
        for (uint i = 0; i < patientAddresses.length; i++) {
            if (patientAddresses[i] == msg.sender) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            patientAddresses.push(msg.sender);
        }
   
        emit PermissionGranted(msg.sender, _doctor);
        auditContract.addLog(
            msg.sender, 
            "GrantPermission", 
            string(abi.encodePacked("Permission granted to doctor: ", toHexString(_doctor)))
        );
    }

    function revokePermission(address _doctor) public {
        require(permissions[msg.sender][_doctor].isGranted, "Permission non accordee");
        delete permissions[msg.sender][_doctor];
        emit PermissionRevoked(msg.sender, _doctor);
        // Appel à ContractAudit pour enregistrer l'action
        auditContract.addLog(
            msg.sender, 
            "GrantPermission", 
            string(abi.encodePacked("Permission revoked to doctor: ", toHexString(_doctor)))
        );
    }

    function updatePatientRecordByDoctor(address _patientAddress, string memory _name, string memory _dateOfBirth, string memory _ipfsHash) public {
        require(permissions[_patientAddress][msg.sender].isGranted, "Permission non accordee");
        require(patients[_patientAddress].patientAddress != address(0), "Patient non enregistre");

        patients[_patientAddress].name = _name;
        patients[_patientAddress].dateOfBirth = _dateOfBirth;
        patients[_patientAddress].ipfsHash = _ipfsHash;

        emit PatientUpdated(_patientAddress, _ipfsHash);
        auditContract.addLog(
            msg.sender, 
            "UpdatePatientRecord", 
            string(abi.encodePacked("Patient: ", _name, ", IPFS Hash: ", _ipfsHash))
        );
    }

    function getPatient(address _patientAddress) public view returns (Patient memory) {
        require(patients[_patientAddress].patientAddress != address(0), "Patient non enregistre");
        return patients[_patientAddress];
    }

    function checkPermission(address _patientAddress, address _doctor) public view returns (bool) {
        return permissions[_patientAddress][_doctor].isGranted;
    }

    function getAllPatients() public view returns (address[] memory) {
        return patientAddresses;
    }

    function deletePatient(address _patientAddress) public onlyAdmin {
        require(patients[_patientAddress].patientAddress != address(0), "Le patient n'existe pas");

        delete patients[_patientAddress];

        for (uint i = 0; i < patientAddresses.length; i++) {
            if (patientAddresses[i] == _patientAddress) {
                patientAddresses[i] = patientAddresses[patientAddresses.length - 1];
                patientAddresses.pop();
                break;
            }
        }

        emit PatientDeleted(_patientAddress);
    }

    function getAllPatientDetails() public view returns (Patient[] memory) {
        Patient[] memory allPatients = new Patient[](patientAddresses.length);
        for (uint i = 0; i < patientAddresses.length; i++) {
            address patientAddr = patientAddresses[i];
            allPatients[i] = patients[patientAddr];
        }
        return allPatients;
    }

}
