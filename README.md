# RAG-based AI Assistant

## Panoramica del Progetto  

Questo progetto implementa un assistente AI basato su Retrieval-Augmented Generation (RAG), progettato per rispondere a domande relative al corso *Natural Language Processing and Large Language Models (2024/2025)*. L'assistente combina il recupero di informazioni da una base di conoscenza strutturata con la generazione di risposte in linguaggio naturale, garantendo accuratezza e pertinenza nei risultati.

### Componenti Principali  

- **Preprocessing dei Dati:** Estrazione, pulizia e strutturazione dei materiali del corso, inclusi slide, libri di testo e documenti correlati.  
- **Sistema di Embedding:** Conversione del testo in rappresentazioni vettoriali per un recupero efficiente basato sulla similarità.  
- **Indice FAISS:** Archiviazione e organizzazione degli embedding per ricerche rapide e precise.  
- **Riformulazione delle Query:** Analisi e ottimizzazione delle domande degli utenti, integrando il contesto della conversazione per migliorare la precisione del recupero.  
- **Modulo di Recupero:** Selezione dei segmenti testuali più pertinenti dalla base di conoscenza.  
- **Generatore di Risposte:** Utilizzo di un modello di linguaggio avanzato per fornire risposte chiare e contestualizzate.  
- **Buffer Conversazionale:** Gestione della cronologia delle interazioni per garantire continuità nelle domande successive.  

### Flusso di Lavoro  

1. **Elaborazione della Query:** L'utente invia una domanda all'assistente.  
2. **Ottimizzazione della Query:** Il sistema riformula la domanda, includendo il contesto della conversazione se necessario.  
3. **Recupero delle Informazioni:** Il modulo di retrieval esegue una ricerca nell'indice FAISS per individuare contenuti pertinenti.  
4. **Generazione della Risposta:** Il modello AI integra le informazioni recuperate per produrre una risposta chiara e informativa.  
5. **Gestione del Contesto:** La memoria conversazionale viene aggiornata per mantenere la coerenza tra le interazioni.  

Questa architettura garantisce risposte precise e contestualizzate, escludendo richieste non pertinenti al corso.

---

## Installazione

Per configurare il progetto, segui questi passaggi:

1. **Clona il repository:**
   ```bash
   git clone https://github.com/jacopovolpe/LLM
   cd LLM
   ```

2. **Crea un ambiente virtuale:** *(consigliato)*
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows, usa `venv\Scripts\activate`
   ```

3. **Installa le dipendenze richieste:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente:**
   Crea un file `.env` nella directory principale e aggiungi i token API necessari:
   ```bash
   HUGGING_FACE_TOKEN=your_hugging_face_token_here
   GEMINI_TOKEN=your_gemini_token_here
   ```

---

## Avvio del Sistema

Per avviare l'assistente, esegui il comando:
   ```bash
   python app.py
   ```
   Questo avvierà il server in locale sulla porta `5000`.

Se vuoi renderlo accessibile da altri dispositivi nella stessa rete locale (LAN), usa:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
   
Per trovare l'indirizzo IP della tua macchina:
- **Windows:**
  ```bash
  ipconfig
  ```
- **Linux/Mac:**
  ```bash
  ifconfig
  ```

Una volta avviato, apri il browser e visita `http://localhost:5000` per interagire con l'assistente AI.

---

## Utilizzo

Dopo aver avviato l'applicazione, puoi inviare domande utilizzando l'interfaccia web. L'assistente elaborerà la richiesta, recupererà informazioni pertinenti e genererà una risposta coerente basata sul contesto della conversazione.

---

## Struttura del Progetto

```
ai-assistant/
¦
+-- app.py                  # Applicazione principale e API
+-- Assistant.py            # Classe principale con la logica dell'assistente
+-- GenerationModel.py      # Classe Wrapper per i modelli di generazione del testo
+-- Preparation.ipynb       # Notebook per preprocessing e setup FAISS
+-- Test.ipynb              # Notebook con i test dell'assistente
+-- TestAssistant.ipynb     # Notebook per testare l'assistente
+-- requirements.txt        # Dipendenze del progetto
+-- data/                   # Archivio dei dati
¦   +-- faiss_index/        # Indice FAISS
¦   +-- FINAL_DOC/          # Documenti finali elaborati
¦   +-- logs/               # Log di esecuzione
¦   +-- preprocessing/      # File di preprocessing
¦   +-- questions/          # Domande di test
¦   +-- slides/             # Slide del corso in formato PDF
¦   +-- source/             # Documenti di origine
+-- static/                 # File statici per l'interfaccia web
+-- templates/              # Template HTML per l'interfaccia web
¦   +-- index.html          # Pagina principale
+-- .gitignore              # File per escludere file non necessari dal repository
+-- LLM_Report_Gruppo7.pdf  # Report del progetto
+-- README.md               # Documentazione del progetto
```

---

## Dipendenze

Il progetto richiede i seguenti pacchetti Python:

- requests
- langchain
- huggingface_hub
- sentence-transformers
- pypdf
- numpy
- tensorflow

Puoi installare tutte le dipendenze con:
```bash
pip install -r requirements.txt
```
