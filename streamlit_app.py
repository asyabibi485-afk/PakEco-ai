import streamlit as st
import plotly.express as px

from backend import CITIES, aqi_label, fetch_city, compare_cities, gemini_answer

st.set_page_config(page_title="PakEco AI", page_icon="🌍", layout="wide")

st.title("🌍 PakEco AI")
st.subheader("Pakistan Environmental Pollution Monitoring & City Comparison")
st.info(
    "Air-quality values are model-based Open-Meteo data. They are not guaranteed "
    "official ground-station measurements."
)

with st.sidebar:
    st.header("Controls")
    city = st.selectbox("Select city", list(CITIES))
    selected = st.multiselect(
        "Compare cities",
        list(CITIES),
        default=["Karachi", "Lahore", "Islamabad", "Peshawar"],
    )

try:
    data = fetch_city(city)
except Exception as exc:
    st.error(f"Could not retrieve data: {exc}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("US AQI", "—" if data["us_aqi"] is None else round(data["us_aqi"]))
c2.metric("PM2.5", "—" if data["pm25"] is None else f'{data["pm25"]:.1f} µg/m³')
c3.metric("PM10", "—" if data["pm10"] is None else f'{data["pm10"]:.1f} µg/m³')
c4.metric("Temperature", "—" if data["temperature"] is None else f'{data["temperature"]:.1f} °C')

st.caption(f"AQI category: **{aqi_label(data['us_aqi'])}** · Retrieved: {data['retrieved_at']}")

st.markdown("### 📈 Hourly trend")
fig = px.line(
    data["hourly"],
    x="time",
    y=["PM2.5 (µg/m³)", "PM10 (µg/m³)"],
    markers=True,
    title=f"{city} particulate matter",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🏙️ City comparison")
if not selected:
    selected = [city]
df, errors = compare_cities(selected)
st.dataframe(df, use_container_width=True, hide_index=True)
if not df.empty:
    fig2 = px.bar(df.sort_values("US AQI", ascending=False), x="City", y="US AQI",
                  text="US AQI", title="US AQI comparison")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 🤖 Gemini Environmental Assistant")
question = st.text_area("Ask a question", placeholder="Why is PM2.5 important?")
if st.button("Ask Gemini", type="primary"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        context = {
            "city": city,
            "US AQI": data["us_aqi"],
            "AQI category": aqi_label(data["us_aqi"]),
            "PM2.5": data["pm25"],
            "PM10": data["pm10"],
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "wind": data["wind"],
        }
        st.write(gemini_answer(question, context))

st.markdown("---")
st.caption(
    "Data: Open-Meteo Air Quality and Weather APIs. "
    "Air-quality data are based on atmospheric-composition forecasts. "
    "See README/PRD for limitations and attribution."
)
