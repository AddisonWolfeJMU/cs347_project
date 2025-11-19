import requests

def geocode_city(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
    resp = requests.get(url).json()

    if "results" not in resp or len(resp["results"]) == 0:
        return None

    result = resp["results"][0]
    return {
        "lat": result["latitude"],
        "lon": result["longitude"],
    }

def main():
    city = "San Francisco"
    location = geocode_city(city)
    if location:
        print(f"City: {location['city']}, Country: {location['country']}, Latitude: {location['lat']}, Longitude: {location['lon']}")
    else:
        print("City not found.")

if __name__ == "__main__":
    main()