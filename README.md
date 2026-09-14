# PakEco AI

Pakistan Environmental & Ecosystem Detector.

## Files

- `app.py` — Gradio frontend for Hugging Face Spaces
- `backend.py` — risk calculation, Gemini integration, and RateLimit fallback
- `streamlit_app.py` — Streamlit version for Streamlit Community Cloud
- `requirements.txt` — Python dependencies

## Gemini Secret

Create an environment secret named:

`GEMINI_API_KEY`

Never hardcode the API key in source code.

## Hugging Face

Create a Gradio Space and upload `app.py`, `backend.py`, and `requirements.txt`.

## Streamlit

Create a Streamlit Community Cloud app and set the main file to `streamlit_app.py`.
Add `GEMINI_API_KEY` under the app's Secrets.

## Important

PakEco is an AI environmental screening prototype. User-entered values are not official government measurements.
