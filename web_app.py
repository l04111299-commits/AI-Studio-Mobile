import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq
import requests

# --- Page Config ---
st.set_page_config(page_title="AI Mega Studio Pro", page_icon="🎙️", layout="wide")

# --- Streamlit Secrets & API Logic ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        client = Groq(api_key=st.session_state.api_key)
except Exception:
    st.error("API Key ka masla hai. Secrets check karein.")

# --- Professional Audio Engine ---
def apply_pro_effects(audio_segment, pitch_val, echo_val, speed_val):
    try:
        # Speed Adjustment
        if speed_val != 0:
            new_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
        
        # Pitch for Spotify-Style Depth
        if pitch_val != 0:
            new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
            
        # Echo/Reverb
        if echo_val > 0:
            delay = 150 
            echo = audio_segment - (30 - echo_val)
            audio_segment = audio_segment.overlay(echo, position=delay)
            
        # Mastering: Normalize makes it sound clean
        audio_segment = effects.normalize(audio_segment)
        return audio_segment
    except Exception:
        return audio_segment

# --- Sidebar (Pro Controls) ---
st.sidebar.header("🎚️ Pro Audio Controls")
p_val = st.sidebar.select_slider("Voice Depth (Pitch):", options=[-10, -5, 0, 5, 10], value=-5)
e_val = st.sidebar.slider("Reverb (Echo):", 0, 5, 1)
s_val = st.sidebar.select_slider("Talk Speed:", options=[-10, 0, 10, 20], value=0)

voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🎙️ Movie Narrator": "en-US-GuyNeural"
}

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

# --- TAB 1: TTS (Text to Speech) ---
with tab1:
    st.subheader("✍️ Bulk TTS Generator")
    script = st.text_area("Script Likhein (Part divide karne ke liye --- use karein):", height=200)
    v_choice = st.radio("Voice Style Select Karein:", list(voices.keys()), horizontal=True)
    
    if st.button("Generate TTS"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Processing Part {i+1}..."):
                    communicate = edge_tts.Communicate(p_text, voices[v_choice])
                    asyncio.run(communicate.save(f"part_{i}.mp3"))
                    raw = AudioSegment.from_file(f"part_{i}.mp3")
                    final = apply_pro_effects(raw, p_val, e_val, s_val)
                    st.audio(final.export(io.BytesIO(), format="mp3"), format="audio/mp3")
                    os.remove(f"part_{i}.mp3")

# --- TAB 2: Dialogue Mixer ---
with tab2:
    st.subheader("👥 Multi-Voice Dialogue Mixer")
    st.info("Line 1 Male ki hogi, Line 2 Female ki (Separated by ---)")
    mix_script = st.text_area("Dialogue Lines:", placeholder="Line 1 --- Line 2 --- Line 3")
    
    if st.button("Mix Dialogues"):
        if mix_script:
            lines = [l.strip() for l in mix_script.split("---") if l.strip()]
            combined = AudioSegment.empty()
            for idx, line in enumerate(lines):
                # Alternate between Male and Female
                vid = voices["👦 Male (Madhur)"] if idx % 2 == 0 else voices["👧 Female (Swara)"]
                communicate = edge_tts.Communicate(line, vid)
                asyncio.run(communicate.save("mix.mp3"))
                segment = apply_pro_effects(AudioSegment.from_file("mix.mp3"), p_val, e_val, s_val)
                combined += segment + AudioSegment.silent(duration=500)
                os.remove("mix.mp3")
            st.audio(combined.export(io.BytesIO(), format="mp3"))

# --- TAB 3: Editor ---
with tab3:
    st.subheader("📁 Audio Effects Editor")
    up = st.file_uploader("Apni Audio File Upload Karein:", type=["mp3", "wav"])
    if up and st.button("Apply Sidebar Effects"):
        processed = apply_pro_effects(AudioSegment.from_file(up), p_val, e_val, s_val)
        st.audio(processed.export(io.BytesIO(), format="mp3"))

# --- TAB 4: Jarvis AI ---
with tab4:
    st.subheader("🤖 Jarvis Assistant (Pro Mode)")
    voice_type = st.selectbox("Jarvis Voice Style:", ["Movie Narrator (Deep)", "Urdu Professional", "Standard Hindi"])
    v_map = {"Movie Narrator (Deep)": "en-US-GuyNeural", "Urdu Professional": "ur-PK-AsadNeural", "Standard Hindi": "hi-IN-MadhurNeural"}

    user_query = st.text_input("Talk to Jarvis:", key="jarvis_v3")
    if st.button("Submit Order"):
        if user_query:
            try:
                key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.api_key
                active_client = Groq(api_key=key)
                res = active_client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are Jarvis. Speak Roman Urdu. Call user Boss."},
                              {"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile",
                )
                answer = res.choices[0].message.content
                st.write(f"🤖 **Jarvis:** {answer}")
                
                vid = v_map[voice_type]
                communicate = edge_tts.Communicate(answer, vid)
                asyncio.run(communicate.save("j.mp3"))
                j_raw = AudioSegment.from_file("j.mp3")
                j_final = apply_pro_effects(j_raw, p_val, e_val, s_val)
                st.audio(j_final.export(io.BytesIO(), format="mp3"))
                os.remove("j.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 5: Image Generation ---
with tab5:
    st.subheader("🎨 AI Image Generation")
    prompt = st.text_input("Tasveer ka idea likhein (English):", key="img_v3")
    if st.button("Generate Image"):
        if prompt:
            with st.spinner("AI Tasveer bana raha hai..."):
                img_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&model=flux"
                st.image(img_url, use_container_width=True)
                img_data = requests.get(img_url).content
                st.download_button("⬇️ Download Image", img_data, "ai_generated.jpg")







