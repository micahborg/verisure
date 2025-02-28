require("dotenv").config();
const fs = require("fs");
const snarkjs = require("snarkjs");

async function validate(proofOfTask) {
  try {
    console.log("Verifying proof...");

    // Load Verifier Key (You must generate a `verification_key.json`)
    const vKey = JSON.parse(fs.readFileSync("./verification_key.json"));

    // Verify the proof using snarkjs
    const isValid = await snarkjs.groth16.verify(vKey, proofOfTask.publicSignals, proofOfTask.proof);

    console.log(isValid ? "Proof is valid!" : "Proof is invalid.");
    return isValid;
  } catch (err) {
    console.error("Verification failed:", err.message);
    return false;
  }
}

module.exports = { validate };
