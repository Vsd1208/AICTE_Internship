import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from io import BytesIO
import json

# Ensure streamlit_audio_recorder is installed before importing
import subprocess
import sys
try:
    from streamlit_audio_recorder import st_audio_recorder  # type: ignore
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "git+https://github.com/stefanrmmr/streamlit_audio_recorder.git"
        ])
        from streamlit_audio_recorder import st_audio_recorder  # type: ignore
        AUDIO_RECORDER_AVAILABLE = True
    except Exception:
        AUDIO_RECORDER_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Lecture Voice-to-Notes Generator",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .quiz-question {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .flashcard {
        background-color: #fff9e6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'notes' not in st.session_state:
    st.session_state.notes = ""
if 'quiz' not in st.session_state:
    st.session_state.quiz = []
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []

# Header
st.markdown('<div class="main-header">🎓 Lecture Voice-to-Notes Generator</div>', unsafe_allow_html=True)
st.markdown("Convert your lecture recordings into comprehensive study materials!")

# Sidebar for API Key
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", value="AIzaSyBC331qIx_dkg-0N2O1EN2SZTCFGvuro0k", type="password", help="Get your API key from Google AI Studio")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")
    
    st.markdown("---")
    st.markdown("### 📖 How to Use:")
    st.markdown("""
    1. Enter your Gemini API key
    2. Upload an audio file or record live
    3. Transcribe the audio
    4. Generate notes, quizzes, or flashcards
    """)
    
    st.markdown("---")
    st.markdown("### 🔑 Get API Key:")
    st.markdown("[Google AI Studio](https://makersuite.google.com/app/apikey)")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🎤 Record/Upload", "📝 Notes", "📋 Quiz", "🗂️ Flashcards"])

