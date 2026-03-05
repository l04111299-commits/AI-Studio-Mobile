import streamlit as st
import asyncio
import edge_tts
import os
from pydub import AudioSegment, effects
from datetime import datetime

# Page Configuration for Mobile
st.set_page_config(page_title="AI Audio Studio Mobile", page_icon="🎙️")

st.title("🎙️ AI Mobile Production Pro")
st.markdown("---")

# 1. Script Input
script = st.text_area("Apna Script Likhen (Bulk ke liye '---' use karein):", height=150)

# 2. Voice & Style Settings
col1, col2 = st.columns(2)
with col1:
    voice = st.selectbox("Awaz Chunein:", ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "ur-PK-AsadNeural", "ur-PK-UzmaNeural"])
    speed = st.select_slider("Speed:", options=["-25%", "-15%", "0%", "+10%"], value="-15%")

with col2:
    pitch = st.select_slider("Pitch (Bhari/Halki):", options=["-15Hz", "-10Hz", "0Hz", "+10Hz", "+15Hz"], value="0Hz")
    mastering = st.checkbox("Auto-Mastering", value=True)

echo_val = st.slider("Echo Level:", 0, 10, 3)

# 3. Processing Logic
async def generate_audio(text, voice, rate, pitch):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    temp_file = "temp_web.mp3"
    await communicate.save(temp_file)
    return temp_file

if st.button("🚀 GENERATE AUDIO"):
    if script:
        scripts = [s.strip() for s in script.split("---") if s.strip()]
        
        for idx, s_text in enumerate(scripts):
            with st.spinner(f"Processing Part {idx+1}..."):
                # TTS Generation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                temp_mp3 = loop.run_until_complete(generate_audio(s_text, voice, speed, pitch))
                
                # Audio Effects with Pydub
                audio = AudioSegment.from_file(temp_mp3)
                
                if mastering:
                    audio = effects.normalize(audio) + 5
                
                if echo_val > 0:
                    echo = audio - (25 - echo_val)
                    audio = audio.overlay(echo, position=200)
                
                final_name = f"Mobile_Master_{idx+1}.mp3"
                audio.export(final_name, format="mp3")
                
                # Display Result
                st.audio(final_name)
                with open(final_name, "rb") as f:
                    st.download_button(f"⬇️ Download Part {idx+1}", f, file_name=final_name)
                
                # Clean up
                os.remove(temp_mp3)
    else:
        st.error("Pehle script to likhen!")

st.markdown("---")
st.caption("Powered by Gemini & Streamlit | Mobile Ready")