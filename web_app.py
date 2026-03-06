import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os

st.set_page_config(page_title="AI Audio Studio Pro", page_icon="🎙️")

st.title("🎙️ AI All-in-One Audio Studio")
st.markdown("---")

# --- Effects Function ---
def apply_audio_effects(audio_segment, pitch_val, echo_val):
    # 1. Pitch Change (Bhari Awaz)
    if pitch_val != 0:
        new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)
    
    # 2. Echo Effect
    if echo_val > 0:
        # Create a delay based on echo level
        delay = 200 # ms
        echo = audio_segment - (25 - echo_val) # Reduce volume of echo
        audio_segment = audio_segment.overlay(echo, position=delay)
    
    # 3. Mastering (Normalize volume)
    audio_segment = effects.normalize(audio_segment)
    return audio_segment

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Master Controls")
pitch = st.sidebar.slider("Pitch (Bhari Awaz):", -15, 15, -10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)

# --- Main Tabs ---
tab1, tab2 = st.tabs(["✍️ Text-to-Speech", "📁 Upload & Edit"])

# TAB 1: TTS
with tab1:
    script = st.text_area("Script Likhein:", placeholder="Yahan apna text likhein...")
    voice = st.selectbox("Awaz Chunein:", ["hi-IN-MadhurNeural", "ur-PK-AsadNeural", "ur-PK-UzmaNeural"])
    
    if st.button("🚀 Generate AI Voice"):
        if script:
            with st.spinner("AI Awaz bana raha hai..."):
                # Run Edge-TTS
                communicate = edge_tts.Communicate(script, voice)
                temp_file = "temp_tts.mp3"
                asyncio.run(communicate.save(temp_file))
                
                # Apply Effects
                sound = AudioSegment.from_file(temp_file)
                processed = apply_audio_effects(sound, pitch, echo)
                
                # Show Result
                out_io = io.BytesIO()
                processed.export(out_io, format="mp3")
                st.audio(out_io)
                st.download_button("⬇️ Download AI Voice", out_io, "ai_studio_tts.mp3")
                os.remove(temp_file)

# TAB 2: Upload
with tab2:
    uploaded_file = st.file_uploader("Apni Audio Upload Karein (MP3/WAV):", type=["mp3", "wav"])
    if uploaded_file:
        if st.button("✨ Edit Uploaded Audio"):
            with st.spinner("Editing jari hai..."):
                sound = AudioSegment.from_file(uploaded_file)
                processed = apply_audio_effects(sound, pitch, echo)
                
                out_io = io.BytesIO()
                processed.export(out_io, format="mp3")
                st.audio(out_io)
                st.download_button("⬇️ Download Edited Audio", out_io, "edited_studio.mp3")
