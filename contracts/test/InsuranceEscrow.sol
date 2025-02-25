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

import {Test, console} from "forge-std/Test.sol";
import {IAttestationCenter} from "../src/IAttestationCenter.sol";
import {InsuranceEscrow} from "../src/InsuranceEscrow.sol";


contract InsuranceEscrowTest is Test {
    InsuranceEscrow escrowContract;
    address insuranceCompany = address(0x123);
    address attestationCenter = address(0x456);
    address provider = address(0x789);
    uint256 initialDeposit = 10 ether;

    function setUp() public {
        escrowContract = new InsuranceEscrow(attestationCenter, insuranceCompany, address(0));

        // Simulate deposit from the insurance company
        vm.deal(insuranceCompany, initialDeposit); // Fund the insurance company
        vm.prank(insuranceCompany); // impersonate address for subsequent operations
        escrowContract.depositToEscrow{value: initialDeposit}();
    }

    // ✅ Test: Only insurance company can deposit funds
    function testOnlyInsuranceCompanyCanDeposit() public {
        vm.deal(address(this), 1 ether);
        vm.expectRevert("Not authorized");
        escrowContract.depositToEscrow{value: 1 ether}();
    }

    // // ✅ Test: Correct escrow balance after deposit
    // function testEscrowBalanceAfterDeposit() public {
    //     uint256 balance = escrowContract.getEscrowBalance();
    //     assertEq(balance, initialDeposit, "Escrow balance should match the deposited amount");
    // }

    // ✅ Test: After task submission transfers correct payout
    function testClaimPayoutAfterApproval() public {
        uint256 claimAmount = 5 ether;

        // Simulate approved task submission
        vm.prank(attestationCenter);
        escrowContract.afterTaskSubmission(
            IAttestationCenter.TaskInfo({
                proofOfTask: "claim123",
                data: abi.encode(provider, claimAmount),
                taskPerformer: provider,
                taskDefinitionId: uint16(block.number)
            }),
            true, // _isApproved Claim approved
            hex"", // Dummy tpSignature
            [uint256(0), uint256(0)], // Dummy taSignature
            new uint256[](0) 
        );

        // ✅ Assert escrow balance decreased
        assertEq(escrowContract.getEscrowBalance(), initialDeposit - claimAmount, "Escrow balance did not decrease correctly");

        // ✅ Assert provider received the payout
        assertEq(provider.balance, claimAmount, "Provider did not receive the correct payout");
    }

    // ✅ Test: Only insurance company can withdraw remaining funds
    function testWithdrawEscrow() public {
        uint256 withdrawAmount = 2 ether;

        // Simulate withdrawal
        vm.prank(insuranceCompany);
        escrowContract.withdrawEscrow(withdrawAmount);

        // ✅ Assert escrow balance reduced
        assertEq(escrowContract.getEscrowBalance(), initialDeposit - withdrawAmount, "Escrow balance did not decrease correctly");
    }

    // ✅ Test: Unauthorized withdrawal should fail
    function testUnauthorizedWithdrawRevert() public {
        vm.expectRevert("Not authorized");
        escrowContract.withdrawEscrow(1 ether);
    }

    // ✅ Test: Claim rejection should not transfer funds
    function testClaimRejectionNoPayout() public {
        uint256 claimAmount = 3 ether;

        // Simulate rejected claim submission
        vm.prank(attestationCenter);
        vm.expectRevert("Claim not approved");
        escrowContract.afterTaskSubmission(
            IAttestationCenter.TaskInfo({
                proofOfTask: "claim123",
                data: abi.encode(provider, claimAmount),
                taskPerformer: provider,
                taskDefinitionId: uint16(block.number)
            }),
            false, // Claim rejected
            hex"", // Dummy tpSignature
            [uint256(0), uint256(0)], // Dummy taSignature
            new uint256[](0)   //y operator IDs
        );

        // ✅ Assert escrow balance remains the same
        console.log("Escrow balance after claim rejection:", escrowContract.getEscrowBalance());
        assertEq(escrowContract.getEscrowBalance(), initialDeposit, "Escrow balance should remain unchanged on rejection");

        // ✅ Assert provider did not receive funds
        console.log("Provider balance after claim rejection:", provider.balance);
        assertEq(provider.balance, 0, "Provider should not have received any payout");
    }
}
