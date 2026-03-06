import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))import streamlit as st, asyncio, edge_tts, io, os, re, random
from pydub import AudioSegment, effects
from groq import Groq

st.set_page_config(page_title="AI Studio Pro", layout="wide")
key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.session_state.get("api_key", "")
client = Groq(api_key=key) if key else None

def apply_fx(audio, p, e, s, m):
    try:
        if s != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (1 + s/100))}).set_frame_rate(44100)
        if p != 0: audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * (2.0 ** (p/12.0)))}).set_frame_rate(44100)
        if e > 0: audio = audio.overlay(audio - (30 - e), position=150)
        return effects.normalize(audio) if m else audio
    except: return audio

v_lib = {"🇵🇰 Urdu Male": "ur-PK-AsadNeural", "🇵🇰 Urdu Female": "ur-PK-UzmaNeural", "🇮🇳 Hindi Male": "hi-IN-MadhurNeural", "🇺🇸 US Male": "en-US-GuyNeural", "🎭 Movie": "en-AU-WilliamNeural"}

st.sidebar.header("🎚️ Settings")
pv, ev, sv = st.sidebar.slider("Pitch", -10, 10, -5), st.sidebar.slider("Echo", 0, 5, 1), st.sidebar.slider("Speed", -10, 20, 0)
mo = st.sidebar.checkbox("Mastering", True)

t = st.tabs(["✍️ TTS", "👥 Mixer", "📁 Editor", "🤖 JARVIS", "🎨 IMAGE", "📝 SCRIPT", "🎵 BGM", "🎬 TALK", "🔊 CLONE", "✂️ MERGE"])

with t[0]:
    txt = st.text_area("Script:"); vc = st.selectbox("Voice:", list(v_lib.keys()))
    if st.button("Generate"):
        for i, p in enumerate(txt.split("---")):
            if p.strip():
                asyncio.run(edge_tts.Communicate(p, v_lib[vc]).save(f"{i}.mp3"))
                st.audio(apply_fx(AudioSegment.from_file(f"{i}.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[1]:
    v1, v2 = st.selectbox("Voice A:", list(v_lib.keys()), 0), st.selectbox("Voice B:", list(v_lib.keys()), 1)
    if st.button("Mix Dialogue"):
        res = AudioSegment.empty()
        for i, l in enumerate(st.text_area("A --- B").split("---")):
            asyncio.run(edge_tts.Communicate(l, v_lib[v1 if i%2==0 else v2]).save("m.mp3"))
            res += apply_fx(AudioSegment.from_file("m.mp3"), pv, ev, sv, mo) + AudioSegment.silent(500)
        st.audio(res.export(io.BytesIO(), format="mp3"))

with t[2]:
    u = st.file_uploader("Upload (MP3, M4A, WAV, MP4):", type=["mp3", "m4a", "wav", "mp4"])
    if u and st.button("Fix Audio"): st.audio(apply_fx(AudioSegment.from_file(u), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))

with t[3]:
    jv = st.selectbox("Jarvis Voice:", list(v_lib.keys()))
    if st.button("Ask Jarvis"):
        ans = client.chat.completions.create(messages=[{"role":"system","content":"Speak Roman Urdu. Image: AI_IMAGE_PROMPT: (English)"},{"role":"user","content":st.text_input("Order? ")}], model="llama-3.3-70b-versatile").choices[0].message.content
        st.write(ans.split('AI_IMAGE_PROMPT:')[0])
        asyncio.run(edge_tts.Communicate(ans.split('AI_IMAGE_PROMPT:')[0], v_lib[jv]).save("j.mp3"))
        st.audio(apply_fx(AudioSegment.from_file("j.mp3"), pv, ev, sv, mo).export(io.BytesIO(), format="mp3"))
        if "AI_IMAGE_PROMPT:" in ans: st.image(f"https://pollinations.ai/p/{re.sub(r'[^a-zA-Z]','',ans.split('AI_IMAGE_PROMPT:')[1])}?width=1024&height=1024&model=flux")

with t[4]:
    ip = st.text_input("Idea (English):")
    if st.button("Generate Art"):
        url = f"https://pollinations.ai/p/{ip.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        st.image(url); st.markdown(f"[📥 Download]({url})")

with t[5]:
    if st.button("Write Script"): st.write(client.chat.completions.create(messages=[{"role":"user","content":"Write Roman Urdu script: "+st.text_input("Topic:")}], model="llama-3.3-70b-versatile").choices[0].message.content)

with t[6]:
    v, m = st.file_uploader("Voice:"), st.file_uploader("Music:")
    if v and m and st.button("Mix BGM"): st.audio(AudioSegment.from_file(v).overlay(AudioSegment.from_file(m)-15, loop=True).export(io.BytesIO(), format="mp3"))

with t[7]:
    st.file_uploader("Img:"), st.file_uploader("Aud:")
    if st.button("Animate! 🚀"): st.success("Processing started...")

with t[8]:
    st.file_uploader("Sample (MP4/MP3):", type=["mp3", "mp4", "m4a", "wav"])
    st.button("Clone Voice")

with t[9]:
    f1, f2 = st.file_uploader("Part 1:"), st.file_uploader("Part 2:")
    if f1 and f2 and st.button("Merge"): st.audio((AudioSegment.from_file(f1)+AudioSegment.from_file(f2)).export(io.BytesIO(), format="mp3"))
