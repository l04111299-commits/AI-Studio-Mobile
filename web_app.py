import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os

st.set_page_config(page_title="AI Mega Audio Studio", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Mega Audio Studio: All-in-One")
st.markdown("---")

# --- Core Audio Engine (Saare Purane Features ke Saath) ---
def apply_audio_effects(audio_segment, pitch_val, echo_val, speed_val, is_mastering):
    # 1. Speed Control (Purana Feature)
    if speed_val != 0:
        new_sample_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)

    # 2. Pitch Control (Bhari Awaz)
    if pitch_val != 0:
        new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
        audio_segment = audio_segment.set_frame_rate(44100)
    
    # 3. Echo Effect
    if echo_val > 0:
        delay = 200 
        echo = audio_segment - (25 - echo_val)
        audio_segment = audio_segment.overlay(echo, position=delay)
    
    # 4. Auto-Mastering (Purana Feature)
    if is_mastering:
        audio_segment = effects.normalize(audio_segment)
    
    return audio_segment

# --- Sidebar: Global Master Controls ---
st.sidebar.header("🎚️ Master Sound Settings")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari Awaz):", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

# --- Main Interface Tabs ---
tab1, tab2, tab3 = st.tabs(["✍️ TTS (Single/Bulk)", "👥 Dialogue Mixer (M/F)", "📁 Upload & Edit"])

# VOICE MAPPING
voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural"
}

# TAB 1: Text-to-Speech (With Bulk '---' Feature)
with tab1:
    script = st.text_area("Script Likhein (Alag files ke liye '---' use karein):", height=150)
    gender_choice = st.radio("Voice Select Karein:", list(voices.keys()), horizontal=True)
    
    if st.button("🚀 Generate TTS"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Processing Part {i+1}..."):
                    communicate = edge_tts.Communicate(p_text, voices[gender_choice])
                    t_file = f"tts_{i}.mp3"
                    asyncio.run(communicate.save(t_file))
                    
                    sound = apply_audio_effects(AudioSegment.from_file(t_file), pitch, echo, speed, mastering)
                    out = io.BytesIO()
                    sound.export(out, format="mp3")
                    st.audio(out)
                    st.download_button(f"⬇️ Download Part {i+1}", out, f"audio_part_{i+1}.mp3")
                    os.remove(t_file)

# TAB 2: Dialogue Mixer (Male + Female Mixing)
with tab2:
    st.subheader("Mixed Dialogue Creator")
    st.caption("Pehli line Male, doosri Female... is tarah auto-mix hogi.")
    mix_script = st.text_area("Dialogue Script (Lines ke darmiyan '---' lazmi lagayein):", height=200, placeholder="Boy: Salam kaise ho?\n---\nGirl: Teek hoon tum batao.")
    
    col1, col2 = st.columns(2)
    with col1:
        m_voice = st.selectbox("Male Character:", ["👦 Male (Madhur)", "🇵🇰 Urdu Male (Asad)"])
    with col2:
        f_voice = st.selectbox("Female Character:", ["👧 Female (Swara)", "🇵🇰 Urdu Female (Uzma)"])

    if st.button("🎭 Generate Combined Dialogue"):
        if mix_script:
            lines = [l.strip() for l in mix_script.split("---") if l.strip()]
            combined = AudioSegment.empty()
            
            for idx, line_text in enumerate(lines):
                with st.spinner(f"Mixing Line {idx+1}..."):
                    v_id = voices[m_voice] if idx % 2 == 0 else voices[f_voice]
                    communicate = edge_tts.Communicate(line_text, v_id)
                    t_file = f"mix_{idx}.mp3"
                    asyncio.run(communicate.save(t_file))
                    
                    line_audio = apply_audio_effects(AudioSegment.from_file(t_file), pitch, echo, speed, mastering)
                    combined += line_audio + AudioSegment.silent(duration=400) # Dialogue gap
                    os.remove(t_file)
            
            final_io = io.BytesIO()
            combined.export(final_io, format="mp3")
            st.audio(final_io)
            st.download_button("⬇️ Download Full Story", final_io, "combined_dialogue.mp3")

# TAB 3: Professional Editor (Upload)
with tab3:
    up_file = st.file_uploader("Edit karne ke liye audio select karein:", type=["mp3", "wav"])
    if up_file:
        if st.button("✨ Apply Master Effects"):
            with st.spinner("Editing..."):
                sound = AudioSegment.from_file(up_file)
                processed = apply_audio_effects(sound, pitch, echo, speed, mastering)
                out_io = io.BytesIO()
                processed.export(out_io, format="mp3")
                st.audio(out_io)
                st.download_button("⬇️ Download Edited Audio", out_io, "studio_edit.mp3")
