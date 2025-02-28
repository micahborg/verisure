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

import {Script, console} from "forge-std/Script.sol";
import "forge-std/Test.sol";
//import {RiscZeroCheats} from "risc0/test/RiscZeroCheats.sol";
//import {IRiscZeroVerifier} from "risc0/IRiscZeroVerifier.sol";
import {InsuranceEscrow} from "../contracts/InsuranceEscrow.sol";

import {IAttestationCenter} from "../contracts/IAttestationCenter.sol";

// How to:
// Either `source ../../.env` or replace variables in command.
// forge script script/InsuranceEscrow.s.sol --rpc-url $L2_RPC --private-key $PRIVATE_KEY_DEPLOYER
// --broadcast -vvvv --verify --etherscan-api-key $L2_ETHERSCAN_API_KEY --chain
// $L2_CHAIN --verifier-url $L2_VERIFIER_URL
contract InsuranceEscrowDeploy is Script {
    function setUp() public {}

    //string constant CONFIG_FILE = "script/config.toml";
    //address verifier = 0xAC292cF957Dd5BA174cdA13b05C16aFC71700327; // from https://dev.risczero.com/api/blockchain-integration/contracts/verifier

    function run() public {
        vm.startBroadcast();
        address attestationCenter = 0x2eafD96019EF96c87dEA317C0B39AD1F3a59e1d5; // Polygon Amoy

        // Read and log the chainID
        uint256 chainId = block.chainid;
        console.log("You are deploying on ChainID %d", chainId);

        // Deploy the application contract.
        InsuranceEscrow escrow = new InsuranceEscrow(
            //verifier,
            attestationCenter, 
            msg.sender /* Insurance Company Addy */, 
            address(0) /* Staking Pool Addy */
        ); 

        IAttestationCenter(attestationCenter).setAvsLogic(address(escrow));
        console.log("Deployed InsuranceEscrow to", address(escrow));

        vm.stopBroadcast();
    }
}
