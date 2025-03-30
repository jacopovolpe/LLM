import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from LLM.Assistant import Assistant

app = Flask(__name__)

GEMINI_TOKEN = "INSERISCI_TOKEN_QUI"
COHERE_TOKEN = "INSERISCI_TOKEN_QUI"

assistant =  Assistant(faiss_index="LLM/data/faiss_index/ALL__22_03_2025__BGE-M3__MAX_INNER_PRODUCT",
                       embedding_model="BAAI/bge-m3",
                       generation_model1="GEMINI",
                       token1=GEMINI_TOKEN,
                       generation_model2="COMMAND_R_PLUS", 
                       token2=COHERE_TOKEN,
                       log_file="LLM/data/logs/assistant.log")

#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------- CHATBOT --------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Domanda non valida"}), 400

    response = assistant.ask(question)
    return jsonify(response)

@app.route("/get_history")
def get_history():
    return assistant.get_history()

@app.route("/reset")
def reset():
    assistant.clear_history()
    return jsonify({"status": "success", "message": "Cronologia cancellata"})



#---------------------------------------------------------------------------------------------------------------------#
#---------------- LOGS -----------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

@app.route("/logs")
def logs():
    return render_template("showLogInterface.html")

@app.route("/get_logs", methods=["POST"])
def get_logs():
    """Ottiene il contenuto di un file JSON di risposte"""
    data = request.json
    file_name = data.get("file_name", "")
    file_path = os.path.join("LLM/data/logs/", file_name)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File non trovato"}), 404
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return jsonify(json_data), 200
    except Exception as e:
        return jsonify({"error": f"Errore nella lettura del file: {str(e)}"}), 500

#---------------------------------------------------------------------------------------------------------------------#
#-------------- QUESTIONS --------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
RESPONSES_FOLDER = "LLM/data/questions/responses"


@app.route("/questions")
def questions():
    return render_template("questionEvaluator.html")

@app.route("/get_questions", methods=["POST"])
def get_questions():
    """Ottiene il contenuto di un file JSON di risposte"""
    data = request.json
    file_name = data.get("file_name", "")
    file_path = os.path.join(RESPONSES_FOLDER, file_name)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File non trovato"}), 404
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return jsonify(json_data), 200
    except Exception as e:
        return jsonify({"error": f"Errore nella lettura del file: {str(e)}"}), 500

@app.route("/save_questions", methods=["POST"])
def save_questions():
    """Salva i dati aggiornati in un file JSON"""
    data = request.json
    file_name = data.get("file_name", "")
    json_data = data.get("data", {})
    
    if not file_name:
        return jsonify({"error": "Nome file non specificato"}), 400
        
    file_path = os.path.join(RESPONSES_FOLDER, file_name)
    
    try:
        # Assicurati che la directory esista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Scrivi il file JSON
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)
            
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": f"Errore nel salvataggio del file: {str(e)}"}), 500
    
@app.route("/list_response_files", methods=["GET"])
def list_response_files():
    """Lista tutti i file JSON nella cartella delle risposte"""
    if not os.path.exists(RESPONSES_FOLDER):
        return jsonify([]), 200
        
    files = [f for f in os.listdir(RESPONSES_FOLDER) if f.endswith('.json')]
    return jsonify(files), 200


#---------------------------------------------------------------------------------------------------------------------#
#---------------- APP ------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
