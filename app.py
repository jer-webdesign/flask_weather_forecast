import os
import random
import datetime
import requests
import math
from flask import Flask, jsonify, render_template, request
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# --- Retry Session Setup ---
def get_retry_session():
    """
    Create a requests session with retry logic to handle API failures.
    This helps avoid crashing if an API is temporarily unavailable.
    """
    retry_strategy = Retry(
        total=3,  # number of retries
        status_forcelist=[429, 500, 502, 503, 504],  # retry on these HTTP codes
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1  # wait time between retries: 1s, 2s, 4s...
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

session = get_retry_session()

# --- Constants and Mock Data ---
MOCK_LOCATION = {
    "country": "Canada",
    "cities": ["Calgary", "Edmonton", "Toronto", "Vancouver"],
    "coords": {
        "Calgary": {"lat": 51.0447, "lon": -114.0719},
        "Edmonton": {"lat": 53.5461, "lon": -113.4938},
        "Toronto": {"lat": 43.65107, "lon": -79.347015},
        "Vancouver": {"lat": 49.2827, "lon": -123.1207},
    },
    "mockData": {
        "Calgary": {"temperature": 18, "windspeed": 12},
        "Edmonton": {"temperature": 10, "windspeed": 15},
        "Toronto": {"temperature": 22, "windspeed": 9},
        "Vancouver": {"temperature": 16, "windspeed": 11},
    },
}

# Weather code mapping to descriptive text and icons
WEATHER_CODE_MAP = {
    0: ('Sunny', '<i class="fas fa-sun" style="color: #f9d71c;"></i>'),
    1: ('Partly Cloudy', '<i class="fas fa-cloud-sun" style="color: #fbbf24;"></i>'),
    2: ('Partly Cloudy', '<i class="fas fa-cloud-sun" style="color: #fbbf24;"></i>'),
    3: ('Cloudy', '<i class="fas fa-cloud" style="color:rgb(172, 195, 220);"></i>'),
    61: ('Rainy', '<i class="fas fa-cloud-showers-heavy" style="color:rgb(13, 100, 240);"></i>'),
    71: ('Snowy', '<i class="fas fa-snowflake" style="color: #bae6fd;"></i>'),
    95: ('Thunderstorm', '<i class="fas fa-bolt" style="color: #facc15;"></i>'),
}

# --- Utility Functions ---
def c_to_f(celsius):
    # Convert Celsius to Fahrenheit
    return round(celsius * 9 / 5 + 32, 1)

def calculate_feels_like(temp_c, wind_kmh, humidity):
    # Simple feels-like temperature estimation formula
    wind_ms = wind_kmh / 3.6
    e = math.exp(17.27 * temp_c / (237.7 + temp_c))
    feels_like = temp_c + 0.33 * (humidity / 100) * 6.105 * e - 0.7 * wind_ms - 4.0
    return round(feels_like, 1)

def get_weather_condition(code):
    # Get weather description and icon from code
    return WEATHER_CODE_MAP.get(code, WEATHER_CODE_MAP[3])  # fallback to Cloudy

def generate_mock_daily(city):
    # Generate mock daily weather data for 7 days
    base_temp = MOCK_LOCATION["mockData"][city]["temperature"]
    days = 7
    today = datetime.date.today()
    time = [(today + datetime.timedelta(days=i)).isoformat() for i in range(days)]

    def rand_arr(base, low_delta=0, high_delta=5):
        return [base + random.randint(low_delta, high_delta) for _ in range(days)]

    return {
        "time": time,
        "temperature_2m_max": rand_arr(base_temp, 0, 5),
        "temperature_2m_min": rand_arr(base_temp, -5, 0),
        "wind_speed_10m_max": rand_arr(10, 0, 5),
        "wind_gusts_10m_max": rand_arr(20, 0, 10),
        "relative_humidity_2m_mean": rand_arr(50, 0, 10),
        "apparent_temperature_max": rand_arr(base_temp, 0, 3),
        "precipitation_probability_mean": [random.randint(0, 50) for _ in range(days)],
        "precipitation_sum": [random.randint(0, 10) for _ in range(days)],
        "weathercode": [random.choice(list(WEATHER_CODE_MAP.keys())) for _ in range(days)],
    }

# --- Cached API Requests ---
@lru_cache(maxsize=128)
def fetch_countries_from_api():
    # Fetch country list with retries and caching
    url = "https://countriesnow.space/api/v0.1/countries"
    r = session.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()
    return tuple(c['country'] for c in data.get('data', []))

@lru_cache(maxsize=512)
def fetch_cities_from_api(country):
    # Fetch city list by country with retries and caching
    url = "https://countriesnow.space/api/v0.1/countries"
    r = session.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()
    for c in data.get('data', []):
        if c['country'].lower() == country.lower():
            return tuple(c.get("cities", []))
    return tuple()

@lru_cache(maxsize=256)
def fetch_city_coordinates(city):
    # Geocode a city to latitude/longitude
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}
    r = session.get(url, params=params, timeout=5)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    lat, lon = results[0]["latitude"], results[0]["longitude"]
    return (lat, lon)

