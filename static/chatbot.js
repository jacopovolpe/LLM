const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const sendBtn = document.getElementById('sendBtn');
const textInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const responseSizeOptions = document.querySelectorAll('input[name="responseSize"]');

// Stato dell'applicazione
let recognition;
let currentThinkingMessage = null;

// Inizializzazione UI
initUI();


// Event Listeners
startBtn.addEventListener('click', () => recognition && recognition.start());
resetBtn.addEventListener('click', handleReset);
sendBtn.addEventListener('click', () => sendMessage());
textInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });


// Carica la cronologia al caricamento della pagina
document.addEventListener("DOMContentLoaded", loadHistory);

// Funzioni
function initUI() {
    
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

function handleReset() {
    fetch("/reset");
    chatBox.innerHTML = '';
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


    try {
        let response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                question: userMessage 
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
        htmlResponse = improveHTML(result.final_response);
       addMessage('bot', htmlResponse, true);

        
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
                const htmlAnswer = improveHTML(entry.final_response);
                addMessage('bot', htmlAnswer, true);
            });
        } else {
            console.error("Formato della cronologia non valido:", history);
        }
    } catch (error) {
        console.error("Errore durante il caricamento della cronologia:", error);
    }
}
