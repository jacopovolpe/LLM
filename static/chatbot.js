const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const sendBtn = document.getElementById('sendBtn');
const toggleSpeakBtn = document.getElementById('toggleSpeakBtn');
const textInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const responseSizeOptions = document.querySelectorAll('input[name="responseSize"]');

// Stato dell'applicazione
let recognition;
let isSpeakEnabled = false;
let currentThinkingMessage = null;
let voices = [];

// Inizializzazione UI
initUI();

// Inizializzazione del riconoscimento vocale
initSpeechRecognition();

// Event Listeners
startBtn.addEventListener('click', () => recognition && recognition.start());
resetBtn.addEventListener('click', handleReset);
sendBtn.addEventListener('click', () => sendMessage());
textInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
toggleSpeakBtn.addEventListener('click', toggleSpeech);

// Inizializzazione sintesi vocale
if ('speechSynthesis' in window) {
    loadVoices();
    speechSynthesis.onvoiceschanged = loadVoices;
} else {
    console.warn('La sintesi vocale non è supportata in questo browser.');
    toggleSpeakBtn.disabled = true;
}

// Carica la cronologia al caricamento della pagina
document.addEventListener("DOMContentLoaded", loadHistory);

// Funzioni
function initUI() {
    toggleSpeakBtn.style.backgroundColor = "#34a853";
    
    // Migliora l'UI delle opzioni dimensione risposta
    responseSizeOptions.forEach(option => {
        const label = document.querySelector(`label[for="${option.id}"]`);
        if (label) {
            label.classList.add('toggle-label');
            
            // Aggiorna lo stile attivo per l'opzione selezionata
            if (option.checked) {
                label.classList.add('active-option');
            }
            
            // Aggiungi event listener per aggiornare lo stile quando cambia la selezione
            option.addEventListener('change', updateResponseSizeUI);
        }
    });
}

function updateResponseSizeUI() {
    // Rimuovi la classe attiva da tutte le etichette
    document.querySelectorAll('.toggle-label').forEach(label => {
        label.classList.remove('active-option');
    });
    
    // Aggiungi la classe attiva all'etichetta dell'opzione selezionata
    responseSizeOptions.forEach(option => {
        if (option.checked) {
            const label = document.querySelector(`label[for="${option.id}"]`);
            if (label) {
                label.classList.add('active-option');
            }
        }
    });
}

function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'it-IT';

        recognition.onstart = () => {
            startBtn.disabled = true;
            startBtn.classList.add('recording');
            addStatusMessage('Ascolto in corso...');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            removeStatusMessage();
            sendMessage(transcript);
        };

        recognition.onerror = (event) => {
            removeStatusMessage();
            addMessage('bot', `Errore: ${event.error}`, false);
            resetRecognitionState();
        };

        recognition.onend = () => {
            resetRecognitionState();
            removeStatusMessage();
        };
    } else {
        addMessage('bot', 'Il riconoscimento vocale non è supportato in questo browser.', false);
        startBtn.disabled = true;
    }
}

function resetRecognitionState() {
    startBtn.disabled = false;
    startBtn.classList.remove('recording');
}

