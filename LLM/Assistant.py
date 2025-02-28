import requests
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np

import tensorflow as tf
import os

# Disabilita alcuni warning
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)



class Assistant:
    def __init__(self,
                 HUGGING_FACE_TOKEN="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", 
                 MODEL_LLM="mistralai/Mistral-7B-Instruct-v0.2",
                 faiss_index="LLM/data/faiss_index/ALL_faiss_index__all-MiniLM-L6-v2",
                 max_history=5):

        self.API_URL = f"https://api-inference.huggingface.co/models/{MODEL_LLM}"
        self.HEADERS = {"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"}

        self.faiss_index = faiss_index
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = FAISS.load_local(faiss_index, self.embeddings, allow_dangerous_deserialization=True)

        
        self.history = []  
        self.max_history = max_history 
        
    def get_relevant_chunks(self, question, top_k=50, min_contribution=0.1, diversity_threshold=0.5):
        """
        Seleziona i chunk che contribuiscono almeno al 10% della CDF delle similarità dei top 50 risultati.
        Applica anche un filtro di diversità per evitare troppi chunk simili tra loro.
        """
    
        # Recupera tutti i documenti con similarità
        docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=top_k)
        
        # Estrai i punteggi e normalizza in una distribuzione cumulativa
        scores = np.array([score for _, score in docs_with_scores])
        sorted_indices = np.argsort(scores)[::-1]  # Ordina per score decrescente
        sorted_scores = scores[sorted_indices]
        cdf = np.cumsum(sorted_scores) / np.sum(sorted_scores)  # Normalizza in CDF
        
        # Calcola la soglia dinamica adattiva invece di un valore fisso
        dynamic_threshold = max(min_contribution, np.percentile(cdf, 10))
        
        # Filtra i chunk che contribuiscono almeno alla soglia dinamica
        relevant_chunks = []
        selected_embeddings = []
        for idx, cdf_value in enumerate(cdf):
            if cdf_value >= dynamic_threshold:
                chunk_content = docs_with_scores[sorted_indices[idx]][0].page_content
                chunk_embedding = self.embeddings.embed_query(chunk_content)
                
                # Controlla la diversità semantica rispetto ai chunk già selezionati
                if all(np.linalg.norm(np.array(chunk_embedding) - np.array(e)) > diversity_threshold for e in selected_embeddings):
                    relevant_chunks.append(chunk_content)
                    selected_embeddings.append(chunk_embedding)
        
        return "\n".join(relevant_chunks)
    
    def get_simple_chunks(self, question, k=5):
        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n".join([doc.page_content for doc in docs])
        return context

    def generate_response(self, question, debug = False):
        
        context = self.get_simple_chunks(question, k = 5) 
    

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
            f"{question}\n\n"
            
            "Instructions:\n"
            "- Convert structured or formatted information into natural, flowing sentences.\n"
            "- Ensure that the response is clear, concise, and sounds natural when spoken aloud.\n"
            "- If the context includes symbols, lists, or bullet points, integrate the information smoothly into sentences.\n"
            "- If the answer is not in the provided context, state: \"I'm sorry, but I don't have enough information to answer that.\"\n"
            "- Avoid making assumptions or fabricating details.\n"
            "- Use a conversational and engaging tone to make the response pleasant for text-to-speech.\n"
            "\n-----END_PROMPT-----\n"
        )



        payload = {"inputs": prompt}
        response = requests.post(self.API_URL, headers=self.HEADERS, json=payload)

        if debug:
            print(f"API Response Code: {response.status_code}")
            print(f"Total Response: \n{response}\n\n\n\n")
            print(f"API Raw Response: {response.text}")

        if response.status_code != 200:
            return f"Errore API ({response.status_code}): {response.text}"
        
        try:
            response_json = response.json()
            clean_response = response_json[0].get("generated_text", "Errore nella generazione della risposta")
            clean_response = clean_response.split("-----END_PROMPT-----")[-1].strip() 
            clean_response = clean_response.split("Response:")[-1].strip() 
            clean_response = clean_response.split("Answer:")[-1].strip() 
            clean_response = clean_response.split("Assistant:")[-1].strip() 
            return clean_response

        
        except requests.exceptions.JSONDecodeError:
            return "Errore nel parsing della risposta JSON"


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
    
    
    #-------------------------------------------------------------    
    def ask(self, question, debug=False):
        question = question.lower()
        response = self.generate_response(question, debug)  
        self.add_to_history(question, response)
        return response