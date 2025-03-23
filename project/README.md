

# CityX Crime Dashboard

This project provides an interactive web UI for exploring crime trends in CityX. It is divided into two main sections:
- **Level 3: Geo-Spatial Mapping & Basic Web UI** – Visualize crime hotspots on an interactive map.
- **Level 4: Advanced Web UI & Report Extraction** – Automatically extract and classify police reports from PDF files.

# Project Structure

project/
├── __pycache__/              
├── .streamlit/
│   └── config.toml             # Streamlit theme settings
├── police_reports/             # Folder containing PDF police reports
│   ├── police_crime_report_1.pdf
│   ├── police_crime_report_2.pdf
│   ├── ...
├── app.py                      # Main Streamlit dashboard (entry point)
├── Competition_Dataset.csv     # Dataset used for training & inference
├── Dockerfile                  # Docker configuration
├── level3.py                   # Level 3: Geo-Spatial Mapping code
├── level4.py                   # Level 4: PDF extraction & classification
├── model.py                    # Level 2: Model loading, training, & severity assignment
├── README.md                   # This file
└── requirements.txt            # Python dependencies

# Setup & Installation

1. Clone the repository or download the project files.
2. Install dependencies:**
   ```bash
   pip install -r requirements.txt


# How to Combine and Run - using docker ( Bonus Part A )

1. Ensure Docker is installed and running on local 
2. from project/ directory run 'docker build -t cityx-crime-dashboard .'
3. run 'docker run -p 8501:8501 cityx-crime-dashboard'
4. open http://localhost:8501 

# How to Combine and Run - using AWS ( Bonus Part B)



# ADDITIONAL NOTES:

# For Level 3 
 -The mapping can be zoomed in and out, showcasing the total amount of crimes in the section, when zoomed out completely all crimes are summed up. 
 - When each pointer is touched by the mouse, it reads oit the catgeory of the crime
 - Each area on the map can be selected to showcase the crimes surrounding the parameter