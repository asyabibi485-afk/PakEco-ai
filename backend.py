    """
PakEco AI Backend

- Open-Meteo Air Quality API
- Open-Meteo Weather API
- Gemini Environmental Assistant
- City comparison
- Shared backend logic for Streamlit / Gradio
"""

import os
from datetime import datetime, timezone

import pandas as pd
import requests


# ============================================================
# PAKISTAN CITIES
# ============================================================

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


# ============================================================
# API URLS
# ============================================================

AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ============================================================
# AQI LABEL
# ============================================================

def aqi_label(value):

    if value is None:
        return "Unavailable"

    try:
        if pd.isna(value):
            return "Unavailable"

        value = float(value)

    except (TypeError, ValueError):
        return "Unavailable"

    if value <= 50:
        return "Good"

    if value <= 100:
        return "Moderate"

    if value <= 150:
        return "Unhealthy for Sensitive Groups"

    if value <= 200:
        return "Unhealthy"

    if value <= 300:
        return "Very Unhealthy"

    return "Hazardous"


# ============================================================
# FETCH CITY DATA
# ============================================================

def fetch_city(city: str):

    if city not in CITIES:
        raise ValueError(
            f"Unknown city: {city}"
        )

    latitude, longitude = CITIES[city]

    # --------------------------------------------------------
    # AIR QUALITY
    # --------------------------------------------------------

    aq_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "pm2_5,pm10,us_aqi,european_aqi"
        ),
        "hourly": (
            "pm2_5,pm10,us_aqi,european_aqi"
        ),
        "forecast_days": 2,
        "timezone": "auto",
    }

    try:

        response = requests.get(
            AQ_URL,
            params=aq_params,
            timeout=30,
        )

        response.raise_for_status()

        aq_data = response.json()

    except requests.exceptions.Timeout as exc:

        raise RuntimeError(
            "Open-Meteo air-quality request timed out."
        ) from exc

    except requests.exceptions.RequestException as exc:

        raise RuntimeError(
            f"Open-Meteo air-quality request failed: {exc}"
        ) from exc

    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

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

        weather_response = requests.get(
            WEATHER_URL,
            params=weather_params,
            timeout=30,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

    except requests.exceptions.Timeout as exc:

        raise RuntimeError(
            "Open-Meteo weather request timed out."
        ) from exc

    except requests.exceptions.RequestException as exc:

        raise RuntimeError(
            f"Open-Meteo weather request failed: {exc}"
        ) from exc

    # --------------------------------------------------------
    # CURRENT DATA
    # --------------------------------------------------------

    current = aq_data.get(
        "current",
        {}
    ) or {}

    weather_current = weather_data.get(
        "current",
        {}
    ) or {}

    hourly = aq_data.get(
        "hourly",
        {}
    ) or {}

    # --------------------------------------------------------
    # HOURLY DATAFRAME
    # --------------------------------------------------------

    frame = pd.DataFrame(
        {
            "time": hourly.get(
                "time",
                []
            ),

            "PM2.5 (µg/m³)": hourly.get(
                "pm2_5",
                []
            ),

            "PM10 (µg/m³)": hourly.get(
                "pm10",
                []
            ),

            "US AQI": hourly.get(
                "us_aqi",
                []
            ),

            "European AQI": hourly.get(
                "european_aqi",
                []
            ),
        }
    )

    # --------------------------------------------------------
    # RETURN CITY DATA
    # --------------------------------------------------------

    return {
        "city": city,

        "latitude": latitude,

        "longitude": longitude,

        "pm25": current.get(
            "pm2_5"
        ),

        "pm10": current.get(
            "pm10"
        ),

        "us_aqi": current.get(
            "us_aqi"
        ),

        "eu_aqi": current.get(
            "european_aqi"
        ),

        "temperature": weather_current.get(
            "temperature_2m"
        ),

        "humidity": weather_current.get(
            "relative_humidity_2m"
        ),

        "wind": weather_current.get(
            "wind_speed_10m"
        ),

        "timezone": aq_data.get(
            "timezone",
            ""
        ),

        "hourly": frame,

        "retrieved_at": datetime.now(
            timezone.utc
        ).strftime(
            "%Y-%m-%d %H:%M UTC"
        ),
    }


# ============================================================
# COMPARE CITIES
# ============================================================

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

                    "PM2.5 (µg/m³)": data[
                        "pm25"
                    ],

                    "PM10 (µg/m³)": data[
                        "pm10"
                    ],

                    "Temperature (°C)": data[
                        "temperature"
                    ],

                    "Humidity (%)": data[
                        "humidity"
                    ],

                    "Wind (km/h)": data[
                        "wind"
                    ],

                    "AQI Category": aqi_label(
                        data["us_aqi"]
                    ),
                }
            )

        except Exception as exc:

            errors.append(
                f"{city}: "
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            )

    return (
        pd.DataFrame(rows),
        errors,
    )


