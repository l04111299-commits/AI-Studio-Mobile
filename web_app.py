import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

# --- Page Config ---
st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- API Check ---
key = st.secrets.get("GROQ_API_KEY", st.session_state.get("api_key", ""))
client = Groq(api_key=key) if key else None

# --- Audio Engine ---
def apply_pro_effects(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        if m: audio = effects.normalize(audio)
        return audio
    except: return audio

# --- Voice Library ---
v_lib = {"🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural", "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male (Madhur)": "hi-IN-MadhurNeural", "🇺🇸 US Male (Guy)": "en-US-GuyNeural"}

# --- Sidebar ---
st.sidebar.header("🎚️ Global Settings")
pv, ev, sv = st.sidebar.select_slider("Voice Depth:", [-10, -5, 0, 5, 10], 0), st.sidebar.slider("Echo:", 0, 5, 1), st.sidebar.select_slider("Speed:", [-10, 0, 10, 20], 0)
m_on = st.sidebar.checkbox("Auto-Mastering", True)

# --- All 10 Tabs (Saray Features) ---
t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]: # TTS
    script = st.text_area("Script (--- separated):", key="t1")
    v_c = st.selectbox("Select Voice:", list(v_lib.keys()), key="v1")
    if st.button("Generate TTS"):
        for i, p in enumerate(script.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[v_c]).save("t.mp3"))
                st.audio(apply_pro_effects(AudioSegment.from_file("t.mp3"), pv, ev, sv, m_on).export(io.BytesIO(), format="mp3"))

with t[1]: # Mixer
    v_a, v_b = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogues"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A---B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v_a if i%2==0 else v_b]).save("m.mp3"))
            res += apply_pro_effects(AudioSegment.from_file("m.mp3"), pv, ev, sv, m_on) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]: # Editor
    up = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if up and st.button("Apply Effects"):
        st.audio(apply_pro_effects(AudioSegment.from_file(up), pv, ev, sv, m_on).export(io.BytesIO(), format="mp3"))

with t[3]: # Jarvis
    q = st.text_input("Order Boss?")
    if st.button("Execute"):
        ans = client.chat.completions.create(messages=[{"role":"user","content":q}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans); asyncio.run(edge_tts.Communicate(ans, v_lib["🇵🇰 Urdu Male (Asad)"]).save("j.mp3"))
        st.audio(apply_pro_effects(AudioSegment.from_file("j.mp3"), pv, ev, sv, m_on).export(io.BytesIO(), format="mp3"))

with t[4]: # Image
    pi = st.text_input("Image Idea:")
    if st.button("Generate"):
        url = f"https://pollinations.ai/p/{pi.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,99)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]: # Script
    if st.button("Write AI Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]: # BGM
    v, m = st.file_uploader("Voice"), st.file_uploader("Music")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15).export(io.BytesIO(), format="mp3"))

with t[7]: # Talk
    st.file_uploader("Photo"); st.file_uploader("Audio")
    st.button("Animate! 🚀")

with t[8]: # Clone
    st.file_uploader("Sample (MP4/MP3)", type=["mp4","mp3","m4a"])
    st.button("Clone Now")

with t[9]: # Merge
    f1, f2 = st.file_uploader("File 1"), st.file_uploader("File 2")
    if f1 and f2 and st.button("Merge Now"):
        st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))
