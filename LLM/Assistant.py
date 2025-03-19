import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import re
import time
from datetime import datetime
import json
from typing import List, Dict, Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document

EMBEDDING_MODEL = "BAAI/bge-m3"
FAISS_INDEX = "LLM/data/faiss_index/ALL__11Marzo2025_split__bge-m3"

try:
    from GenerationModel import GoogleGemini
except ImportError:
    from LLM.GenerationModel import GoogleGemini

class Assistant:
    def __init__(self,
                 faiss_index=FAISS_INDEX,
                 embedding_model=EMBEDDING_MODEL,  
                 max_history=5,
                 log_file="LLM/data/logs/assistant.log"):
        self.faiss_index = faiss_index
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

        self.generation_model = GoogleGemini()

        try:
            self.vectorstore = FAISS.load_local(faiss_index, self.embeddings, allow_dangerous_deserialization=True)
            self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        except Exception as e:
            raise RuntimeError(f"Error loading FAISS: {e}")
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
        self.history = []
        self.max_history = max_history
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.query_reformulation_chain = self._create_query_reformulation_chain()
        self.qa_chain = self._create_qa_chain()
    
    def _create_query_reformulation_chain(self):
        template = (
            "You are an assistant specialized in conversation analysis and question reformulation. "
            "Analyze the user's question and conversation history to formulate an optimized query for searching in the knowledge database.\n\n"
            "Conversation history:\n{chat_history}\n\n"
            "Original user question:\n{question}\n\n"
            "Instructions:\n"
            "1. Analyze context and identify key concepts and entities.\n"
            "2. Disambiguate implicit references based on history.\n"
            "3. Expand acronyms or specialized terms.\n"
            "4. Reformulate the question into a complete, explicit search query as a single question or phrase.\n"
            "5. Determine if the new query follows previous context or is separate.\n\n"
            "Generate ONLY the reformulated query without additional explanation."
        )
        prompt = PromptTemplate(template=template, input_variables=["chat_history", "question"])
        return LLMChain(llm=self.generation_model.llm, prompt=prompt)
    
    def _create_qa_chain(self):
        template = (
            "You are an advanced AI assistant using Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses. "
            "Leverage relevant information retrieved from a structured knowledge base. "
            "Convert structured or formatted information into natural, flowing sentences. "
            "If the context includes symbols or bullet points, integrate them smoothly. "
            "If the answer is not in the provided context, do not fabricate details.\n\n"
            "Context:\n{context}\n\n"
            "Conversation History:\n{chat_history}\n\n"
            "Reformulated User Query:\n{question}\n\n"
            "Answer:\n"
        )
        prompt = PromptTemplate(template=template, input_variables=["context", "chat_history", "question"])
        return ConversationalRetrievalChain.from_llm(
            llm=self.generation_model.llm,
            retriever=self.retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    def generate_response(self, question: str, response_length: str = "MEDIUM", debug: bool = False) -> dict:
        if debug:
            start_time = time.time()

        reformulated_query = self.query_reformulation_chain.invoke({
            "question": question,
            "chat_history": self.get_history_for_prompt()
        })["text"].strip()

        if debug:
            print(f"Original query: {question}")
            print(f"Reformulated query: {reformulated_query}")
            query_time = time.time()
            print(f"Query reformulation time: {(query_time - start_time) * 1000:.3f} ms")

        result = self.qa_chain.invoke({"question": reformulated_query})
        raw_response = result["answer"]

        retrieved_docs = result.get("source_documents", [])
        if debug:
            rag_time = time.time()
            print(f"RAG generation time: {(rag_time - query_time) * 1000:.3f} ms")
            print(f"Total time: {(rag_time - start_time) * 1000:.3f} ms")

        final_response = self.clarify_response(raw_response)
        interaction_json = self.interaction(question, reformulated_query, raw_response, final_response, retrieved_docs)
        self.add_to_history(question, final_response, reformulated_query)
        
        return interaction_json
    
    def clarify_response(self, response: str) -> str:
        for marker in ["-----END_PROMPT-----", "Response:", "Answer:", "Assistant:"]:
            if marker in response:
                response = response.split(marker)[-1].strip()
        return re.sub(r"/Length: (LONG|MEDIUM|SHORT|VERY_SHORT)/", "", response, flags=re.IGNORECASE).strip()
    
    def add_to_history(self, question: str, answer: str, reformulated_query=None) -> None:
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append({"original_question": question, "final_response": answer, "reformulated_query":reformulated_query})
    
    def clear_history(self) -> None:
        self.history.clear()
        self.memory.clear()
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.history
    
    def get_history_for_prompt(self) -> str:
        return "\n".join(f"User: {entry['original_question']}\nAssistant: {entry['final_response']}" for entry in self.history)
    
    def interaction(self,
                    original_question: str,
                    reformulated_query: str,
                    raw_response: str,
                    final_response: str,
                    retrieved_docs: Optional[List[Document]] = None,
                    log: bool = True) -> dict:
        entry = {
            "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M"),
            "original_question": original_question,
            "reformulated_query": reformulated_query,
            "raw_response": raw_response,
            "final_response": final_response,
            "generation_model": self.generation_model.modelName(),
            "embedding_model": EMBEDDING_MODEL,
            "faiss_index": FAISS_INDEX,
        }
        if retrieved_docs:
            entry["retrieved_documents"] = [doc.page_content for doc in retrieved_docs]
        if log:
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
        return entry
    
    def ask(self, question: str, response_length: str = "MEDIUM", debug: bool = False) -> dict:
        return self.generate_response(question, response_length, debug)
