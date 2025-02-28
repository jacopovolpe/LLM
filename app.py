from flask import Flask, render_template, request, jsonify
from LLM.Assistant import Assistant

app = Flask(__name__)

assistant = Assistant()

@app.route("/")
def index():
    return render_template("index.html")  # Serve la pagina HTML

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Domanda non valida"}), 400

    response = assistant.ask_assistant(question, debug=True)
    return jsonify({"response": response})

@app.route("/get_history")
def get_history():
    return assistant.get_history()

@app.route("/reset")
def reset():
    assistant.clear_history()
    return jsonify({"status": "success", "message": "Cronologia cancellata"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
