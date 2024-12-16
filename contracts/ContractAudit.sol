// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ContractAudit {
    
    struct Log {
        address userAddress;  
        string action;        
        string details;      
        uint256 timestamp;    
    }

    Log[] public logs; 

    event LogAdded(address indexed user, string action, string details, uint256 timestamp);

    function addLog(address _userAddress, string memory _action, string memory _details) public {
        logs.push(Log({
            userAddress: _userAddress,
            action: _action,
            details: _details,
            timestamp: block.timestamp
        }));

        emit LogAdded(_userAddress, _action, _details, block.timestamp);
    }

    function getAllLogs() public view returns (Log[] memory) {
        return logs;
    }

    function getLogCount() public view returns (uint256) {
        return logs.length;
    }
}
