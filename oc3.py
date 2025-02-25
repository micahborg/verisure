import fitz  # PyMuPDF
import json
import re
from datetime import datetime
import os

class ClaimExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.lines = self.extract_text_from_pdf()
        
    def extract_text_from_pdf(self):
        """Extracts text from a PDF file using PyMuPDF with improved handling."""
        try:
            doc = fitz.open(self.pdf_path)
            text = ""
            for page in doc:
                text += page.get_text("text")
            return [line.strip() for line in text.split("\n") if line.strip()]
        except Exception as e:
            print(f"Error extracting PDF: {str(e)}")
            return []
            
    def parse_claim_data(self):
        """Extracts claim data with improved error handling and validation."""
        if not self.lines or len(self.lines) < 133:
            return {"error": "PDF format not recognized or incomplete"}
            
        claim_data = {}
        
        # Core patient information
        try:
            claim_data["Policy Holder Name"] = self.lines[118]
            claim_data["Patient Name"] = self.lines[116]
            claim_data["Patient DOB"] = self.sanitize_date(self.lines[117])
            claim_data["Patient Sex"] = "Male" if "Male" in self.lines[10] else "Female"
            claim_data["Policy Holder DOB"] = self.sanitize_date(self.lines[119])
            
            # Relationship field
            relationship = "Flag for Review"
            if "Spouse" in self.lines[16]:
                relationship = "Spouse"
            elif "Self" in self.lines[15]:
                relationship = "Self"
            elif "Child" in self.lines[17]:
                relationship = "Child"
            claim_data["Relationship to Enrollee"] = relationship
            
            # Contact information
            claim_data["Address"] = self.lines[120]
            claim_data["Email"] = self.validate_email(self.lines[121])
            claim_data["Phone Number"] = self.validate_phone(self.lines[133])
            
            # Medicare information
            claim_data["Medicare Part A Effective"] = self.sanitize_date(self.lines[123])
            claim_data["Medicare Part B Effective"] = self.sanitize_date(self.lines[124])
            claim_data["Medicare HMO Effective"] = self.sanitize_date(self.lines[125])
            claim_data["ESRD Date"] = self.sanitize_date(self.lines[126])
            
            # Accident information
            accident_date = self.lines[65]
            if accident_date != "5A. DATE OF ACCIDENT":
                claim_data["Accident Date"] = self.sanitize_date(accident_date)
            else:
                claim_data["Accident Date"] = "N/A"
                
            # Service information
            claim_data["Provider Name"] = self.lines[127]
            claim_data["Service Description"] = self.lines[128]
            claim_data["Date of Service From"] = self.sanitize_date(self.lines[129])
            claim_data["Charge Amount"] = self.validate_currency(self.lines[130])
            
            # Policy number reconstruction
            policy_number = ""
            for i in range(107, 116):
                policy_number += self.lines[i]
            claim_data["Policy Number"] = policy_number.strip()
            
            # Add extraction metadata
            claim_data["Extraction Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            claim_data["Source File"] = os.path.basename(self.pdf_path)
            
        except Exception as e:
            claim_data["parsing_error"] = str(e)
            claim_data["error_location"] = "Data extraction phase"
            
        return claim_data
    
    def sanitize_date(self, date_str):
        """Validate and standardize date format."""
        try:
            # Clean the string and check for common date patterns
            date_str = date_str.strip()
            date_pattern = re.compile(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})')
            match = date_pattern.search(date_str)
            
            if match:
                month, day, year = match.groups()
                # Ensure 4-digit year
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                return f"{month.zfill(2)}/{day.zfill(2)}/{year}"
            return date_str
        except:
            return "Invalid Date Format"
    
    def validate_email(self, email_str):
        """Validate email format."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if email_pattern.match(email_str):
            return email_str
        return f"Invalid Email: {email_str}"
    
    def validate_phone(self, phone_str):
        """Validate and format phone number."""
        # Remove non-numeric characters
        digits = re.sub(r'\D', '', phone_str)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone_str
    
    def validate_currency(self, amount_str):
        """Validate and format currency amount."""
        try:
            # Remove any currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', amount_str)
            # Format as currency with 2 decimal places
            return f"${float(cleaned):.2f}"
        except:
            return amount_str

def process_claim_file(pdf_path, output_json=None):
    """Process a claim file and optionally save to JSON."""
    extractor = ClaimExtractor(pdf_path)
    claim_data = extractor.parse_claim_data()
    
    if output_json:
        with open(output_json, 'w') as json_file:
            json.dump(claim_data, json_file, indent=4)
        print(f"Extracted claim information saved to {output_json}")
    
    return claim_data

# Example usage
if __name__ == "__main__":
    pdf_path = r"C:\Users\nisch\Desktop\verisure\samples\sample_claim.pdf"
    output_json_path = r"C:\Users\nisch\Desktop\verisure\samples\claim_data.json"
    claim_data = process_claim_file(pdf_path, output_json_path)
    print(json.dumps(claim_data, indent=2))
