import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests
import re

# --- Page Config ---
st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- API Logic ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

try:
    key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
    client = Groq(api_key=key)
except Exception:
    st.sidebar.warning("⚠️ API Key missing!")

# --- Pro Audio Engine ---
def apply_pro_effects(audio_segment, pitch_val, echo_val, speed_val, is_mastering):
    try:
        if speed_val != 0:
            new_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
        if pitch_val != 0:
            new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
        if echo_val > 0:
            delay = 150 
            echo = audio_segment - (30 - echo_val)
            audio_segment = audio_segment.overlay(echo, position=delay)
        if is_mastering:
            audio_segment = effects.normalize(audio_segment)
        return audio_segment
    except Exception:
        return audio_segment

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Global Settings")
p_val = st.sidebar.select_slider("Voice Depth:", options=[-10, -5, 0, 5, 10], value=-5, key="p_side")
e_val = st.sidebar.slider("Echo:", 0, 5, 1, key="e_side")
s_val = st.sidebar.select_slider("Speed:", options=[-10, 0, 10, 20], value=0, key="s_side")
mastering_on = st.sidebar.checkbox("Auto-Mastering", value=True, key="m_side")

# --- All 10 Tabs (Purane + Naye) ---
tabs = st.tabs([
    "✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", 
    "📝 SCRIPT", "🎵 BGM", "🎬 TALKING HEAD", "🔊 CLONE", "✂️ MERGE"
])

# --- TAB 1: TTS (Original) ---
with tabs[0]:
    st.subheader("Bulk Text to Speech")
    script = st.text_area("Script (--- use karein split ke liye):", key="t1_in")
    if st.button("Generate TTS", key="t1_btn"):
        parts = [s.strip() for s in script.split("---") if s.strip()]
        for i, p in enumerate(parts):
            communicate = edge_tts.Communicate(p, "ur-PK-AsadNeural")
            asyncio.run(communicate.save(f"t_{i}.mp3"))
            st.audio(apply_pro_effects(AudioSegment.from_file(f"t_{i}.mp3"), p_val, e_val, s_val, mastering_on).export(io.BytesIO(), format="mp3"))

# --- TAB 2: Mixer (Original) ---
with tabs[1]:
    st.subheader("Dialogue Mixer")
    diag = st.text_area("Dialogues (A --- B):", key="t2_in")
    if st.button("Mix Now", key="t2_btn"):
        lines = [l.strip() for l in diag.split("---") if l.strip()]
        combined = AudioSegment.empty()
        for idx, line in enumerate(lines):
            v = "ur-PK-AsadNeural" if idx % 2 == 0 else "ur-PK-UzmaNeural"
            communicate = edge_tts.Communicate(line, v)
            asyncio.run(communicate.save("m.mp3"))
            combined += apply_pro_effects(AudioSegment.from_file("m.mp3"), p_val, e_val, s_val, mastering_on) + AudioSegment.silent(500)
        st.audio(combined.export(io.BytesIO(), format="mp3"))

# --- TAB 3: Editor (Original) ---
with tabs[2]:
    st.subheader("Audio Effects Editor")
    up = st.file_uploader("MP3 Upload:", type=["mp3"], key="t3_u")
    if up and st.button("Apply Effects", key="t3_btn"):
        st.audio(apply_pro_effects(AudioSegment.from_file(up), p_val, e_val, s_val, mastering_on).export(io.BytesIO(), format="mp3"))

# --- TAB 4: Jarvis (Original) ---
with tabs[3]:
    st.subheader("Jarvis AI")
    q = st.text_input("Order Boss?", key="t4_in")
    if st.button("Execute", key="t4_btn"):
        res = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. For images: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":q}], model="llama-3.3-70b-versatile")
        ans = res.choices[0].message.content
        st.write(f"🤖 Jarvis: {ans.split('AI_IMAGE_PROMPT:')[0]}")
        if "AI_IMAGE_PROMPT:" in ans:
            p = re.sub(r'[^a-zA-Z0-9\s]', '', ans.split("AI_IMAGE_PROMPT:")[1]).replace(' ', '%20')
            st.image(f"https://pollinations.ai/p/{p}?width=1024&height=1024&model=flux")

# --- TAB 5: Image (Original) ---
with tabs[4]:
    st.subheader("Image Gen")
    p_i = st.text_input("Idea:", key="t5_in")
    if st.button("Generate Image", key="t5_btn"):
        st.image(f"https://pollinations.ai/p/{p_i.replace(' ','%20')}?width=1024&height=1024&model=flux")

# --- TAB 6 & 7: Script & BGM ---
with tabs[5]:
    st.subheader("AI Script Writer")
    topic = st.text_input("Topic:")
    if st.button("Write"):
        res = client.chat.completions.create(messages=[{"role":"user","content":f"Write script in Roman Urdu: {topic}"}], model="llama-3.3-70b-versatile")
        st.text_area("Script:", value=res.choices[0].message.content, height=200)

with tabs[6]:
    st.subheader("BGM Mixer")
    v_f = st.file_uploader("Voice:", type=["mp3"], key="v_bg")
    m_f = st.file_uploader("Music:", type=["mp3"], key="m_bg")
    if v_f and m_f and st.button("Mix BGM"):
        v = AudioSegment.from_file(v_f)
        m = AudioSegment.from_file(m_f) - 15
        st.audio(v.overlay(m, loop=True).export(io.BytesIO(), format="mp3"))

# --- TAB 8, 9, 10: Naye Features ---
with tabs[7]:
    st.subheader("🎬 Talking Head (Beta)")
    st.file_uploader("Image:", type=["jpg"], key="th_i")
    st.file_uploader("Audio:", type=["mp3"], key="th_a")
    st.info("Talking Head logic is ready for API connection.")

with tabs[8]:
    st.subheader("🔊 Voice Cloning")
    st.file_uploader("Sample:", type=["wav"], key="cl_s")
    st.text_area("Script to Speak:", key="cl_t")
    st.button("Start Cloning")

with tabs[9]:
    st.subheader("✂️ Audio Merger")
    f1 = st.file_uploader("Part 1:", type=["mp3"], key="mr_1")
    f2 = st.file_uploader("Part 2:", type=["mp3"], key="mr_2")
    if f1 and f2 and st.button("Merge"):
        merged = AudioSegment.from_file(f1) + AudioSegment.from_file(f2)
        st.audio(merged.export(io.BytesIO(), format="mp3"))
