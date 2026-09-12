# 🌍 PakEco AI

## Pakistan Environmental Pollution Monitoring & City Comparison

PakEco AI is a hackathon-ready environmental application with **two frontends** and a shared Python backend:

- **Gradio frontend** — `gradio_app.py`
- **Streamlit dashboard** — `streamlit_app.py`
- **Shared backend** — `backend.py`
- **Gemini AI assistant**
- **Open-Meteo air-quality + weather APIs**

Gradio is used as the interactive AI/demo frontend, while Streamlit provides the richer dashboard experience.

## Architecture

```text
                 ┌─────────────────────┐
                 │     User / Browser   │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
          Gradio Frontend       Streamlit Dashboard
        gradio_app.py            streamlit_app.py
                 │                     │
                 └──────────┬──────────┘
                            │
                       backend.py
                            │
             ┌──────────────┼──────────────┐
             │              │              │
        Open-Meteo      Open-Meteo      Gemini API
       Air Quality       Weather          AI
```

## Features

- Pakistani city selector
- US AQI and European AQI
- PM2.5 and PM10
- Temperature, humidity and wind
- Hourly particulate-matter charts
- Multi-city comparison
- AQI ranking chart
- Gemini Environmental Assistant
- Shared backend for both UIs
- Graceful API/AI errors
- No Open-Meteo API key required for the standard MVP request

## Data sources

Open-Meteo Air Quality API:
https://open-meteo.com/en/docs/air-quality-api

Open-Meteo Weather API:
https://open-meteo.com/en/docs

Gemini API:
https://ai.google.dev/gemini-api/docs

The air-quality API documents PM2.5, PM10, European AQI and US AQI variables and explains that the forecast is based on CAMS atmospheric-composition forecast data.

## Important limitation

The pollution values are **model-based** and tied to selected coordinates. They should not be described as official ground-monitoring station measurements.

## 1. Run locally

Python 3.10+ is recommended because current Gradio documentation requires Python 3.10 or higher.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

## 2. Add Gemini API key

Get a key from Google AI Studio.

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
```

macOS/Linux:

```bash
export GEMINI_API_KEY="YOUR_KEY"
```

Never upload the key to GitHub.

## 3. Run Gradio frontend

```bash
python gradio_app.py
```

Gradio normally opens a local web interface.

## 4. Run Streamlit dashboard

Open another terminal in the same folder:

```bash
streamlit run streamlit_app.py
```

## 5. GitHub deployment

Upload these files:

```text
PakEco-AI/
├── backend.py
├── gradio_app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── PRD.md
├── DEMO_SCRIPT.md
├── .gitignore
├── .env.example
├── project.json
└── data/
    └── sample_data.csv
```

Do NOT upload `.env`, API keys, or `secrets.toml`.

## 6. Streamlit deployment

1. Create a GitHub repository.
2. Upload the project.
3. Open Streamlit Community Cloud.
4. Choose your repository.
5. Set the main file to `streamlit_app.py`.
6. Deploy.
7. Open **Settings → Secrets**.
8. Add:

```toml
GEMINI_API_KEY = "YOUR_REAL_KEY"
```

9. Save and reboot the app.

## 7. Gradio deployment options

For the Gradio frontend, the easiest portfolio/hackathon hosting route is a Hugging Face Space using the Gradio SDK.

Upload:

```text
backend.py
gradio_app.py
requirements.txt
README.md
```

If the platform expects `app.py`, either rename `gradio_app.py` to `app.py` or configure the entry point according to the host's current instructions.

Add `GEMINI_API_KEY` as a secret/environment variable in the hosting platform.

## Hackathon submission

Recommended submission package:

- Project name: **PakEco AI**
- GitHub URL
- Streamlit demo URL
- Gradio demo URL
- PRD
- 2–3 minute demo video
- Presentation
- Technology list
- Data-source/AI limitations

## Responsible AI

PakEco AI:
- identifies its data sources;
- distinguishes model data from station observations;
- does not intentionally generate pollution measurements;
- avoids medical diagnosis;
- explains uncertainty;
- keeps API keys outside source control.

## Attribution

Follow the current Open-Meteo attribution requirements when publishing the application or redistributing its data. See the Open-Meteo documentation for current CAMS/Open-Meteo acknowledgement language.
