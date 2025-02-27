"use client"; // Mark this component as a client component

import React, { useRef, useState } from 'react';
import { Button, VStack, Text, Center } from '@chakra-ui/react';

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [jsonOutput, setJsonOutput] = useState<string>("");

  // Handle the file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      console.log('File selected:', file.name);
  
      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append('file', file);
  
      try {
        // Send the file to the Flask API
        const response = await fetch('http://localhost:5000/process-pdf', {
          method: 'POST',
          body: formData,
        });
  
        console.log('Response status:', response.status);
  
        if (!response.ok) {
          const errorData = await response.json();
          console.error('Error response:', errorData);
          throw new Error('Failed to process PDF');
        }
  
        // Parse the JSON response
        const result = await response.json();
        console.log('Processed data:', result.data);
  
        // Display the JSON output
        setJsonOutput(JSON.stringify(result.data, null, 2)); // Format JSON with indentation
      } catch (error) {
        console.error('Error processing PDF:', error);
        alert('Failed to process PDF. Please try again.');
      }
    } else {
      alert('Please upload a PDF file');
    }
  };
  // Trigger the file input when the button is clicked
  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <>
      <Center>
        <VStack spacing={6}>
          <Text>Please upload your claim (PDF)</Text>
          <Button onClick={triggerFileInput} colorScheme="teal" size="lg">
            Upload Claim
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            style={{ display: 'none' }} // Hide the file input
          />
          <Text mt={6}>JSON Output:</Text>
          <VStack spacing={4}>
            {/* Display JSON output */}
            <Text border="1px" p={4} w="100%" maxW="600px" bg="gray.100" borderRadius="md" textAlign="left">
              {jsonOutput || "{ 'status': 'pending', 'claim_id': 12345 }"}
            </Text>
          </VStack>
        </VStack>
      </Center>
    </>
  );
}
