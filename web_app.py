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

# --- Streamlit Secrets & Session Logic ---
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

# --- FULL 30+ VOICE LIBRARY (RESTORED) ---
voices = {
    # URDU & HINDI
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🇮🇳 Hindi Male (Madhur)": "hi-IN-MadhurNeural",
    "🇮🇳 Hindi Female (Swara)": "hi-IN-SwaraNeural",
    "🇮🇳 Hindi Female (Ananya)": "hi-IN-AnanyaNeural",
    # ENGLISH - INDIA
    "🎙️ EN-India Male (Prabhat)": "en-IN-PrabhatNeural",
    "🎙️ EN-India Female (Neerja)": "en-IN-NeerjaNeural",
    # ENGLISH - US
    "🇺🇸 US Male (Guy)": "en-US-GuyNeural",
    "🇺🇸 US Female (Aria)": "en-US-AriaNeural",
    "🇺🇸 US Male (Christopher)": "en-US-ChristopherNeural",
    "🇺🇸 US Female (Jenny)": "en-US-JennyNeural",
    "🇺🇸 US Male (Eric)": "en-US-EricNeural",
    "🇺🇸 US Female (Michelle)": "en-US-MichelleNeural",
    # ENGLISH - UK
    "🇬🇧 UK Male (Ryan)": "en-GB-RyanNeural",
    "🇬🇧 UK Female (Sonia)": "en-GB-SoniaNeural",
    "🇬🇧 UK Male (Libby)": "en-GB-LibbyNeural",
    "🇬🇧 UK Female (Mia)": "en-GB-MiaNeural",
    # ENGLISH - AUSTRALIA
    "🇦🇺 AU Male (William)": "en-AU-WilliamNeural",
    "🇦🇺 AU Female (Natasha)": "en-AU-NatashaNeural",
    # KIDS & SPECIAL
    "👦 Young Boy (US)": "en-US-GuyNeural", 
    "👧 Young Girl (US)": "en-US-AnaNeural",
    "🤖 Sci-Fi Robot": "en-GB-RyanNeural",
    "📻 Vintage Radio": "en-PH-JamesNeural",
    "🎭 Movie Narrator": "en-AU-WilliamNeural",
    # ARABIC & OTHERS
    "🇸🇦 Arabic Male (Hamed)": "ar-SA-HamedNeural",
    "🇸🇦 Arabic Female (Zariyah)": "ar-SA-ZariyahNeural",
    "🇦🇪 Arabic Male (Hamdan)": "ar-AE-HamdanNeural",
    "🇿🇦 SA Male (Luke)": "en-ZA-LukeNeural",
    "🇨🇦 CA Female (Clara)": "en-CA-ClaraNeural",
    "🇮🇪 IE Male (Connor)": "en-IE-ConnorNeural",
}

# --- Sidebar ---
st.sidebar.header("🎚️ Studio Settings")
p_val = st.sidebar.select_slider("Voice Depth (Pitch):", options=[-10, -5, 0, 5, 10], value=-5)
e_val = st.sidebar.slider("Reverb (Echo):", 0, 5, 1)
s_val = st.sidebar.select_slider("Talk Speed:", options=[-10, 0, 10, 20], value=0)
mastering_on = st.sidebar.checkbox("Auto-Mastering (Clean Sound)", value=True)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

with tab1:
    st.subheader("✍️ Bulk Text to Speech (30+ Voices)")
    script = st.text_area("Script Likhein (Split with ---):", key="tts_vfinal")
    v_choice = st.selectbox("Awaz Chunain:", list(voices.keys()), key="v_sel_tts")
    if st.button("Generate TTS"):
        parts = [s.strip() for s in script.split("---") if s.strip()]
        for i, p_text in enumerate(parts):
            communicate = edge_tts.Communicate(p_text, voices[v_choice])
            asyncio.run(communicate.save(f"t_{i}.mp3"))
            st.audio(apply_pro_effects(AudioSegment.from_file(f"t_{i}.mp3"), p_val, e_val, s_val, mastering_on).export(io.BytesIO(), format="mp3"))

with tab2:
    st.subheader("👥 Multi-Voice Dialogue Mixer")
    c1, c2 = st.columns(2)
    with c1: v1 = st.selectbox("Voice 1:", list(voices.keys()), index=0)
    with c2: v2 = st.selectbox("Voice 2:", list(voices.keys()), index=1)
    mix_script = st.text_area("Dialogues (Line 1 --- Line 2):")
    if st.button("Mix Voices"):
        lines = [l.strip() for l in mix_script.split("---") if l.strip()]
        combined = AudioSegment.empty()
        for idx, line in enumerate(lines):
            target_v = voices[v1] if idx % 2 == 0 else voices[v2]
            communicate = edge_tts.Communicate(line, target_v)
            asyncio.run(communicate.save("m.mp3"))
            combined += apply_pro_effects(AudioSegment.from_file("m.mp3"), p_val, e_val, s_val, mastering_on) + AudioSegment.silent(duration=500)
        st.audio(combined.export(io.BytesIO(), format="mp3"))

with tab3:
    st.subheader("📁 Audio Effects Editor")
    up = st.file_uploader("Audio File:", type=["mp3", "wav"])
    if up and st.button("Apply Effects"):
        st.audio(apply_pro_effects(AudioSegment.from_file(up), p_val, e_val, s_val, mastering_on).export(io.BytesIO(), format="mp3"))

with tab4:
    st.subheader("🤖 Jarvis Assistant (Pro Art & Speech)")
    j_style = st.selectbox("Jarvis Voice:", list(voices.keys()), index=0)
    user_q = st.text_input("Ask Jarvis:", key="jq_final")
    if st.button("Submit"):
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. For images: AI_IMAGE_PROMPT: (English)"}, {"role": "user", "content": user_query}],
            model="llama-3.3-70b-versatile",
        )
        ans = res.choices[0].message.content
        text_ans = ans.split("AI_IMAGE_PROMPT:")[0].strip()
        st.write(f"🤖 **Jarvis:** {text_ans}")
        communicate = edge_tts.Communicate(text_ans, voices[j_style])
        asyncio.run(communicate.save("j.mp3"))
        st.audio(apply_pro_effects(AudioSegment.from_file("j.mp3"), p_val, e_val, s_val, mastering_on).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans:
            img_p = re.sub(r'[^a-zA-Z0-9\s]', '', ans.split("AI_IMAGE_PROMPT:")[1])
            url = f"https://pollinations.ai/p/{img_p.replace(' ', '%20')}?width=1024&height=1024&model=flux"
            st.image(url)

with tab5:
    st.subheader("🎨 Image Generation")
    p_direct = st.text_input("English Idea:")
    if st.button("Generate"):
        url = f"https://pollinations.ai/p/{p_direct.replace(' ', '%20')}?width=1024&height=1024&model=flux"
        st.image(url)
