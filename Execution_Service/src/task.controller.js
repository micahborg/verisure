"use strict";
const { Router } = require("express")
const { execFile } = require("child_process");
const path = require("path");
const fs = require("fs");
const CustomError = require("./utils/validateError");
const CustomResponse = require("./utils/validateResponse");
const oracleService = require("./oracle.service");
const dalService = require("./dal.service");

const rustBinaryPath = path.join(__dirname, "../../contracts_zk/target/release/publisher");

const router = Router();

router.post("/execute", async (req, res) => {
    console.log("Executing task");

    // Write claim data to temp files
    fs.writeFileSync("temp_claim.json", JSON.stringify(req.body.claim));


    execFile(rustBinaryPath, ["--claim-file", "temp_claim.json"], (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution error: ${error.message}`);
            return res.status(500).send({ error: "Proof generation failed" });
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).send({ error: "Proof generation error", stderr });
        }

        console.log(`Proof output: ${stdout}`);
        const receipt = JSON.parse(stdout);  // Parse Rust JSON output

        return res.status(200).send({
            proofOfTask: receipt.control_id,
            claimJournal: receipt.journal,
            message: "Task executed successfully"
        });
    });
});


module.exports = router
