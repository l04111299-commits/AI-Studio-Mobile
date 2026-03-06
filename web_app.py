import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os

st.set_page_config(page_title="AI Studio: All-in-One", page_icon="🎙️")

st.title("🎙️ AI Studio: TTS + Editor")
st.markdown("---")

# --- Professional Effects Function ---
def apply_audio_effects(audio_segment, pitch_val, echo_val, speed_val, is_mastering):
    # 1. Speed Change
    if speed_val != 0:
        # Simple speed change logic
        new_sample_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)

    # 2. Pitch Change (Bhari Awaz)
    if pitch_val != 0:
        new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)
    
    # 3. Echo Effect
    if echo_val > 0:
        delay = 200 
        echo = audio_segment - (25 - echo_val)
        audio_segment = audio_segment.overlay(echo, position=delay)
    
    # 4. Auto-Mastering (Normalize)
    if is_mastering:
        audio_segment = effects.normalize(audio_segment)
    
    return audio_segment

# --- Sidebar: Full Controls ---
st.sidebar.header("🎚️ Audio Master Controls")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari Awaz):", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

# --- Main Tabs ---
tab1, tab2 = st.tabs(["✍️ Text-to-Speech (Bulk)", "📁 Upload & Edit"])

# TAB 1: TTS with Bulk Feature
with tab1:
    script = st.text_area("Script Likhein (Bulk ke liye '---' use karein):", placeholder="Line 1\n---\nLine 2")
    voice = st.selectbox("Awaz Chunein:", ["hi-IN-MadhurNeural", "ur-PK-AsadNeural", "ur-PK-UzmaNeural"])
    
    if st.button("🚀 Generate AI Voices"):
        if script:
            scripts = [s.strip() for s in script.split("---") if s.strip()]
            for idx, s_text in enumerate(scripts):
                with st.spinner(f"Processing Part {idx+1}..."):
                    communicate = edge_tts.Communicate(s_text, voice)
                    temp_file = f"temp_{idx}.mp3"
                    asyncio.run(communicate.save(temp_file))
                    
                    sound = AudioSegment.from_file(temp_file)
                    processed = apply_audio_effects(sound, pitch, echo, speed, mastering)
                    
                    out_io = io.BytesIO()
                    processed.export(out_io, format="mp3")
                    st.audio(out_io, format="audio/mp3")
                    st.download_button(f"⬇️ Download Part {idx+1}", out_io, f"ai_part_{idx+1}.mp3")
                    os.remove(temp_file)

# TAB 2: Upload & Edit
with tab2:
    uploaded_file = st.file_uploader("Apni Audio Upload Karein (MP3/WAV):", type=["mp3", "wav"])
    if uploaded_file:
        if st.button("✨ Apply Effects to Upload"):
            with st.spinner("Editing in progress..."):
                sound = AudioSegment.from_file(uploaded_file)
                # For uploads, we usually don't change speed unless asked, but effects are applied
                processed = apply_audio_effects(sound, pitch, echo, speed, mastering)
                
                out_io = io.BytesIO()
                processed.export(out_io, format="mp3")
                st.audio(out_io)
                st.download_button("⬇️ Download Edited Audio", out_io, "edited_studio.mp3")
