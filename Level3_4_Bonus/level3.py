import os
import pandas as pd
import folium
from folium.plugins import HeatMap, MiniMap, MeasureControl

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

    # Convert coordinates to numeric and drop rows with missing values
    df["latitude (y)"] = pd.to_numeric(df["latitude (y)"])
    df["longitude (x)"] = pd.to_numeric(df["longitude (x)"])
    df.dropna(subset=["latitude (y)", "longitude (x)"], inplace=True)

    if df.empty:
        print("No valid rows. Nothing to display.")
        return "No valid data for the map."

    # Base map centered around median coordinates
    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    #  MiniMap and MeasureControl tools for additional interactivity
    sanfran_map.add_child(MiniMap())
    sanfran_map.add_child(MeasureControl())

    # A dictionary to hold a FeatureGroup for each crime category.
    category_groups = {}

    # Get the respective category
    if "category" in df.columns:
        unique_categories = df["category"].unique()
    else:
        unique_categories = ["Crime"]

    # FeatureGroup for each category 
    for category in unique_categories:
        group = folium.FeatureGroup(name=category)
        category_groups[category] = group
        sanfran_map.add_child(group)

    # Create markers and add them to the corresponding category FeatureGroup.
    lat_column = "latitude (y)"
    lon_column = "longitude (x)"
    labels = df["category"].tolist() if "category" in df.columns else ["Crime"] * len(df)

    for lat, lon, label in zip(df[lat_column], df[lon_column], labels):
        popup_info = f"""
        <div style="width:150px;">
          <strong>{label}</strong><br>
          Lat: {lat:.4f}<br>
          Lon: {lon:.4f}
        </div>
        """
        marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_info, max_width=200),
            tooltip=label,
            icon=folium.Icon(color="black", icon="info-sign")
        )
        # Add the marker to its respective category group
        category_groups[label].add_child(marker)

    # HeatMap layer for overall incident concentration
    heat_map = [[row[lat_column], row[lon_column]] for _, row in df.iterrows()]
    HeatMap(heat_map, radius=15, name="Crime Heatmap").add_to(sanfran_map)

    folium.LayerControl(collapsed=False).add_to(sanfran_map)

    return sanfran_map._repr_html_()
