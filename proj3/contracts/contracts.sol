pragma solidity ^0.5.0;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";
contract MedicalRecord is ERC721Full {
    constructor() public ERC721Full("MedicalRecordToken", "MRT") {}
    struct PatientRecord {
        string HospitalName;
        string DoctorName;
        uint Age;
        uint Height;
        uint Weight;
        string MedicalHistory;
        string MedicalExam;
        uint256 RecordDate;
    }
    mapping(uint256 => PatientRecord) public MedicalDataBank;
    event SavePatientRecord(uint256 tokenId, string HospitalName,
        string DoctorName,
        uint Age,
        uint Height,
        uint Weight,
        string MedicalHistory,
        string MedicalExam,  uint256 RecordDate);
   
    function setPatientRecord(
        address Patient,
        string memory HospitalName,
        string memory DoctorName,
        uint Age,
        uint Height,
        uint Weight,
        string memory MedicalHistory,
        string memory MedicalExam,
        uint256 initialRecordDate,
        string memory tokenURI
    ) public returns (uint256) {
        uint256 tokenId = totalSupply();
        _mint(Patient, tokenId);
        _setTokenURI(tokenId, tokenURI);
        MedicalDataBank[tokenId] = PatientRecord(HospitalName, DoctorName, Age, Height, Weight, MedicalHistory, MedicalExam, initialRecordDate);
        emit SavePatientRecord(tokenId, HospitalName, DoctorName, Age, Height, Weight, MedicalHistory, MedicalExam, initialRecordDate);
        return tokenId;
    }
}