import folium
import pandas as pd

def visualize_on_map(parking_lots_df, output_html):
    """
    Create an interactive map with parking lot markers.
    Clicking a marker fetches real estate ownership details.
    """
    if not parking_lots_df.empty:
        center_lat = parking_lots_df['lat'].mean()
        center_lon = parking_lots_df['lon'].mean()
    else:
        center_lat, center_lon = 39.8283, -98.5795  # Default to USA center

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    for idx, row in parking_lots_df.iterrows():
        popup_text = f"""
        <b>{row.get('name', 'Parking')}</b><br>
        City: {row['city']}, {row['state']}<br>
        <button onclick="fetchOwnership({row['lat']}, {row['lon']})">Who Owns This?</button>
        <div id="ownership-info-{row['lat']}-{row['lon']}"></div>
        """

        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # JavaScript to fetch ownership details
    ownership_script = """
    <script>
    async function fetchOwnership(lat, lon) {
        const url = `http://127.0.0.1:5000/get-ownership?lat=${lat}&lon=${lon}`;
        const response = await fetch(url);
        const data = await response.json();
        document.getElementById(`ownership-info-${lat}-${lon}`).innerHTML = 
            `<b>Owner:</b> ${data.owner || 'Unknown'}<br>
             <b>Contact:</b> ${data.contact || 'N/A'}`;
    }
    </script>
    """
    m.get_root().html.add_child(folium.Element(ownership_script))

    m.save(output_html)
    print(f"Map saved to {output_html}")
    return m

# Example usage:
if __name__ == "__main__":
    # Example DataFrame with parking lot locations
    data = {
        "name": ["Parking Lot A", "Parking Lot B"],
        "lat": [33.4484, 27.9506],
        "lon": [-112.0740, -82.4572],
        "city": ["Phoenix", "Tampa"],
        "state": ["Arizona", "Florida"]
    }
    df = pd.DataFrame(data)
    visualize_on_map(df, "parking_lots_map.html")
