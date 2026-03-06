import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os

st.set_page_config(page_title="AI Studio: Global Pro", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Studio: Global All-in-One")
st.markdown("---")

# --- Audio Effects Function (Original Features) ---
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

# --- Sidebar: Master Controls ---
st.sidebar.header("🎚️ Master Controls")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari Awaz):", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

# --- Voice Database ---
voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🎬 Movie Narrator (US)": "en-US-GuyNeural",
    "🎭 Deep Cinematic (UK)": "en-GB-ThomasNeural",
    "🎤 Hollywood Style (US)": "en-US-ChristopherNeural"
}

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["✍️ TTS (Single/Bulk)", "👥 Dialogue Mixer", "📁 Upload & Edit"])

# TAB 1: TTS (Original Radio Button Style)
with tab1:
    script = st.text_area("Script Likhein (Bulk ke liye '---' use karein):")
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
                    st.download_button(f"⬇️ Download Part {i+1}", out, f"audio_{i+1}.mp3")
                    os.remove(t_file)

# TAB 2: Dialogue Mixer (Mixing M/F)
with tab2:
    st.subheader("Mixed Dialogue Creator")
    mix_script = st.text_area("Dialogue Script (Line 1 --- Line 2):", placeholder="Line 1\n---\nLine 2")
    col1, col2 = st.columns(2)
    with col1:
        v1 = st.selectbox("Character 1:", list(voices.keys()), index=0)
    with col2:
        v2 = st.selectbox("Character 2:", list(voices.keys()), index=1)

    if st.button("🎭 Combine Dialogue"):
        if mix_script:
            lines = [l.strip() for l in mix_script.split("---") if l.strip()]
            combined = AudioSegment.empty()
            for idx, line_text in enumerate(lines):
                with st.spinner(f"Mixing Line {idx+1}..."):
                    v_id = voices[v1] if idx % 2 == 0 else voices[v2]
                    communicate = edge_tts.Communicate(line_text, v_id)
                    t_file = f"mix_{idx}.mp3"
                    asyncio.run(communicate.save(t_file))
                    line_audio = apply_audio_effects(AudioSegment.from_file(t_file), pitch, echo, speed, mastering)
                    combined += line_audio + AudioSegment.silent(duration=400)
                    os.remove(t_file)
            f_out = io.BytesIO()
            combined.export(f_out, format="mp3")
            st.audio(f_out)
            st.download_button("⬇️ Download Full Dialogue", f_out, "dialogue.mp3")

# TAB 3: Editor
with tab3:
    up_file = st.file_uploader("Edit Audio:", type=["mp3", "wav"])
    if up_file and st.button("✨ Apply Master Effects"):
        sound = apply_audio_effects(AudioSegment.from_file(up_file), pitch, echo, speed, mastering)
        out_io = io.BytesIO()
        sound.export(out_io, format="mp3")
        st.audio(out_io)
