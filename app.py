import gradio as gr
from backend import analyze_environment

PAKISTAN_CITIES = [
    "Peshawar", "Islamabad", "Rawalpindi", "Lahore", "Karachi",
    "Quetta", "Multan", "Faisalabad", "Abbottabad", "Mardan",
    "Swat", "Nowshera", "Sialkot", "Gujranwala", "Bahawalpur",
    "Sukkur", "Hyderabad", "Dera Ismail Khan", "Gilgit", "Skardu",
    "Muzaffarabad"
]

def clear_all():
    return "Peshawar", 100, 30, 5, 5, 5, ""

with gr.Blocks(title="PakEco AI", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
# 🇵🇰 PakEco AI
## 🌱 Pakistan Environmental & Ecosystem Detector

Analyze environmental conditions of Pakistani cities using environmental indicators and Google Gemini AI.

**Gemini RateLimit fallback:** If Gemini is unavailable or rate-limited, PakEco automatically generates a local screening report.
""")

    with gr.Row():
        with gr.Column():
            city = gr.Dropdown(PAKISTAN_CITIES, value="Peshawar", label="🏙️ Pakistani City")
            aqi = gr.Number(value=100, minimum=0, maximum=500, label="🌫️ Air Quality Index (AQI)")
            temperature = gr.Number(value=30, minimum=-20, maximum=60, label="🌡️ Temperature (°C)")
        with gr.Column():
            water = gr.Slider(0, 10, value=5, step=1, label="💧 Water Pollution (0–10)")
            waste = gr.Slider(0, 10, value=5, step=1, label="🗑️ Waste Pollution (0–10)")
            green = gr.Slider(0, 10, value=5, step=1, label="🌳 Green Area Condition (0–10)")

    with gr.Row():
        analyze = gr.Button("🔍 Analyze Environment", variant="primary")
        clear = gr.Button("🧹 Clear")

    output = gr.Markdown("Enter values and click **Analyze Environment**.")

    analyze.click(
        analyze_environment,
        [city, aqi, temperature, water, waste, green],
        output
    )

    clear.click(
        clear_all,
        [],
        [city, aqi, temperature, water, waste, green, output]
    )

    gr.Markdown("""
---
### 📊 PakEco AI checks
🌫️ Air Pollution • 💧 Water Pollution • 🗑️ Waste • 🌳 Green Areas • 🌡️ Temperature • 🌍 Ecosystem • ⚠️ Risk

### ⚠️ Disclaimer
PakEco AI is an environmental screening prototype, not an official government monitoring system.
""")

if __name__ == "__main__":
    app.launch()
