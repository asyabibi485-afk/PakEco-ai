import gradio as gr
import plotly.express as px

from backend import CITIES, aqi_label, fetch_city, compare_cities, gemini_answer

def get_pollution(city):
    try:
        d = fetch_city(city)
        summary = (
            f"### {city}\n"
            f"**US AQI:** {d['us_aqi'] if d['us_aqi'] is not None else '—'} "
            f"({aqi_label(d['us_aqi'])})  \n"
            f"**PM2.5:** {d['pm25'] if d['pm25'] is not None else '—'} µg/m³  \n"
            f"**PM10:** {d['pm10'] if d['pm10'] is not None else '—'} µg/m³  \n"
            f"**Temperature:** {d['temperature'] if d['temperature'] is not None else '—'} °C  \n"
            f"**Humidity:** {d['humidity'] if d['humidity'] is not None else '—'} %  \n"
            f"**Wind:** {d['wind'] if d['wind'] is not None else '—'} km/h  \n"
            f"**Retrieved:** {d['retrieved_at']}"
        )
        frame = d["hourly"]
        fig = px.line(
            frame,
            x="time",
            y=["PM2.5 (µg/m³)", "PM10 (µg/m³)"],
            markers=True,
            title=f"{city} particulate matter trend",
        )
        return summary, fig
    except Exception as exc:
        return f"Unable to retrieve {city}: {type(exc).__name__}: {exc}", None

def compare(selected):
    if not selected:
        selected = ["Karachi", "Lahore", "Islamabad", "Peshawar"]
    df, errors = compare_cities(selected)
    if df.empty:
        return "No city data available.", None
    fig = px.bar(df.sort_values("US AQI", ascending=False), x="City", y="US AQI", text="US AQI",
                 title="US AQI comparison")
    note = ""
    if errors:
        note = "\n\nUnavailable: " + ", ".join(errors)
    return df.to_markdown(index=False) + note, fig

def ask_ai(question, city):
    if not question.strip():
        return "Please enter a question."
    try:
        data = fetch_city(city)
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
        return gemini_answer(question, context)
    except Exception as exc:
        return f"Could not prepare the AI context: {type(exc).__name__}: {exc}"

with gr.Blocks(title="PakEco AI") as demo:
    gr.Markdown(
        "# 🌍 PakEco AI\n"
        "### Pakistan Environmental Pollution Monitoring & City Comparison\n"
        "Gradio frontend + Python backend + Open-Meteo + Gemini"
    )
    gr.Markdown(
        "⚠️ Air-quality values are model-based environmental data, not guaranteed "
        "official ground-station measurements."
    )

    with gr.Tab("Pollution Dashboard"):
        city = gr.Dropdown(choices=list(CITIES), value="Karachi", label="Select city")
        get_btn = gr.Button("🔎 Get Pollution Data", variant="primary")
        summary = gr.Markdown()
        chart = gr.Plot()
        get_btn.click(get_pollution, inputs=city, outputs=[summary, chart])

    with gr.Tab("Compare Cities"):
        cities = gr.CheckboxGroup(
            choices=list(CITIES),
            value=["Karachi", "Lahore", "Islamabad", "Peshawar"],
            label="Cities to compare",
        )
        compare_btn = gr.Button("📊 Compare Cities", variant="primary")
        comparison = gr.Markdown()
        comparison_chart = gr.Plot()
        compare_btn.click(compare, inputs=cities, outputs=[comparison, comparison_chart])

    with gr.Tab("Gemini Assistant"):
        ai_city = gr.Dropdown(choices=list(CITIES), value="Karachi", label="City context")
        question = gr.Textbox(
            label="Question",
            placeholder="Why is PM2.5 important?",
            lines=3,
        )
        ask_btn = gr.Button("🤖 Ask Gemini", variant="primary")
        answer = gr.Markdown()
        ask_btn.click(ask_ai, inputs=[question, ai_city], outputs=answer)

if __name__ == "__main__":
    demo.launch()
