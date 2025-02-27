const socket = io();
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');

recognition.continuous = true;
recognition.interimResults = false;

startBtn.addEventListener('click', () => {
    const inputLang = document.getElementById('input-lang').value;
    const outputLang = document.getElementById('output-lang').value;
    recognition.lang = inputLang;
    recognition.start();
    document.getElementById('status').textContent = 'Listening...';
    startBtn.classList.add('hidden');
    stopBtn.classList.remove('hidden');
});

stopBtn.addEventListener('click', () => {
    recognition.stop();
    document.getElementById('status').textContent = 'Stopped listening';
    stopBtn.classList.add('hidden');
    startBtn.classList.remove('hidden');
});

recognition.onresult = (event) => {
    const transcript = event.results[event.results.length - 1][0].transcript;
    document.getElementById('transcript').textContent = transcript;
    const inputLang = document.getElementById('input-lang').value;
    const outputLang = document.getElementById('output-lang').value;
    socket.emit('process_audio', { transcript: transcript, input_lang: inputLang, output_lang: outputLang });
    document.getElementById('status').textContent = 'Processing...';
};

recognition.onerror = (event) => {
    document.getElementById('status').textContent = `Error: ${event.error}`;
    stopBtn.classList.add('hidden');
    startBtn.classList.remove('hidden');
};

socket.on('translated_update', (data) => {
    document.getElementById('translated').textContent = data.text;
    document.getElementById('speak-btn').classList.remove('hidden');
});

socket.on('audio_ready', (data) => {
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.src = data.url;
    audioPlayer.classList.remove('hidden');
    audioPlayer.play();
    document.getElementById('status').textContent = 'Translation complete';
});

socket.on('error', (data) => {
    document.getElementById('status').textContent = data.message;
});
