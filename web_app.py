import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests
import re
import random

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

# --- Voice Library ---
voice_library = {
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🇮🇳 Hindi Male (Madhur)": "hi-IN-MadhurNeural",
    "🇮🇳 Hindi Female (Swara)": "hi-IN-SwaraNeural",
    "🇺🇸 US Male (Guy)": "en-US-GuyNeural",
    "🎭 Movie Narrator": "en-AU-WilliamNeural"
}

# --- Tabs ---
tabs = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

# --- TAB 5: IMAGE GEN (FIXED) ---
with tabs[4]:
    st.subheader("🎨 Direct AI Image Generation")
    prompt = st.text_input("Apna idea likhein (English mein):", key="img_prompt")
    
    if st.button("Generate Image", key="img_btn"):
        if prompt:
            with st.spinner("🖌️ AI Tasveer bana raha hai..."):
                # Clean prompt to remove special characters
                clean_prompt = re.sub(r'[^a-zA-Z0-9\s]', '', prompt).replace(' ', '%20')
                seed = random.randint(1, 100000)
                # Updated URL logic to prevent '0' or blank results
                img_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&model=flux"
                
                st.image(img_url, caption=f"Result for: {prompt}", use_container_width=True)
                st.success("✅ Image Generated!")
                st.markdown(f"[🔗 Direct Link]({img_url})")
        else:
            st.warning("Pehle kuch likhein!")

# --- TAB 4: JARVIS (IMAGE FIX) ---
with tabs[3]:
    st.subheader("🤖 Jarvis AI")
    user_q = st.text_input("Order Boss?", key="jarvis_q")
    if st.button("Execute", key="jarvis_btn"):
        res = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. If user asks for image, end with AI_IMAGE_PROMPT: (English Prompt)"},{"role":"user","content":user_q}], model="llama-3.3-70b-versatile")
        ans = res.choices[0].message.content
        st.write(f"🤖 Jarvis: {ans.split('AI_IMAGE_PROMPT:')[0]}")
        
        if "AI_IMAGE_PROMPT:" in ans:
            img_p = re.sub(r'[^a-zA-Z0-9\s]', '', ans.split("AI_IMAGE_PROMPT:")[1]).strip().replace(' ', '%20')
            if img_p:
                st.image(f"https://pollinations.ai/p/{img_p}?width=1024&height=1024&model=flux", caption="Jarvis Created This")

# Baaki saare tabs (TTS, Mixer, etc.) pehle wale code se shamil raheinge...
