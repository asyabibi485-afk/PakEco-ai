"""
PakEco AI backend
- Open-Meteo air-quality + weather data
- Gemini environmental assistant
This module contains application logic used by both Gradio and Streamlit.
"""
import os
from datetime import datetime

import pandas as pd
import requests

CITIES = {
    "Karachi": (24.8607, 67.0011),
    "Lahore": (31.5204, 74.3587),
    "Islamabad": (33.6844, 73.0479),
    "Peshawar": (34.0151, 71.5249),
    "Quetta": (30.1798, 66.9750),
    "Multan": (30.1575, 71.5249),
    "Faisalabad": (31.4504, 73.1350),
    "Rawalpindi": (33.5651, 73.0169),
    "Hyderabad": (25.3960, 68.3578),
    "Gujranwala": (32.1877, 74.1945),
}

AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def aqi_label(value):
    if value is None or pd.isna(value):
        return "Unavailable"
    value = float(value)
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 150:
        return "Unhealthy for sensitive groups"
    if value <= 200:
        return "Unhealthy"
    if value <= 300:
        return "Very unhealthy"
    return "Hazardous"

def fetch_city(city: str):
    if city not in CITIES:
        raise ValueError(f"Unknown city: {city}")

    lat, lon = CITIES[city]

    aq_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "pm2_5,pm10,us_aqi,european_aqi",
        "hourly": "pm2_5,pm10,us_aqi,european_aqi",
        "forecast_days": 2,
        "timezone": "auto",
    }
    aq = requests.get(AQ_URL, params=aq_params, timeout=20)
    aq.raise_for_status()
    aq_data = aq.json()

    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    }
    weather = requests.get(WEATHER_URL, params=weather_params, timeout=20)
    weather.raise_for_status()
    weather_data = weather.json()

    current = aq_data.get("current", {})
    wc = weather_data.get("current", {})
    hourly = aq_data.get("hourly", {})

    frame = pd.DataFrame({
        "time": hourly.get("time", []),
        "PM2.5 (µg/m³)": hourly.get("pm2_5", []),
        "PM10 (µg/m³)": hourly.get("pm10", []),
        "US AQI": hourly.get("us_aqi", []),
        "European AQI": hourly.get("european_aqi", []),
    })

    return {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "pm25": current.get("pm2_5"),
        "pm10": current.get("pm10"),
        "us_aqi": current.get("us_aqi"),
        "eu_aqi": current.get("european_aqi"),
        "temperature": wc.get("temperature_2m"),
        "humidity": wc.get("relative_humidity_2m"),
        "wind": wc.get("wind_speed_10m"),
        "timezone": aq_data.get("timezone", ""),
        "hourly": frame,
        "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }

def compare_cities(cities):
    rows = []
    errors = []
    for city in cities:
        try:
            d = fetch_city(city)
            rows.append({
                "City": city,
                "US AQI": d["us_aqi"],
                "PM2.5 (µg/m³)": d["pm25"],
                "PM10 (µg/m³)": d["pm10"],
                "Temperature (°C)": d["temperature"],
                "Humidity (%)": d["humidity"],
                "Wind (km/h)": d["wind"],
                "AQI Category": aqi_label(d["us_aqi"]),
            })
        except Exception as exc:
            errors.append(f"{city}: {type(exc).__name__}")
    return pd.DataFrame(rows), errors

def gemini_answer(question, city_data):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini is not configured. Add GEMINI_API_KEY to your environment or hosting secrets."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"""
You are PakEco AI, an environmental information assistant for Pakistan.
Use the supplied dashboard values as the only factual measurements.
Do not invent pollution measurements. Explain that Open-Meteo air-quality
values are model-based and not necessarily ground-station observations.
Do not diagnose medical conditions. For health concerns, recommend official
public-health guidance and a qualified professional.

Dashboard:
{city_data}

Question:
{question}

Answer briefly and practically for a general Pakistani audience.
"""
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )
        return getattr(interaction, "output_text", str(interaction))
    except Exception as exc:
        return (
            "Gemini could not answer right now. Your pollution dashboard remains available. "
            f"Technical error: {type(exc).__name__}"
        )
