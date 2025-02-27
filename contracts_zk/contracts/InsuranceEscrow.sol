// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.20;

/*______     __      __                              __      __ 
 /      \   /  |    /  |                            /  |    /  |
/$$$$$$  | _$$ |_   $$ |____    ______   _______   _$$ |_   $$/   _______ 
$$ |  $$ |/ $$   |  $$      \  /      \ /       \ / $$   |  /  | /       |
$$ |  $$ |$$$$$$/   $$$$$$$  |/$$$$$$  |$$$$$$$  |$$$$$$/   $$ |/$$$$$$$/ 
$$ |  $$ |  $$ | __ $$ |  $$ |$$    $$ |$$ |  $$ |  $$ | __ $$ |$$ |
$$ \__$$ |  $$ |/  |$$ |  $$ |$$$$$$$$/ $$ |  $$ |  $$ |/  |$$ |$$ \_____ 
$$    $$/   $$  $$/ $$ |  $$ |$$       |$$ |  $$ |  $$  $$/ $$ |$$       |
 $$$$$$/     $$$$/  $$/   $$/  $$$$$$$/ $$/   $$/    $$$$/  $$/  $$$$$$$/
*/
/**
 * @author Othentic Labs LTD.
 * @notice Terms of Service: https://www.othentic.xyz/terms-of-service
 */

import { IRiscZeroVerifier } from './IRiscZeroVerifier.sol';
import { ImageID } from './ImageID.sol';
import './IAvsLogic.sol';

contract InsuranceEscrow is IAvsLogic {
    address public attestationCenter;
    address public insuranceCompany;
    address public stakingPool; // Optional: Address for staking rewards integration
    uint256 public totalEscrowBalance;

    address public immutable verifier; // RISC-V Zero verifier contract
    bytes32 public constant imageId = ImageID.PARSE_CLAIM_ID;

    mapping(address => uint256) public providerBalances;

    event Deposited(address indexed insurer, uint256 amount);
    event ClaimPaid(address indexed provider, uint256 amount);
    event EscrowWithdrawn(address indexed insurer, uint256 amount);

    event ProofVerified(uint256 x);


    constructor(address _verifier, address _attestationCenter, address _insuranceCompany, address _stakingPool) {
        verifier = _verifier;
        attestationCenter = _attestationCenter;
        insuranceCompany = _insuranceCompany;
        stakingPool = _stakingPool;
    }

    /**
     * @dev Allows insurance company to deposit funds into the escrow.
     */
    function depositToEscrow() external payable {
        require(msg.sender == insuranceCompany, "Not authorized");
        require(msg.value > 0, "Deposit must be greater than zero");
        totalEscrowBalance += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    /**
     * @dev Triggered automatically after task submission and approval.
     * Transfers claim amount from escrow to the healthcare provider.
     */
    function afterTaskSubmission(
        IAttestationCenter.TaskInfo calldata _taskInfo, 
        bool _isApproved, 
        bytes calldata /*_tpSignature*/, 
        uint256[2] calldata /*_taSignature*/, 
        uint256[] calldata /*_operatorIds*/
    ) external {
        require(msg.sender == attestationCenter, "Not allowed");
        require(_isApproved, "Claim not approved");

        // Extract claim amount and provider from task data
        (address provider, uint256 claimAmount) = abi.decode(_taskInfo.data, (address, uint256));
        require(totalEscrowBalance >= claimAmount, "Insufficient escrow funds");

        // Transfer funds to the provider
        totalEscrowBalance -= claimAmount;
        providerBalances[provider] += claimAmount;
        payable(provider).transfer(claimAmount);

        emit ClaimPaid(provider, claimAmount);
    }

    function beforeTaskSubmission(
        IAttestationCenter.TaskInfo calldata _taskInfo, 
        bool _isApproved, 
        bytes calldata _tpSignature, 
        uint256[2] calldata _taSignature, 
        uint256[] calldata _operatorIds
    ) external {
        // No implementation
    }

    /**
     * @dev Allows insurance company to withdraw any unallocated funds.
     */
    function withdrawEscrow(uint256 amount) external {
        require(msg.sender == insuranceCompany, "Not authorized");
        require(amount <= totalEscrowBalance, "Insufficient funds");
        totalEscrowBalance -= amount;
        payable(insuranceCompany).transfer(amount);
        emit EscrowWithdrawn(msg.sender, amount);
    }

    /**
     * @dev Returns the current escrow balance.
     */
    function getEscrowBalance() external view returns (uint256) {
        return totalEscrowBalance;
    }

    /**
     * @dev Call verifier contract to verify the proof of execution.
     */
    function verifyProof(uint256 x, bytes calldata seal) public {
        bytes memory journal = abi.encode(x);
        IRiscZeroVerifier(verifier).verify(seal, imageId, sha256(journal));
        emit ProofVerified(x);
    }
}
