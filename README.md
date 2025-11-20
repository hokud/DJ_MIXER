# 🎧 DJ MIXER

DJ MIXER is a creative AI tool that helps DJs and music lovers craft seamless, emotionally engaging mixes.  
It analyzes Spotify tracks by tempo, key, energy, and danceability and then uses generative AI to describe each track’s *vibe* and *transition logic*.

By combining data-driven precision with human like emotional reasoning, the app recommends harmonically and energetically compatible tracks and explains *why* they flow together.

---

## Features
- **Audio Feature Analysis:** Fetches BPM, key (Camelot), energy, and danceability using Spotify’s Web API.
- **Generative Vibe Analysis:** Uses GPT to add emotional and descriptive tags (e.g., *“dreamy build”*, *“late-night euphoric groove”*).
- **Hybrid Recommendation Engine:** Blends deterministic scoring (BPM, key, energy) with AI reasoning for DJ-style suggestions.
- **AI Transition Explanations:** Automatically generates natural-language explanations for why two tracks mix well.
- **Streamlit Interface:** Clean UI for exploring matches, vibes, and creative transitions.

---

## Tech Stack
**Languages/Frameworks:** Python, Streamlit  
**APIs:** Spotify Web API (Spotipy), OpenAI API  
**Libraries:** pandas, scikit-learn, python-dotenv, tenacity  

---

## Getting Started
**You will need:** a Spotify account

### Install Requirements
pip install -r requirements.txt

### Run the App
streamlit run app/ui.py

---

## *THIS IS A WORK IN PROGRESS*
