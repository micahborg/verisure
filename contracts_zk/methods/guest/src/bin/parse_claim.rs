// Copyright 2023 RISC Zero, Inc.
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

extern crate alloc; // Enable `alloc` for heap allocations

use json::parse;
use alloc::string::String;  // import `String` for `no_std`
use alloc::vec::Vec;        // import `Vec` for `no_std`
use serde_json::Value;
use json_core::Outputs;
use risc0_zkvm::{
    guest::env,
    sha::{Impl, Sha256},
};

fn main() {
    let claim_json: String = env::read();
    let required_json: String = env::read();

    let claim: Value = serde_json::from_str(&claim_json).unwrap();
    let required_fields: Vec<String> = serde_json::from_str(&required_json).unwrap();

    // Check for required fields
    for field in required_fields.iter() {
        if let Some(value) = claim.get(field) {
            //println!("Claim: {:?}", value);
            let value_str = value.as_str().unwrap_or("");
    
            assert!(
                !value_str.is_empty(),
                "Missing required field or empty: {}",
                field
            );
        } else {
            panic!("Missing required field: {}", field);
        }
    }    

    let data = parse(&claim_json).unwrap();
    let total_charge = data["28_total_charge"].as_f32().unwrap();

    let sha = *Impl::hash_bytes(&claim_json.as_bytes());
    let out = Outputs {
        data: total_charge,
        hash: sha,
    };

    env::commit(&out);
}

