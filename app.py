import os
from flask import Flask, render_template, request, jsonify, send_file
from LLM.Assistant import Assistant

app = Flask(__name__)

assistant = Assistant()
LOG_FILE_PATH = "LLM/data/logs/assistant.log"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def logs():
    return render_template("showLogInterface.html")

@app.route("/get_logs")
def get_logs():
    if os.path.exists(LOG_FILE_PATH):
        return send_file(LOG_FILE_PATH, mimetype="text/plain")
    return jsonify({"error": "File di log non trovato"}), 404

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    responseLength = data.get("responseLength", "MEDIUM")
    if not question:
        return jsonify({"error": "Domanda non valida"}), 400

    response = assistant.ask(question, responseLength, debug=True)
    return jsonify(response)

@app.route("/get_history")
def get_history():
    return assistant.get_history()

@app.route("/reset")
def reset():
    assistant.clear_history()
    return jsonify({"status": "success", "message": "Cronologia cancellata"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
