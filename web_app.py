import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os

st.set_page_config(page_title="AI Studio: Pro Dialogue", page_icon="🎙️")

st.title("🎙️ AI Studio: TTS + Dialogue Editor")
st.markdown("---")

# --- Audio Effects Function ---
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

# --- Sidebar: All Controls ---
st.sidebar.header("🎚️ Master Controls")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari Awaz):", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

# --- Main Tabs ---
tab1, tab2 = st.tabs(["✍️ Text-to-Speech", "📁 Upload & Edit"])

with tab1:
    # --- Naya Dialogue Slider ---
    mode = st.select_slider("Select Mode:", options=["Single Line", "Dialogue (Bulk)"], value="Single Line")
    
    if mode == "Dialogue (Bulk)":
        st.caption("Tip: Lines ke darmiyan '---' likhen taake alag alag files banen.")
    
    script = st.text_area("Script Likhein:")
    
    gender_choice = st.radio("Gender Select Karein:", ["👦 Male (Madhur)", "👧 Female (Swara)", "🇵🇰 Urdu Male (Asad)", "🇵🇰 Urdu Female (Uzma)"], horizontal=True)
    
    voice_map = {
        "👦 Male (Madhur)": "hi-IN-MadhurNeural",
        "👧 Female (Swara)": "hi-IN-SwaraNeural",
        "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
        "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural"
    }
    selected_voice = voice_map[gender_choice]

    if st.button("🚀 Generate"):
        if script:
            # Dialogue mode logic
            if mode == "Dialogue (Bulk)":
                scripts = [s.strip() for s in script.split("---") if s.strip()]
            else:
                scripts = [script.strip()]

            for idx, s_text in enumerate(scripts):
                with st.spinner(f"Processing... {idx+1}"):
                    communicate = edge_tts.Communicate(s_text, selected_voice)
                    temp_file = f"temp_{idx}.mp3"
                    asyncio.run(communicate.save(temp_file))
                    
                    sound = AudioSegment.from_file(temp_file)
                    processed = apply_audio_effects(sound, pitch, echo, speed, mastering)
                    
                    out_io = io.BytesIO()
                    processed.export(out_io, format="mp3")
                    st.audio(out_io)
                    st.download_button(f"⬇️ Download Result {idx+1}", out_io, f"audio_{idx+1}.mp3")
                    os.remove(temp_file)

with tab2:
    uploaded_file = st.file_uploader("Apni Audio Upload Karein:", type=["mp3", "wav"])
    if uploaded_file:
        if st.button("✨ Edit Upload"):
            sound = AudioSegment.from_file(uploaded_file)
            processed = apply_audio_effects(sound, pitch, echo, speed, mastering)
            out_io = io.BytesIO()
            processed.export(out_io, format="mp3")
            st.audio(out_io)
            st.download_button("⬇️ Download Edited", out_io, "edited.mp3")

