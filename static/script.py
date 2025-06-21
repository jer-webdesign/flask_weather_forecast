from js import document, fetch, setTimeout
from pyodide.ffi import create_proxy
import asyncio
from datetime import datetime

# --- DOM Elements ---
loader = document.getElementById("loader")
loader_overlay = document.getElementById("loader-overlay")
country_select = document.getElementById("country-select")
city_select = document.getElementById("city-select")
forecast_grid = document.getElementById("forecast-grid")
current_content = document.getElementById("current-content")
data_source_select = document.getElementById("data-source-select")
temp_unit_button = document.getElementById("temperature-unit-button")
dark_mode_button = document.getElementById("dark-mode-button")

# --- State ---
class AppState:
    unit = "celsius"
    dark_mode = False
    loading_count = 0

state = AppState()

# --- Loader Controls ---
def show_loader():
    state.loading_count += 1
    loader.classList.remove("hidden")
    loader_overlay.classList.add("active")

def hide_loader():
    state.loading_count = max(state.loading_count - 1, 0)
    if state.loading_count == 0:
        loader.classList.add("hidden")
        loader_overlay.classList.remove("active")

# --- UI Updates ---
def update_temp_unit_button():
    temp_unit_button.textContent = "°F" if state.unit == "celsius" else "°C"

def toggle_temp_unit(event=None):
    state.unit = "fahrenheit" if state.unit == "celsius" else "celsius"
    update_temp_unit_button()
    asyncio.ensure_future(fetch_weather())

def toggle_dark_mode(event=None):
    state.dark_mode = not state.dark_mode
    document.body.classList.toggle("dark", state.dark_mode)
    dark_mode_button.textContent = "☀️" if state.dark_mode else "🌙"

def clear_children(element):
    while element.firstChild:
        element.removeChild(element.firstChild)

def get_temp_unit_symbol():
    return "°C" if state.unit == "celsius" else "°F"

# --- Render Functions ---
def render_current_weather(current):
    date_obj = datetime.fromisoformat(current["date"] + "T00:00:00")
    current_content.innerHTML = f"""
        <section class="weather-icon-condition">
            <h3>{date_obj.strftime('%A, %B %d, %Y')}</h3>
            <p>{current['weather_icon']}<br><strong>{current['weather_text']}</strong></p>
        </section>
        <section id="current-temperature">
            <p><strong>{current['temperature']}°{state.unit[0].upper()}</strong></p>
        </section>
        <section class="current-wind-humidity-feels-like">
            <p><i class="fa-solid fa-wind"></i> Wind: {current['windspeed']} km/h</p>
            <p><i class="fa-solid fa-tint"></i> Humidity: {current['humidity']}%</p>
            <p><i class="fa-solid fa-temperature-high"></i> Feels Like: {current['feels_like']}{get_temp_unit_symbol()}</p>
        </section>
    """

def render_forecast(forecast):
    clear_children(forecast_grid)
    for day in forecast:
        date_obj = datetime.fromisoformat(day["date"] + "T00:00:00")
        avg_temp = round((day["max"] + day["min"]) / 2)
        rain_info = f"<p><i class='fa-solid fa-cloud-showers-heavy'></i> Rain: {day['rain']} mm</p>" if day["rain"] > 0 else ""

        card = document.createElement("div")
        card.className = "weather-content"
        card.innerHTML = f"""
            <section class="weather-forecast">
                <strong>{date_obj.strftime('%a, %B %d')}</strong>
                <div class="avg-icon-row">{day['weather_icon']}<p>{avg_temp}°{state.unit[0].upper()}</p></div>
                <p><strong>{day['weather_text']}</strong></p>
                <p>H: {day['max']}°{state.unit[0].upper()}</p>
                <p>L: {day['min']}°{state.unit[0].upper()}</p>
                <p><i class="fa-solid fa-wind"></i> Wind: {day['wind_speed']} km/h</p>
                <p><i class="fa-solid fa-wind"></i> Gust: {day['wind_gust']} km/h</p>
                <p><i class="fa-solid fa-tint"></i> Humidity: {day['humidity']}%</p>
                <p><i class="fa-solid fa-cloud-rain"></i> P.O.P: {day['precipitation']}%</p>
                {rain_info}
            </section>
        """
        forecast_grid.appendChild(card)

# --- Data Fetching Functions ---
async def fetch_countries(event=None):
    source = data_source_select.value
    res = await fetch(f"/locations?source={source}")
    data = (await res.json()).to_py()

    country_select.innerHTML = ""
    for country in data.get("countries", []):
        opt = document.createElement("option")
        opt.value = country
        opt.textContent = country
        country_select.appendChild(opt)

    if data.get("countries"):
        country_select.value = data["countries"][0]
        await fetch_cities()
    hide_loader()

async def fetch_cities(event=None):
    show_loader()
    source = data_source_select.value
    country = country_select.value
    if not country:
        hide_loader()
        return

    res = await fetch(f"/cities?source={source}&country={country}")
    data = (await res.json()).to_py()

    city_select.innerHTML = ""
    for city in data.get("cities", []):
        opt = document.createElement("option")
        opt.value = city
        opt.textContent = city
        city_select.appendChild(opt)

    if data.get("cities"):
        city_select.value = data["cities"][0]
        await fetch_weather()
    hide_loader()

async def fetch_weather(event=None):
    show_loader()
    source = data_source_select.value
    city = city_select.value
    if not city:
        hide_loader()
        return

    url = f"/weather?source={source}&city={city}&unit={state.unit}"
    res = await fetch(url)
    data = (await res.json()).to_py()

    if "error" in data:
        current_content.textContent = data["error"]
        forecast_grid.innerHTML = ""
        hide_loader()
        return

    render_current_weather(data["current"])
    render_forecast(data["forecast"])
    hide_loader()

# --- Event Binding ---
data_source_select.addEventListener("change", create_proxy(fetch_countries))
country_select.addEventListener("change", create_proxy(fetch_cities))
city_select.addEventListener("change", create_proxy(fetch_weather))
temp_unit_button.addEventListener("click", create_proxy(toggle_temp_unit))
dark_mode_button.addEventListener("click", create_proxy(toggle_dark_mode))

# --- Initialization ---

def init_app():
    show_loader()
    update_temp_unit_button()
    asyncio.ensure_future(fetch_countries())

setTimeout(create_proxy(init_app), 100)
