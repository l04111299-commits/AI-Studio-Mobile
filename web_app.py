import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests
import re

# --- Page Config (Must be at the top) ---
st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- CSS for Better UI ---
st.markdown("""<style> .stTabs [data-baseweb="tab-list"] { gap: 10px; } 
            .stTabs [data-baseweb="tab"] { padding: 10px 20px; background-color: #f0f2f6; border-radius: 5px; }
            </style>""", unsafe_allow_html=True)

# --- API Session Logic ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        client = Groq(api_key=st.session_state.api_key)
except Exception:
    st.sidebar.warning("⚠️ Groq Key missing!")

# --- Audio Engine ---
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

# --- 30+ Voice Library ---
voice_list = {
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🇮🇳 Hindi Male (Madhur)": "hi-IN-MadhurNeural",
    "🇮🇳 Hindi Female (Swara)": "hi-IN-SwaraNeural",
    "🇮🇳 Hindi Female (Ananya)": "hi-IN-AnanyaNeural",
    "🇺🇸 US Male (Guy)": "en-US-GuyNeural",
    "🇺🇸 US Female (Aria)": "en-US-AriaNeural",
    "🇬🇧 UK Male (Ryan)": "en-GB-RyanNeural",
    "🇬🇧 UK Female (Sonia)": "en-GB-SoniaNeural",
    "🎙️ EN-India Male (Prabhat)": "en-IN-PrabhatNeural",
    "🎙️ EN-India Female (Neerja)": "en-IN-NeerjaNeural",
    "👦 Young Boy": "en-US-GuyNeural", 
    "👧 Young Girl": "en-US-AnaNeural",
    "🤖 Sci-Fi Robot": "en-GB-RyanNeural",
    "🎭 Movie Narrator": "en-AU-WilliamNeural",
    "🇸🇦 Arabic Male (Hamed)": "ar-SA-HamedNeural",
    "🇸🇦 Arabic Female (Zariyah)": "ar-SA-ZariyahNeural"
}

# --- Sidebar ---
st.sidebar.header("🎚️ Studio Settings")
p_val = st.sidebar.select_slider("Voice Depth:", options=[-10, -5, 0, 5, 10], value=-5, key="p_v_sidebar")
e_val = st.sidebar.slider("Reverb (Echo):", 0, 5, 1, key="e_v_sidebar")
s_val = st.sidebar.select_slider("Talk Speed:", options=[-10, 0, 10, 20], value=0, key="s_v_sidebar")
mastering_on = st.sidebar.checkbox("Auto-Mastering (Clean Sound)", value=True, key="m_v_sidebar")

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

with tab1:
    st.subheader("✍️ Bulk Text to Speech")
    script = st.text_area("Script Likhein (Split with ---):", key="main_tts_input")
    v_choice = st.selectbox("Awaz Chunain:", list(voice_list.keys()), key="main_tts_voice")
    if st.button("Generate TTS", key="main_tts_btn"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Part {i+1}..."):
                    communicate = edge_tts.Communicate(p_text, voice_list[v_choice])
                    asyncio.run(communicate.save(f"t_{i}.mp3"))
                    raw = AudioSegment.from_file(f"t_{i}.mp3")
                    final = apply_pro_effects(raw, p_val, e_val, s_val, mastering_on)
                    st.audio(final.export(io.BytesIO(), format="mp3"))
                    os.remove(f"t_{i}.mp3")

with tab2:
    st.subheader("👥 Multi-Voice Mixer")
    c1, c2 = st.columns(2)
    with c1: v1 = st.selectbox("Voice 1:", list(voice_list.keys()), index=0, key="mx_v1")
    with c2: v2 = st.selectbox("Voice 2:", list(voice_list.keys()), index=1, key="mx_v2")
    mix_text = st.text_area("Dialogues (L1 --- L2):", key="mx_input")
    if st.button("Mix Now", key="mx_btn"):
        lines = [l.strip() for l in mix_text.split("---") if l.strip()]
        combined = AudioSegment.empty()
        for idx, line in enumerate(lines):
            target = voice_list[v1] if idx % 2 == 0 else voice_list[v2]
            communicate = edge_tts.Communicate(line, target)
            asyncio.run(communicate.save("m.mp3"))
            combined += apply_pro_effects(AudioSegment.from_file("m.mp3"), p_val, e_val, s_val, mastering_on) + AudioSegment.silent(duration=500)
            os.remove("m.mp3")
        st.audio(combined.export(io.BytesIO(), format="mp3"))

with tab3:
    st.subheader("📁 Audio Effects Editor")
    up = st.file_uploader("Upload File:", type=["mp3", "wav"], key="edit_up")
    if up and st.button("Apply Effects", key="edit_btn"):
        res = apply_pro_effects(AudioSegment.from_file(up), p_val, e_val, s_val, mastering_on)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with tab4:
    st.subheader("🤖 Jarvis AI (Pro)")
    j_v = st.selectbox("Jarvis Voice:", list(voice_list.keys()), index=0, key="jr_voice")
    user_q = st.text_input("Order Boss?", key="jr_input")
    if st.button("Submit", key="jr_btn"):
        if user_q:
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. For images: AI_IMAGE_PROMPT: (English Prompt)"}, {"role": "user", "content": user_q}],
                model="llama-3.3-70b-versatile"
            )
            ans = res.choices[0].message.content
            text_ans = ans.split("AI_IMAGE_PROMPT:")[0].strip()
            st.write(f"🤖 **Jarvis:** {text_ans}")
            communicate = edge_tts.Communicate(text_ans, voice_list[j_v])
            asyncio.run(communicate.save("j.mp3"))
            st.audio(apply_pro_effects(AudioSegment.from_file("j.mp3"), p_val, e_val, s_val, mastering_on).export(io.BytesIO(), format="mp3"))
            os.remove("j.mp3")
            if "AI_IMAGE_PROMPT:" in ans:
                img_p = re.sub(r'[^a-zA-Z0-9\s]', '', ans.split("AI_IMAGE_PROMPT:")[1])
                url = f"https://pollinations.ai/p/{img_p.replace(' ', '%20')}?width=1024&height=1024&model=flux"
                st.image(url)

with tab5:
    st.subheader("🎨 Direct Image Gen")
    p_in = st.text_input("Idea (English):", key="id_direct_in")
    if st.button("Generate", key="id_direct_btn"):
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', p_in).replace(' ', '%20')
        st.image(f"https://pollinations.ai/p/{clean}?width=1024&height=1024&model=flux")
