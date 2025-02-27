// Copyright 2024 RISC Zero, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This application demonstrates how to send an off-chain proof request
// to the Bonsai proving service and publish the received proofs directly
// to your deployed app contract.

use anyhow::{Result};
use clap::Parser;
use methods::PARSE_CLAIM_ELF;
use serde_json::json;
use json_core::Outputs;
use risc0_zkvm::{default_prover, ExecutorEnv/*, ProverOpts, VerifierContext*/};


/// Arguments of the publisher CLI.
#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// Path to the JSON claim data file
    #[clap(short, long)]
    claim_file: String,
}


fn main() -> Result<()> {
    env_logger::init();
    let args = Args::parse();

    // Read claim JSON file dynamically
    let claim_data = std::fs::read_to_string(&args.claim_file)
        .expect("Error reading claim file");

    let env = ExecutorEnv::builder()
        .write(&claim_data)
        .unwrap()
        .build()
        .unwrap();

    let prover = default_prover();
    let prove_result = prover.prove(env, PARSE_CLAIM_ELF);

    match prove_result {
        Ok(proof_session) => {
            let receipt = proof_session.receipt;
            let outputs: Outputs = receipt.journal.decode().unwrap();

            // Output proof JSON to stdout (so Node.js can capture it)
            let output = json!({
                "receipt": receipt,
                "total_charge": outputs.data,
                "hash": outputs.hash,
            });

            println!("{}", output.to_string());
            Ok(())
        },
        Err(prove_err) => {
            eprintln!("Failed to generate proof -> {}", prove_err);
            Err(prove_err)
        }
    }
}

