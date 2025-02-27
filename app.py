from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import time
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', static_url_path='/static')
socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('process_audio')
def process_audio(data):
    transcript = data.get('transcript')
    input_lang = data.get('input_lang', 'en-US')
    output_lang = data.get('output_lang', 'es-ES')

    try:
        translated = GoogleTranslator(source=input_lang[:2], target=output_lang[:2]).translate(transcript)
        socketio.emit('translated_update', {'text': translated})

        audio_file = f"static/audio/translated_{int(time.time())}.mp3"
        tts = gTTS(text=translated, lang=output_lang[:2], slow=False)
        tts.save(audio_file)
        socketio.emit('audio_ready', {'url': f'/{audio_file}'})
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        socketio.emit('error', {'message': f'Error: {e}'})

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
