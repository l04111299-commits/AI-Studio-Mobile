import streamlit as st
import asyncio
import edge_tts
import os
from pydub import AudioSegment, effects

st.set_page_config(page_title="AI Mobile Production Pro", page_icon="🎙️")

st.title("🎙️ AI Mobile Production Pro")
st.markdown("---")

# 1. Function to fix formatting
async def generate_audio(text, voice, rate, pitch):
    # Format: Rate must be '+0%' or '-10%' etc.
    # Pitch must be '+0Hz' or '-10Hz' etc.
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    temp_file = "temp_web.mp3"
    await communicate.save(temp_file)
    return temp_file

# 2. Input Section
script = st.text_area("Apna Script Likhen (Bulk ke liye '---' use karein):", height=150)

col1, col2 = st.columns(2)
with col1:
    voice = st.selectbox("Awaz Chunein:", ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "ur-PK-AsadNeural", "ur-PK-UzmaNeural"])
    # Hum symbols slider se hata rahe hain taake error na aaye
    speed_val = st.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=-15)

with col2:
    pitch_val = st.select_slider("Pitch (Bhari/Halki):", options=[-15, -10, 0, 10, 15], value=0)
    mastering = st.checkbox("Auto-Mastering", value=True)

echo_val = st.slider("Echo Level:", 0, 10, 3)

# 3. Processing Logic
if st.button("🚀 GENERATE AUDIO"):
    if script:
        scripts = [s.strip() for s in script.split("---") if s.strip()]
        
        # Proper formatting for edge-tts
        final_speed = f"{speed_val:+d}%"
        final_pitch = f"{pitch_val:+d}Hz"
        
        for idx, s_text in enumerate(scripts):
            with st.spinner(f"Processing Part {idx+1}..."):
                # Run TTS
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    temp_mp3 = loop.run_until_complete(generate_audio(s_text, voice, final_speed, final_pitch))
                    
                    # Audio Effects
                    audio = AudioSegment.from_file(temp_mp3)
                    if mastering:
                        audio = effects.normalize(audio) + 5
                    
                    if echo_val > 0:
                        echo = audio - (25 - echo_val)
                        audio = audio.overlay(echo, position=200)
                    
                    final_name = f"Final_Audio_{idx+1}.mp3"
                    audio.export(final_name, format="mp3")
                    
                    st.audio(final_name)
                    with open(final_name, "rb") as f:
                        st.download_button(f"⬇️ Download Part {idx+1}", f, file_name=final_name)
                    
                    os.remove(temp_mp3)
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("Pehle script likhen!")
