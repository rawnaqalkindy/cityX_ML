import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, MeasureControl

base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")

def create_map():
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    # Rename columns due to reversed values in original dataset
    df.rename(columns={
        "latitude (y)": "temp_long",
        "longitude (x)": "temp_lat"
    }, inplace=True)
    df.rename(columns={
        "temp_long": "longitude (x)",
        "temp_lat": "latitude (y)"
    }, inplace=True)

    # Make the values numeric and drop missing values
    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True)

    if df.empty:
        print("No valid rows. Nothing to display.")
        return "No valid data for the map."

    # Folium map centered around the median coordinates
    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
        control_scale=True
    )
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
    ).add_to(sanfran_map)

    # MiniMap for context
    sanfran_map.add_child(MiniMap())
    # MeasureControl tool for distance measuring
    sanfran_map.add_child(MeasureControl())

    # Marker cluster for grouping incidents
    incidents = MarkerCluster(name="Incidents").add_to(sanfran_map)
    lat_column = "latitude (y)"
    lon_column = "longitude (x)"

    # Label the cluster with their categories 
    if "category" in df.columns:
        labels = df["category"].tolist()
    else:
        labels = ["Crime" for _ in range(len(df))]

    # Created markers with pop up info
    for lat, lon, label in zip(df[lat_column], df[lon_column], labels):
        popup_info = f"""
        <div style="width:150px;">
          <strong>{label}</strong><br>
          Lat: {lat:.4f}<br>
          Lon: {lon:.4f}
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_info, max_width=200),
            tooltip=label,
            icon=folium.Icon(color="black", icon="info-sign")
        ).add_to(incidents)

    # HeatMap layer to visualize concentration
    heat_map = [[row[lat_column], row[lon_column]] for _, row in df.iterrows()]
    HeatMap(heat_map, radius=15, name="Crime Heatmap").add_to(sanfran_map)

    # Layer control for toggling map layers
    folium.LayerControl(collapsed=False).add_to(sanfran_map)

    return sanfran_map._repr_html_()
