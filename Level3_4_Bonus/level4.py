# level4.py
import os
import re
import pandas as pd
import PyPDF2
from model import assign_severity

base_path = "/app/police_reports"

# Extracting the text from pdf reports
def extract_text(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error in reading file")
    return text

# Parses the police reports and finds+stores matches
def parse_report(text):
    patterns = {
        "report_number": r"Report Number:\s*([^\n]+)",
        "date_time": r"Date & Time:\s*([^\n]+)",
        "reporting_officer": r"Reporting Officer:\s*([^\n]+)",
        "incident_location": r"Incident Location:\s*([^\n]+)",
        "coordinates": r"Coordinates:\s*\(([^)]+)\)",
        "detailed_description": r"Detailed Description:\s*([\s\S]+?)(?=\n\s*\w)",
        "police_district": r"Police District:\s*([^\n]+)",
        "resolution": r"Resolution:\s*([^\n]+)",
        "suspect_description": r"Suspect Description:\s*([^\n]+)",
        "victim_information": r"Victim Information:\s*([^\n]+)",
    }
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        data[key] = match.group(1).strip() if match else ""
    return data

def process_reports():
    pdf_files = [
        os.path.join(base_path, "police_crime_report_1.pdf"),
        os.path.join(base_path, "police_crime_report_2.pdf"),
        os.path.join(base_path, "police_crime_report_3.pdf"),
        os.path.join(base_path, "police_crime_report_4.pdf"),
        os.path.join(base_path, "police_crime_report_5.pdf"),
        os.path.join(base_path, "police_crime_report_6.pdf"),
        os.path.join(base_path, "police_crime_report_7.pdf"),
        os.path.join(base_path, "police_crime_report_9.pdf"),
        os.path.join(base_path, "police_crime_report_10.pdf")
    ]
    
    reports = []
    for pdf in pdf_files:
        if os.path.exists(pdf):
            text = extract_text(pdf)
            report_data = parse_report(text)
            file_name = os.path.basename(pdf)
            number_match = re.search(r"(\d+)\.pdf$", file_name)     # Extracting the number of the file
            if number_match:
                report_data["file"] = number_match.group(1)
            else:
                report_data["file"] = file_name
            reports.append(report_data)
        else:
            print(f"File not found: {pdf}")
    df_reports = pd.DataFrame(reports)
    return df_reports


