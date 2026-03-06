# ... (Baki purana code waisa hi rahega, bas Jarvis wala hissa update kiya hai) ...

with tab4:
    st.subheader("🤖 Jarvis: Script Writer & Assistant")
    st.info("Jarvis se kahein: 'Ek horror story ki script likho' ya 'YouTube video ka intro likho'.")
    
    # Input area for user
    user_query = st.text_area("Jarvis ko Order dein:", placeholder="Boss, aaj kya likhna hai?")
    
    if st.button("Order Jarvis"):
        if user_query:
            try:
                # Groq AI Response (Llama 3)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are Jarvis, a professional script writer and AI assistant. When asked for a script, provide a detailed and creative script. Speak in Roman Urdu/Hindi. Call the user 'Boss'."},
                        {"role": "user", "content": user_query}
                    ],
                    model="llama3-8b-8192",
                )
                reply_text = chat_completion.choices[0].message.content
                
                # Show the Script/Response in a Text Box so it's easy to copy
                st.success("Jarvis ne Script taiyar kar di hai:")
                st.text_area("Copy your script from here:", value=reply_text, height=300)
                
                # Jarvis Voice Output (Brief summary)
                with st.spinner("Jarvis is speaking..."):
                    short_reply = "Boss, maine aapki script niche likh di hai. Aap ise copy kar sakte hain."
                    communicate = edge_tts.Communicate(short_reply, "hi-IN-MadhurNeural")
                    asyncio.run(communicate.save("j_voice.mp3"))
                    
                    # Professional Jarvis Tone
                    j_audio = apply_audio_effects(AudioSegment.from_file("j_voice.mp3"), -12, 2, 0, True)
                    st.audio(j_audio.export(io.BytesIO(), format="mp3"))
                    os.remove("j_voice.mp3")
            
            except Exception as e:
                st.error(f"Error: {e}")
