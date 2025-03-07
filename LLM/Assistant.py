import requests
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings 
import numpy as np
import re
import tensorflow as tf
import os
import time
from datetime import datetime
import json

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

##------------------------------------------------------------------------------------------
# Configurazione dei token per l'accesso ai servizi
JV_HF_TOKEN = "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"
RS_HF_TOKEN = "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"

JV_GEMINI_TOKEN = "AIzaSyArDcTFUTzztpgCIlogXSYQwBhUieZxv7Y"
RS_GEMINI_TOKEN = "AIzaSyAS0kVBJkyFyosoCwqAQyJM0ElyKEzrmgM"
VM_GEMINI_TOKEN = "AIzaSyD22Kr3nfSrvkE45KJlbIZHLuTA_cYuBYM"

# Modelli e indici utilizzati
GENERATION_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
FAISS_INDEX = "data/faiss_index/ALL__6Marzo2025__all-miniLM-L6-v2"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------

import google.generativeai as genai

# Configura il modello Gemini
genai.configure(api_key=VM_GEMINI_TOKEN)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def call_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

##------------------------------------------------------------------------------------------

def call_model_on_huggingface(prompt):
    payload = {"inputs": prompt}
        
    API_URL = f"https://api-inference.huggingface.co/models/{GENERATION_MODEL}"
    HEADERS = {"Authorization": f"Bearer {RS_HF_TOKEN}"}

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        return f"Errore API ({response.status_code}): {response.text}"
    
    response_json = response.json()
    if isinstance(response_json, list) and len(response_json) > 0:
        response_text = response_json[0].get("generated_text", "Errore nella generazione della risposta")
    else:
        response_text = "Errore nella generazione della risposta"
    
    return response_text

##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------

class Assistant:
    def __init__(self,
                 faiss_index=FAISS_INDEX,
                 embedding_model=EMBEDDING_MODEL, 
                 max_history=5,
                 log_file = "logs/assistant.log"):
      
        self.faiss_index = faiss_index
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore = FAISS.load_local(faiss_index, self.embeddings, allow_dangerous_deserialization=True)

        self.history = []  
        self.max_history = max_history 
        self.log_file = log_file

    def generate_response(self, question, responseLength, debug=False):
        
        if debug:
            start_time = time.time()

        docs = self.vectorstore.similarity_search(question, k=5)
        context = "\n".join([doc.page_content for doc in docs])
        
        if debug:
            elapsed_time = (time.time() - start_time) * 1000
            print(f"Tempo impiegato per il retrivial: {elapsed_time:.3f} ms")
    
        prompt = (
            "You are an advanced AI assistant utilizing Retrieval-Augmented Generation (RAG) "
            "to provide accurate and context-aware responses. Your goal is to assist users by leveraging "
            "relevant information retrieved from a structured knowledge base. The provided information may contain "
            "symbols, bullet points, or other formatting, but your response should be fluid, natural, and well-structured, "
            "suitable for spoken language.\n\n"
            
            "Context (structured information):\n"
            f"{context}\n\n"
            
            "Conversation History:\n"
            f"{self.get_history_for_prompt()}\n\n"
            
            "User's Question:\n"
            f"{question}\n\n\n"
            
            "Instructions:\n"
            "- Convert structured or formatted information into natural, flowing sentences.\n"
            "- Ensure that the response is clear, concise, and sounds natural when spoken aloud.\n"
            "- If the context includes symbols, lists, or bullet points, integrate the information smoothly into sentences.\n"
            "- If the answer is not in the provided context, state: \"I'm sorry, but I don't have enough information to answer that.\"\n"
            "- Avoid making assumptions or fabricating details.\n"
            "- Use a conversational and engaging tone to make the response pleasant for text-to-speech.\n"
            f"- generate a answer with a length {responseLength}.\n"
            "\n-----END_PROMPT-----\n"
            "Answer:\n"
        )

        response = call_gemini(prompt)

        if debug:
            print(f"prompt: \n\n\n{prompt}\n\n")
            print(f"API Raw Response: {response}")

        clear_response = self.clarify_response(response)
        self.log_interaction(question, docs, response, clear_response)

        return clear_response

    def clarify_response(self, clean_response):
        clean_response = clean_response.split("-----END_PROMPT-----")[-1].strip() 
        clean_response = clean_response.split("Response:")[-1].strip() 
        clean_response = clean_response.split("Answer:")[-1].strip() 
        clean_response = clean_response.split("Assistant:")[-1].strip() 
        
        # Remove any length indicators (case-insensitive)
        clean_response = re.sub(r"/Length: LONG/gi", "", clean_response)
        clean_response = re.sub(r"/Length: MEDIUM/gi", "", clean_response)
        clean_response = re.sub(r"/Length: VERY_SHORT/gi", "", clean_response)
        
        # Final strip to remove any leading/trailing whitespace
        clean_response = clean_response.strip()
        
        return clean_response
    
    def add_to_history(self, question, answer):
        if len(self.history) >= self.max_history:
            self.history.pop(0) 

        self.history.append({"question": question, "answer": answer})
        
    def clear_history(self):
        self.history.clear()
        
    def get_history(self):
        return self.history
    
    def get_history_for_prompt(self):
        history_string = ""
        
        if len(self.history) > 0:                  
            for entry in self.get_history():
                history_string += f"\n[question:'{entry['question']}, answer:'{entry['answer']}']"
            
        return history_string
    
    def ask(self, question, responseLength=None, debug=False):
        question = question.lower()
        response = self.generate_response(question, responseLength, debug)  
        self.add_to_history(question, response)
        return response
    
    def log_interaction(self, question, docs, response, clear_response):
        entry = {
            "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M"),
            "question": question,
            "retrieved_docs": [doc.page_content for doc in docs],
            "response": response,
            "clear_response": clear_response,
            "GENERATION_MODEL": GENERATION_MODEL,
            "EMBEDDING_MODEL": EMBEDDING_MODEL,
            "FAISS_INDEX": FAISS_INDEX
        }
        
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                try:
                    log_data = json.load(f)
                except json.JSONDecodeError:
                    log_data = []
        else:
            log_data = []
        
        log_data.append(entry)
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)