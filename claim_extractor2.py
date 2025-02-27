import sys
import json
import PyPDF2
import fitz  # PyMuPDF for raw text extraction
import re
from datetime import datetime

class ClaimExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.claim_data = {}
        self.raw_lines = self.extract_raw_text_lines_pdf() # Extract raw lines using PyMuPDF

    def extract_form_data(self):
        # (Existing PyPDF2 form field extraction - no change)
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            form_data = {}
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        field = annotation.get_object()
                        if '/T' in field:
                            field_name = field['/T']
                            field_value = field.get('/V', '')
                            form_data[field_name] = field_value
            return form_data

    def extract_raw_text_lines_pdf(self):
        """Extracts raw text lines from PDF using PyMuPDF."""
        try:
            doc = fitz.open(self.pdf_path)
            text = "\n".join([page.get_text("text") for page in doc])
            return [line.strip() for line in text.split("\n") if line.strip()]
        except Exception as e:
            print(f"Error extracting raw text lines from PDF: {str(e)}")
            return []


    def sanitize_date(self, mm, dd, yy):
        """Combines and sanitizes date components into MM/DD/YYYY format for single dates."""
        if mm and dd and yy:
            return f"{mm.zfill(2)}/{dd.zfill(2)}/{yy}"
        return ""

    def parse_claim_data(self):
        # Extract raw form data (using PyPDF2 - still used for fillable fields)
        form_data = self.extract_form_data()
        if not form_data:
            print("No form data found in the PDF.")
            return {}

        # Mapping raw field names to desired JSON keys and transformations (mostly unchanged)
        data_mapping = {
            "1a_identification_number": "insurance_id",
            "2_patient_name": "pt_name",
            "3_patient_dob": ("birth_mm", "birth_dd", "birth_yy"),
            "4_policy_holder_name": "ins_name",
            "5_patient_address": "pt_street",
            "7_policy_holder_address": "ins_street",
            "11_policy_holder_group_number": "ins_policy",
            "11a_policy_holder_dob": ("ins_dob_mm", "ins_dob_dd", "ins_dob_yy"),
            "11b_policy_holder_other_claim_id": None,
            "11c_insurance_plan_name": "ins_plan_name",
            "14_date_of_current_illness": ("cur_ill_mm", "cur_ill_dd", "cur_ill_yy"),
            "15_date_of_similar_illness": ("sim_ill_mm", "sim_ill_dd", "sim_ill_yy"),
            "16_date_unable_to_work": ("work_mm_from", "work_dd_from", "work_yy_from", "work_mm_end", "work_dd_end", "work_yy_end"),
            "17_name_of_other_source": "ref_physician",
            "17a_referring_physician_id": "id_physician",
            "17b_referring_physician_npi": "physician number 17a",
            "18_date_of_hospital_stay": ("hosp_mm_from", "hosp_dd_from", "hosp_yy_from", "hosp_mm_end", "hosp_dd_end", "hosp_yy_end"),
            "19_additional_claim_info": "Suppl",
            "20_outside_lab_charges": "charge",
            "21_diagnosis_codes": ["diagnosis1", "diagnosis2", "diagnosis3", "diagnosis4", "diagnosis5", "diagnosis6", "diagnosis7", "diagnosis8", "diagnosis9", "diagnosis10", "diagnosis11", "diagnosis12"],
            "22_resubmission_code": "medicaid_resub",
            "23_prior_authorization_number": "prior_auth",
            "24a_dates_of_service": "RAW_LINES_24A_DATES_OF_SERVICE", # Placeholder - will handle in code
            "24b_place_of_service": ["place1", "", "", "", "", ""],
            "24c_emergency_indicator": ["emg1", "emg2", "emg3", "emg4", "emg5", "emg6"],
            "24d_procedure_codes": ["cpt1", "cpt2", "cpt3", "cpt4", "cpt5", "cpt6"],
            "24e_diagnosis_pointer": ["diag1", "diag2", "diag3", "diag4", "diag5", "diag6"],
            "24f_charges": ["ch1", "ch2", "ch3", "ch4", "ch5", "ch6"],
            "24g_days_or_units": ["day1", "day2", "day3", "day4", "day5", "day6"],
            "24h_epsdt_family_plan": ["epsdt1", "epsdt2", "epsdt3", "epsdt4", "epsdt5", "epsdt6"],
            "24i_id_qualifier": ["type1", "type2", "type3", "type4", "type5", "type6"],
            "24j_rendering_provider_id": ["local1", "local2", "local3", "local4", "local5", "local6"],
            "25_federal_tax_id": "tax_id",
            "26_patient_account_number": "pt_account",
            "28_total_charge": "t_charge",
            "29_amount_paid": "0.00",
            "31_signature_is_valid": "physician_signature",
            "33_billing_provider_info": "doc_name"
        }
        # Checkbox
        try:
            # Extract checkbox values from raw lines
            transformed_data["3_patient_sex"] = "Male" if "Male" in self.lines[10] else "Female" # Updated Code 
            
            relationship = "N/A"
            if "Spouse" in self.lines[16]:
                relationship = "Spouse"
            elif "Self" in self.lines[15]:
                relationship = "Self"
            elif "Child" in self.lines[17]:
                relationship = "Child"
            transformed_data["6_relationship_to_policy_holder"] =  relationship
            
            transformed_data["10a_patient_condition_related_to_employment"] = "Yes" if "YES" in self.lines[62] else "No"  
            transformed_data["10b_patient_condition_related_to_auto_accident"] =  "Yes" if "YES" in self.lines[64] else "No" 
            transformed_data["10c_patient_condition_related_to_other_accident"] = "Yes" if "YES" in self.lines[66] else "No"
            
            transformed_data["11a_policy_holder_sex"] = "Male" if "Male" in self.lines[70] else "Female" # There is no mention of Female in the document
            transformed_data["11d_other_health_benefit_plan"] = "Yes" if "YES" in self.lines[76] else "No" 
            transformed_data["27_accept_assignment"] = "Yes" if "YES" in self.lines[142] else "No"
        except Exception as e:
            print(f"Error checkbox value: {e}")

        # sets initial data values
        transformed_data = {}
        transformed_data["1_type_of_insurance"] = "GROUP HEALTH PLAN"
        transformed_data["3_patient_sex"] = "F"
        transformed_data["6_relationship_to_policy_holder"] = "Spouse"
        transformed_data["10a_patient_condition_related_to_employment"] = "NO"
        transformed_data["10b_patient_condition_related_to_auto_accident"] = "NO"
        transformed_data["10c_patient_condition_related_to_other_accident"] = "NO"
        transformed_data["11a_policy_holder_sex"] = "M"
        transformed_data["11d_other_health_benefit_plan"] = "NO"
        transformed_data["12_patient_valid_signed"] = "Yes"
        transformed_data["13_polcy_holder_valid_signed"] = "Yes"
        transformed_data["27_accept_assignment"] = "Yes"
        transformed_data["29_amount_paid"] = "0.00"
        transformed_data["31_signature_is_valid"] = "Yes"

        # Extract Checkbox Values
        # Checkbox
        try:
            # Extract checkbox values from raw lines
            transformed_data["3_patient_sex"] = "Male" if "Male" in self.lines[10] else "Female" # Updated Code 
            
            relationship = "N/A"
            if "Spouse" in self.lines[16]:
                relationship = "Spouse"
            elif "Self" in self.lines[15]:
                relationship = "Self"
            elif "Child" in self.lines[17]:
                relationship = "Child"
            transformed_data["6_relationship_to_policy_holder"] =  relationship
            
            transformed_data["10a_patient_condition_related_to_employment"] = "Yes" if "YES" in self.lines[62] else "No"  
            transformed_data["10b_patient_condition_related_to_auto_accident"] =  "Yes" if "YES" in self.lines[64] else "No" 
            transformed_data["10c_patient_condition_related_to_other_accident"] = "Yes" if "YES" in self.lines[66] else "No"
            
            transformed_data["11a_policy_holder_sex"] = "Male" if "Male" in self.lines[70] else "Female" # There is no mention of Female in the document
            transformed_data["11d_other_health_benefit_plan"] = "Yes" if "YES" in self.lines[76] else "No" 
            transformed_data["27_accept_assignment"] = "Yes" if "YES" in self.lines[142] else "No"

        except Exception as e:
            print(f"Error checkbox value: {e}")

        for target_key, source_fields in data_mapping.items():
            if target_key == "24a_dates_of_service": # Handle 24a_dates_of_service specially using raw lines
                if len(self.raw_lines) >= 37: # Make sure lines exist
                    from_date_parts = [self.raw_lines[31], self.raw_lines[32], self.raw_lines[33]] # Lines 032-034 (index 31-33)
                    to_date_parts = [self.raw_lines[34], self.raw_lines[35], self.raw_lines[36]]   # Lines 035-037 (index 34-36)
                    from_date_str = self.sanitize_date(*from_date_parts)
                    to_date_str = self.sanitize_date(*to_date_parts)
                    if from_date_str and to_date_str:
                        transformed_data[target_key] = [f"{from_date_str} - {to_date_str}"] # Create list with date range
                    else:
                        transformed_data[target_key] = [] # Empty list if dates missing
                else:
                    transformed_data[target_key] = [] # Empty list if raw lines not enough
            elif isinstance(source_fields, str): # ... (rest of existing data transformation logic - unchanged) ...
                transformed_data[target_key] = form_data.get(source_fields, "")
            elif isinstance(source_fields, tuple) and len(source_fields) == 3:
                date_parts = [form_data.get(field, "") for field in source_fields]
                transformed_data[target_key] = self.sanitize_date(*date_parts)
            elif isinstance(source_fields, tuple) and len(source_fields) > 3:
                date_parts = [form_data.get(field, "") for field in source_fields]
                from_date_parts = date_parts[:3]
                to_date_parts = date_parts[3:]
                from_date_str = self.sanitize_date(*from_date_parts)
                to_date_str = self.sanitize_date(*to_date_parts)
                if from_date_str and to_date_str:
                    transformed_data[target_key] = f"{from_date_str} - {to_date_str}"
                else:
                    transformed_data[target_key] = ""
            elif isinstance(source_fields, list):
                 transformed_data[target_key] = [form_data.get(field, "") for field in source_fields if form_data.get(field, "")]
            elif source_fields is None:
                transformed_data[target_key] = ""

        # Address combination and other post-processing (unchanged)
        transformed_data["5_patient_address"] = ", ".join(filter(None, [transformed_data.get("5_patient_address"), form_data.get("pt_city", ""), form_data.get("pt_state", ""), form_data.get("pt_zip", "")]))
        transformed_data["7_policy_holder_address"] = ", ".join(filter(None, [transformed_data.get("7_policy_holder_address"), form_data.get("ins_city", ""), form_data.get("ins_state", ""), form_data.get("ins_zip", "")]))

        return transformed_data



def main(pdf_path):
    extractor = ClaimExtractor(pdf_path)
    transformed_claim_data = extractor.parse_claim_data()
    print(json.dumps(transformed_claim_data, indent=4))


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter PDF path: ")
    main(pdf_path)