from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')
socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def index():
    logger.debug("Serving index.html")
    return render_template('index.html')

@socketio.on('process_audio')
def process_audio(data):
    logger.debug(f"Received process_audio event with data: {data}")
    transcript = data.get('transcript')
    input_lang = data.get('input_lang', 'en-US')
    output_lang = data.get('output_lang', 'es-ES')

    if not transcript:
        logger.error("No transcript received")
        socketio.emit('error', {'message': 'No transcript provided'})
        return

    try:
        # Log before translation
        logger.debug(f"Translating '{transcript}' from {input_lang[:2]} to {output_lang[:2]}")
        translated = GoogleTranslator(source=input_lang[:2], target=output_lang[:2]).translate(transcript)
        logger.debug(f"Translation successful: {translated}")
        socketio.emit('translated_update', {'text': translated})

        # Log before TTS
        audio_file = f"static/audio/translated_{int(time.time())}.mp3"
        logger.debug(f"Generating audio file: {audio_file}")
        tts = gTTS(text=translated, lang=output_lang[:2], slow=False)
        tts.save(audio_file)
        logger.debug(f"Audio file saved: {audio_file}")
        socketio.emit('audio_ready', {'url': f'/{audio_file}'})
    except Exception as e:
        logger.error(f"Error in process_audio: {str(e)}")
        socketio.emit('error', {'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        logger.debug("Creating static/audio directory")
        os.makedirs('static/audio')
    port = int(os.environ.get('PORT', 5000))
    logger.debug(f"Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
