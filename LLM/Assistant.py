##------------------------------------------------------------------------------------------
# Configurazione dei token per l'accesso ai servizi
JV_HF_TOKEN = "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"
RS_HF_TOKEN = "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"

JV_GEMINI_TOKEN = "AIzaSyArDcTFUTzztpgCIlogXSYQwBhUieZxv7Y"
RS_GEMINI_TOKEN = "AIzaSyAS0kVBJkyFyosoCwqAQyJM0ElyKEzrmgM"
VM_GEMINI_TOKEN = "AIzaSyD22Kr3nfSrvkE45KJlbIZHLuTA_cYuBYM"

# Modelli e indici utilizzati
#GENERATION_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
#GENERATION_MODEL = "gemini-1.5-pro-latest"
FAISS_INDEX = "LLM/data/faiss_index/ALL__6Marzo2025__bge-m3"
#EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MODEL = "BAAI/bge-m3"

##-----------------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------------
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Disabilita i messaggi di avviso di TensorFlow
import re
import time
from datetime import datetime
import json


from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature=0.5,
    api_key=VM_GEMINI_TOKEN
    )

'''
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(
            model="claude-3-7-sonnet-20250219",  # Utilizza il modello Claude 3.7 Sonnet
            temperature=0.5,
            anthropic_api_key="YOUR_ANTHROPIC_API_KEY" )
'''

class Assistant:
    def __init__(self,
                 faiss_index=FAISS_INDEX,
                 embedding_model=EMBEDDING_MODEL,  
                 max_history=5,
                 log_file="LLM/data/logs/assistant.log"):
        
        self.faiss_index = faiss_index
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        try:
            self.vectorstore = FAISS.load_local(faiss_index, self.embeddings, allow_dangerous_deserialization=True)
            self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        except Exception as e:
            raise RuntimeError(f"Errore nel caricamento di FAISS: {e}")
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.history = []
        self.max_history = max_history
        self.log_file = log_file
    
            
        os.makedirs(os.path.dirname(log_file), exist_ok=True) 
        
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm
            retriever=self.retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self.get_prompt_template()}
        )
    
    def get_prompt_template(self):
        template = (
            "You are an advanced AI assistant utilizing Retrieval-Augmented Generation (RAG) "
            "to provide accurate and context-aware responses. Your goal is to assist users by leveraging "
            "relevant information retrieved from a structured knowledge base. The provided information may contain "
            "symbols, bullet points, or other formatting, but your response should be fluid, natural, and well-structured, "
            "suitable for spoken language.\n\n"
            
            "Context (structured information):\n"
            "{context}\n\n"
            
            "Conversation History:\n"
            "{chat_history}\n\n"
            
            "User's Question:\n"
            "{question}\n\n\n"
            
            "Instructions:\n"
            "- Convert structured or formatted information into natural, flowing sentences.\n"
            "- Ensure that the response is clear, concise, and sounds natural when spoken aloud.\n"
            "- If the context includes symbols, lists, or bullet points, integrate the information smoothly into sentences.\n"
            "- If the answer is not in the provided context, state: \"I'm sorry, but I don't have enough information to answer that.\"\n"
            "- Avoid making assumptions or fabricating details.\n"
            "- Use a conversational and engaging tone to make the response pleasant for text-to-speech.\n"
            
            "\n-----END_PROMPT-----\n"
            "Answer:\n"
        )
        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
    
    def generate_response(self, question, responseLength, debug=False):
        if debug:
            start_time = time.time()
        
        response = self.qa_chain.invoke({
            "question": question
        })
        
        response = response["answer"]
        
        if debug:
            elapsed_time = (time.time() - start_time) * 1000
            print(f"Tempo impiegato per la generazione della risposta: {elapsed_time:.3f} ms")
        
        clear_response = self.clarify_response(response)
        
        self.log_interaction(question, response, clear_response)
        self.add_to_history(question, clear_response)
        
        return clear_response
    
    def clarify_response(self, clean_response):
        for marker in ["-----END_PROMPT-----", "Response:", "Answer:", "Assistant:"]:
            if marker in clean_response:
                clean_response = clean_response.split(marker)[-1].strip()
        
        clean_response = re.sub(r"/Length: LONG/", "", clean_response, flags=re.IGNORECASE)
        clean_response = re.sub(r"/Length: MEDIUM/", "", clean_response, flags=re.IGNORECASE)
        clean_response = re.sub(r"/Length: VERY_SHORT/", "", clean_response, flags=re.IGNORECASE)
        
        return clean_response.strip()
    
    def add_to_history(self, question, answer):
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append({"question": question, "answer": answer})
    
    def clear_history(self):
        self.history.clear()
    
    def get_history(self):
        # Restituisce la cronologia come vettore (lista di dizionari)
        return self.history
    
    def get_history_for_prompt(self):
        history_string = ""
        if self.history:
            for entry in self.get_history():
                history_string += f"\n[question: '{entry['question']}', answer: '{entry['answer']}']"
        return history_string
    
    
    def log_interaction(self, question, response, clear_response):
        entry = {
            "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M"),
            "question": question,
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
    
    def ask(self, question, responseLength="MEDIUM", debug=False):
        # Convertiamo la domanda in minuscolo (se desiderato)
        question = question_processed = question.lower()
        response = self.generate_response(question_processed, responseLength, debug)
        return response
