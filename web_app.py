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

# --- Initialize Memory (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Audio Engine ---
def apply_audio_effects(audio_segment, pitch_val, echo_val, speed_val, is_mastering):
    try:
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
    except Exception as e:
        st.error(f"Audio Processing Error: {e}")
        return audio_segment

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Master Controls")
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

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

with tab1:
    script = st.text_area("Script Likhein (--- for Bulk):", key="tts_tab")
    v_choice = st.radio("Voice:", list(voices.keys()), horizontal=True)
    if st.button("Generate TTS"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Generating Part {i+1}..."):
                    communicate = edge_tts.Communicate(p_text, voices[v_choice])
                    asyncio.run(communicate.save(f"t_{i}.mp3"))
                    s = apply_audio_effects(AudioSegment.from_file(f"t_{i}.mp3"), pitch, echo, speed, mastering)
                    st.audio(s.export(io.BytesIO(), format="mp3"))
                    os.remove(f"t_{i}.mp3")

with tab2:
    st.info("Line 1 Male, Line 2 Female...")
    mix_script = st.text_area("Dialogue Lines:", key="mix_tab")
    col1, col2 = st.columns(2)
    with col1: mv = st.selectbox("Male Voice:", list(voices.keys()), index=0)
    with col2: fv = st.selectbox("Female Voice:", list(voices.keys()), index=1)
    if st.button("Mix Dialogue"):
        if mix_script:
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

with tab4:
    st.subheader("🤖 Jarvis AI (With Memory)")
    # Clear Memory Button
    if st.button("Clear Memory"):
        st.session_state.messages = []
        st.rerun()

    user_q = st.text_input("Ask Jarvis:", key="jarvis_input")
    
    if st.button("Talk to Jarvis") and user_q:
        # Add user message to memory
        st.session_state.messages.append({"role": "user", "content": user_query := user_q})
        
        try:
            # Prepare context for Jarvis
            context = [{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. Call user Boss. Remember previous context."}]
            context.extend(st.session_state.messages[-6:]) # Last 3 pairs of conversation

            chat_completion = client.chat.completions.create(messages=context, model="llama3-8b-8192")
            ans = chat_completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            
            st.write(f"🤖 **Jarvis:** {ans}")
            
            # Voice Output
            communicate = edge_tts.Communicate(ans, "hi-IN-MadhurNeural")
            asyncio.run(communicate.save("j.mp3"))
            j_v = apply_audio_effects(AudioSegment.from_file("j.mp3"), -15, 2, 0, True)
            st.audio(j_v.export(io.BytesIO(), format="mp3"))
            os.remove("j.mp3")
        except Exception as e:
            st.error(f"Jarvis Error: {e}")

with tab5:
    st.subheader("🎨 AI Image Generator")
    prompt = st.text_input("Tasveer ka idea likhein (English):", key="img_prompt")
    if st.button("Generate Image"):
        if prompt:
            with st.spinner("AI Tasveer bana raha hai..."):
                image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
                st.image(image_url, use_container_width=True)
                r = requests.get(image_url)
                st.download_button("⬇️ Download Image", r.content, "ai_image.jpg")