# ============================================================
# PREPARE GEMINI DATA
# ============================================================

def _prepare_gemini_data(city_data):

    if city_data is None:

        return (
            "No dashboard data is available."
        )

    if isinstance(
        city_data,
        dict
    ):

        clean_data = {}

        for key, value in city_data.items():

            # Do not send the complete hourly
            # dataframe to Gemini.

            if key == "hourly":
                continue

            if isinstance(
                value,
                (
                    str,
                    int,
                    float,
                    bool,
                ),
            ):

                clean_data[key] = value

            elif value is None:

                clean_data[key] = None

            else:

                clean_data[key] = str(
                    value
                )

        return str(clean_data)

    return str(city_data)


# ============================================================
# GEMINI ENVIRONMENTAL ASSISTANT
# ============================================================

def gemini_answer(
    question,
    city_data
):

    # --------------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------------

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        return (
            "❌ Gemini API key is not configured.\n\n"
            "Please add GEMINI_API_KEY to "
            "Streamlit Secrets.\n\n"
            "The PakEco pollution dashboard "
            "is still working."
        )

    # --------------------------------------------------------
    # CHECK QUESTION
    # --------------------------------------------------------

    if question is None:

        return (
            "Please enter an environmental question."
        )

    question = str(
        question
    ).strip()

    if not question:

        return (
            "Please enter an environmental question."
        )

    # --------------------------------------------------------
    # DASHBOARD DATA
    # --------------------------------------------------------

    dashboard = _prepare_gemini_data(
        city_data
    )

    # --------------------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are PakEco AI, an environmental information
assistant for Pakistan.

Your job is to explain air pollution and
environmental information in a simple,
practical way.

IMPORTANT RULES:

1. Use the supplied dashboard values as the
   only factual pollution measurements.

2. Never invent PM2.5, PM10, AQI, temperature,
   humidity, or wind measurements.

3. Explain that Open-Meteo air-quality values
   are model-based estimates and may differ
   from ground-station observations.

4. Do not diagnose diseases or medical conditions.

5. If the user asks about health effects,
   provide general educational information.

6. If dashboard data is unavailable,
   clearly say so.

7. Give short, practical answers suitable
   for a general Pakistani audience.

8. You may recommend general pollution-reduction
   measures and following local public-health
   guidance.

CURRENT PAK-ECO DASHBOARD:

{dashboard}

USER QUESTION:

{question}

