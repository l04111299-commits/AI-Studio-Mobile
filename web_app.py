import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment, effects
import io
import os
from groq import Groq

# --- Groq Setup (Aapki API Key) ---
client = Groq(api_key="Gsk_uMvdF5TgK8Qxds9W3CceWGdyb3FY3Ji7jT3we7KL4f86Tmdno8hW")

st.set_page_config(page_title="AI Super Studio & Jarvis Pro", page_icon="🎙️", layout="wide")

# --- Audio Effects Engine ---
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
st.sidebar.header("🎚️ Master Sound Settings")
speed = st.sidebar.select_slider("Speed:", options=[-25, -15, 0, 10, 20], value=0)
pitch = st.sidebar.select_slider("Pitch (Bhari/Halki):", options=[-15, -10, 0, 10, 15], value=-10)
echo = st.sidebar.slider("Echo Level:", 0, 10, 3)
mastering = st.sidebar.checkbox("Auto-Mastering", value=True)

voices = {
    "👦 Male (Madhur)": "hi-IN-MadhurNeural",
    "👧 Female (Swara)": "hi-IN-SwaraNeural",
    "🇵🇰 Urdu Male (Asad)": "ur-PK-AsadNeural",
    "🇵🇰 Urdu Female (Uzma)": "ur-PK-UzmaNeural",
    "🎙️ Movie Narrator": "en-US-GuyNeural"
}

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["✍️ TTS", "👥 Dialogue Mixer", "📁 Editor", "🤖 JARVIS BRAIN"])

# --- TAB 1, 2, 3 (Pehle Wala Professional Code) ---
with tab1:
    script = st.text_area("Script Likhein (--- for Bulk):")
    v_choice = st.selectbox("Voice:", list(voices.keys()))
    if st.button("Generate TTS"):
        parts = [s.strip() for s in script.split("---") if s.strip()]
        for i, p_text in enumerate(parts):
            communicate = edge_tts.Communicate(p_text, voices[v_choice])
            asyncio.run(communicate.save(f"t_{i}.mp3"))
            s = apply_audio_effects(AudioSegment.from_file(f"t_{i}.mp3"), pitch, echo, speed, mastering)
            st.audio(s.export(io.BytesIO(), format="mp3"))
            os.remove(f"t_{i}.mp3")

# --- TAB 4: JARVIS (WITH GROQ AI BRAIN) ---
with tab4:
    st.subheader("🤖 Jarvis: Super AI Mode")
    st.info("Aap Roman Urdu ya English mein kuch bhi pooch sakte hain.")
    
    user_query = st.text_input("Jarvis se Baat Karein:", placeholder="Boss, main aapki kya madad karoon?")
    
    if st.button("Poochhen Jarvis se") or (user_query and st.session_state.get('last_query') != user_query):
        st.session_state['last_query'] = user_query
        
        if user_query:
            # 1. Groq AI Response (Llama 3)
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are Jarvis, a highly intelligent AI assistant. Speak in Roman Urdu/Hindi. Be brief, professional, and helpful. Call the user 'Boss'."},
                        {"role": "user", "content": user_query}
                    ],
                    model="llama3-8b-8192",
                )
                reply_text = chat_completion.choices[0].message.content
            except Exception as e:
                reply_text = "Boss, server mein thora masla hai, par main sun raha hoon."

            # 2. Automation Check (If user says YouTube etc)
            if "youtube" in user_query.lower():
                st.link_button("Open YouTube", "https://www.youtube.com")
            
            # 3. Jarvis Voice Output
            with st.spinner("Jarvis is speaking..."):
                communicate = edge_tts.Communicate(reply_text, "hi-IN-MadhurNeural")
                asyncio.run(communicate.save("j_reply.mp3"))
                
                # Jarvis ki signature bhari awaz
                j_audio = AudioSegment.from_file("j_reply.mp3")
                j_proc = apply_audio_effects(j_audio, -15, 2, 0, True) 
                
                st.audio(j_proc.export(io.BytesIO(), format="mp3"))
                st.write(f"🤖 **Jarvis:** {reply_text}")
                os.remove("j_reply.mp3")


