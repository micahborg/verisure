// gaia-node-setup.js
const { setupElizaGaiaNode } = require('./eliza-node');
const fs = require('fs');
const path = require('path');

// Configuration for the Gaia node
const config = {
  nodeId: process.env.NODE_ID || "eliza-insurance-processor",
  nodeType: "performer",
  boundlessConfig: {
    zkProofType: "groth16",
    circuitPath: path.join(__dirname, "circuits", "insurance-claim.json")
  },
  aggregatorEndpoints: [
    "https://aggregator1.gaianet.ai",
    "https://aggregator2.gaianet.ai"
  ],
  apiKey: process.env.GAIA_API_KEY
};

// Ensure required directories exist
function ensureDirectories() {
  const dirs = [
    path.join(__dirname, "data"),
    path.join(__dirname, "logs"),
    path.join(__dirname, "circuits")
  ];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`Created directory: ${dir}`);
    }
  });
}

// Initialize the ELIZA Gaia node
async function initializeNode() {
  try {
    ensureDirectories();
    
    // Save configuration
    fs.writeFileSync(
      path.join(__dirname, "config.json"),
      JSON.stringify(config, null, 2)
    );
    
    console.log("Starting ELIZA insurance claim processor node...");
    const elizaNode = setupElizaGaiaNode();
    
    // This would be replaced with actual Gaia node startup logic
    console.log(`Node successfully connected with ID: ${elizaNode.nodeConnection.nodeId}`);
    
    // Example of processing a claim
    const exampleClaim = "Hello, I need to file a claim. My policy number is POL-12345-XYZ. " +
      "The incident date was 2/15/2025. There was damage to my living room ceiling from a water leak. " +
      "I'm claiming $1,200 for repairs.";
    
    const result = await elizaNode.processClaimAndGenerateProof(exampleClaim);
    console.log("Claim processing result:", JSON.stringify(result, null, 2));
    
    // In a real implementation, this would start a server or connect to the Gaia network
    console.log("Node is running and ready to process insurance claims");
    
    return elizaNode;
  } catch (error) {
    console.error("Failed to initialize ELIZA Gaia node:", error);
    process.exit(1);
  }
}

// Run the node
if (require.main === module) {
  initializeNode();
}

module.exports = { initializeNode };