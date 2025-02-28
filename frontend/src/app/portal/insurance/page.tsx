"use client"; // Mark this component as a client component
import React, { useRef, useEffect, useState } from "react";
import { Button, VStack, Text, Center, Heading } from "@chakra-ui/react";

export default function Home() {
  const [hasContract, setHasContract] = useState<boolean>(false);
  const [escrowBalance, setEscrowBalance] = useState<number>(0);

  // useEffect(() => {
  //   // Check if the user has a contract
  //   if (contract) {
  //     setHasContract(true);
  //   }
  // }

  return (
    <Center>
      <VStack>
        <Heading fontSize="5xl" m={10}>VeriSure</Heading>
        <Text>Current Escrow Balance: </Text>
        
      </VStack>
    </Center>
  );
}
