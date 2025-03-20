import requests
import json

def fetch_electric_charging_stations(api_key, state, limit):
    url = "https://developer.nrel.gov/api/alt-fuel-stations/v1.json"
    params = {
        "api_key": "jHxaYAKMxxfMw3zd8fKaf6sESgiReJtFcH5C7sej",
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
    return [station for station in stations if station['city'].lower() == city.lower()]

def append_markers_to_html(stations, html_file):
    """
    Appends markers for charging stations to an existing Leaflet.js map.
    """
    marker_script = "\n".join([
        f"L.marker([{station['latitude']}, {station['longitude']}]).addTo(map).bindPopup('{station['station_name']}');"
        for station in stations if 'latitude' in station and 'longitude' in station
    ])

    with open(html_file, "r+", encoding="utf-8") as file:
        content = file.read()
        
        # Find the place to insert markers (before </script>)
        insert_position = content.rfind("</script>")
        
        if insert_position != -1:
            new_content = content[:insert_position] + marker_script + "\n" + content[insert_position:]
            file.seek(0)
            file.write(new_content)
            file.truncate()
        else:
            print("Could not find </script> tag. Ensure Leaflet map script exists.")

def main():
    api_key = "jHxaYAKMxxfMw3zd8fKaf6sESgiReJtFcH5C7sej"
    limit = 200
    cities = {"Phoenix": "AZ", "Atlanta": "GA", "Tampa": "FL"}
    
    all_stations = []
    for city, state in cities.items():
        stations = fetch_electric_charging_stations(api_key, state, limit)
        city_stations = filter_stations_by_city(stations, city)
        all_stations.extend(city_stations)

    if all_stations:
        append_markers_to_html(all_stations, "parking_lots_map.html")
    else:
        print("No charging stations found.")



if __name__ == "__main__":
    main()

