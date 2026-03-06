import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
import webbrowser

st.set_page_config(page_title="AI Super Studio & Jarvis", page_icon="🎙️", layout="wide")

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

# --- Voice Database ---
voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🎙️ Movie Narrator": "en-US-GuyNeural"
}

# --- Sidebar Controls ---
st.sidebar.header("🎚️ Master Controls")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch:", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

# --- Main Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["✍️ TTS", "👥 Dialogue", "📁 Editor", "🤖 JARVIS AI"])

# --- TAB 4: JARVIS (New Feature) ---
with tab4:
    st.subheader("🤖 Jarvis Voice Assistant")
    st.write("Jarvis se baatein karein ya commands dein.")
    
    # Mobile par Speech recognition ke liye text input hi best hai
    user_input = st.text_input("Jarvis ko Order dein (e.g., 'Open YouTube' ya 'Kaise ho?'):")
    
    if st.button("Submit to Jarvis"):
        if user_input:
            query = user_input.lower()
            response_text = ""
            
            # 1. Automation Logic
            if "youtube" in query:
                response_text = "Boss, YouTube khul raha hai."
                st.markdown("[Click here to Open YouTube](https://www.youtube.com)")
            elif "google" in query:
                response_text = "Boss, Google open kar raha hoon."
                st.markdown("[Click here to Open Google](https://www.google.com)")
            elif "kaise ho" in query or "hello" in query:
                response_text = "Main bilkul theek hoon Boss, aap batayein main aapki kya madad kar sakta hoon?"
            else:
                response_text = f"Boss, aapne kaha: {user_input}. Main abhi is par kaam kar raha hoon."

            # 2. Jarvis Voice Output (Using edge-tts for Mobile)
            with st.spinner("Jarvis is thinking..."):
                communicate = edge_tts.Communicate(response_text, "hi-IN-MadhurNeural")
                temp_j = "jarvis_reply.mp3"
                asyncio.run(communicate.save(temp_j))
                
                # Apply Jarvis Voice Style (Bhari Voice)
                j_sound = AudioSegment.from_file(temp_j)
                j_proc = apply_audio_effects(j_sound, -12, 2, 0, True) # Fixed Jarvis style
                
                out_j = io.BytesIO()
                j_proc.export(out_io := io.BytesIO(), format="mp3")
                st.audio(out_io)
                st.write(f"🤖 Jarvis: {response_text}")
                os.remove(temp_j)

# --- (Baki Tab 1, 2, 3 ka purana code waisa hi rahega) ---
with tab1:
    script = st.text_area("TTS Script:")
    v_choice = st.selectbox("Voice:", list(voices.keys()))
    if st.button("Generate TTS"):
        if script:
            communicate = edge_tts.Communicate(script, voices[v_choice])
            asyncio.run(communicate.save("t.mp3"))
            s = apply_audio_effects(AudioSegment.from_file("t.mp3"), pitch, echo, speed, mastering)
            st.audio(s.export(io.BytesIO(), format="mp3"))

with tab2:
    st.write("Dialogue Mixer Feature Active.")
    # (Dialogue mixer logic yahan paste karein jo pehle di thi)

with tab3:
    up = st.file_uploader("Upload Audio")
    if up:
        s = apply_audio_effects(AudioSegment.from_file(up), pitch, echo, speed, mastering)
        st.audio(s.export(io.BytesIO(), format="mp3"))