with tab1:
    st.markdown('<div class="section-header">Audio Input</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Audio File")
        uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a', 'ogg', 'flac'])
        
        if uploaded_file:
            st.audio(uploaded_file, format='audio/wav')
            
            if st.button("🎯 Transcribe Uploaded Audio"):
                if not api_key:
                    st.error("Please enter your Gemini API key in the sidebar!")
                else:
                    with st.spinner("Transcribing audio..."):
                        try:
                            # Save uploaded file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name
                            
                            # Convert to WAV if needed
                            audio = AudioSegment.from_file(tmp_path)
                            base, _ = os.path.splitext(tmp_path)
                            wav_path = base + '.wav'
                            audio.export(wav_path, format='wav')
                            
                            # Transcribe using speech recognition
                            recognizer = sr.Recognizer()
                            with sr.AudioFile(wav_path) as source:
                                audio_data = recognizer.record(source)
                                text = recognizer.recognize_google(audio_data)
                                st.session_state.transcribed_text = text
                            
                            # Cleanup
                            os.unlink(wav_path)
                            st.success("✅ Transcription complete!")
                        except Exception as e:
                            st.error(f"Error during transcription: {str(e)}")
    with col2:
        st.subheader("Or Record Audio Live")
        if AUDIO_RECORDER_AVAILABLE:
            audio_bytes = st_audio_recorder(
                pause_threshold=2.0,
                sample_rate=16000,
                key="audio_recorder"
            )
            
            if audio_bytes is not None and len(audio_bytes) > 0:
                st.audio(audio_bytes, format="audio/wav")
                if st.button("🎯 Transcribe Recorded Audio"):
                    if not api_key:
                        st.error("Please enter your Gemini API key in the sidebar!")
                    else:
                        with st.spinner("Transcribing audio..."):
                            try:
                                # Save recorded audio to temp file
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                    tmp_file.write(audio_bytes)
                                    wav_path = tmp_file.name
                            
                                # Transcribe using speech recognition
                                recognizer = sr.Recognizer()
                                with sr.AudioFile(wav_path) as source:
                                    audio_data = recognizer.record(source)
                                    text = recognizer.recognize_google(audio_data)
                                    st.session_state.transcribed_text = text
                            
                                # Cleanup
                                os.unlink(wav_path)
                                st.success("✅ Transcription complete!")
                            except Exception as e:
                                st.error(f"Error during transcription: {str(e)}")
            else:
                st.warning("Press the microphone button above to record your audio.")
    
    # Display transcribed text
    if st.session_state.transcribed_text:
        st.markdown('<div class="section-header">Transcribed Text</div>', unsafe_allow_html=True)
        st.text_area("", st.session_state.transcribed_text, height=200, key="transcript_display")
        
        # Option to edit transcribed text
        edited_text = st.text_area("Edit transcription if needed:", st.session_state.transcribed_text, height=150)
        if st.button("💾 Save Edited Text"):
            st.session_state.transcribed_text = edited_text
            st.success("Text updated!")

with tab2:
    st.markdown('<div class="section-header">Generated Study Notes</div>', unsafe_allow_html=True)
    
    if not st.session_state.transcribed_text:
        st.warning("⚠️ Please transcribe audio first in the Record/Upload tab!")
    else:
        if not st.session_state.get("detailed_summary") or not st.session_state.get("bullet_points"):
            if not api_key:
                st.error("Please enter your Gemini API key in the sidebar!")
            else:
                with st.spinner("Generating notes..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        # Generate Detailed Summary
                        prompt_summary = f"""
                        Convert the following lecture transcript into a detailed summary.
                        Make sure to:
                        - Identify key concepts and main ideas
                        - Organize information logically
                        - Highlight important terms and definitions
                        - Include examples if mentioned
                        - Make it easy to study from

                        Transcript:
                        {st.session_state.transcribed_text}
                        """
                        response_summary = model.generate_content(prompt_summary)
                        st.session_state.detailed_summary = response_summary.text
                        
                        # Generate Bullet Points
                        prompt_bullets = f"""
                        Convert the following lecture transcript into concise bullet points.
                        Make sure to:
                        - List key concepts and main ideas
                        - Use clear, short sentences
                        - Highlight important terms and definitions
                        - Include examples if mentioned

                        Transcript:
                        {st.session_state.transcribed_text}
                        """
                        response_bullets = model.generate_content(prompt_bullets)
                        st.session_state.bullet_points = response_bullets.text

                    except Exception as e:
                        st.error(f"Error generating notes: {str(e)}")
        
        if st.session_state.get("detailed_summary"):
            st.markdown("### 📄 Detailed Summary")
            st.markdown(st.session_state.detailed_summary)
            st.download_button(
                label="📥 Download Detailed Summary",
                data=st.session_state.detailed_summary,
                file_name="detailed_summary.txt",
                mime="text/plain"
            )
        if st.session_state.get("bullet_points"):
            st.markdown("### • Bullet Points")
            st.markdown(st.session_state.bullet_points)
            st.download_button(
                label="📥 Download Bullet Points",
                data=st.session_state.bullet_points,
                file_name="bullet_points.txt",
                mime="text/plain"
            )

with tab3:
    st.markdown('<div class="section-header">Generate Quiz</div>', unsafe_allow_html=True)
    
    if not st.session_state.transcribed_text:
        st.warning("⚠️ Please transcribe audio first in the Record/Upload tab!")
    else:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            num_questions = st.slider("Number of questions:", 3, 10, 5)
        with col2:
            difficulty = st.select_slider(
                "Difficulty level:",
                options=["Easy", "Medium", "Hard"]
            )
        with col3:
            st.write("")
            st.write("")
            generate_quiz = st.button("📋 Generate Quiz")
        
        if generate_quiz:
            if not api_key:
                st.error("Please enter your Gemini API key in the sidebar!")
            else:
                with st.spinner("Generating quiz..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        prompt = f"""
                        Create a {difficulty.lower()} difficulty quiz with {num_questions} multiple-choice questions based on this lecture transcript.
                        
                        Format your response as a JSON array with this structure:
                        [
                            {{
                                "question": "Question text",
                                "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                                "correct_answer": "A",
                                "explanation": "Brief explanation"
                            }}
                        ]
                        
                        Transcript:
                        {st.session_state.transcribed_text}
                        
                        Return ONLY the JSON array, no other text.
                        """
                        
                        response = model.generate_content(prompt)
                        # Clean the response to get only JSON
                        response_text = response.text.strip()
                        if response_text.startswith("```json"):
                            response_text = response_text[7:]
                        if response_text.endswith("```"):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                        
                        st.session_state.quiz = json.loads(response_text)
                        
                    except Exception as e:
                        st.error(f"Error generating quiz: {str(e)}")
        
        if st.session_state.quiz:
            st.markdown("### 📝 Quiz Questions:")
            
            for i, q in enumerate(st.session_state.quiz):
                st.markdown(f'<div class="quiz-question">', unsafe_allow_html=True)
                st.markdown(f"**Question {i+1}:** {q['question']}")
                
                user_answer = st.radio(
                    "Select your answer:",
                    q['options'],
                    key=f"q_{i}"
                )
                
                if st.button(f"Check Answer", key=f"check_{i}"):
                    selected = user_answer[0] # Get letter (A, B, C, or D)
                    if selected == q['correct_answer']:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is {q['correct_answer']}")
                    st.info(f"💡 {q['explanation']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

with tab4:
    st.markdown('<div class="section-header">Generate Flashcards</div>', unsafe_allow_html=True)
    
    if not st.session_state.transcribed_text:
        st.warning("⚠️ Please transcribe audio first in the Record/Upload tab!")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            num_flashcards = st.slider("Number of flashcards:", 5, 20, 10)
        with col2:
            st.write("")
            st.write("")
            generate_flashcards = st.button("🗂️ Generate Flashcards")
        
        if generate_flashcards:
            if not api_key:
                st.error("Please enter your Gemini API key in the sidebar!")
            else:
                with st.spinner("Generating flashcards..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        prompt = f"""
                        Create {num_flashcards} flashcards based on this lecture transcript.
                        Each flashcard should have a question/term on the front and an answer/definition on the back.
                        
                        Format your response as a JSON array:
                        [
                            {{
                                "front": "Question or term",
                                "back": "Answer or definition"
                            }}
                        ]
                        
                        Transcript:
                        {st.session_state.transcribed_text}
                        
                        Return ONLY the JSON array, no other text.
                        """
                        
                        response = model.generate_content(prompt)
                        response_text = response.text.strip()
                        if response_text.startswith("```json"):
                            response_text = response_text[7:]
                        if response_text.endswith("```"):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                        
                        st.session_state.flashcards = json.loads(response_text)
                        
                    except Exception as e:
                        st.error(f"Error generating flashcards: {str(e)}")
        
        if st.session_state.flashcards:
            st.markdown("### 🗂️ Your Flashcards:")
            
            for i, card in enumerate(st.session_state.flashcards):
                with st.container():
                    st.markdown(f'<div class="flashcard">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Card {i+1}**")
                    with col2:
                        show_answer = st.checkbox("Show", key=f"card_{i}")
                    
                    st.markdown(f"**Q:** {card['front']}")
                    
                    if show_answer:
                        st.markdown(f"**A:** {card['back']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Export flashcards
            flashcard_text = "\n\n".join([
                f"Card {i+1}\nQ: {card['front']}\nA: {card['back']}"
                for i, card in enumerate(st.session_state.flashcards)
            ])
            
            st.download_button(
                label="📥 Download Flashcards",
                data=flashcard_text,
                file_name="flashcards.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with Streamlit and Google Gemini AI | Transform your lectures into effective study materials</p>
</div>
""", unsafe_allow_html=True)