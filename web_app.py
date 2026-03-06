import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests

st.set_page_config(page_title="AI Studio Pro", page_icon="🎙️", layout="wide")

# --- Streamlit Secrets Logic ---
# Code mein ab API key nahi likhi, ye dashboard se uthayega
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.warning("⚠️ GROQ_API_KEY Streamlit Secrets mein nahi mili. Sidebar use karein.")
        # Backup: Agar secrets kaam na karein to manual key ka option
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        client = Groq(api_key=st.session_state.api_key)
except Exception as e:
    st.error("Groq Client initialize nahi ho saka.")

# Sidebar for Manual Key (Just in case)
with st.sidebar:
    st.header("🔑 API Settings")
    manual_key = st.text_input("Nayi API Key yahan dalein:", type="password")
    if st.button("Update Key"):
        st.session_state.api_key = manual_key
        st.success("Key updated for this session!")

# --- Audio Engine ---
def apply_audio_effects(audio_segment, pitch_val, echo_val, speed_val, is_mastering):
    if speed_val != 0:
        new_sample_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)
    if pitch_val != 0:
        new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)
    if echo_val > 0:
        delay = 200 
        echo = audio_segment - (25 - echo_val)
        audio_segment = audio_segment.overlay(echo, position=delay)
    if is_mastering:
        audio_segment = effects.normalize(audio_segment)
    return audio_segment

# Master Sidebar Controls
st.sidebar.header("🎚️ Sound Controls")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch:", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural"
}

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

with tab1:
    script = st.text_area("Script:")
    v_choice = st.radio("Voice:", list(voices.keys()), horizontal=True)
    if st.button("Generate TTS"):
        if script:
            communicate = edge_tts.Communicate(script, voices[v_choice])
            asyncio.run(communicate.save("t.mp3"))
            s = apply_audio_effects(AudioSegment.from_file("t.mp3"), pitch, echo, speed, mastering)
            st.audio(s.export(io.BytesIO(), format="mp3"))
            os.remove("t.mp3")

with tab4:
    st.subheader("🤖 Jarvis Assistant")
    user_q = st.text_input("Talk to Jarvis:", key="j_input")
    if st.button("Submit Order") and user_q:
        try:
            # Re-init client with correct key
            current_key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
            active_client = Groq(api_key=current_key)
            
            chat_completion = active_client.chat.completions.create(
                messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. Call user Boss."},
                          {"role": "user", "content": user_q}],
                model="llama3-8b-8192",
            )
            ans = chat_completion.choices[0].message.content
            st.write(f"🤖 Jarvis: {ans}")
            # Voice Output
            communicate = edge_tts.Communicate(ans, "hi-IN-MadhurNeural")
            asyncio.run(communicate.save("j.mp3"))
            j_v = apply_audio_effects(AudioSegment.from_file("j.mp3"), -15, 2, 0, True)
            st.audio(j_v.export(io.BytesIO(), format="mp3"))
            os.remove("j.mp3")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab5:
    st.subheader("🎨 AI Image Gen")
    prompt = st.text_input("Image Prompt (English):", key="i_input")
    if st.button("Generate"):
        if prompt:
            url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&model=flux"
            st.image(url)
            st.download_button("Download Image", requests.get(url).content, "image.jpg")



