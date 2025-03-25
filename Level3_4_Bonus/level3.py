# level3.py
import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster

from model import assign_severity

base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")

def severity_to_icon_color(severity):
    
    color_map = {
        1: "green",
        2: "blue",
        3: "orange",
        4: "red",
        5: "darkred"
    }
    return color_map.get(severity, "gray")

def severity_to_color(severity):
    """
    Returns a color for each severity level.
    You can use discrete named colors (e.g., 'red', 'green')
    or hex codes for a smoother gradient.
    """
    color_map = {
        1: "#ffffb2", 
        2: "#fed976",
        3: "#feb24c",
        4: "#fd8d3c",
        5: "#f03b20",  
    }
    return color_map.get(severity, "#808080")


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
    }, inplace=True)

    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True)

    if df.empty:
        print("No valid rows. Nothing to display.")
        return "<h3>No valid data for the map.</h3>"


    # if len(df) > 300:
    #     df = df.sample(n=300, random_state=42)


    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
    )


    incidents = MarkerCluster().add_to(sanfran_map)


    if "category" in df.columns:
        labels = df["category"].tolist()
    else:
        labels = ["Crime" for _ in range(len(df))]

    lat_col = "latitude (y)"
    lon_col = "longitude (x)"

    for lat, lng, category in zip(df[lat_col], df[lon_col], labels):

        sev = assign_severity(category)
        icon_color = severity_to_icon_color(sev)
        bg_color = severity_to_background_color(sev)

        popup_html = f"""
        <div style="background-color:{bg_color}; color:white; padding:5px; border-radius:4px;">
            <strong>{category}</strong> (Severity {sev})
        </div>
        """
        popup = folium.Popup(popup_html, max_width=200)

 
        folium.Marker(
            location=[lat, lng],
            popup=popup,
            icon=folium.Icon(color=icon_color, icon='info-sign') 
        ).add_to(incidents)

    return sanfran_map._repr_html_()
