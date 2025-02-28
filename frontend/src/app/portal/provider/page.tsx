"use client"; // Mark this component as a client component

import React, { useRef, useState } from "react";
import { Button, VStack, Text, Center, Heading } from "@chakra-ui/react";

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [extractedData, setExtractedData] = useState<string>(""); // State for extracted claim data
  const [aiAnalysis, setAiAnalysis] = useState<string>(""); // State for AI analysis

  // Handle the file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === "application/pdf") {
      console.log("📄 File selected:", file.name);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("http://localhost:5000/process-pdf", {
          method: "POST",
          body: formData,
        });

        console.log("📡 Sent request to Flask");

        if (!response.ok) {
          const errorData = await response.json();
          console.error("❌ Error response:", errorData);
          throw new Error("Failed to process PDF");
        }

        const result = await response.json();
        console.log("✅ Full response:", result);

        if (result.data) {
          console.log("📑 Extracted Claim Data:", result.data);
          setExtractedData(JSON.stringify(result.data, null, 2));
        } else {
          console.warn("⚠️ No extracted claim data found.");
        }

        if (result.ai_analysis) {
          console.log("🤖 AI Analysis:", result.ai_analysis);
          setAiAnalysis(JSON.stringify(result.ai_analysis, null, 2));
        } else {
          console.warn("⚠️ No AI analysis found.");
        }

        // Send logs to Next.js API route for terminal logging
        fetch("/api/logs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "Processed PDF successfully", result }),
        });

      } catch (error) {
        console.error("🔥 Error processing PDF:", error);
        alert("Failed to process PDF. Please try again.");
      }
    } else {
      alert("Please upload a PDF file");
    }
  };

  // Trigger the file input when the button is clicked
  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <Center>
      <VStack>
        <Heading fontSize="5xl" m={10}>VeriSure</Heading>
        <Text>Please upload your claim (PDF)</Text>
        <Button onClick={triggerFileInput} colorScheme="teal" size="lg">
          Upload Claim
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          style={{ display: "none" }} // Hide the file input
        />

        {/* Display Extracted Data */}
        <Text mt={6}>Extracted Claim Data:</Text>
        <Text
          border="1px"
          p={4}
          w="100%"
          maxW="600px"
          maxH="300px"
          bg="gray.100"
          borderRadius="md"
          textAlign="left"
          overflowY="auto"
          whiteSpace="pre-wrap"
        >
          {extractedData || "No data extracted yet."}
        </Text>

        {/* Display AI Analysis */}
        <Text mt={6}>AI Analysis:</Text>
        <Text
          border="1px"
          p={4}
          w="100%"
          maxW="600px"
          maxH="300px"
          bg="gray.100"
          borderRadius="md"
          textAlign="left"
          overflowY="auto"
          whiteSpace="pre-wrap"
        >
          {aiAnalysis || "No AI analysis yet."}
        </Text>
      </VStack>
    </Center>
  );
}
