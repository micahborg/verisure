// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.4;

library IAttestationCenter {
    struct TaskInfo {
        string proofOfTask;
        bytes data;
        address taskPerformer;
        uint16 taskDefinitionId;
    }
}

interface IInsuranceEscrow {
    event ClaimPaid(address indexed provider, uint256 amount);
    event Deposited(address indexed insurer, uint256 amount);
    event EscrowWithdrawn(address indexed insurer, uint256 amount);

    function afterTaskSubmission(
        IAttestationCenter.TaskInfo memory _taskInfo,
        bool _isApproved,
        bytes memory,
        uint256[2] memory,
        uint256[] memory
    ) external;
    function attestationCenter() external view returns (address);
    function beforeTaskSubmission(
        IAttestationCenter.TaskInfo memory _taskInfo,
        bool _isApproved,
        bytes memory _tpSignature,
        uint256[2] memory _taSignature,
        uint256[] memory _operatorIds
    ) external;
    function depositToEscrow() external payable;
    function getEscrowBalance() external view returns (uint256);
    function insuranceCompany() external view returns (address);
    function providerBalances(address) external view returns (uint256);
    function stakingPool() external view returns (address);
    function totalEscrowBalance() external view returns (uint256);
    function withdrawEscrow(uint256 amount) external;
}
