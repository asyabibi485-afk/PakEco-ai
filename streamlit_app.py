import streamlit as st
from backend import analyze_environment

CITIES = [
    "Peshawar", "Islamabad", "Rawalpindi", "Lahore", "Karachi",
    "Quetta", "Multan", "Faisalabad", "Abbottabad", "Mardan",
    "Swat", "Nowshera", "Sialkot", "Gujranwala", "Bahawalpur",
    "Sukkur", "Hyderabad", "Dera Ismail Khan", "Gilgit", "Skardu",
    "Muzaffarabad"
]

st.set_page_config(page_title="PakEco AI", page_icon="🇵🇰", layout="wide")

st.title("🇵🇰 PakEco AI")
st.subheader("🌱 Pakistan Environmental & Ecosystem Detector")
st.write("Analyze environmental conditions using environmental indicators and Gemini AI.")

with st.sidebar:
    st.header("Environmental Inputs")
    city = st.selectbox("🏙️ Pakistani City", CITIES)
    aqi = st.number_input("🌫️ AQI", min_value=0.0, max_value=500.0, value=100.0)
    temperature = st.number_input("🌡️ Temperature (°C)", min_value=-20.0, max_value=60.0, value=30.0)
    water = st.slider("💧 Water Pollution (0–10)", 0.0, 10.0, 5.0, 1.0)
    waste = st.slider("🗑️ Waste Pollution (0–10)", 0.0, 10.0, 5.0, 1.0)
    green = st.slider("🌳 Green Area Condition (0–10)", 0.0, 10.0, 5.0, 1.0)
    analyze = st.button("🔍 Analyze Environment", type="primary")

if analyze:
    with st.spinner("Analyzing environment..."):
        report = analyze_environment(city, aqi, temperature, water, waste, green)
    st.markdown(report)
else:
    st.info("Enter the environmental values in the sidebar and click Analyze Environment.")

st.divider()
st.caption("⚠️ PakEco AI is an environmental screening prototype. User-entered values are not official government measurements.")
