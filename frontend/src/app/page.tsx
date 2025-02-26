import React from 'react';
import { Heading } from '@chakra-ui/react';
import { Center, VStack } from '@chakra-ui/react';
import { Button, ButtonGroup } from "@chakra-ui/react"

export default function Home() {
  return (
    <>
      <Heading>Veri<i>Sure</i></Heading>
      <Center>
        <VStack>
          Please upload your claim here
          <Button>Upload Claim</Button>
        </VStack>
        JSON: Output
      </Center>
    </>
  );
}
