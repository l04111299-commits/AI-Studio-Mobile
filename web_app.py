import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests

# --- Groq Setup ---
client = Groq(api_key="Gsk_uMvdF5TgK8Qxds9W3CceWGdyb3FY3Ji7jT3we7KL4f86Tmdno8hW")

st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- Audio Engine ---
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

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Global Sound Master")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari Voice):", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🎙️ Movie Narrator": "en-US-GuyNeural"
}

# --- Main Interface ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

# --- TAB 1, 2, 3 (Purana Working Code) ---
with tab1:
    script = st.text_area("Script Likhein (--- for Bulk):", key="tts_input")
    v_choice = st.radio("Voice:", list(voices.keys()), horizontal=True)
    if st.button("Generate TTS"):
        parts = [s.strip() for s in script.split("---") if s.strip()]
        for i, p_text in enumerate(parts):
            communicate = edge_tts.Communicate(p_text, voices[v_choice])
            asyncio.run(communicate.save(f"t_{i}.mp3"))
            s = apply_audio_effects(AudioSegment.from_file(f"t_{i}.mp3"), pitch, echo, speed, mastering)
            st.audio(s.export(io.BytesIO(), format="mp3"))
            os.remove(f"t_{i}.mp3")

with tab2:
    st.info("Mixing Mode: Line 1 Male, Line 2 Female...")
    mix_script = st.text_area("Dialogue Lines:", key="mix_input")
    col1, col2 = st.columns(2)
    with col1: mv = st.selectbox("Male Voice:", list(voices.keys()), index=0)
    with col2: fv = st.selectbox("Female Voice:", list(voices.keys()), index=1)
    if st.button("Mix Dialogue"):
        lines = [l.strip() for l in mix_script.split("---") if l.strip()]
        combined = AudioSegment.empty()
        for idx, line in enumerate(lines):
            vid = voices[mv] if idx % 2 == 0 else voices[fv]
            communicate = edge_tts.Communicate(line, vid)
            asyncio.run(communicate.save("m.mp3"))
            combined += apply_audio_effects(AudioSegment.from_file("m.mp3"), pitch, echo, speed, mastering) + AudioSegment.silent(duration=400)
            os.remove("m.mp3")
        st.audio(combined.export(io.BytesIO(), format="mp3"))

with tab3:
    up = st.file_uploader("Upload Audio for Master Edit:", type=["mp3", "wav"])
    if up and st.button("Apply Effects"):
        s = apply_audio_effects(AudioSegment.from_file(up), pitch, echo, speed, mastering)
        st.audio(s.export(io.BytesIO(), format="mp3"))

# --- TAB 4: JARVIS (Chat & Script Writer) ---
with tab4:
    st.subheader("🤖 Jarvis AI Assistant")
    user_q = st.text_input("Ask Jarvis (Script, Info, etc):")
    if st.button("Submit") or user_q:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. Be professional. Call user Boss."},
                      {"role": "user", "content": user_q}],
            model="llama3-8b-8192",
        )
        ans = chat_completion.choices[0].message.content
        st.write(f"🤖 Jarvis: {ans}")
        # Jarvis Voice
        communicate = edge_tts.Communicate(ans, "hi-IN-MadhurNeural")
        asyncio.run(communicate.save("j.mp3"))
        j_v = apply_audio_effects(AudioSegment.from_file("j.mp3"), -15, 2, 0, True)
        st.audio(j_v.export(io.BytesIO(), format="mp3"))
        os.remove("j.mp3")

# --- TAB 5: FREE IMAGE GENERATOR (Pollinations) ---
with tab5:
    st.subheader("🎨 AI Image Generator")
    prompt = st.text_input("Tasveer ka idea likhein (English is better):", placeholder="e.g., A futuristic robot in a dark room")
    
    if st.button("Generate Image"):
        if prompt:
            with st.spinner("AI Tasveer bana raha hai..."):
                # Clean prompt for URL
                clean_prompt = prompt.replace(" ", "%20")
                image_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed=42&model=flux"
                
                # Display Image
                st.image(image_url, caption=f"Generated: {prompt}", use_container_width=True)
                
                # Download Button
                response = requests.get(image_url)
                st.download_button("⬇️ Download Image", response.content, "ai_image.jpg", "image/jpeg")
        else:
            st.warning("Pehle kuch likhein!")
