# claim_validator.py - Module for validating claim data
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple

class ClaimValidator:
    def __init__(self, claim_data: Dict[str, Any]):
        self.claim_data = claim_data
        self.validation_issues = []
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks and return results"""
        # Check for parsing errors first
        if "parsing_error" in self.claim_data:
            return {
                "is_valid": False,
                "issues": [f"Parsing error: {self.claim_data['parsing_error']}"],
                "eligibility": "DENIED",
                "confidence": 1.0
            }
        
        # Run all validation functions
        self._validate_required_fields()
        self._validate_patient_info()
        self._validate_policy_details()
        self._validate_service_dates()
        self._validate_dollar_amounts()
        self._validate_medicare_info()
        
        # Determine overall eligibility
        eligibility, confidence = self._determine_eligibility()
        
        return {
            "is_valid": len(self.validation_issues) == 0,
            "issues": self.validation_issues,
            "eligibility": eligibility,
            "confidence": confidence
        }
        
    def _validate_required_fields(self):
        """Check that all required fields are present and not empty"""
        required_fields = [
            "Patient Name", 
            "Patient DOB", 
            "Policy Holder Name",
            "Policy Number",
            "Date of Service From",
            "Service Description",
            "Charge Amount"
        ]
        
        for field in required_fields:
            if field not in self.claim_data or not self.claim_data[field]:
                self.validation_issues.append(f"Missing required field: {field}")
            elif field in self.claim_data and "Invalid" in str(self.claim_data[field]):
                self.validation_issues.append(f"Invalid value for {field}: {self.claim_data[field]}")
    
    def _validate_patient_info(self):
        """Validate patient demographic information"""
        # Check patient name format
        patient_name = self.claim_data.get("Patient Name", "")
        if patient_name and not re.match(r'^[A-Za-z\s\-\'\.]+$', patient_name):
            self.validation_issues.append(f"Patient name contains invalid characters: {patient_name}")
            
        # Check date of birth is in the past
        patient_dob = self.claim_data.get("Patient DOB", "")
        if patient_dob and patient_dob != "Invalid Date Format":
            try:
                dob_date = datetime.strptime(patient_dob, "%m/%d/%Y")
                if dob_date > datetime.now():
                    self.validation_issues.append(f"Patient DOB is in the future: {patient_dob}")
            except ValueError:
                self.validation_issues.append(f"Patient DOB is not a valid date: {patient_dob}")
                
        # Check relationship field
        relationship = self.claim_data.get("Relationship to Enrollee", "")
        if relationship == "Flag for Review":
            self.validation_issues.append("Relationship to enrollee could not be determined")
    
    def _validate_policy_details(self):
        """Validate insurance policy information"""
        # Check policy number format
        policy_number = self.claim_data.get("Policy Number", "")
        if policy_number and len(policy_number) < 5:
            self.validation_issues.append(f"Policy number appears too short: {policy_number}")
            
        # Check if policy holder and patient are the same person
        if self.claim_data.get("Relationship to Enrollee") == "Self":
            if (self.claim_data.get("Patient Name") != self.claim_data.get("Policy Holder Name") or
                self.claim_data.get("Patient DOB") != self.claim_data.get("Policy Holder DOB")):
                self.validation_issues.append("Relationship is 'Self' but names/DOBs don't match")
    
    def _validate_service_dates(self):
        """Validate service date is reasonable"""
        service_date = self.claim_data.get("Date of Service From", "")
        if service_date and service_date != "Invalid Date Format":
            try:
                date_obj = datetime.strptime(service_date, "%m/%d/%Y")
                
                # Service date is in the future
                if date_obj > datetime.now():
                    self.validation_issues.append(f"Service date is in the future: {service_date}")
                
                # Service date is too old (more than 1 year)
                one_year_ago = datetime.now().replace(year=datetime.now().year - 1)
                if date_obj < one_year_ago:
                    self.validation_issues.append(f"Service date is over 1 year old: {service_date}")
                    
                # Check if accident date is present and after service date
                accident_date = self.claim_data.get("Accident Date", "")
                if accident_date and accident_date != "N/A" and accident_date != "Invalid Date Format":
                    try:
                        accident_date_obj = datetime.strptime(accident_date, "%m/%d/%Y")
                        if accident_date_obj > date_obj:
                            self.validation_issues.append(f"Accident date {accident_date} is after service date {service_date}")
                    except ValueError:
                        pass
                    
            except ValueError:
                self.validation_issues.append(f"Service date is not a valid date: {service_date}")
    
    def _validate_dollar_amounts(self):
        """Validate that dollar amounts are reasonable"""
        charge_amount = self.claim_data.get("Charge Amount", "")
        if charge_amount and charge_amount.startswith("$"):
            try:
                amount = float(charge_amount.replace("$", "").replace(",", ""))
                
                # Flag extremely high amounts
                if amount > 100000:
                    self.validation_issues.append(f"Charge amount is unusually high: {charge_amount}")
                
                # Flag zero or negative amounts
                if amount <= 0:
                    self.validation_issues.append(f"Charge amount must be positive: {charge_amount}")
            except ValueError:
                self.validation_issues.append(f"Charge amount is not a valid dollar value: {charge_amount}")
    
    def _validate_medicare_info(self):
        """Validate Medicare information if present"""
        # Check if any Medicare fields are filled
        has_medicare = any([
            self.claim_data.get("Medicare Part A Effective", "") != "Invalid Date Format" and 
            self.claim_data.get("Medicare Part A Effective", "") != "",
            self.claim_data.get("Medicare Part B Effective", "") != "Invalid Date Format" and
            self.claim_data.get("Medicare Part B Effective", "") != ""
        ])
        
        if has_medicare:
            # Check if patient age is appropriate for Medicare
            patient_dob = self.claim_data.get("Patient DOB", "")
            if patient_dob and patient_dob != "Invalid Date Format":
                try:
                    dob_date = datetime.strptime(patient_dob, "%m/%d/%Y")
                    age = (datetime.now() - dob_date).days // 365
                    
                    # Flag if patient is under 65 and has Medicare without ESRD
                    if age < 65 and not self.claim_data.get("ESRD Date", ""):
                        self.validation_issues.append(f"Patient age ({age}) is under 65 for Medicare without ESRD")
                except ValueError:
                    pass
    
    def _determine_eligibility(self) -> Tuple[str, float]:
        """
        Determine claim eligibility based on validation issues
        Returns: (eligibility_status, confidence_score)
        """
        # Critical issues that automatically deny a claim
        critical_issues = [
            "Missing required field",
            "Policy number appears too short",
            "Service date is in the future",
            "Charge amount must be positive",
            "Service date is over 1 year old"
        ]
        
        # Count issues by severity
        critical_count = sum(1 for issue in self.validation_issues if any(crit in issue for crit in critical_issues))
        minor_count = len(self.validation_issues) - critical_count
        
        # Determine eligibility
        if critical_count > 0:
            return "DENIED", 0.9
        elif minor_count > 2:
            return "NEEDS_REVIEW", 0.7
        elif minor_count > 0:
            return "ELIGIBLE_WITH_WARNINGS", 0.8
        else:
            return "ELIGIBLE", 0.95