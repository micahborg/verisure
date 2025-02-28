"use client";
import React, { createContext, useContext, useEffect, useState } from 'react';
import InsuranceEscrowABI from '@/abi/InsuranceEscrowABI.json';
import { ethers } from 'ethers';

const MetaMaskContext = createContext(null);

export const MetaMaskProvider = ({ children }) => {
    const [isMetaMaskInstalled, setIsMetaMaskInstalled] = useState(false);
    const [isWalletConnected, setWalletConnected] = useState(false);
    const [currentChainId, setCurrentChainId] = useState(null);
    const [currentWalletAddress, setCurrentWalletAddress] = useState(null);

    useEffect(() => {
        console.log('Loading Session Variables...');
        console.log('isMetaMaskInstalled:', sessionStorage.getItem('isMetaMaskInstalled'));
        console.log('isWalletConnected:', sessionStorage.getItem('isWalletConnected'));
        console.log('currentWalletAddress:', sessionStorage.getItem('currentWalletAddress'));

        console.log('Loading State Variables...')
        console.log('isMetaMaskInstalled:', isMetaMaskInstalled);
        console.log('isWalletConnected:', isWalletConnected);
        console.log('currentWalletAddress:', currentWalletAddress);

        if (checkMetaMask()) {
            window.ethereum.on("chainChanged", (chainId) => {
                console.log('Chain changed to:', chainId);
                setCurrentChainId(chainId);
                sessionStorage.setItem('currentChainId', chainId);

                //window.location.reload();
            });
            window.ethereum.on("accountsChanged", (accounts) => {
                console.log('Accounts changed to:', accounts);
                setWalletConnected(accounts.length > 0);
                sessionStorage.setItem('iswalletConnected', accounts.length > 0);
                
                if (accounts.length != 0) {
                    const walletAddress = accounts[0];
                    console.log('Setting current wallet address to:', walletAddress);
                    setCurrentWalletAddress(walletAddress);
                    sessionStorage.setItem('currentWalletAddress', walletAddress);
                }
                if (accounts.length == 0) {
                    console.log('Removing current wallet address...');
                    setCurrentWalletAddress(null);
                    sessionStorage.removeItem('currentWalletAddress');
                    window.location.reload();
                }
            });
        }

        // set all session variables to state variables when the component mounts
        sessionStorage.setItem('isMetaMaskInstalled', isMetaMaskInstalled);
        sessionStorage.setItem('isWalletConnected', isWalletConnected);
        sessionStorage.setItem('currentChainId', currentChainId);
        sessionStorage.setItem('currentWalletAddress', currentWalletAddress);

    }, [isMetaMaskInstalled, isWalletConnected, currentChainId, currentWalletAddress]);

    const checkMetaMask = () => {
        if (typeof window.ethereum !== 'undefined' && window.ethereum.isMetaMask) {
            console.log('MetaMask is installed');
            setIsMetaMaskInstalled(true);
            return true;
        } else {
            console.log('MetaMask is not installed');
            return false;
        }
    };

    const connectWallet = async () => {
        if (!isMetaMaskInstalled) {
            console.log('In order to use this dApp, you need to install MetaMask')
        } else {
            try {
                console.log('Connecting wallet...')

                const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });

                if (accounts.length > 0) {
                    setCurrentWalletAddress(accounts[0]);

                    await window.ethereum.request({
                        method: "wallet_addEthereumChain",
                        params: [{
                            chainName: "Polygon Amoy Testnet", 
                            chainId: "0x13882",
                            nativeCurrency: {
                                name: "MATIC", 
                                symbol: "MATIC",
                                decimals: 18,
                            },
                            rpcUrls: ["https://rpc-amoy.polygon.technology/"],
                            blockExplorerUrls: ["https://amoy.polygonscan.com/"]
                        }],
                    });

                    await window.ethereum.request({
                        "method": "wallet_switchEthereumChain",
                        "params": [
                          {
                            "chainId": "0x13882"
                          }
                        ]
                    });

                    setWalletConnected(true);
                    console.log('Connected to Polygon Amoy Testnet');
                }
            } catch (error) {
                console.error("Failed to connect to wallet:", error);
            }
        }
    };

    //const createInsuranceAccount = async () => {


    const checkEscrowBalance = async () => {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const contractAddress = `0x3C014629faa8E5187d3942d58DC752DB8d7A98c9`; // Insurance contract address
        const contract = new ethers.Contract(contractAddress, InsuranceEscrowABI.abi, signer);

        console.log("token", contract)

        console.log('Checking if company has an account...')
        const hasAccount = await contract.balanceOf(currentWalletAddress);
        if (hasAccount.toString() === '0') {
            console.log('Company does not have an account, creating one...')
            await contract.createInsuranceAccount();
        }

        console.log('Checking balance...')
        const balance = await contract.getEscrowBalance();
        console.log('Current Balance:', balance.toString());

        return balance;
    };

    const checkIsOnChain = () => {
        return currentChainId === "0x13882";
    };
    
    return (
        <MetaMaskContext.Provider value={{ 
            isMetaMaskInstalled, 
            isWalletConnected, 
            currentChainId, 
            currentWalletAddress, 
            checkEscrowBalance,
            connectWallet,
            checkIsOnChain
         }}>
        {children}
        </MetaMaskContext.Provider>
    );
    }

export const useMetaMask = () => useContext(MetaMaskContext);