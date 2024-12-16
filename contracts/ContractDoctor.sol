// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractAudit.sol";

interface IContractPatient {
    function getAllPatients() external view returns (address[] memory);
    function checkPermission(address _patientAddress, address _doctor) external view returns (bool);
}

contract ContractDoctor {
    address public admin;
    IContractPatient public contractPatient;
    ContractAudit public auditContract;

    struct Doctor {
        address doctorAddress;
        string name;
        string specialty;
        bool isRegistered;
    }

    mapping(address => Doctor) public doctors;

    address[] public doctorAddresses;

    event DoctorRegistered(address indexed doctorAddress, string name, string specialty);
    event DoctorDeleted(address indexed doctorAddress);

    constructor(address _contractPatientAddress, address _auditContractAddress) {
        admin = msg.sender;
        contractPatient = IContractPatient(_contractPatientAddress);
        auditContract = ContractAudit(_auditContractAddress);
    }

    function registerDoctor(address _doctorAddress, string memory _name, string memory _specialty) public {
        require(msg.sender == admin, "Seul l'admin peut enregistrer des docteurs");
        require(!doctors[_doctorAddress].isRegistered, "Docteur deja enregistre");

        doctors[_doctorAddress] = Doctor(_doctorAddress, _name, _specialty, true);
        doctorAddresses.push(_doctorAddress);
        emit DoctorRegistered(_doctorAddress, _name, _specialty);
        auditContract.addLog(msg.sender, "RegisterDoctor", string(abi.encodePacked("Doctor: ", _name)));
    }

    function getDoctorInfo(address _doctorAddress) public view returns (string memory, string memory, bool) {
        Doctor memory doctor = doctors[_doctorAddress];
        return (doctor.name, doctor.specialty, doctor.isRegistered);
    }

    function getPatientsWithAccess(address _doctor) public view returns (address[] memory) {
        address[] memory allPatients = contractPatient.getAllPatients();
        address[] memory result = new address[](allPatients.length);
        uint count = 0;

        for (uint i = 0; i < allPatients.length; i++) {
            if (contractPatient.checkPermission(allPatients[i], _doctor)) {
                result[count] = allPatients[i];
                count++;
            }
        }

    assembly {
        mstore(result, count)
        }
        return result;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Seul l'admin peut effectuer cette action.");
        _;
    }

    function getAllDoctors() public view returns (address[] memory) {
        return doctorAddresses;
    }

    function getAllDoctorsDetails() public view returns (Doctor[] memory) {
        Doctor[] memory allDoctors = new Doctor[](doctorAddresses.length);
        for (uint i = 0; i < doctorAddresses.length; i++) {
            allDoctors[i] = doctors[doctorAddresses[i]];
        }
        return allDoctors;
    }

    function deleteDoctor(address _doctorAddress) public onlyAdmin {
        require(doctorAddresses.length > 0, "Aucun medecin a supprimer.");
        require(doctors[_doctorAddress].doctorAddress != address(0), "Medecin non trouve.");

        delete doctors[_doctorAddress];

        for (uint i = 0; i < doctorAddresses.length; i++) {
            if (doctorAddresses[i] == _doctorAddress) {
                doctorAddresses[i] = doctorAddresses[doctorAddresses.length - 1];
                doctorAddresses.pop();
                break;
            }
        }

        emit DoctorDeleted(_doctorAddress);
    }

    function getlistDoctors() public view returns (address[] memory, string[] memory, string[] memory) {
        uint256 length = doctorAddresses.length;

        address[] memory addresses = new address[](length);
        string[] memory names = new string[](length);
        string[] memory specialties = new string[](length);

        // Remplir les tableaux avec les informations
        for (uint256 i = 0; i < length; i++) {
            address doctorAddress = doctorAddresses[i];
            Doctor memory doctor = doctors[doctorAddress];

            addresses[i] = doctor.doctorAddress;
            names[i] = doctor.name;
            specialties[i] = doctor.specialty;
        }    

        return (addresses, names, specialties);
    }


}
