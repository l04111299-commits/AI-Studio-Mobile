import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, AudioOps
import os
import io

# --- Page Config ---
st.set_page_config(page_title="AI Multi-Audio Studio", layout="centered")
st.title("🎙️ AI All-in-One Audio Studio")
st.markdown("Text likhein, File upload karein ya Record karein - Sab edit hoga!")

# --- Sidebar: Effects Settings ---
st.sidebar.header("🎚️ Audio Effects Control")
pitch_val = st.sidebar.slider("Voice Bhari Karein (Pitch)", -20, 20, -10)
echo_delay = st.sidebar.slider("Echo Delay (ms)", 0, 500, 150)
echo_decibel = st.sidebar.slider("Echo Volume", -20, -5, -12)

# --- Functions ---
def apply_effects(audio_path):
    sound = AudioSegment.from_file(audio_path)
    
    # 1. Pitch Modification (Bhari Awaz)
    new_sample_rate = int(sound.frame_rate * (2.0 ** (pitch_val / 12.0)))
    sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    sound = sound.set_frame_rate(44100)

    # 2. Echo Effect
    if echo_delay > 0:
        output = AudioSegment.silent(duration=len(sound) + echo_delay)
        output = output.overlay(sound)
        echo = sound - abs(echo_decibel)
        output = output.overlay(echo, position=echo_delay)
        sound = output

    # 3. Mastering (Loudness & Clarity)
    sound = AudioOps.normalize(sound)
    
    out_io = io.BytesIO()
    sound.export(out_io, format="mp3")
    return out_io

# --- Main App Tabs ---
tab1, tab2, tab3 = st.tabs(["✍️ Text-to-Speech", "📁 Upload & Edit", "🎤 Record Voice"])

# TAB 1: Text-to-Speech
with tab1:
    text = st.text_area("Apna Script Likhein:", "Dosto, aaj hum banayenge ek professional audio.")
    voice = st.selectbox("Awaz Chunein:", ["hi-IN-MadhurNeural (Bhari)", "ur-PK-UzmaNeural (Urdu)"])
    if st.button("Generate TTS Audio"):
        if text:
            async def make_tts():
                v = "hi-IN-MadhurNeural" if "Madhur" in voice else "ur-PK-UzmaNeural"
                communicate = edge_tts.Communicate(text, v)
                await communicate.save("temp.mp3")
            
            asyncio.run(make_tts())
            processed_audio = apply_effects("temp.mp3")
            st.audio(processed_audio)
            st.download_button("Download TTS Audio", processed_audio, "ai_voice.mp3")

# TAB 2: Upload Audio
with tab2:
    uploaded_file = st.file_uploader("Apni Audio File Select Karein (.mp3, .wav)", type=["mp3", "wav"])
    if uploaded_file is not None:
        with open("uploaded.mp3", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Edit & Apply Effects"):
            processed_audio = apply_effects("uploaded.mp3")
            st.audio(processed_audio)
            st.download_button("Download Edited Audio", processed_audio, "edited_audio.mp3")

# TAB 3: Recording (Direct Link)
with tab3:
    st.info("Mobile par recording ke liye aap default recorder use karke 'Upload' tab mein file dal sakte hain. Direct web recording ke liye 'streamlit-mic-recorder' library install karni hogi.")
    st.write("Aap niche diye gaye button se recording testing kar sakte hain (Browser permission chahiye hogi).")
    # Note: Recording ke liye advance JS chahiye hoti hai, filhal best tarika Mobile Recorder + Upload hai.
