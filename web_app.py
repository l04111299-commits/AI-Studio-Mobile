import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests

# --- Page Config ---
st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- Streamlit Secrets Logic ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        client = Groq(api_key=st.session_state.api_key)
except Exception:
    st.error("API Key ka masla hai. Secrets check karein.")

# --- Professional Audio Engine ---
def apply_pro_effects(audio_segment, pitch_val, echo_val, speed_val):
    try:
        # Speed Adjustment
        if speed_val != 0:
            new_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
        
        # Pitch for Spotify-Style Depth
        if pitch_val != 0:
            new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
            
        # Echo/Reverb
        if echo_val > 0:
            delay = 150 
            echo = audio_segment - (30 - echo_val)
            audio_segment = audio_segment.overlay(echo, position=delay)
            
        # Mastering: Normalize makes it sound clean
        audio_segment = effects.normalize(audio_segment)
        return audio_segment
    except Exception as e:
        return audio_segment

# --- Sidebar (Fixed Sliders) ---
st.sidebar.header("🎚️ Pro Audio Controls")
# Sliders fix kiye hain taake crash na ho
p_val = st.sidebar.select_slider("Voice Depth (Pitch):", options=[-10, -5, 0, 5, 10], value=-5)
e_val = st.sidebar.slider("Reverb (Echo):", 0, 5, 1)
s_val = st.sidebar.select_slider("Talk Speed:", options=[-10, 0, 10, 20], value=0)

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

with tab4:
    st.subheader("🤖 Jarvis Assistant (Pro Voice Mode)")
    
    # Spotify-like Voice selection
    voice_type = st.selectbox("Jarvis Voice Style:", 
                              ["Professional Deep Male", "Clear Sweet Female", "Urdu News Style"])
    
    voice_map = {
        "Professional Deep Male": "en-US-GuyNeural",
        "Clear Sweet Female": "hi-IN-SwaraNeural",
        "Urdu News Style": "ur-PK-AsadNeural"
    }

    user_query = st.text_input("Talk to Jarvis:", key="jarvis_final")
    
    if st.button("Submit Order"):
        if user_query:
            try:
                # Key retrieval
                key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
                groq_client = Groq(api_key=key)
                
                # AI Response
                res = groq_client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu beautifully. Call user Boss."},
                              {"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile",
                )
                answer = res.choices[0].message.content
                st.write(f"🤖 **Jarvis:** {answer}")
                
                # Voice Gen
                with st.spinner("Mastering Spotify-Quality Audio..."):
                    vid = voice_map[voice_type]
                    communicate = edge_tts.Communicate(answer, vid)
                    asyncio.run(communicate.save("temp.mp3"))
                    
                    # Apply Pro Effects
                    raw = AudioSegment.from_file("temp.mp3")
                    final_audio = apply_pro_effects(raw, p_val, e_val, s_val)
                    
                    st.audio(final_audio.export(io.BytesIO(), format="mp3"))
                    os.remove("temp.mp3")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- Image Gen (Waisa hi rahega) ---
with tab5:
    st.subheader("🎨 AI Image Gen")
    prompt = st.text_input("Tasveer ka idea likhein:", key="img_final")
    if st.button("Generate"):
        if prompt:
            url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&model=flux"
            st.image(url)






