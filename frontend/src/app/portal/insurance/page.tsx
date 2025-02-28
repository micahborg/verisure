"use client"; // Mark this component as a client component
import React, { useRef, useEffect, useState } from "react";
import { Button, Box, VStack, HStack, Text, Center, Heading, DialogActionTrigger } from "@chakra-ui/react";
import { useMetaMask } from "@/contexts/MetaMaskContext";
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { NumberInputField, NumberInputRoot } from "@/components/ui/number-input"

export default function Home() {
  const [hasContract, setHasContract] = useState<boolean>(false);
  const [escrowBalance, setEscrowBalance] = useState<number>(0);
  const [withdrawAmount, setWithdrawAmount] = useState<number>(0);
  const [depositAmount, setDepositAmount] = useState<number>(0);
  const { checkEscrowBalance, depositToEscrow, withdrawFromEscrow } = useMetaMask();

  useEffect(() => {
    // Check if the user has a contract
    checkEscrowBalance().then((balance: React.SetStateAction<number>) => {
      setEscrowBalance(balance);
    });
  });

  async function handleWithdraw(amount: number) {
    // Withdraw funds from the escrow
    await withdrawFromEscrow(amount);
  }

  async function handleDeposit(amount: number) {
    // Deposit funds into the escrow
    await depositToEscrow(amount);
  }

  return (
    <Center>
      <VStack>
        <Heading fontSize="5xl" m={10}>VeriSure</Heading>
        <Heading fontSize="2xl" mb={5}>Insurer Portal</Heading>

        <Text>Current Escrow Balance: {escrowBalance} POL</Text>
        <HStack>
            <DialogRoot>
            <DialogTrigger asChild>
              <Button size="sm">
              Withdraw
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
              <DialogTitle>Withdraw Funds</DialogTitle>
              </DialogHeader>
              <DialogBody>
              <NumberInputRoot>
                <NumberInputField placeholder="10.005 POL" onChange={(e) => setWithdrawAmount(parseFloat(e.target.value))} />
              </NumberInputRoot>
              </DialogBody>
              <DialogFooter>
              <DialogActionTrigger asChild>
                <Button>Cancel</Button>
              </DialogActionTrigger>
                <Button onClick={() => handleWithdraw(withdrawAmount)}>Withdraw</Button>
              </DialogFooter>
              <DialogCloseTrigger />
            </DialogContent>
            </DialogRoot>

            <DialogRoot>
            <DialogTrigger asChild>
              <Button size="sm">
                Deposit
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Deposit Funds</DialogTitle>
              </DialogHeader>
              <DialogBody>
                <NumberInputRoot>
                  <NumberInputField placeholder="10.005 POL" onChange={(e) => setDepositAmount(parseFloat(e.target.value))} />
                </NumberInputRoot>
              </DialogBody>
              <DialogFooter>
                <DialogActionTrigger asChild>
                  <Button>Cancel</Button>
                </DialogActionTrigger>
                <Button onClick={() => handleDeposit(depositAmount)}>Deposit</Button>
              </DialogFooter>
              <DialogCloseTrigger />
            </DialogContent>
          </DialogRoot>
        
        </HStack>
        
        <Heading fontSize="2xl" mt={10}>Claim Processing History</Heading>
        <VStack>
          <Box>Claim 1</Box>
        </VStack>
      </VStack>
    </Center>
  );
}
