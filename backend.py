import os
from datetime import datetime, timezone

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
    if value is None:
        return "Unavailable"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "Unavailable"

    if value <= 50:
        return "Good"
    elif value <= 100:
        return "Moderate"
    elif value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif value <= 200:
        return "Unhealthy"
    elif value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def fetch_city(city):
    if city not in CITIES:
        raise ValueError(f"Unknown city: {city}")

    latitude, longitude = CITIES[city]

    air_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "pm2_5,pm10,us_aqi,european_aqi",
        "hourly": "pm2_5,pm10,us_aqi,european_aqi",
        "forecast_days": 2,
        "timezone": "auto",
    }

    try:
        response = requests.get(
            AQ_URL,
            params=air_params,
            timeout=30,
        )
        response.raise_for_status()
        air_data = response.json()

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Air-quality API error: {exc}"
        ) from exc

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "timezone": "auto",
    }

    try:
        response = requests.get(
            WEATHER_URL,
            params=weather_params,
            timeout=30,
        )
        response.raise_for_status()
        weather_data = response.json()

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Weather API error: {exc}"
        ) from exc

    current = air_data.get("current", {})
    weather_current = weather_data.get("current", {})
    hourly = air_data.get("hourly", {})

    frame = pd.DataFrame(
        {
            "time": hourly.get("time", []),
            "PM2.5 (µg/m³)": hourly.get("pm2_5", []),
            "PM10 (µg/m³)": hourly.get("pm10", []),
            "US AQI": hourly.get("us_aqi", []),
            "European AQI": hourly.get("european_aqi", []),
        }
    )

    return {
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
        "pm25": current.get("pm2_5"),
        "pm10": current.get("pm10"),
        "us_aqi": current.get("us_aqi"),
        "eu_aqi": current.get("european_aqi"),
        "temperature": weather_current.get("temperature_2m"),
        "humidity": weather_current.get("relative_humidity_2m"),
        "wind": weather_current.get("wind_speed_10m"),
        "timezone": air_data.get("timezone", ""),
        "hourly": frame,
        "retrieved_at": datetime.now(
            timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC"),
    }


def compare_cities(cities):
    rows = []
    errors = []

    for city in cities:
        try:
            data = fetch_city(city)

            rows.append(
                {
                    "City": city,
                    "US AQI": data["us_aqi"],
                    "PM2.5 (µg/m³)": data["pm25"],
                    "PM10 (µg/m³)": data["pm10"],
                    "Temperature (°C)": data["temperature"],
                    "Humidity (%)": data["humidity"],
                    "Wind (km/h)": data["wind"],
                    "AQI Category": aqi_label(
                        data["us_aqi"]
                    ),
                }
            )

        except Exception as exc:
            errors.append(
                f"{city}: {type(exc).__name__}: {exc}"
            )

    return pd.DataFrame(rows), errors


def _prepare_gemini_data(city_data):
    if not city_data:
        return "No dashboard data available."

    if isinstance(city_data, dict):
        clean = {}

        for key, value in city_data.items():
            if key == "hourly":
                continue

            clean[key] = value

        return str(clean)

    return str(city_data)


def gemini_answer(question, city_data):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "❌ Gemini API key is missing.\n\n"
            "Please add GEMINI_API_KEY to "
            "Streamlit Secrets."
        )

    question = str(question).strip()

    if not question:
        return "Please enter a question."

    dashboard = _prepare_gemini_data(city_data)

    prompt = f"""
You are PakEco AI, an environmental assistant
for Pakistan.

Explain environmental and air-pollution topics
in simple language.

Do not invent pollution measurements.

Dashboard data:
{dashboard}

User question:
{question}

Give a concise and useful answer.
"""

    try:
        from google import genai
    except ImportError:
        return (
            "❌ google-genai is not installed.\n\n"
            "Check requirements.txt."
        )

    try:
        client = genai.Client(api_key=api_key)

    except Exception as exc:
        return (
            "❌ Gemini client error:\n\n"
            f"{type(exc).__name__}: {exc}"
        )

    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite",
    ]

    errors = []

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            text = getattr(response, "text", None)

            if text:
                return text.strip()

            errors.append(
                f"{model_name}: empty response"
            )

        except Exception as exc:
            errors.append(
                f"{model_name}: "
                f"{type(exc).__name__}: {exc}"
            )

    return (
        "⚠️ Gemini is temporarily unavailable.\n\n"
        "Your PakEco pollution dashboard is still working.\n\n"
        "Gemini errors detected:\n\n"
        + "\n".join(errors)
    )


def backend_status():
    return {
        "pakeco_backend": "OK",
        "gemini_configured": bool(
            os.getenv("GEMINI_API_KEY")
        ),
        "cities_available": len(CITIES),
        "open_meteo_air_quality": AQ_URL,
        "open_meteo_weather": WEATHER_URL,
    }
