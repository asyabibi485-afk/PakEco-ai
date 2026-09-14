# Product Requirements Document (PRD)
## PakEco AI — Pakistan Environmental Pollution Monitoring & City Comparison

**Version:** 2.0  
**Status:** Hackathon MVP  
**Architecture:** Shared Python backend + Gradio frontend + Streamlit dashboard + Gemini AI

---

## 1. Executive Summary

PakEco AI is an environmental information platform for comparing model-based air-quality information across Pakistani cities.

The product has two user interfaces:

1. **Gradio frontend** for a simple AI/demo experience.
2. **Streamlit dashboard** for interactive analytics and city comparison.

Both interfaces use a shared `backend.py`, which retrieves Open-Meteo data, processes it with Python/Pandas, and sends dashboard context to Gemini for natural-language explanations.

The MVP is for education, awareness, research exploration and hackathon demonstration. It is not an official regulatory monitoring platform.

## 2. Problem

Pollution information can be difficult to understand and compare across Pakistani cities. Users need a simple interface that brings key indicators into one place.

## 3. Solution

PakEco AI provides:

- city selection;
- PM2.5;
- PM10;
- US AQI;
- European AQI;
- weather context;
- hourly trends;
- multi-city comparison;
- Gemini explanations.

## 4. Target Users

- Students
- Researchers
- Hackathon judges
- Environmental-awareness users
- Developers
- Educators

## 5. Functional Requirements

### FR-01 City selection
The system shall provide Pakistani city coordinates.

### FR-02 Pollution retrieval
The backend shall retrieve PM2.5, PM10, US AQI and European AQI.

### FR-03 Weather retrieval
The backend shall retrieve temperature, humidity and wind speed.

### FR-04 Shared backend
Gradio and Streamlit shall call the same Python backend functions.

### FR-05 Gradio UI
The Gradio frontend shall provide:
- city selection;
- pollution button;
- trend chart;
- comparison tab;
- Gemini assistant.

### FR-06 Streamlit UI
The Streamlit dashboard shall provide:
- sidebar controls;
- metrics;
- trend chart;
- comparison table;
- comparison chart;
- Gemini assistant.

### FR-07 AI assistant
Gemini shall answer environmental questions using supplied dashboard context.

### FR-08 Error handling
External API or Gemini failure shall show a user-friendly message instead of crashing the application.

## 6. Data Sources

### Open-Meteo Air Quality API

Used for PM2.5, PM10, US AQI and European AQI.

The API documentation identifies hourly air-quality variables and explains its CAMS-based forecast data sources.

### Open-Meteo Weather API

Used for temperature, humidity and wind speed.

### Gemini API

Used for natural-language environmental explanations.

## 7. API Constraints

### Rate limits
External service limits and commercial conditions can change. The project should cache or minimize repeated requests for production use.

### API availability
Requests can fail due to network errors, server outages or invalid parameters.

### Keys
Gemini API keys must be stored in:
- environment variables locally;
- hosting secrets in deployment.

They must never be committed to GitHub.

### Model availability
Gemini model names and API interfaces can change. Keep the model identifier in one backend function so it can be updated without rewriting the UI.

### Data coverage
Open-Meteo's model data have spatial resolution and domain limitations. A coordinate is not equivalent to a complete city's ground-monitoring network.

### Units
- PM2.5 / PM10: µg/m³
- Temperature: °C
- Humidity: %
- Wind: km/h
- AQI: index

## 8. Data Quality

The application must clearly label pollution information as model-based.

It must not claim:
- official government measurement;
- exact neighborhood-level pollution;
- medical certainty.

## 9. Architecture

```text
Gradio UI ─────┐
               ├──> backend.py ──> Open-Meteo
Streamlit UI ──┘              └──> Gemini
```

## 10. Security

- No hard-coded API keys.
- `.env` ignored by Git.
- Streamlit secrets used in Streamlit Cloud.
- Hosting-platform secret manager used for Gradio hosting.
- No unnecessary personal data sent to Gemini.

## 11. MVP Success Criteria

- [ ] Gradio launches.
- [ ] Streamlit launches.
- [ ] Both interfaces import the same backend.
- [ ] At least 8 Pakistani cities work.
- [ ] PM2.5 works.
- [ ] PM10 works.
- [ ] US AQI works.
- [ ] City comparison works.
- [ ] Charts work.
- [ ] Gemini works with a valid key.
- [ ] Gemini failure does not crash the dashboard.
- [ ] GitHub repository is clean of secrets.
- [ ] Streamlit deployment works.
- [ ] Gradio deployment works or is locally demonstrable.

## 12. Future Enhancements

- Pakistan map
- Historical analytics
- Pollution forecasting
- Official monitoring-station integrations
- IoT sensors
- Alerts
- Urdu AI assistant
- ML prediction
- PDF reports
- Mobile/PWA version

## 13. Responsible AI

The AI layer should explain rather than fabricate. It receives measurements from the backend and is instructed not to invent pollution data.

The project is not a medical diagnostic system.

## 14. Disclaimer

PakEco AI is an educational and hackathon prototype. Model-based air-quality information should not be treated as official regulatory measurements or as medical advice.

## 15. Deliverables

- Gradio frontend
- Streamlit dashboard
- Python backend
- GitHub repository
- PRD
- README
- Demo script
- Live deployment(s)
- Demo video
