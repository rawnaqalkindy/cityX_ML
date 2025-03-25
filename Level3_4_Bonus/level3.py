import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, MeasureControl

base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")

def create_geo_map():
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    # Rename latitude and longitude columns due to reversed values in original dataset
    df.rename(columns={
        "latitude (y)": "temp_long",
        "longitude (x)": "temp_lat"
    }, inplace=True)
    df.rename(columns={
        "temp_long": "longitude (x)",
        "temp_lat": "latitude (y)"
    }, inplace=True)

    # Convert coordinate columns to numeric and drop invalid rows
    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True)

    if df.empty:
        print("No valid rows. Nothing to display.")
        return "<h3>No valid data for the map.</h3>"


    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    sanfran_map.add_child(MiniMap())
    sanfran_map.add_child(MeasureControl())

    lat_col = "latitude (y)"
    lon_col = "longitude (x)"


    if "category" in df.columns:
        categories = df["category"].unique()
    else:
        categories = ["Crime"]


    category_clusters = {}
    for cat in categories:
        category_clusters[cat] = MarkerCluster(name=f"{cat} Incidents")


    for _, row in df.iterrows():
        lat = row[lat_col]
        lng = row[lon_col]
        label = row["category"] if "category" in df.columns else "Crime"
        popup_html = f"""
        <div style="width:150px;">
          <strong>{label}</strong><br>
          Lat: {lat:.4f}<br>
          Lon: {lng:.4f}
        </div>
        """
        marker = folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=label,
            icon=folium.Icon(color="red", icon="info-sign")
        )
        category_clusters[label].add_child(marker)


    for cluster in category_clusters.values():
        sanfran_map.add_child(cluster)

    heat_data = [[row[lat_col], row[lon_col]] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=15, name="Crime Heatmap").add_to(sanfran_map)


    folium.LayerControl().add_to(sanfran_map)

    return sanfran_map._repr_html_()
