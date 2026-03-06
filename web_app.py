import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests

st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- Streamlit Secrets Logic ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        # Agar secrets nahi hain to session state use karein
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        client = Groq(api_key=st.session_state.api_key)
except Exception as e:
    st.error("Groq key setup ka masla hai.")

# Sidebar for Manual Key Entry (Emergency Backup)
with st.sidebar:
    st.header("🔑 API Settings")
    manual_key = st.text_input("Nayi API Key yahan dalein (If needed):", type="password")
    if st.button("Update Key"):
        st.session_state.api_key = manual_key
        st.success("Key updated!")

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

with tab4:
    st.subheader("🤖 Jarvis Assistant (Updated Model)")
    user_q = st.text_input("Talk to Jarvis:", key="j_input_new")
    
    if st.button("Submit Order"):
        if user_q:
            try:
                # Use correct key from secrets or session
                key_to_use = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
                active_client = Groq(api_key=key_to_use)
                
                # Updated Model: llama-3.3-70b-versatile
                chat_completion = active_client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. Call user Boss."},
                              {"role": "user", "content": user_q}],
                    model="llama-3.3-70b-versatile",
                )
                ans = chat_completion.choices[0].message.content
                st.write(f"🤖 **Jarvis:** {ans}")
                
                # Voice Output
                communicate = edge_tts.Communicate(ans, "hi-IN-MadhurNeural")
                asyncio.run(communicate.save("j.mp3"))
                j_v = apply_audio_effects(AudioSegment.from_file("j.mp3"), -15, 2, 0, True)
                st.audio(j_v.export(io.BytesIO(), format="mp3"))
                os.remove("j.mp3")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Pehle kuch likhein Boss!")

# --- (Baki Tabs ka code waisa hi rahega) ---
with tab5:
    st.subheader("🎨 AI Image Gen")
    prompt = st.text_input("Image Prompt (English):", key="i_input")
    if st.button("Generate"):
        if prompt:
            url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&model=flux"
            st.image(url)
            st.download_button("Download Image", requests.get(url).content, "image.jpg")




