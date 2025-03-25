import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, MeasureControl, TimestampedGeoJson

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

    # Convert coordinate columns to numeric
    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True)


    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        df["timestamp"] = "2025-01-01 00:00:00"

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


    incidents = MarkerCluster(name="Incidents").add_to(sanfran_map)
    lat_col = "latitude (y)"
    lon_col = "longitude (x)"
    if "category" in df.columns:
        labels = df["category"].tolist()
    else:
        labels = ["Crime" for _ in range(len(df))]

    for lat, lng, label in zip(df[lat_col], df[lon_col], labels):
        popup_html = f"""
        <div style="width:150px;">
          <strong>{label}</strong><br>
          Lat: {lat:.4f}<br>
          Lon: {lng:.4f}
        </div>
        """
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=label,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(incidents)


    heat_data = [[row[lat_col], row[lon_col]] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=15, name="Crime Heatmap").add_to(sanfran_map)

    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "properties": {
                "time": row["timestamp"],
                "popup": row["category"] if "category" in df.columns else "Crime"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude (x)"], row["latitude (y)"]]
            }
        }
        features.append(feature)

    time_geojson = {
        "type": "FeatureCollection",
        "features": features
    }

  
    TimestampedGeoJson(
        time_geojson,
        period="PT1H",  # Period between time intervals
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options='YYYY-MM-DD HH:mm:ss',
        time_slider_drag_update=True,
        name="Time Slider"
    ).add_to(sanfran_map)

    folium.LayerControl().add_to(sanfran_map)

    return sanfran_map._repr_html_()
