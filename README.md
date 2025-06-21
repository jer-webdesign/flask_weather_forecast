# Weather Forecast Widget

A responsive, interactive weather forecast widget that displays current weather conditions and a 7-day forecast with support for both mock data and live API integration. This project was refactored from a JavaScript frontend-only app into a Python Flask backend with a PyScript-powered frontend, improving maintainability and scalability.

---

## Features

- **Current Weather Display:** Shows today's weather with detailed information  
- **7-Day Forecast:** Complete weekly weather outlook with daily details  
- **Dual Data Sources:** Switch between mock data (for testing) and live API data  
- **Location Selection:** Choose from countries and cities via dropdown menus  
- **Temperature Units:** Toggle between Celsius (°C) and Fahrenheit (°F)  
- **Dark/Light Mode:** Theme toggle for better accessibility and user preference  
- **Responsive Design:** Optimized for all screen sizes from mobile to desktop  
- **Interactive UI:** Smooth transitions and hover effects  
- **Backend Refactoring:** Python Flask server handles API requests, improving code organization  
- **PyScript Frontend:** Uses PyScript for frontend Python scripting 

---

## Light Mode

Clean, bright interface with a blue sky background.

## Dark Mode

Sleek nighttime theme with constellation background.

---

## Technologies Used

- Python 3 with Flask (backend server)  
- PyScript (Python scripting in frontend)  
- HTML5  
- CSS3: Modern styling with CSS variables, flexbox, and grid  
- Font Awesome: Icon library for weather conditions and UI elements  
- Open-Meteo API: Free weather API service  
- Countries Now API: Country and city data  

---

## File Structure

```
weather_forecast_widget/  # Repository root
├── app.py                # Flask backend application
├── static/
│   ├── script.py         # PyScript frontend logic
│   ├── style.css         # CSS styling and themes
│   ├── images/
│   │   ├── blue-sky.jpg                        # Light mode background
│   │   ├── stars-constellation-universe-twin.jpg # Dark mode background
│   │   └── weather-app.png                      # favicon  
├── templates/
│   └── index.html        # Main HTML template with PyScript integration
├── requirements.txt      # Python dependencies
├── Procfile              # Deployment configuration for Render
└── README.md             # Project documentation
```

## Software Component Roles
| Component          | Purpose                                                         |
| ------------------ | --------------------------------------------------------------- |
| `app.py`           | Flask app — routes for `/`, `/locations`, `/cities`, `/weather` |
| `script.py`        | PyScript file — handles DOM, fetches, rendering in the browser  |
| `style.css`        | Styling — light/dark themes, responsive layout, UI design       |
| `index.html`       | Main UI — combines HTML, Flask variables, and loads PyScript    |
| `images/`          | Favicon and background images                                   |
| `requirements.txt` | List of backend dependencies for deployment (`pip install -r`)  |

---

## Logical Architecture (Visual)

|         User's Browser       |
|------------------------------|
| [HTML + CSS + PyScript]      |
|  - index.html                |
|  - style.css                 |
| - script.py (runs in Pyodide)|

               |
               | fetch()
               ↓

|          Flask App (app.py)  |
|------------------------------|
| /locations,/cities,/weather  |
|  - requests to external APIs |
|  - serves mock/live data     |

               |
               ↓

|    External APIs             |
|------------------------------|
|    Open-Meteo                |
|    CountriesNow API          |


---

## How to Use

### Data Source Selection

- **Mock Data:** Uses pre-configured Canadian cities for testing  
- **Live API:** Fetches real-time weather data from Open-Meteo

### Location Selection

- Select your preferred data source (Mock or Live API)  
- Choose a country from the dropdown  
- Select a city from the populated city list  
- Weather data loads automatically  

### Temperature Units

- Click the temperature unit button (°F/°C) to toggle between Fahrenheit and Celsius  
- All temperature displays update instantly  

### Theme Toggle

- Click the moon (🌙) or sun (☀️) button to switch between dark and light modes  
- Theme preference affects colors and background images  

### Free Hosting Constraints

On Render’s free hosting plan, the app goes to sleep after 15 minutes of inactivity and takes about 10 seconds to wake up when accessed again.

---

## API Integration

- **Open-Meteo Weather API**  
  - Geocoding: https://geocoding-api.open-meteo.com/v1/search (Converts city names to latitude/longitude)  
  - Forecast: https://api.open-meteo.com/v1/forecast (Retrieves current and daily weather data)  

- **Countries Now API**  
  - Endpoint: https://countriesnow.space/api/v0.1/countries (Provides country and city data for location selection)  

---

## Mock Data

For testing and offline use, the widget includes mock data for Canadian cities:

- Calgary  
- Edmonton  
- Toronto  
- Vancouver  

---

## Weather Conditions

The widget displays various weather conditions with appropriate icons:

- ☀️ Sunny  
- ⛅ Partly Cloudy  
- ☁️ Cloudy  
- 🌧️ Rainy  
- ❄️ Snowy  
- ⛈️ Thunderstorm  

---

## Responsive Design

- **Desktop (>768px):** Full horizontal layout  
- **Tablet (320px-768px):** Adjusted layout with stacked elements  
- **Mobile (<320px):** Compact vertical layout optimized for small screens  

---

## Deployment Notes

- The backend Flask app is deployed on [Render](https://render.com) (free tier)  
- The frontend uses PyScript to run Python directly in the browser, including a 10-second auto-refresh loop to keep the service responsive despite free hosting limits  
- Make sure environment variables and ports are configured properly for deployment  

---

## Requirements

Python dependencies listed in `requirements.txt`:

- Flask  
- Requests  

---

## Procfile

Render uses the following `Procfile` to start the Flask server:

```
web: python app.py
```

---

## Attributions

- **PyScript:** PyScript Project. Python scripting in the browser. https://pyscript.net  
- **Flask:** Pallets Projects. Flask Web Framework. https://flask.palletsprojects.com/  
- **Render:** Render Cloud Platform. https://render.com  
- Altmann, G. (2022, June 7). Stars, constellation, universe [Illustration]. Pixabay. https://pixabay.com/illustrations/stars-constellation-universe-twin-7249785/  
- uriel. (2020, August 11). Blue sky with white clouds [Photograph]. Unsplash. https://unsplash.com/photos/blue-sky-with-white-clouds-xtgONQzGgOE  
- Prabowo, A. (n.d.). Weather app icons [Icon set]. Flaticon. https://www.flaticon.com/free-icons/weather-app  
- CountriesNow. (n.d.). Countries API. https://countriesnow.space/api/v0.1/countries  
- Open-Meteo. (n.d.). Weather forecast API. https://api.open-meteo.com/v1/forecast  
- Open-Meteo. (n.d.). Geocoding API. https://geocoding-api.open-meteo.com/v1/search  
