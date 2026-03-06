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

# --- Professional Audio Engine ---
def apply_pro_effects(audio_segment, pitch_val, echo_val, speed_val, is_mastering):
    try:
        # Talk Speed
        if speed_val != 0:
            new_rate = int(audio_segment.frame_rate * (1 + speed_val/100))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
        
        # Voice Depth (Pitch)
        if pitch_val != 0:
            new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_val / 12.0)))
            audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
            audio_segment = audio_segment.set_frame_rate(44100)
            
        # Reverb (Echo)
        if echo_val > 0:
            delay = 150 
            echo = audio_segment - (30 - echo_val)
            audio_segment = audio_segment.overlay(echo, position=delay)
            
        # --- AUTO MASTERING FEATURE (RESTORED) ---
        if is_mastering:
            audio_segment = effects.normalize(audio_segment)
        
        return audio_segment
    except Exception:
        return audio_segment

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Sound & API Controls")
with st.sidebar.expander("API Key Management"):
    new_k = st.text_input("Manual Key:", type="password")
    if st.button("Update Key"):
        st.session_state.api_key = new_k

st.sidebar.divider()

# Audio Sliders
p_val = st.sidebar.select_slider("Voice Depth (Pitch):", options=[-10, -5, 0, 5, 10], value=-5)
e_val = st.sidebar.slider("Reverb (Echo):", 0, 5, 1)
s_val = st.sidebar.select_slider("Talk Speed:", options=[-10, 0, 10, 20], value=0)

# Auto Mastering Checkbox (RESTORED)
mastering_on = st.sidebar.checkbox("Auto-Mastering (Clean Sound)", value=True)

voices = {
    "👦 Male": "hi-IN-MadhurNeural",
    "👧 Female": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male": "ur-PK-AsadNeural",
    "🎙️ Movie Narrator": "en-US-GuyNeural"
}

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS AI", "🎨 IMAGE GEN"])

# --- TAB 1: Bulk TTS ---
with tab1:
    st.subheader("✍️ Bulk Text to Speech")
    script = st.text_area("Script Likhein (Split with ---):", height=200, key="tts_f")
    v_choice = st.radio("Voice Style:", list(voices.keys()), horizontal=True)
    
    if st.button("Generate TTS", key="btn_tts"):
        if script:
            parts = [s.strip() for s in script.split("---") if s.strip()]
            for i, p_text in enumerate(parts):
                with st.spinner(f"Part {i+1} generating..."):
                    communicate = edge_tts.Communicate(p_text, voices[v_choice])
                    asyncio.run(communicate.save(f"t_{i}.mp3"))
                    raw = AudioSegment.from_file(f"t_{i}.mp3")
                    final = apply_pro_effects(raw, p_val, e_val, s_val, mastering_on)
                    st.audio(final.export(io.BytesIO(), format="mp3"))
                    os.remove(f"t_{i}.mp3")

# --- TAB 2: Dialogue Mixer ---
with tab2:
    st.subheader("👥 Multi-Voice Mixer")
    mix_script = st.text_area("Lines (Line 1 Male --- Line 2 Female):", key="mix_f")
    if st.button("Mix Voices", key="btn_mix"):
        lines = [l.strip() for l in mix_script.split("---") if l.strip()]
        combined = AudioSegment.empty()
        for idx, line in enumerate(lines):
            vid = voices["👦 Male"] if idx % 2 == 0 else voices["👧 Female"]
            communicate = edge_tts.Communicate(line, vid)
            asyncio.run(communicate.save("m.mp3"))
            segment = apply_pro_effects(AudioSegment.from_file("m.mp3"), p_val, e_val, s_val, mastering_on)
            combined += segment + AudioSegment.silent(duration=500)
            os.remove("m.mp3")
        st.audio(combined.export(io.BytesIO(), format="mp3"))

# --- TAB 3: Editor ---
with tab3:
    st.subheader("📁 Audio Effects Editor")
    up = st.file_uploader("Upload Audio:", type=["mp3", "wav"], key="edit_f")
    if up and st.button("Apply Effects", key="btn_edit"):
        processed = apply_pro_effects(AudioSegment.from_file(up), p_val, e_val, s_val, mastering_on)
        st.audio(processed.export(io.BytesIO(), format="mp3"))

# --- TAB 4: JARVIS AI (Speech & Image Gen) ---
with tab4:
    st.subheader("🤖 Jarvis Assistant (Speech & Art)")
    j_voice = st.selectbox("Jarvis Voice:", ["Narrator", "Urdu", "Hindi"], key="jv_f")
    j_map = {"Narrator": "en-US-GuyNeural", "Urdu": "ur-PK-AsadNeural", "Hindi": "hi-IN-MadhurNeural"}
    
    user_q = st.text_input("Ask Jarvis:", key="jq_f")
    sys_prompt = "You are Jarvis. Speak Roman Urdu. If Boss asks for an image, add 'AI_IMAGE_PROMPT: (English prompt)' at the end."

    if st.button("Submit", key="btn_j"):
        if user_q:
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_q}],
                model="llama-3.3-70b-versatile",
            )
            ans = res.choices[0].message.content
            text_only = ans.split("AI_IMAGE_PROMPT:")[0].strip()
            st.write(f"🤖 **Jarvis:** {text_only}")
            
            # Audio
            communicate = edge_tts.Communicate(text_only, j_map[j_voice])
            asyncio.run(communicate.save("j.mp3"))
            j_audio = apply_pro_effects(AudioSegment.from_file("j.mp3"), p_val, e_val, s_val, mastering_on)
            st.audio(j_audio.export(io.BytesIO(), format="mp3"))
            os.remove("j.mp3")
            
            # Image Gen
            if "AI_IMAGE_PROMPT:" in ans:
                img_p = re.sub(r'[^a-zA-Z0-9\s]', '', ans.split("AI_IMAGE_PROMPT:")[1])
                img_url = f"https://pollinations.ai/p/{img_p.replace(' ', '%20')}?width=1024&height=1024&model=flux"
                st.image(img_url, caption="Jarvis Art")
                st.download_button("Download", requests.get(img_url).content, "art.jpg", key="dl_j")

# --- TAB 5: Image Generation ---
with tab5:
    st.subheader("🎨 Direct Image Gen")
    p_direct = st.text_input("English Prompt:", key="id_f")
    if st.button("Generate Art", key="btn_id"):
        clean_p = re.sub(r'[^a-zA-Z0-9\s]', '', p_direct).replace(' ', '%20')
        url = f"https://pollinations.ai/p/{clean_p}?width=1024&height=1024&model=flux"
        st.image(url)
        st.download_button("Download", requests.get(url).content, "image.jpg", key="dl_id")


