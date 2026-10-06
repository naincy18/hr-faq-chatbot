import speech_recognition as sr
import pyttsx3
import tempfile
import re


def transcribe_audio(audio_bytes):
    """
    Converts recorded audio (WAV bytes from st.audio_input) into text
    using Google's free speech-to-text API. Needs internet.
    Returns None if transcription fails.
    """
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with sr.AudioFile(tmp.name) as source:
            audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except (sr.UnknownValueError, sr.RequestError):
        return None


def strip_html(text):
    """Remove HTML tags/badges before speaking so TTS doesn't read raw markup."""
    return re.sub(r"<[^>]+>", " ", text).strip()


def speak_text(text):
    """Speaks text aloud using the local system's TTS engine (offline, free)."""
    clean_text = strip_html(text)
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.say(clean_text)
    engine.runAndWait()
    engine.stop()