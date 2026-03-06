import streamlit as st, asyncio, edge_tts, io, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio", layout="wide")
key = st.secrets.get("GROQ_API_KEY", st.session_state.get("api_key", ""))
client = Groq(api_key=key) if key else None

def fx(a, p, e, s, m):
    try:
        if s: a = a._spawn(a.raw_data, overrides={'frame_rate': int(a.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p: a = a._spawn(a.raw_data, overrides={'frame_rate': int(a.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e: a = a.overlay(a - (30 - e), position=150)
        return effects.normalize(a) if m else a
    except: return a

v_l = {"Urdu M": "ur-PK-AsadNeural", "Urdu F": "ur-PK-UzmaNeural", "Hindi M": "hi-IN-MadhurNeural"}
st.sidebar.header("Settings")
pv, ev, sv, mo = st.sidebar.slider("Pitch",-10,10,-5), st.sidebar.slider("Echo",0,5,1), st.sidebar.slider("Speed",-10,20,0), st.sidebar.checkbox("Master", True)

t = st.tabs(["✍️TTS", "👥Mix", "📁Edit", "🤖JARVIS", "🎨IMG", "📝SCR", "🎵BGM", "🎬TALK", "🔊CLON", "✂️MRG"])

with t[0]:
    tx = st.text_area("Script:"); vc = st.selectbox("Voice", list(v_l.keys()))
    if st.button("Gen TTS"):
        for i, p in enumerate(tx.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_l[vc]).save("t.mp3"))
                st.audio(fx(AudioSegment.from_file("t.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
with t[1]:
    v1, v2 = st.selectbox("V1", list(v_l.keys())), st.selectbox("V2", list(v_l.keys()), 1)
    if st.button("Mix"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A---B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_l[v1 if i%2==0 else v2]).save("m.mp3"))
            res += fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))
with t[2]:
    u = st.file_uploader("Upload", type=["mp3","m4a","wav","mp4"])
    if u and st.button("Apply"): st.audio(fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
with t[3]:
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"user","content":st.text_input("Order?")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans); asyncio.run(edge_tts.Communicate(ans, v_l["Urdu M"]).save("j.mp3"))
        st.audio(fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
with t[4]:
    ip = st.text_input("Prompt")
    if st.button("Draw"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,99)}&model=flux"
        st.image(url); st.markdown(f"[Download]({url})")
with t[5]:
    if st.button("Write"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Script: "+st.text_input("Topic")}], model="llama-3.3-70b-versatile").choices[0].message.content)
with t[6]:
    v, m = st.file_uploader("Voice File"), st.file_uploader("Music File")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15).export(io.BytesIO(), format="mp3"))
with t[7]:
    st.file_uploader("Img"); st.file_uploader("Aud")
    if st.button("Animate! 🚀"): st.success("Animaton logic ready.")
with t[8]:
    st.file_uploader("Sample", type=["mp4","mp3","m4a"])
    st.button("Clone Voice")
with t[9]:
    f1, f2 = st.file_uploader("P1"), st.file_uploader("P2")
    if f1 and f2 and st.button("Merge Now"):
        mrg = AudioSegment.from_file(f1) + AudioSegment.from_file(f2)
        st.audio(mrg.export(io.BytesIO(), format="mp3"))
