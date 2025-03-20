import requests
import os
import csv

def fetch_electric_charging_stations(api_key, state, limit):
    url = "https://developer.nrel.gov/api/alt-fuel-stations/v1.json"
    params = {
        "api_key": api_key,
        "fuel_type": "ELEC",
        "state": state,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    
    data = response.json()
    return data.get("fuel_stations", [])
    

def filter_stations_by_city(stations, city):
    return [station for station in stations if station.get('city', '').lower() == city.lower()]

def print_station_details(station):
    """Prints charging station details in the specified format."""
    print("=" * 50)
    print(f"Station Name: {station.get('station_name', 'Unknown')}")
    print(f"City: {station.get('city', 'Unknown')}")
    print(f"State: {station.get('state', 'Unknown')}")
    print(f"Zip: {station.get('zip', 'Unknown')}")
    print(f"Latitude: {station.get('latitude', 'Unknown')}")
    print(f"Longitude: {station.get('longitude', 'Unknown')}")
    print(f"EV Connector Types: {station.get('ev_connector_types', 'Unknown')}")
    print(f"EV DC Fast Count: {station.get('ev_dc_fast_count', 'None')}")
    print(f"EV Level 2 Count: {station.get('ev_level2_evse_num', 'None')}")
    print(f"EV Network: {station.get('ev_network', 'Non-Networked')}")
    print("=" * 50)

def save_to_csv(stations, filename="charging_stations.csv"):
    """Saves station data to a CSV file for mapping."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Station Name", "City", "State", "Zip", "Latitude", "Longitude", 
            "EV Connector Types", "EV DC Fast Count", "EV Level 2 Count", "EV Network"
        ])
        for station in stations:
            writer.writerow([
                station.get('station_name', 'Unknown'),
                station.get('city', 'Unknown'),
                station.get('state', 'Unknown'),
                station.get('zip', 'Unknown'),
                station.get('latitude', 'Unknown'),
                station.get('longitude', 'Unknown'),
                ', '.join(station.get('ev_connector_types', ['Unknown'])),
                station.get('ev_dc_fast_count', 'None'),
                station.get('ev_level2_evse_num', 'None'),
                station.get('ev_network', 'Non-Networked')
            ])
    print(f"\n✅ Data saved to {filename}")

def main():
    api_key = os.getenv("NREL_API_KEY", "jHxaYAKMxxfMw3zd8fKaf6sESgiReJtFcH5C7sej")
    limit = 1000
    cities = {"Phoenix": "AZ", "Atlanta": "GA", "Tampa": "FL"}
    
    all_stations = []
    
    for city, state in cities.items():
        stations = fetch_electric_charging_stations(api_key, state, limit)
        city_stations = filter_stations_by_city(stations, city)
        
        if city_stations:
            print(f"\nCharging Stations in {city}, {state}:")
            for station in city_stations:
                print_station_details(station)
            all_stations.extend(city_stations)
        else:
            print(f"\nNo charging stations found in {city}, {state}.")
    
    if all_stations:
        save_to_csv(all_stations)

import csv

def generate_html_map(csv_filename, output_html="charging_stations_map.html"):
    """Generates an HTML file to visualize charging stations on a map."""
    
    # Start of the HTML file with Leaflet.js setup
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>EV Charging Stations Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    
    <style>
        #map { height: 600px; width: 100%; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">EV Charging Stations Map</h2>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([33.4484, -112.0740], 5);  // Centered in the US
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
        }).addTo(map);

        // Custom orange marker icon
        var orangeIcon = L.icon({
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x-orange.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34]
        });
    """

    # Read the CSV file and add markers
    with open(csv_filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Latitude"] and row["Longitude"]:
                latitude = row["Latitude"]
                longitude = row["Longitude"]
                station_name = row["Station Name"]
                city = row["City"]
                state = row["State"]
                zip_code = row["Zip"]
                ev_connectors = row["EV Connector Types"]
                ev_network = row["EV Network"]

                # Leaflet.js marker script with orange marker
                html_content += f"""
        L.marker([{latitude}, {longitude}], {{icon: orangeIcon}}).addTo(map)
        .bindPopup("<b>{station_name}</b><br>City: {city}, {state}<br>Zip: {zip_code}<br>EV Connector: {ev_connectors}<br>Network: {ev_network}");
    """

    # Close the HTML script
    html_content += """
    </script>
</body>
</html>
"""

    # Save the HTML file
    with open(output_html, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"\n✅ Map saved as {output_html}")


# Run the function to generate the HTML file
generate_html_map("charging_stations.csv")



if __name__ == "__main__":
    main()
