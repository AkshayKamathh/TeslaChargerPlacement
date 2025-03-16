import requests

def fetch_electric_charging_stations(api_key, state, limit):
    """
    Fetches electric vehicle charging stations from the NREL API.

    Parameters:
    - api_key: Your NREL API key.
    - state: Two-character state code (e.g., AZ for Arizona).
    - limit: Maximum number of results to return (up to 200).

    Returns:
    - A list of dictionaries containing station information.
    """
    url = "https://developer.nrel.gov/api/alt-fuel-stations/v1.json"
    params = {
        "api_key": api_key,
        "fuel_type": "ELEC",
        "state": state,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    
    data = response.json()
    stations = data.get("fuel_stations", [])
    
    return stations

def filter_stations_by_city(stations, city):
    """
    Filters stations by city name.

    Parameters:
    - stations: List of station dictionaries.
    - city: City name to filter by.

    Returns:
    - List of stations in the specified city.
    """
    return [station for station in stations if station['city'].lower() == city.lower()]

def display_station_info(stations, city):
    """
    Prints detailed information about each charging station in a city, including coordinates.

    Parameters:
    - stations: List of station dictionaries.
    - city: City name for context.
    """
    print(f"Electric Vehicle Charging Stations in {city}:")
    for station in stations:
        print(f"Station Name: {station['station_name']}")
        print(f"City: {station['city']}")
        print(f"State: {station['state']}")
        print(f"Zip: {station['zip']}")
        print(f"Latitude: {station['latitude']}")
        print(f"Longitude: {station['longitude']}")
        print(f"EV Connector Types: {station['ev_connector_types']}")
        print(f"EV DC Fast Count: {station.get('ev_dc_fast_num', 0)}")
        print(f"EV Level 2 Count: {station.get('ev_level2_evse_num', 0)}")
        print(f"EV Network: {station.get('ev_network', 'Non-Networked')}")
        print("-" * 50)

def main():
    api_key = "jHxaYAKMxxfMw3zd8fKaf6sESgiReJtFcH5C7sej"
    limit = 200
    
    # Cities and their corresponding states
    cities = {
        "Phoenix": "AZ",
        "Atlanta": "GA",
        "Tampa": "FL"
    }
    
    for city, state in cities.items():
        stations = fetch_electric_charging_stations(api_key, state, limit)
        city_stations = filter_stations_by_city(stations, city)
        
        if city_stations:
            display_station_info(city_stations, city)
        else:
            print(f"No electric vehicle charging stations found in {city}.")

if __name__ == "__main__":
    main()

# import requests

# def fetch_electric_charging_stations(api_key, state, limit):
#     """
#     Fetches electric vehicle charging stations from the NREL API.

#     Parameters:
#     - api_key: Your NREL API key.
#     - state: Two-character state code (e.g., AZ for Arizona).
#     - limit: Maximum number of results to return (up to 200).

#     Returns:
#     - A list of dictionaries containing station information.
#     """
#     url = "https://developer.nrel.gov/api/alt-fuel-stations/v1.json"
#     params = {
#         "api_key": api_key,
#         "fuel_type": "ELEC",
#         "state": state,
#         "limit": limit
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return []
    
#     data = response.json()
#     stations = data.get("fuel_stations", [])
    
#     return stations

# def filter_stations_by_city(stations, city):
#     """
#     Filters stations by city name.

#     Parameters:
#     - stations: List of station dictionaries.
#     - city: City name to filter by.

#     Returns:
#     - List of stations in the specified city.
#     """
#     return [station for station in stations if station['city'].lower() == city.lower()]

# def display_station_info(stations, city):
#     """
#     Prints detailed information about each charging station in a city.

#     Parameters:
#     - stations: List of station dictionaries.
#     - city: City name for context.
#     """
#     print(f"Electric Vehicle Charging Stations in {city}:")
#     for station in stations:
#         print(f"Station Name: {station['station_name']}")
#         print(f"City: {station['city']}")
#         print(f"State: {station['state']}")
#         print(f"Zip: {station['zip']}")
#         print(f"EV Connector Types: {station['ev_connector_types']}")
#         print(f"EV DC Fast Count: {station.get('ev_dc_fast_num', 0)}")
#         print(f"EV Level 2 Count: {station.get('ev_level2_evse_num', 0)}")
#         print(f"EV Network: {station.get('ev_network', 'Non-Networked')}")
#         print("-" * 50)

# def main():
#     api_key = "jHxaYAKMxxfMw3zd8fKaf6sESgiReJtFcH5C7sej"
#     limit = 200
    
#     # Cities and their corresponding states
#     cities = {
#         "Phoenix": "AZ",
#         "Atlanta": "GA",
#         "Tampa": "FL"
#     }
    
#     for city, state in cities.items():
#         stations = fetch_electric_charging_stations(api_key, state, limit)
#         city_stations = filter_stations_by_city(stations, city)
        
#         if city_stations:
#             display_station_info(city_stations, city)
#         else:
#             print(f"No electric vehicle charging stations found in {city}.")

# if __name__ == "__main__":
#     main()