def fetch_weather_data(lat, lon, unit):
    # Fetch 7-day weather forecast data from Open-Meteo
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "weathercode",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_mean",
            "precipitation_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "relative_humidity_2m_mean",
            "apparent_temperature_max"
        ]),
        "current_weather": "true",
        "temperature_unit": unit,
        "wind_speed_unit": "kmh",
        "timezone": "auto"
    }
    r = session.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=5)
    r.raise_for_status()
    return r.json()

def convert_temperature(value, unit):
    return round(value, 1) if unit == "celsius" else c_to_f(value)

# --- Flask Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/locations")
def get_locations():
    # Get list of countries for dropdown
    source = request.args.get("source", "mock")
    try:
        countries = [MOCK_LOCATION["country"]] if source == "mock" else fetch_countries_from_api()
        return jsonify({"countries": countries})
    except Exception as e:
        return jsonify({"countries": [], "error": str(e)}), 500

@app.route("/cities")
def get_cities():
    # Get cities for the selected country
    source = request.args.get("source", "mock")
    country = request.args.get("country", "").strip()
    try:
        cities = MOCK_LOCATION["cities"] if source == "mock" and country == MOCK_LOCATION["country"] else fetch_cities_from_api(country)
        return jsonify({"cities": cities})
    except Exception as e:
        return jsonify({"cities": [], "error": str(e)}), 500

@app.route("/weather")
def get_weather():
    # Main endpoint to fetch current and 7-day forecast weather
    source = request.args.get("source", "mock")
    city = request.args.get("city", "").strip()
    unit = request.args.get("unit", "celsius").lower()

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    try:
        if source == "mock":
            # Use predefined mock data
            if city not in MOCK_LOCATION["cities"]:
                return jsonify({"error": f"City '{city}' not in mock data"}), 404
            current_temp_c = MOCK_LOCATION["mockData"][city]["temperature"]
            current_wind = MOCK_LOCATION["mockData"][city]["windspeed"]
            current_humidity = random.randint(10, 80)
            daily = generate_mock_daily(city)
        else:
            # Use live API data
            coords = fetch_city_coordinates(city)
            if not coords:
                return jsonify({"error": f"City '{city}' not found in geocoding API"}), 404
            lat, lon = coords
            data = fetch_weather_data(lat, lon, unit)
            current_temp_c = data["current_weather"]["temperature"]
            current_wind = data["current_weather"]["windspeed"]
            daily = data["daily"]
            current_humidity = daily["relative_humidity_2m_mean"][0]

        current_temp = current_temp_c if unit == "celsius" else c_to_f(current_temp_c)
        feels_like = calculate_feels_like(current_temp_c, current_wind, current_humidity)
        weather_code = daily["weathercode"][0]
        weather_text, weather_icon = get_weather_condition(weather_code)

        # Current weather card
        current = {
            "temperature": round(current_temp, 1),
            "windspeed": round(current_wind, 1),
            "humidity": current_humidity,
            "weather_text": weather_text,
            "feels_like": round(feels_like, 1),
            "weather_icon": weather_icon,
            "date": daily["time"][0]
        }

        # Forecast cards
        forecast = []
        for i in range(7):
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]
            if unit != "celsius":
                max_temp = c_to_f(max_temp)
                min_temp = c_to_f(min_temp)
            day_code = daily["weathercode"][i]
            day_text, day_icon = get_weather_condition(day_code)

            forecast.append({
                "date": daily["time"][i],
                "max": round(max_temp, 1),
                "min": round(min_temp, 1),
                "wind_speed": daily["wind_speed_10m_max"][i],
                "wind_gust": daily["wind_gusts_10m_max"][i],
                "humidity": daily["relative_humidity_2m_mean"][i],
                "precipitation": daily["precipitation_probability_mean"][i],
                "rain": daily["precipitation_sum"][i],
                "weather_text": day_text,
                "weather_icon": day_icon,
            })

        return jsonify({"current": current, "forecast": forecast})

    except requests.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {str(http_err)}"}), 500
    except Exception as err:
        return jsonify({"error": f"Unexpected error: {str(err)}"}), 500

# --- App Entry Point ---
if __name__ == "__main__":
    # Run the app on port 5000 (or environment PORT if defined)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
