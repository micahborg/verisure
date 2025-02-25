import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extracts text directly from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return [line.strip() for line in text.split("\n") if line.strip()]

def parse_claim_data(lines):
    """Extracts claim data for your specific PDF form."""
    claim_data = {}

    # Hardcoded indices for your specific PDF form
    claim_data["Policy Holder Name"] = lines[118]  # Eth Den
    claim_data["Patient Name"] = lines[116]  # Eig Gam
    claim_data["Patient DOB"] = lines[117]  # 06/14/2000
    claim_data["Patient Sex"] = "Male" if "Male" in lines[10] else "Female"  # Male
    claim_data["Policy Holder DOB"] = lines[119]  # 06/14/1973

    # Fix Relationship to Enrollee
    relationship = "Flag for Review"
    if "Spouse" in lines[16]:  # Hardcoded for your form
        relationship = "Spouse"
    claim_data["Relationship to Enrollee"] = relationship

    claim_data["Address"] = lines[120]  # 1874 Curtis Hotel, Denver, Colorado, 80202
    claim_data["Email"] = lines[121]  # eiggam@gmail.coom

    # Fix Medicare Part A Effective Date
    medicare_a_effective = lines[123]  # Hardcoded for your form (04/12/1999)
    claim_data["Medicare Part A Effective"] = medicare_a_effective

    # Fix Medicare Part B Effective Date
    medicare_b_effective = lines[124]  # Hardcoded for your form (05/20/1997)
    claim_data["Medicare Part B Effective"] = medicare_b_effective
    
    # Medicare HMO
    medicare_hmo_effective = lines[125]  
    claim_data["Medicare HMO Effective"] = medicare_hmo_effective

    claim_data["ESRD Date"] = lines[126]  # 01/14/2021

   # Fix Accident Date
    accident_date = lines[65]  # Hardcoded for your form
    if accident_date != "5A. DATE OF ACCIDENT":
        claim_data["Accident Date"] = accident_date
    else:
        claim_data["Accident Date"] = "Flag for Review"

    claim_data["Provider Name"] = lines[127]  # Dr. Djsowj Aosdje
    claim_data["Service Description"] = lines[128]  # Office Visits, Therapy
    claim_data["Date of Service From"] = lines[129]  # 02/23/2025
    claim_data["Charge Amount"] = lines[130]  # 499.99
    claim_data["Phone Number"] = lines[133]  # 9130000000

    policy_number = ""
    for i in range(107, 116):  # Lines 107-115 contain the policy number digits
        policy_number += lines[i]  # Concatenate each digit
        claim_data["Policy Number"] = policy_number

    return claim_data

# Example usage
pdf_path = r"C:\Users\nisch\OneDrive\Desktop\verisure\samples\sample_claim.pdf"
lines = extract_text_from_pdf(pdf_path)

# Parse claim data
claim_data = parse_claim_data(lines)

print("\nExtracted Claim Information:")
for key, value in claim_data.items():
    print(f"{key}: {value}")