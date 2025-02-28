"use client"; // Mark this component as a client component

import React, { useRef, useState } from "react";
import { Button, VStack, Text, Center, Heading, Box } from "@chakra-ui/react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useMetaMask } from "@/contexts/MetaMaskContext";


const MotionButton = motion.create(Button);

export default function Home() {
  const { isMetaMaskInstalled, connectWallet } = useMetaMask();
  const router = useRouter();

  async function handleConnectProvider() {
    if (!isMetaMaskInstalled) {
      alert("MetaMask is not installed. Please install MetaMask to continue.");
      return;
    }
    await connectWallet().then(() => {
        router.push("/portal/provider");
    });
  }

  async function handleConnectInsurance() {
    if (!isMetaMaskInstalled) {
      alert("MetaMask is not installed. Please install MetaMask to continue.");
      return;
    }
    await connectWallet().then(() => {
        router.push("/portal/insurance");
    });
  }

  return (
    <Center>
      <VStack gap={4}>
        <Box m={20} textAlign={"center"}>
          <Heading fontSize="5xl" mb={3}>VeriSure</Heading>
          <Text fontSize="xl">AI & ZK-Powered AVS for Insurance Claims Validation</Text>
        </Box>

        <MotionButton 
          mb={2}
          borderRadius="full"
          size="2xl" 
          onClick={handleConnectProvider}
          initial={{ opacity: 0, y: 20 }} // Starting state: transparent and 20px down
          animate={{ opacity: 1, y: 0 }} // Ending state: fully visible and in original position
          transition={{ duration: 0.5 }} // Animation duration
        >
          I'm a healthcare provider
        </MotionButton>

        <MotionButton 
          borderRadius="full"
          size="2xl" 
          onClick={handleConnectInsurance}
          initial={{ opacity: 0, y: 20 }} // Starting state: transparent and 20px down
          animate={{ opacity: 1, y: 0 }} // Ending state: fully visible and in original position
          transition={{ duration: 0.7 }} // Animation duration
        >
          I'm an insurance company
        </MotionButton>

      </VStack>
    </Center>
  );
}
