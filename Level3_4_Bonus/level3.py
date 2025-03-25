# level3.py
import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster

base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")

def create_geo_map():

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    df.rename(columns={
        "latitude (y)": "temp_long",
        "longitude (x)": "temp_lat"
    }, inplace=True)
    df.rename(columns={
        "temp_long": "longitude (x)",
        "temp_lat": "latitude (y)"
    }, inplace=True) # Rename due to opposite values in original dataset


    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True) 

    if df.empty:
        print("No valid rows. Nothing to display.")
        return "<h3>No valid data for the map.</h3>"

    if len(df) > 100:
        df = df.sample(n=100, random_state=42)     # Sample data for quicker results, comment out for testing full dataset

    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    incidents = MarkerCluster().add_to(sanfran_map)
    lat_col = "latitude (y)"
    lon_col = "longitude (x)"
    if "category" in df.columns:
        labels = df["category"].tolist()
    else:
        labels = ["Crime" for _ in range(len(df))]

    for lat, lng, label in zip(df[lat_col], df[lon_col], labels):
        folium.Marker(
            location=[lat, lng],
            popup=label
        ).add_to(incidents)

    return sanfran_map._repr_html_()
