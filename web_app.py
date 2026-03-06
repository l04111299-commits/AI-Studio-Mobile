import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests

st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- Initialize Session State for API Key ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Sidebar for Key Entry
with st.sidebar:
    st.header("🔑 API Settings")
    key_input = st.text_input("Groq API Key (If not in Secrets):", value=st.session_state.api_key, type="password")
    if st.button("Update Key"):
        st.session_state.api_key = key_input
        st.success("Key updated for this session!")

# Initialize Groq Client
try:
    # First try secrets, then session state
    client_key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
    client = Groq(api_key=client_key)
except:
    st.error("Groq Key setup karein, Boss!")

# --- Audio Engine (Spotify-Style Mastering) ---
def apply_audio_effects(audio_segment, pitch_val, echo_val, speed_val):
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
            delay = 150 
            echo = audio_segment - (30 - echo_val)
            audio_segment = audio_segment.overlay(echo, position=delay)
        
        # Pro Mastering Effects: Normalize
        audio_segment = effects.normalize(audio_segment)
        return audio_segment
    except Exception as e:
        return audio_segment

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Sound Controls")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari Voice):", options=[-15, -10, 0, 10, 15], value=-5)
echo = st.sidebar.slider("Echo Level:", 0, 10, 1)

voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🎙️ Movie Narrator (Deep)": "en-US-GuyNeural"
}

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

# --- TAB 1: Bulk TTS (Fixed for Part Division) ---
with tab1:
    st.subheader("✍️ Bulk Text to Speech (Parts separated by ---)")
    script = st.text_area("Script Likhein (Part divide karne ke liye --- use karein):", height=200)
    v_choice = st.radio("Voice Style Select Karein:", list(voices.keys()), horizontal=True)
    
    if st.button("Generate TTS"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Processing Part {i+1}..."):
                    communicate = edge_tts.Communicate(p_text, voices[v_choice])
                    asyncio.run(communicate.save(f"part_{i}.mp3"))
                    
                    raw_audio = AudioSegment.from_file(f"part_{i}.mp3")
                    final_audio = apply_audio_effects(raw_audio, pitch, echo, speed)
                    
                    st.audio(final_audio.export(io.BytesIO(), format="mp3"))
                    os.remove(f"part_{i}.mp3")

# --- TAB 4: JARVIS AI (Updated for Image Generation) ---
with tab4:
    st.subheader("🤖 Jarvis Assistant (Speech & Image Gen)")
    user_q = st.text_input("Ask Jarvis:", key="j_input_image")
    
    # System Prompt for Image Gen Logic
    system_instruction = """You are Jarvis. Speak Roman Urdu. Call user Boss. 
    If user asks to 'create', 'generate' or 'make' an image/photo of something, 
    your response MUST contain the phrase 'AI_IMAGE_PROMPT:' followed by the precise English 
    description of the image to generate. 
    Do not generate image prompts for other requests."""

    if st.button("Submit Order"):
        if user_q:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction},
                              {"role": "user", "content": user_q}],
                    model="llama-3.3-70b-versatile",
                )
                ans = chat_completion.choices[0].message.content
                
                # --- AUDIO OUTPUT (Pehle Jarvis Bolega) ---
                # Remove image prompt part from audio answer
                audio_ans = ans.split("AI_IMAGE_PROMPT:")[0]
                st.write(f"🤖 **Jarvis:** {audio_ans}")
                communicate = edge_tts.Communicate(audio_ans, "hi-IN-MadhurNeural")
                asyncio.run(communicate.save("j.mp3"))
                j_v = apply_audio_effects(AudioSegment.from_file("j.mp3"), -5, 1, 0)
                st.audio(j_v.export(io.BytesIO(), format="mp3"))
                os.remove("j.mp3")
                
                # --- IMAGE OUTPUT (Agar prompt mili) ---
                if "AI_IMAGE_PROMPT:" in ans:
                    with st.spinner("Boss, AI Tasveer bana raha hai..."):
                        image_prompt = ans.split("AI_IMAGE_PROMPT:")[1].strip()
                        
                        # Use Pollinations AI for free generation
                        image_url = f"https://pollinations.ai/p/{image_prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
                        
                        # Display and Download button
                        st.image(image_url, caption=f"Style: Generated from your idea", use_container_width=True)
                        img_data = requests.get(image_url).content
                        st.download_button("⬇️ Download Image", img_data, "jarvis_generated.jpg")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- TAB 5: Image Generation (Direct Mode) ---
with tab5:
    st.subheader("🎨 Direct AI Image Gen")
    prompt = st.text_input("Tasveer ka idea likhein (English):", key="img_prompt")
    if st.button("Generate Image"):
        if prompt:
            with st.spinner("AI Tasveer bana raha hai..."):
                url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&model=flux"
                st.image(url, use_container_width=True)
                img_data = requests.get(url).content
                st.download_button("⬇️ Download Image", img_data, "ai_image.jpg")
