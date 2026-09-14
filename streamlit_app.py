            import os

import streamlit as st
import plotly.express as px

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="PakEco AI",
    page_icon="🌍",
    layout="wide",
)

# ============================================================
# LOAD GEMINI API KEY FROM STREAMLIT SECRETS
# ============================================================

if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend import (
    CITIES,
    aqi_label,
    fetch_city,
    compare_cities,
    gemini_answer,
)

# ============================================================
# TITLE
# ============================================================

st.title("🌍 PakEco AI")

st.subheader(
    "Pakistan Environmental Pollution Monitoring & City Comparison"
)

st.info(
    "Air-quality values are model-based Open-Meteo data. "
    "They are not guaranteed official ground-station measurements."
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Controls")

    city = st.selectbox(
        "Select city",
        list(CITIES),
    )

    selected = st.multiselect(
        "Compare cities",
        list(CITIES),
        default=[
            "Karachi",
            "Lahore",
            "Islamabad",
            "Peshawar",
        ],
    )

# ============================================================
# FETCH SELECTED CITY
# ============================================================

try:

    data = fetch_city(city)

except Exception as exc:

    st.error(
        f"❌ Could not retrieve data: {exc}"
    )

    st.stop()

# ============================================================
# CURRENT AIR QUALITY METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

# US AQI
if data["us_aqi"] is None:
    c1.metric("US AQI", "—")
else:
    c1.metric(
        "US AQI",
        round(data["us_aqi"])
    )

# PM2.5
if data["pm25"] is None:
    c2.metric("PM2.5", "—")
else:
    c2.metric(
        "PM2.5",
        f'{data["pm25"]:.1f} µg/m³'
    )

# PM10
if data["pm10"] is None:
    c3.metric("PM10", "—")
else:
    c3.metric(
        "PM10",
        f'{data["pm10"]:.1f} µg/m³'
    )

# Temperature
if data["temperature"] is None:
    c4.metric("Temperature", "—")
else:
    c4.metric(
        "Temperature",
        f'{data["temperature"]:.1f} °C'
    )

# ============================================================
# AQI CATEGORY
# ============================================================

st.caption(
    f"AQI category: **{aqi_label(data['us_aqi'])}** "
    f"· Retrieved: {data['retrieved_at']}"
)

# ============================================================
# WEATHER INFORMATION
# ============================================================

w1, w2, w3 = st.columns(3)

if data["humidity"] is None:
    w1.metric("Humidity", "—")
else:
    w1.metric(
        "Humidity",
        f'{data["humidity"]:.0f}%'
    )

if data["wind"] is None:
    w2.metric("Wind", "—")
else:
    w2.metric(
        "Wind",
        f'{data["wind"]:.1f} km/h'
    )

w3.metric(
    "City",
    city
)

# ============================================================
# HOURLY TREND
# ============================================================

st.markdown("### 📈 Hourly Pollution Trend")

if data["hourly"].empty:

    st.warning(
        "Hourly pollution data is unavailable."
    )

else:

    fig = px.line(
        data["hourly"],
        x="time",
        y=[
            "PM2.5 (µg/m³)",
            "PM10 (µg/m³)"
        ],
        markers=True,
        title=f"{city} Particulate Matter",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# ============================================================
# CITY COMPARISON
# ============================================================

st.markdown("### 🏙️ Pakistan City Comparison")

if not selected:

    selected = [city]

df, errors = compare_cities(selected)

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    fig2 = px.bar(
        df.sort_values(
            "US AQI",
            ascending=False
        ),
        x="City",
        y="US AQI",
        text="US AQI",
        title="US AQI Comparison",
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
    )

else:

    st.warning(
        "No city comparison data is currently available."
    )

if errors:

    with st.expander("⚠️ City data errors"):

        for error in errors:
            st.write(error)

# ============================================================
# GEMINI ENVIRONMENTAL ASSISTANT
# ============================================================

st.markdown(
    "### 🤖 Gemini Environmental Assistant"
)

question = st.text_area(
    "Ask a question",
    placeholder=(
        "Example: Why is PM2.5 important?"
    ),
)

if st.button(
    "🤖 Ask Gemini",
    type="primary",
):

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        # ----------------------------------------------------
        # Dashboard context sent to Gemini
        # ----------------------------------------------------

        context = {
            "city": city,

            "US AQI": data["us_aqi"],

            "AQI category": aqi_label(
                data["us_aqi"]
            ),

            "PM2.5": data["pm25"],

            "PM10": data["pm10"],

            "temperature": data[
                "temperature"
            ],

            "humidity": data[
                "humidity"
            ],

            "wind": data[
                "wind"
            ],
        }

        # ----------------------------------------------------
        # Ask Gemini
        # ----------------------------------------------------

        with st.spinner(
            "🤖 PakEco AI is thinking..."
        ):

            answer = gemini_answer(
                question,
                context,
            )

        st.markdown("#### 🤖 PakEco AI")

        st.write(answer)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Data: Open-Meteo Air Quality and Weather APIs. "
    "Air-quality data are based on atmospheric-composition "
    "forecasts and may differ from ground-station observations. "
    "See README/PRD for limitations and attribution."
)
