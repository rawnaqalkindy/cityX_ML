import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, MeasureControl

base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")

def create_geo_map():
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

    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True)

    if df.empty:
        print("No valid rows. Nothing to display.")
        return "<h3>No valid data for the map.</h3>"

    # Create the base map
    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # Add MiniMap and MeasureControl
    sanfran_map.add_child(MiniMap())
    sanfran_map.add_child(MeasureControl())

    lat_col = "latitude (y)"
    lon_col = "longitude (x)"


    if "category" in df.columns:
        categories = df["category"].unique()
        category_groups = {}
        for cat in categories:

            group = folium.FeatureGroup(name=f"{cat} Incidents", show=False)
            marker_cluster = MarkerCluster().add_to(group)
            category_groups[cat] = marker_cluster
            sanfran_map.add_child(group)
        

        for _, row in df.iterrows():
            lat = row[lat_col]
            lng = row[lon_col]
            cat = row["category"]
            popup_html = f"""
            <div style="width:150px;">
              <strong>{cat}</strong><br>
              Lat: {lat:.4f}<br>
              Lon: {lng:.4f}
            </div>
            """
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=cat,
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(category_groups[cat])
    else:

        group = folium.FeatureGroup(name="Incidents", show=False)
        marker_cluster = MarkerCluster().add_to(group)
        sanfran_map.add_child(group)
        for lat, lng in zip(df[lat_col], df[lon_col]):
            popup_html = f"""
            <div style="width:150px;">
              <strong>Crime</strong><br>
              Lat: {lat:.4f}<br>
              Lon: {lng:.4f}
            </div>
            """
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=200),
                tooltip="Crime",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(marker_cluster)

    
    heat_data = [[row[lat_col], row[lon_col]] for _, row in df.iterrows()]
    heat_group = folium.FeatureGroup(name="Crime Heatmap", show=False)
    HeatMap(heat_data, radius=15).add_to(heat_group)
    sanfran_map.add_child(heat_group)


    folium.LayerControl(collapsed=False).add_to(sanfran_map)

    return sanfran_map._repr_html_()
