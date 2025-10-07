# 🎓 Lecture Voice-to-Notes Generator

Convert your lecture recordings or live audio into comprehensive study materials, including detailed summaries, bullet-point notes, multiple-choice quizzes, and flashcards, powered by the **Google Gemini API** and Streamlit.

## ✨ Features

* **Audio Transcription (Tab 1):** Upload audio files (`.wav`, `.mp3`, `.m4a`, etc.) or record audio live using your microphone. Uses Google's Speech Recognition for transcription.
* **Study Notes Generation (Tab 2):** Automatically generates a **Detailed Summary** and **Concise Bullet Points** from the transcribed lecture text.
* **Quiz Generation (Tab 3):** Creates customizable multiple-choice quizzes (3-10 questions) with adjustable difficulty levels (Easy, Medium, Hard).
* **Flashcard Generation (Tab 4):** Generates term/definition flashcards for effective memorization.
* **Export Functionality:** Download generated notes, quizzes, and flashcards as plain text files.
* **Interactive Review:** Check your answers instantly within the quiz and flip flashcards in the app.

## ⚙️ Prerequisites

You must have Python installed. The application requires an **API Key** from Google AI Studio.

1.  **Get a Gemini API Key:** Obtain your key from the Google AI Studio documentation or dashboard.

## 🚀 Installation and Setup

### 1. Install Dependencies

The app requires the following Python libraries. You can install them using the `requirements.txt` file provided.

```bash
pip install -r requirements.txt
