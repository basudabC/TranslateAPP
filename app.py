from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import threading
import time
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Global variables
recognizer = sr.Recognizer()
is_listening = False
current_input_lang = 'en-US'
current_output_lang = 'es-ES'
listener_thread = None

def audio_listener():
    logging.debug("Starting audio listener thread")
    with sr.Microphone() as source:
        socketio.emit('status', {'message': 'Adjusting for ambient noise...'})
        recognizer.adjust_for_ambient_noise(source, duration=1)
        socketio.emit('status', {'message': 'Ready to listen...'})

        while is_listening:
            try:
                logging.debug("Listening for audio...")
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                socketio.emit('status', {'message': 'Processing...'})

                transcript = recognizer.recognize_google(audio, language=current_input_lang)
                socketio.emit('transcript_update', {'text': transcript})

                translated = GoogleTranslator(source=current_input_lang[:2], target=current_output_lang[:2]).translate(transcript)
                socketio.emit('translated_update', {'text': translated})

                audio_file = f"static/audio/translated_{int(time.time())}.mp3"
                tts = gTTS(text=translated, lang=current_output_lang[:2], slow=False)
                tts.save(audio_file)
                socketio.emit('audio_ready', {'url': f'/{audio_file}'})

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                socketio.emit('error', {'message': 'Could not understand audio'})
            except sr.RequestError as e:
                socketio.emit('error', {'message': f'Speech service error: {e}'})
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                socketio.emit('error', {'message': f'Error: {e}'})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_listening')
def start_listening(data):
    global is_listening, current_input_lang, current_output_lang, listener_thread
    if not is_listening:
        current_input_lang = data.get('input_lang', 'en-US')
        current_output_lang = data.get('output_lang', 'es-ES')
        is_listening = True
        socketio.emit('status', {'message': 'Starting real-time translation...'})
        listener_thread = threading.Thread(target=audio_listener, daemon=True)
        listener_thread.start()
        logging.debug("Started listening thread")

@socketio.on('stop_listening')
def stop_listening():
    global is_listening
    is_listening = False
    socketio.emit('status', {'message': 'Stopped listening'})
    logging.debug("Stopped listening")

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    port = int(os.environ.get('PORT', 5000))  # Use Heroku's port or default to 5000
    socketio.run(app, host='0.0.0.0', port=port, debug=True)