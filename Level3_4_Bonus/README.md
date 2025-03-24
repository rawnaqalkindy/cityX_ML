

# CityX Crime Dashboard

This project provides an interactive web UI for exploring crime trends in CityX. It is divided into two main sections:
- **Level 3: Geo-Spatial Mapping & Basic Web UI** – Visualize crime hotspots on an interactive map.
- **Level 4: Advanced Web UI & Report Extraction** – Automatically extract and classify police reports from PDF files.

# Setup & Installation

1. Clone the repository or download the project files.
2. Install dependencies:**
   ```bash
   pip install -r requirements.txt

# How to Combine and Run - using docker ( Bonus Part A )

1. Ensure Docker is installed and running on local 
2. change directory to cityX_ML/Level3_4_Bonus 
3. run 'docker build -t cityx-crime-dashboard .'
4. run 'docker run -p 8501:8501 cityx-crime-dashboard'
5. open http://localhost:8501 

# How to Combine and Run - using AWS ( Bonus Part B )




# ADDITIONAL NOTES:
 - For level 3:
 - The mapping can be zoomed in and out, showcasing the total amount of crimes in the section, when zoomed out completely all crimes are summed up. 
 - When each pointer is touched by the mouse, it reads oit the catgeory of the crime
 - Each area on the map can be selected to showcase the crimes surrounding the parameter
