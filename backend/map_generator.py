import os
import requests
import pandas as pd
import folium
import time
import numpy as np
from sklearn.cluster import KMeans

def extract_parking_lots_by_bbox(city_name, state, bbox):
    """
    Extract parking lot data for a specified city using a bounding box.
    """
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
        if 'elements' in data and len(data['elements']) > 0:
            print(f"Found {len(data['elements'])} parking facilities in {place_name}")
            parking_lots = []
            for element in data['elements']:
                if element['type'] == 'node':
                    lat = element['lat']
                    lon = element['lon']
                elif 'center' in element:
                    lat = element['center']['lat']
                    lon = element['center']['lon']
                else:
                    continue
                tags = element.get('tags', {})
                lot = {
                    'id': element['id'],
                    'type': element['type'],
                    'lat': lat,
                    'lon': lon,
                    'name': tags.get('name', f"Parking {element['id']}"),
                    'access': tags.get('access', 'unknown'),
                    'capacity': tags.get('capacity', 'unknown'),
                    'fee': tags.get('fee', 'unknown'),
                    'city': city_name,
                    'state': state
                }
                parking_lots.append(lot)
            return pd.DataFrame(parking_lots)
        else:
            print(f"No parking facilities found for {place_name}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error extracting parking lots for {place_name}: {e}")
        return pd.DataFrame()

def visualize_on_map(parking_lots_df, output_html):
    """
    Create an interactive map with parking lot markers.
    Markers are initially red. An external JS file (marker_click.js) will change a marker's icon to green on click.
    """
    # Compute the map center
    if not parking_lots_df.empty:
        center_lat = parking_lots_df['lat'].mean()
        center_lon = parking_lots_df['lon'].mean()
    else:
        center_lat, center_lon = 39.8283, -98.5795

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Group by city/state and add markers
    for (city, state), group in parking_lots_df.groupby(['city', 'state']):
        count = len(group)
        # Use different division factors per city (adjust as needed)
        if city == "Phoenix":
            division_factor = 160
        elif city == "Tampa":
            division_factor = 40 
        else:
            division_factor = 80

        num_markers = max(1, (count // division_factor))
        print(f"For {city}, {state}: {count} parking lots, showing {num_markers} markers.")

        # Use K-Means clustering if needed
        if count > num_markers:
            group_reset = group.reset_index(drop=True)
            coords = group_reset[['lat', 'lon']].values
            kmeans = KMeans(n_clusters=num_markers, random_state=42, n_init=10)
            labels = kmeans.fit_predict(coords)
            centers = kmeans.cluster_centers_
            selected_rows = []
            for cluster_id in range(num_markers):
                cluster_points = group_reset[labels == cluster_id]
                cluster_coords = cluster_points[['lat', 'lon']].values
                sq_dists = np.sum((cluster_coords - centers[cluster_id])**2, axis=1)
                best_idx = cluster_points.index[np.argmin(sq_dists)]
                selected_rows.append(best_idx)
            selected_df = group_reset.loc[selected_rows]
        else:
            selected_df = group

        city_layer = folium.FeatureGroup(name=f"{city}, {state}")
        for idx, row in selected_df.iterrows():
            popup_text = f"<b>{row.get('name', 'Parking')}</b><br>City: {city}, {state}"
            if 'capacity' in row and pd.notna(row['capacity']) and row['capacity'] != 'unknown':
                popup_text += f"<br>Capacity: {row['capacity']}"
            if 'access' in row and pd.notna(row['access']) and row['access'] != 'unknown':
                popup_text += f"<br>Access: {row['access']}"
            if 'fee' in row and pd.notna(row['fee']) and row['fee'] != 'unknown':
                popup_text += f"<br>Fee: {row['fee']}"
            # Create red markers initially
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(city_layer)
        city_layer.add_to(m)

    folium.LayerControl().add_to(m)

    # Expose the map object using its variable name from Folium:
    map_var = m.get_name()  # e.g. "map_abcd1234"
    # This will set myMap to the Folium map object stored in window['map_abcd1234']
    expose_script = f"<script>var myMap = window['{map_var}']; console.log('myMap loaded:', myMap);</script>"
    m.get_root().html.add_child(folium.Element(expose_script))
    
    # Link to the external JS file (marker_click.js should be in the same directory as the HTML file)
    m.get_root().html.add_child(folium.Element('<script src="marker_click.js"></script>'))

    m.save(output_html)
    print(f"Map saved to {output_html}")
    return m

# Main execution
if __name__ == "__main__":
    # Set output directory to the "tesla" folder on your Desktop
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "tesla")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cities = [
        ("Phoenix", "Arizona"),
        ("Tampa", "Florida"),
        ("Atlanta", "Georgia")
    ]
    city_bboxes = {
        "Phoenix": (33.2000, -112.3000, 33.8000, -111.9000),
        "Tampa": (27.9000, -82.5500, 28.1500, -82.3500),
        "Atlanta": (33.6500, -84.5500, 33.9000, -84.2500)
    }
    all_parking_lots = []
    for city, state in cities:
        if city in city_bboxes:
            print(f"Processing {city}...")
            # Pause between requests to avoid rate limiting
            if all_parking_lots:
                time.sleep(5)
            bbox = city_bboxes[city]
            parking_lots = extract_parking_lots_by_bbox(city, state, bbox)
            if not parking_lots.empty:
                all_parking_lots.append(parking_lots)
        else:
            print(f"No bounding box defined for {city}, skipping")

    if all_parking_lots:
        combined_df = pd.concat(all_parking_lots, ignore_index=True)
        print(f"Total parking lots found: {len(combined_df)}")
        html_path = os.path.join(output_dir, "parking_lots_map.html")
        visualize_on_map(combined_df, html_path)
        # Save CSV file in the same directory
        csv_path = os.path.join(output_dir, "parking_lots_data.csv")
        combined_df.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")
    else:
        print("No parking lots found in any city")
