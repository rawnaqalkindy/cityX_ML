

# CityX Crime Dashboard

**Important Note: The original dataset has been shrank to 300 entries. This is for deployment puposes, in order to stay within free resources. The file that is responsible for shrinking the dataset is shrink_dataset.py.

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

# How to Combine and Run - using Railway ( Bonus Part B )

1. Ensure railway deployment is running
2. open https://cityxml-production.up.railway.app