function addStatusMessage(text) {
    const statusDiv = document.createElement('div');
    statusDiv.classList.add('status-message');
    statusDiv.textContent = text;
    chatBox.appendChild(statusDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return statusDiv;
}

function removeStatusMessage() {
    const statusMessages = document.querySelectorAll('.status-message');
    statusMessages.forEach(msg => chatBox.removeChild(msg));
}

function toggleSpeech() {
    isSpeakEnabled = !isSpeakEnabled;
    if (!isSpeakEnabled) {
        toggleSpeakBtn.style.backgroundColor = "#9AA0A6";
        stopSpeaking();
    } else {
        toggleSpeakBtn.style.backgroundColor = "#34a853";
    }
}

function handleReset() {
    fetch("/reset");
    chatBox.innerHTML = '';
    stopSpeaking();
}

async function sendMessage(userMessage = textInput.value.trim()) {
    if (!userMessage) return;
    
    addMessage('user', userMessage, false);
    textInput.value = '';
    
    if (currentThinkingMessage) {
        chatBox.removeChild(currentThinkingMessage);
    }
    
    currentThinkingMessage = addMessage('bot', 'Thinking...', false);
    currentThinkingMessage.classList.add('thinking');

    let responseLength = getSelectedResponseLength();

    try {
        let response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                question: userMessage, 
                responseLength: responseLength 
            })
        });
        
        const result = await response.json();
        
        if (currentThinkingMessage) {
            chatBox.removeChild(currentThinkingMessage);
            currentThinkingMessage = null;
        }

        // Aggiungi la query riformulata con una classe diversa
        if (result.reformulated_query) {
            addReformulatedQuery(result.reformulated_query);
        }

        // Usa final_response invece di response
        const htmlResponse = convertMarkdownToHTML(result.final_response);
        addMessage('bot', htmlResponse, true);

        if (isSpeakEnabled) {
            speak(result.final_response);
        }
    } catch (error) {
        console.error(error);
        if (currentThinkingMessage) {
            chatBox.removeChild(currentThinkingMessage);
            currentThinkingMessage = null;
        }
        addMessage('bot', 'Errore durante l\'invio della richiesta.', false);
    }
}

function addReformulatedQuery(text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'reformulated-query');
    
    const messageHeader = document.createElement('div');
    messageHeader.classList.add('reformulated-header');
    messageHeader.textContent = 'Reformulated query:';
    
    const messageText = document.createElement('p');
    messageText.textContent = text;
    
    messageDiv.appendChild(messageHeader);
    messageDiv.appendChild(messageText);
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageDiv;
}

function getSelectedResponseLength() {
    if (document.getElementById("shortResponse").checked) {
        return "VERY_SHORT";
    } else if (document.getElementById("longResponse").checked) {
        return "LONG";
    }
    return "MEDIUM"; // Default
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

function loadVoices() {
    voices = speechSynthesis.getVoices();
}

function speak(text) {
    if (!('speechSynthesis' in window)) return;
    
    // Rimuovi i markdown prima di leggere il testo
    const plainText = text.replace(/\*\*(.*?)\*\*/g, '$1') // Bold
                         .replace(/\*(.*?)\*/g, '$1')     // Italic
                         .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Links
                         .replace(/#{1,6}\s(.*)/g, '$1')  // Headers
                         .replace(/```.*\n([\s\S]*?)```/g, '') // Code blocks
                         .replace(/`(.*?)`/g, '$1');      // Inline code
    
    const utterance = new SpeechSynthesisUtterance(plainText);
    utterance.lang = 'en-GB';
    
    // Trova una voce adatta o usa la prima disponibile
    let selectedVoice = voices.find(voice => voice.lang === 'en-GB' && voice.name.includes('Female')) || 
                        voices.find(voice => voice.lang === 'en-GB') || 
                        voices[0];
    
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }
    
    utterance.rate = 1.2;
    utterance.pitch = 1;
    speechSynthesis.speak(utterance);
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
                // Mostra la domanda originale
                addMessage('user', entry.original_question, false);
                
                // Mostra la query riformulata se presente
                if (entry.reformulated_query) {
                    addReformulatedQuery(entry.reformulated_query);
                }
                
                // Mostra la risposta finale
                const htmlAnswer = convertMarkdownToHTML(entry.final_response);
                addMessage('bot', htmlAnswer, true);
            });
        } else {
            console.error("Formato della cronologia non valido:", history);
        }
    } catch (error) {
        console.error("Errore durante il caricamento della cronologia:", error);
    }
}

// Funzione per convertire il markdown in HTML (assicurati che questa funzione sia implementata)
function convertMarkdownToHTML(markdown) {
    // Se la funzione non è già implementata nel tuo codice, aggiungi qui l'implementazione
    // Per semplicità, assumo che sia già implementata altrove
    return markdown; // Questa è solo una risposta segnaposto
}