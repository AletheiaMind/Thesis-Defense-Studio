# Thesis Defense Studio

Streamlit prototype with three pages:

1. Student profile onboarding
2. Upload-and-review document critique
3. AI thesis defense simulation with a final score

## Run locally

1. Create a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set `OPENAI_API_KEY` if you want live AI responses.
4. Start the app:
   ```bash
   streamlit run app.py
   ```

If no API key is set, the prototype falls back to local heuristic responses so the UI still works.

## how to debug the API call ##

Set NVIDIA_DEBUG = true in secrets.toml:3, then run Streamlit.
Or set environment variable NVIDIA_DEBUG=true before launch.
Trigger a review/defense call to see the outgoing request print.