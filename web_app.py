import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

# --- Page Config (Old Style) ---
st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- API Logic ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

try:
    key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
    client = Groq(api_key=key)
except Exception:
    st.sidebar.warning("⚠️ API Key missing!")

# --- Audio Engine ---
def apply_pro_effects(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        if m: audio = effects.normalize(audio)
        return audio
    except: return audio

# --- Original Voice Library ---
v_lib = {
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🇮🇳 Hindi Male (Madhur)": "hi-IN-MadhurNeural",
    "🇮🇳 Hindi Female (Swara)": "hi-IN-SwaraNeural",
    "🇺🇸 US Male (Guy)": "en-US-GuyNeural",
    "🎭 Movie Narrator": "en-AU-WilliamNeural"
}

# --- Sidebar (Old Settings) ---
st.sidebar.header("🎚️ Global Settings")
p_val = st.sidebar.select_slider("Voice Depth:", options=[-10, -5, 0, 5, 10], value=-5)
e_val = st.sidebar.slider("Echo:", 0, 5, 1)
s_val = st.sidebar.select_slider("Speed:", options=[-10, 0, 10, 20], value=0)
m_on = st.sidebar.checkbox("Auto-Mastering", value=True)

# --- Original 10 Tabs ---
tabs = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

# TAB 1: TTS
with tabs[0]:
    st.subheader("Bulk Text to Speech")
    script = st.text_area("Script (--- use karein split ke liye):")
    v_choice = st.selectbox("Select Voice:", list(v_lib.keys()))
    if st.button("Generate TTS"):
        for i, p in enumerate(script.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[v_choice]).save(f"{i}.mp3"))
                st.audio(apply_pro_effects(AudioSegment.from_file(f"{i}.mp3"), p_val, e_val, s_val, m_on).export(io.BytesIO(), format="mp3"))

# TAB 3: Editor (MP4/M4A Fix)
with tabs[2]:
    st.subheader("Audio Effects Editor")
    up = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if up and st.button("Apply Pro Effects"):
        st.audio(apply_pro_effects(AudioSegment.from_file(up), p_val, e_val, s_val, m_on).export(io.BytesIO(), format="mp3"))

# TAB 4: Jarvis
with tabs[3]:
    st.subheader("Jarvis AI Assistant")
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    q = st.text_input("Order Boss?")
    if st.button("Execute"):
        res = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. For images: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":q}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(f"🤖 Jarvis: {res.split('AI_IMAGE_PROMPT:')[0]}")
        asyncio.run(edge_tts.Communicate(res.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_pro_effects(AudioSegment.from_file("j.mp3"), p_val, e_val, s_val, m_on).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in res:
            p = re.sub(r'[^a-zA-Z0-9\s]', '', res.split("AI_IMAGE_PROMPT:")[1]).replace(' ', '%20')
            st.image(f"https://pollinations.ai/p/{p}?width=1024&height=1024&model=flux")

# TAB 5: Image
with tabs[4]:
    st.subheader("AI Image Generator")
    pi = st.text_input("Tasveer ka idea:")
    if st.button("Generate Image"):
        url = f"https://pollinations.ai/p/{pi.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url)
        st.markdown(f"[📥 Download Link]({url})")

# TAB 8: Talking Head
with tabs[7]:
    st.subheader("🎬 AI Talking Head")
    st.file_uploader("Select Image:", type=["jpg", "png"])
    st.file_uploader("Select Audio:", type=["mp3", "m4a"])
    if st.button("Animate My Photo! 🚀"): st.success("Processing...")

# TAB 9: Cloning
with tabs[8]:
    st.subheader("🔊 Voice Cloning")
    st.file_uploader("Upload Sample (MP4, MP3, M4A):", type=["mp3", "mp4", "m4a"])
    st.button("Clone & Generate Audio")

# TAB 10: Merger
with tabs[9]:
    st.subheader("✂️ Audio Merger")
    f1 = st.file_uploader("Part 1:")
    f2 = st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge Now"):
        mrg = AudioSegment.from_file(f1) + AudioSegment.from_file(f2)
        st.audio(mrg.export(io.BytesIO(), format="mp3"))