Answer clearly and briefly.
"""

    # --------------------------------------------------------
    # IMPORT GEMINI
    # --------------------------------------------------------

    try:

        from google import genai

    except ImportError:

        return (
            "❌ Gemini library is not installed.\n\n"
            "Add this package to requirements.txt:\n\n"
            "google-genai"
        )

    # --------------------------------------------------------
    # CREATE GEMINI CLIENT
    # --------------------------------------------------------

    try:

        client = genai.Client(
            api_key=api_key
        )

    except Exception as exc:

        return (
            "❌ Gemini client could not be initialized.\n\n"
            f"Technical error: "
            f"{type(exc).__name__}: {str(exc)}"
        )

    # --------------------------------------------------------
    # GEMINI MODEL FALLBACK
    # --------------------------------------------------------

    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite",
    ]

    errors = []

    # --------------------------------------------------------
    # TRY GEMINI MODELS
    # --------------------------------------------------------

    for model_name in models:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            # ------------------------------------------------
            # NORMAL RESPONSE
            # ------------------------------------------------

            text = getattr(
                response,
                "text",
                None
            )

            if text:

                return text.strip()

            # ------------------------------------------------
            # CANDIDATE RESPONSE FALLBACK
            # ------------------------------------------------

            candidates = getattr(
                response,
                "candidates",
                None
            )

            if candidates:

                try:

                    text_parts = []

                    for candidate in candidates:

                        content = getattr(
                            candidate,
                            "content",
                            None
                        )

                        if content is None:
                            continue

                        parts = getattr(
                            content,
                            "parts",
                            []
                        )

                        for part in parts:

                            part_text = getattr(
                                part,
                                "text",
                                None
                            )

                            if part_text:

                                text_parts.append(
                                    part_text
                                )

                    if text_parts:

                        return "\n".join(
                            text_parts
                        ).strip()

                except Exception:
                    pass

            errors.append(
                f"{model_name}: empty response"
            )

        # ----------------------------------------------------
        # GEMINI ERROR
        # ----------------------------------------------------

        except Exception as exc:

            error_text = str(
                exc
            ).lower()

            error_type = type(
                exc
            ).__name__

            # IMPORTANT:
            # Keep the REAL error message so
            # we can diagnose the problem.

            errors.append(
                f"{model_name}: "
                f"{error_type}: "
                f"{str(exc)}"
            )

            # ------------------------------------------------
            # RATE LIMIT / QUOTA
            # ------------------------------------------------

            if any(
                word in error_text
                for word in [
                    "429",
                    "rate",
                    "quota",
                    "resource exhausted",
                    "too many requests",
                ]
            ):

                continue

            # ------------------------------------------------
            # SERVER / TEMPORARY ERROR
            # ------------------------------------------------

            if any(
                word in error_text
                for word in [
                    "503",
                    "unavailable",
                    "overloaded",
                    "500",
                    "internal",
                ]
            ):

                continue

            # ------------------------------------------------
            # MODEL NOT FOUND
            # ------------------------------------------------

            if any(
                word in error_text
                for word in [
                    "404",
                    "not found",
                    "model",
                    "unsupported",
                ]
            ):

                continue

            # ------------------------------------------------
            # AUTHENTICATION
            # ------------------------------------------------

            if any(
                word in error_text
                for word in [
                    "401",
                    "403",
                    "api key",
                    "authentication",
                    "permission",
                    "unauthorized",
                ]
            ):

                return (
                    "❌ Gemini authentication failed.\n\n"
                    "Please check your "
                    "GEMINI_API_KEY in "
                    "Streamlit Secrets.\n\n"
                    f"Technical error:\n"
                    f"{type(exc).__name__}: {str(exc)}\n\n"
                    "Your PakEco pollution dashboard "
                    "is still available."
                )

            continue

    # ========================================================
    # FINAL DEBUG ERROR
    # ========================================================

    return (
        "⚠️ Gemini is temporarily unavailable.\n\n"
        "Your PakEco pollution dashboard is still working.\n\n"
        "Gemini errors detected:\n\n"
        + "\n".join(errors)
    )


# ============================================================
# BACKEND STATUS
# ============================================================

def backend_status():

    gemini_configured = bool(
        os.getenv(
            "GEMINI_API_KEY"
        )
    )

    return {
        "pakeco_backend": "OK",

        "gemini_configured": (
            gemini_configured
        ),

        "cities_available": len(
            CITIES
        ),

        "open_meteo_air_quality": AQ_URL,

        "open_meteo_weather": WEATHER_URL,
                }
