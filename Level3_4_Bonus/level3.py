import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, MiniMap, MeasureControl
from folium import MacroElement
from jinja2 import Template

base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")


class SelectDeselectControl(MacroElement):
    _template = Template("""
        {% macro script(this, kwargs) %}
        // Custom control for select/deselect all marker clusters
        L.Control.SelectDeselect = L.Control.extend({
            options: { position: 'topright' },
            onAdd: function(map) {
                var container = L.DomUtil.create('div', 'select-deselect-control leaflet-bar');
                container.style.background = 'white';
                container.style.padding = '5px';
                container.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
                container.innerHTML = '<button id="selectAll" style="margin:2px; padding:5px;">Select All</button> <button id="deselectAll" style="margin:2px; padding:5px;">Deselect All</button>';
                return container;
            }
        });
        L.control.selectDeselect = function(opts) {
            return new L.Control.SelectDeselect(opts);
        }
        var mapObj = window["{{ this._parent.get_name() }}"];
        L.control.selectDeselect({ position: 'topright' }).addTo(mapObj);

        // After a short delay, attach click events to the buttons
        setTimeout(function() {
            var markerClusters = [];
            mapObj.eachLayer(function(layer) {
                if (layer instanceof L.MarkerClusterGroup) {
                    markerClusters.push(layer);
                }
            });
            document.getElementById('selectAll').onclick = function(){
                markerClusters.forEach(function(cluster) {
                    if (!mapObj.hasLayer(cluster)) {
                        mapObj.addLayer(cluster);
                    }
                });
            };
            document.getElementById('deselectAll').onclick = function(){
                markerClusters.forEach(function(cluster) {
                    if (mapObj.hasLayer(cluster)) {
                        mapObj.removeLayer(cluster);
                    }
                });
            };
        }, 1000);
        {% endmacro %}
    """)


class ZoomMarkerToggle(MacroElement):
    def __init__(self, zoom_threshold=14):
        super(ZoomMarkerToggle, self).__init__()
        self._name = 'ZoomMarkerToggle'
        self.zoom_threshold = zoom_threshold
        self._template = Template("""
            {% macro script(this, kwargs) %}
            var mapObj = window["{{ this._parent.get_name() }}"];
            mapObj.on('zoomend', function() {
                var zoomLevel = mapObj.getZoom();
                mapObj.eachLayer(function(layer) {
                    if (layer instanceof L.MarkerClusterGroup) {
                        if (zoomLevel < {{ this.zoom_threshold }} && mapObj.hasLayer(layer)) {
                            mapObj.removeLayer(layer);
                        }
                        if (zoomLevel >= {{ this.zoom_threshold }} && !mapObj.hasLayer(layer)) {
                            mapObj.addLayer(layer);
                        }
                    }
                });
            });
            {% endmacro %}
        """)

def create_geo_map():
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    # Swap latitude and longitude columns because they are reversed in the original dataset
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

    # Create the base map centered at the median coordinates
    sanfran_map = folium.Map(
        location=[df["latitude (y)"].median(), df["longitude (x)"].median()],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    # Reposition MiniMap to bottom left so it doesn't cover the checklist
    sanfran_map.add_child(MiniMap(position="bottomleft"))
    sanfran_map.add_child(MeasureControl())

    lat_col = "latitude (y)"
    lon_col = "longitude (x)"


    if "category" in df.columns:
        categories = df["category"].unique()
    else:
        categories = ["Crime"]

    category_clusters = {}
    for cat in categories:
        category_clusters[cat] = MarkerCluster(name=f"{cat} Incidents", disableClusteringAtZoom=16)
    

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


    folium.LayerControl(collapsed=False, position='topright').add_to(sanfran_map)


    sanfran_map.add_child(SelectDeselectControl())
    sanfran_map.add_child(ZoomMarkerToggle(zoom_threshold=14))

    return sanfran_map._repr_html_()

