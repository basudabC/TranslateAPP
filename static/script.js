const socket = io();

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');

startBtn.addEventListener('click', () => {
    const inputLang = document.getElementById('input-lang').value;
    const outputLang = document.getElementById('output-lang').value;
    socket.emit('start_listening', { input_lang: inputLang, output_lang: outputLang });
    startBtn.classList.add('hidden');
    stopBtn.classList.remove('hidden');
});

stopBtn.addEventListener('click', () => {
    socket.emit('stop_listening');
    stopBtn.classList.add('hidden');
    startBtn.classList.remove('hidden');
});

socket.on('status', (data) => {
    document.getElementById('status').textContent = data.message;
});

socket.on('transcript_update', (data) => {
    document.getElementById('transcript').textContent = data.text;
});

socket.on('translated_update', (data) => {
    document.getElementById('translated').textContent = data.text;
    document.getElementById('speak-btn').classList.remove('hidden');
});

socket.on('audio_ready', (data) => {
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.src = data.url;
    audioPlayer.classList.remove('hidden');
    audioPlayer.play();  // Auto-play translated audio
});

socket.on('error', (data) => {
    document.getElementById('status').textContent = data.message;
});