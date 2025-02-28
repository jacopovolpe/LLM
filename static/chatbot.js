const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const sendBtn = document.getElementById('sendBtn');
const toggleSpeakBtn = document.getElementById('toggleSpeakBtn');
const textInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');

let recognition;
let isSpeakEnabled = true;
toggleSpeakBtn.style.backgroundColor = "green";

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'it-IT';

    recognition.onstart = () => {
        startBtn.disabled = true;
        startBtn.classList.add('recording');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        sendMessage(transcript);
        startBtn.disabled = false;
        startBtn.classList.remove('recording');
    };

    recognition.onerror = (event) => {
        addMessage('bot', `Errore: ${event.error}`, false);
        startBtn.disabled = false;
        startBtn.classList.remove('recording');
    };

    recognition.onend = () => {
        startBtn.disabled = false;
        startBtn.classList.remove('recording');
    };
} else {
    addMessage('bot', 'Il riconoscimento vocale non è supportato in questo browser.', false);
    startBtn.disabled = true;
}


let wakeRecognition;

if ('webkitSpeechRecognition' in window) {
    wakeRecognition = new webkitSpeechRecognition();
    wakeRecognition.continuous = true;
    wakeRecognition.interimResults = false;
    wakeRecognition.lang = 'it-IT';

    wakeRecognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
        console.log("Wake word detected:", transcript);
        if (transcript === "ok boss") {
            recognition.start();
        }
    };

    wakeRecognition.onerror = (event) => {
        console.error("Errore riconoscimento wake word:", event.error);
    };

    wakeRecognition.start();
}



startBtn.addEventListener('click', () => recognition.start());
resetBtn.addEventListener('click', () => {
    fetch("/reset");
    chatBox.innerHTML = '';
    stopSpeaking();
});
sendBtn.addEventListener('click', () => sendMessage());
textInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

toggleSpeakBtn.addEventListener('click', () => {
    isSpeakEnabled = !isSpeakEnabled;
    if (!isSpeakEnabled) {
        toggleSpeakBtn.style.backgroundColor = "gray";
        stopSpeaking();
    } else {
        toggleSpeakBtn.style.backgroundColor = "green";
    }
});

async function sendMessage(userMessage = textInput.value.trim()) {
    if (userMessage) {
        addMessage('user', userMessage, false);
        textInput.value = '';
        const thinkingMessage = addMessage('bot', 'Thinking...', false);
        thinkingMessage.classList.add('thinking');

        try {
            let response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: userMessage })
            });
            const result = await response.json();
            console.log(response);
            thinkingMessage.classList.remove('thinking');
            chatBox.removeChild(thinkingMessage);

            
            addMessage('bot', result.response, false);
            

            if (isSpeakEnabled) {
                speak(result.response);
            }
        } catch (error) {
            console.error(error);
            addMessage('bot', 'Errore durante l\'invio della richiesta.', false);
            chatBox.removeChild(thinkingMessage);
        }
    }
}

function addMessage(sender, text, isHTML) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'user' ? 'user-msg' : 'bot-msg');

    if (isHTML) {
        messageDiv.innerHTML = text;
    } else {
        const messageText = document.createElement('p');
        messageText.textContent = text;
        messageDiv.appendChild(messageText);
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageDiv;
}


let voices = [];
function loadVoices() {  voices = speechSynthesis.getVoices();  console.log(voices); }
speechSynthesis.onvoiceschanged = loadVoices;
function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text );
        utterance.lang = 'en-GB';
        utterance.voice = voices[4];
        //utterance.lang = 'it-IT';
        //utterance.voice = voices[1];
        utterance.rate = 1.2;
        utterance.pitch = 1;
        speechSynthesis.speak(utterance);
    } else {
        console.log('La sintesi vocale non è supportata in questo browser.');
    }
}

function stopSpeaking() {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
    }
}


async function loadHistory() {
    try {
        let response = await fetch("/get_history");
        let history = await response.json();

        if (Array.isArray(history)) {
            history.forEach(entry => {
                addMessage('user', entry.question, false);
                addMessage('bot', entry.answer, false);
            });
        } else {
            console.error("Formato della cronologia non valido:", history);
        }
    } catch (error) {
        console.error("Errore durante il caricamento della cronologia:", error);
    }
}
document.addEventListener("DOMContentLoaded", loadHistory);
