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

# --- Streamlit Secrets & Session Logic ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        client = Groq(api_key=st.session_state.api_key)
except Exception:
    st.sidebar.warning("⚠️ Groq Key missig!")

# --- Professional Audio Engine ---
def apply_pro_effects(audio_segment, pitch_val, echo_val, speed_val):
    try:
        # Talk Speed
        if speed_val != 0:
            new_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
        
        # Voice Depth (Pitch) - Spotify Style
        if pitch_val != 0:
            new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
            
        # Reverb (Echo)
        if echo_val > 0:
            delay = 150 
            echo = audio_segment - (30 - echo_val)
            audio_segment = audio_segment.overlay(echo, position=delay)
            
        # Mastering: Normalize for clean sound
        audio_segment = effects.normalize(audio_segment)
        return audio_segment
    except Exception:
        return audio_segment

# --- Sidebar (Error-Proof Sliders) ---
st.sidebar.header("🔑 Settings & Pro Audio")
with st.sidebar.expander("API Key Management"):
    new_k = st.text_input("Manual Key:", type="password")
    if st.button("Update"):
        st.session_state.api_key = new_k

st.sidebar.divider()

# Sliders FIX: Options aur Value strictly matched
p_val = st.sidebar.select_slider("Voice Depth (Pitch):", options=[-10, -5, 0, 5, 10], value=-5)
e_val = st.sidebar.slider("Reverb (Echo):", 0, 5, 1)
s_val = st.sidebar.select_slider("Talk Speed:", options=[-10, 0, 10, 20], value=0)

voices = {
    "👦 Male": "hi-IN-MadhurNeural",
    "👧 Female": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male": "ur-PK-AsadNeural",
    "🎙️ Movie Narrator": "en-US-GuyNeural"
}

# --- Main Tabs (All features restored) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

# --- TAB 1: Bulk TTS ---
with tab1:
    st.subheader("✍️ Bulk Text to Speech (Parts separated by ---)")
    script = st.text_area("Script Likhein (e.g., Hello Boss --- Welcome):", height=200)
    v_choice = st.radio("Voice Style Select Karein:", list(voices.keys()), horizontal=True)
    
    if st.button("Generate TTS"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Processing Part {i+1}..."):
                    communicate = edge_tts.Communicate(p_text, voices[v_choice])
                    asyncio.run(communicate.save(f"part_{i}.mp3"))
                    
                    raw_audio = AudioSegment.from_file(f"part_{i}.mp3")
                    final_audio = apply_pro_effects(raw_audio, p_val, e_val, s_val)
                    
                    st.audio(final_audio.export(io.BytesIO(), format="mp3"))
                    os.remove(f"part_{i}.mp3")

# --- TAB 2: Dialogue Mixer ---
with tab2:
    st.subheader("👥 Multi-Voice Dialogue Mixer")
    st.info("Line 1 Male, Line 2 Female (Separated by ---)")
    mix_script = st.text_area("Dialogues Likhein:", placeholder="e.g., Kahan ja rahe ho? --- Gher ja rahi hun!")
    
    if st.button("Mix Dialogues"):
        if mix_script:
            lines = [l.strip() for l in mix_script.split("---") if l.strip()]
            combined = AudioSegment.empty()
            for idx, line in enumerate(lines):
                # Alternate between Male and Female
                vid = voices["👦 Male"] if idx % 2 == 0 else voices["👧 Female"]
                communicate = edge_tts.Communicate(line, vid)
                asyncio.run(communicate.save("mix.mp3"))
                segment = apply_pro_effects(AudioSegment.from_file("mix.mp3"), p_val, e_val, s_val)
                combined += segment + AudioSegment.silent(duration=500)
                os.remove("mix.mp3")
            st.audio(combined.export(io.BytesIO(), format="mp3"))

# --- TAB 3: Audio Editor ---
with tab3:
    st.subheader("📁 Pro Effects Editor")
    up_file = st.file_uploader("Audio File Upload Karein:", type=["mp3", "wav"])
    if up_file and st.button("Apply Sidebar Effects"):
        raw_ed = AudioSegment.from_file(up_file)
        final_ed = apply_pro_effects(raw_ed, p_val, e_val, s_val)
        st.audio(final_ed.export(io.BytesIO(), format="mp3"))

# --- TAB 4: JARVIS (Speech & Art Ability restored) ---
with tab4:
    st.subheader("🤖 Jarvis Assistant (Updated Pro Model)")
    j_voice_type = st.selectbox("Jarvis Voice Chunain:", ["Narrator (Deep)", "Urdu Male Professional", "Standard Male Hindi"])
    j_v_map = {"Narrator (Deep)": "en-US-GuyNeural", "Urdu Male Professional": "ur-PK-AsadNeural", "Standard Male Hindi": "hi-IN-MadhurNeural"}

    user_query = st.text_input("Ask Jarvis:", key="jarvis_v3_final")
    
    # System Prompt for Art Gen Logic
    sys_instruction = "You are Jarvis. Speak Roman Urdu beautifully. If Boss asks to create an image, reply with text first, then end with 'AI_IMAGE_PROMPT: (precise English description)'."

    if st.button("Submit Order"):
        if user_query:
            try:
                chat_res = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_instruction}, {"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile",
                )
                full_ans = chat_res.choices[0].message.content
                
                # Split text and image prompt
                text_ans = full_ans.split("AI_IMAGE_PROMPT:")[0]
                st.write(f"🤖 **Jarvis:** {text_ans}")
                
                # Audio with Pro Mastering
                communicate = edge_tts.Communicate(text_ans, j_v_map[j_voice_type])
                asyncio.run(communicate.save("j.mp3"))
                j_raw = AudioSegment.from_file("j.mp3")
                # Pitch -5 se robotic awaz khatam ho jayegi
                j_final = apply_pro_effects(j_raw, p_val, e_val, s_val)
                st.audio(j_final.export(io.BytesIO(), format="mp3"))
                os.remove("j.mp3")
                
                # Image Logic
                if "AI_IMAGE_PROMPT:" in full_ans:
                    with st.spinner("AI Art bana raha hai..."):
                        img_prompt = full_ans.split("AI_IMAGE_PROMPT:")[1].strip()
                        img_url = f"https://pollinations.ai/p/{img_prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
                        st.image(img_url, caption="Jarvis Generated Art", use_container_width=True)
                        img_data = requests.get(img_url).content
                        st.download_button("⬇️ Download Art", img_data, "jarvis_art.jpg")
                        
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 5: Image Generation (Direct Mode restored) ---
with tab5:
    st.subheader("🎨 Direct AI Image Gen")
    p_direct = st.text_input("Tasveer ka idea likhein (English):", key="img_v3_final")
    if st.button("Generate Image"):
        if p_direct:
            with st.spinner("AI Tasveer bana raha hai..."):
                url_direct = f"https://pollinations.ai/p/{p_direct.replace(' ', '%20')}?width=1024&height=1024&model=flux"
                st.image(url_direct, use_container_width=True)
                img_data_direct = requests.get(url_direct).content
                st.download_button("⬇️ Download Image", img_data_direct, "ai_image.jpg")

