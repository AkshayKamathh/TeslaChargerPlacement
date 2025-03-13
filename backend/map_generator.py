import os
import requests
import pandas as pd
import folium
import time
import numpy as np
from sklearn.cluster import KMeans

def extract_parking_lots_by_bbox(city_name, state, bbox):
    """Extract parking lot data using Overpass API."""
    south, west, north, east = bbox
    place_name = f"{city_name}, {state}, USA"
    print(f"Extracting parking lots for {place_name} using bounding box...")

    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="parking"]({south},{west},{north},{east});
      way["amenity"="parking"]({south},{west},{north},{east});
      relation["amenity"="parking"]({south},{west},{north},{east});
    );
    out center;
    """
    
    try:
        response = requests.post(overpass_url, data=overpass_query)
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        if 'elements' in data and data['elements']:
            print(f"Found {len(data['elements'])} parking facilities in {place_name}")
            parking_lots = []
            for element in data['elements']:
                lat, lon = element.get('lat'), element.get('lon')
                if 'center' in element:
                    lat, lon = element['center']['lat'], element['center']['lon']
                if lat is None or lon is None:
                    continue
                
                tags = element.get('tags', {})
                lot = {
                    'id': element['id'],
                    'lat': lat,
                    'lon': lon,
                    'name': tags.get('name', f"Parking {element['id']}"),
                    'city': city_name,
                    'state': state
                }
                parking_lots.append(lot)
            return pd.DataFrame(parking_lots)
        
        print(f"No parking facilities found for {place_name}")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"Error extracting parking lots for {place_name}: {e}")
        return pd.DataFrame()

def visualize_on_map(parking_lots_df, output_html):
    """Generate a map with clustered parking lot markers."""
    if parking_lots_df.empty:
        print("No data available for visualization.")
        return

    center_lat, center_lon = parking_lots_df['lat'].mean(), parking_lots_df['lon'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    clustered_parking_lots = []
    
    for (city, state), group in parking_lots_df.groupby(['city', 'state']):
        count = len(group)
        division_factor = 160 if city == "Phoenix" else 40 if city == "Tampa" else 80
        num_markers = max(1, count // division_factor)

        if count > num_markers:
            coords = group[['lat', 'lon']].values
            kmeans = KMeans(n_clusters=num_markers, random_state=42, n_init=10)
            labels = kmeans.fit_predict(coords)
            centers = kmeans.cluster_centers_

            selected_rows = []
            for cluster_id in range(num_markers):
                cluster_points = group.iloc[np.where(labels == cluster_id)]
                cluster_coords = cluster_points[['lat', 'lon']].values
                sq_dists = np.sum((cluster_coords - centers[cluster_id])**2, axis=1)
                best_idx = cluster_points.index[np.argmin(sq_dists)]
                selected_rows.append(best_idx)

            selected_df = group.loc[selected_rows]
        else:
            selected_df = group

        clustered_parking_lots.append(selected_df)

    final_parking_lots_df = pd.concat(clustered_parking_lots, ignore_index=True)

    # Add markers with default red icons
    for _, row in final_parking_lots_df.iterrows():
        popup_text = f"<b>{row.get('name', 'Parking')}</b><br>City: {row['city']}, {row['state']}"

        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)


    # Expose myMap for JavaScript
    map_var = m.get_name()
    expose_script = f"""
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            window.myMap = window["{map_var}"];
            console.log("myMap successfully assigned:", myMap);
        }});
    </script>
    """
    m.get_root().html.add_child(folium.Element(expose_script))

    # Link marker_click.js for marker click functionality
    m.get_root().html.add_child(folium.Element('<script src="marker_click.js"></script>'))

    m.save(output_html)
    print(f"Map saved to {output_html}")

if __name__ == "__main__":
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "teslareal", "backend")
    os.makedirs(output_dir, exist_ok=True)

    cities = {
        "Phoenix": ("Arizona", (33.2000, -112.3000, 33.8000, -111.9000)),
        "Tampa": ("Florida", (27.9000, -82.5500, 28.1500, -82.3500)),
        "Atlanta": ("Georgia", (33.6500, -84.5500, 33.9000, -84.2500))
    }

    all_parking_lots = []
    for city, (state, bbox) in cities.items():
        print(f"Processing {city}...")
        parking_lots = extract_parking_lots_by_bbox(city, state, bbox)
        if not parking_lots.empty:
            all_parking_lots.append(parking_lots)

    if all_parking_lots:
        combined_df = pd.concat(all_parking_lots, ignore_index=True)
        print(f"Total parking lots found: {len(combined_df)}")

        html_path = os.path.join(output_dir, "parking_lots_map.html")
        visualize_on_map(combined_df, html_path)

        csv_path = os.path.join(output_dir, "parking_lots_data.csv")
        combined_df.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")
    else:
        print("No parking lots found in any city")
