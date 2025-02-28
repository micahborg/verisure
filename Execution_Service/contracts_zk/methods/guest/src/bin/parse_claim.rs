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
//use alloc::vec::Vec;        // import `Vec` for `no_std`
use serde_json::Value;
use json_core::Outputs;
use risc0_zkvm::{
    guest::env,
    sha::{Impl, Sha256},
};

const REQUIRED_FIELDS: &[&str] = &[
    "1_type_of_insurance",
    "1a_identification_number",
    "2_patient_name",
    "3_patient_dob",
    "3_patient_sex",
    "4_policy_holder_name",
    "5_patient_address",
    "6_relationship_to_policy_holder",
    "7_policy_holder_address",
    "10a_patient_condition_related_to_employment",
    "10b_patient_condition_related_to_auto_accident",
    "10c_patient_condition_related_to_other_accident",
    "11_policy_holder_group_number",
    "11a_policy_holder_dob",
    "11a_policy_holder_sex",
    "12_patient_valid_signed",
    "13_polcy_holder_valid_signed",
    "14_date_of_current_illness",
    "21_diagnosis_codes",
    "24a_dates_of_service",
    "24d_procedure_codes",
    "28_total_charge"
];

fn main() {
    let claim_json: String = env::read();
    //let required_json: String = env::read();

    let claim: Value = serde_json::from_str(&claim_json).unwrap();
    //let required_fields: Vec<String> = serde_json::from_str(&required_json).unwrap();

    // Check for required fields
    for field in REQUIRED_FIELDS.iter() {
        if let Some(value) = claim.get(field) {
            if value.is_array() {
                let array = value.as_array().unwrap();
                assert!(
                    !array.is_empty(),
                    "Required list field is empty: {}",
                    field
                );
            } else {
                let value_str = value.as_str().unwrap_or("");
                assert!(
                    !value_str.is_empty(),
                    "Missing required field or empty: {}",
                    field
                );
            }
        } else {
            panic!("Missing required field: {}", field);
        }
    }

    let data = parse(&claim_json).unwrap();
    let total_charge = data["28_total_charge"]
        .as_str()  // Get the string
        .unwrap()  // Unwrap the Option<&str>
        .parse::<f32>()  // Convert to f32
        .unwrap();  // Unwrap Result<f32, ParseFloatError>

    let sha = *Impl::hash_bytes(&claim_json.as_bytes());
    let out = Outputs {
        data: total_charge,
        hash: sha,
    };

    env::commit(&out);
}

