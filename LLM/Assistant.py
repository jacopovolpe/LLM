import os
import json
from datetime import datetime
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain.schema import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class Assistant:
    def __init__(self,
                 faiss_index,
                 embedding_model,  
                 generation_model1,
                 generation_model2,
                 max_history = 5,
                 log_file="LLM/data/logs/assistant.log"):
        
        self.faiss_index = faiss_index
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        self.generation_model1 = generation_model1
        self.generation_model2 = generation_model2
        
        try:
            self.vectorstore = FAISS.load_local(faiss_index, self.embeddings, allow_dangerous_deserialization=True)
            self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        except Exception as e:
            raise RuntimeError(f"Error loading FAISS: {e}")
        
        self.history = []
        self.max_history = max_history
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        self.query_handling_chain = self._create_query_handling_chain()
        self.qa_chain = self._create_qa_chain()

    def _create_query_handling_chain(self):
        template = (
            '''
            You are an expert assistant specialized in NLP and LLMs. 
            Analyze the user's query considering conversation history and retrieved documents.
            Determine if the question is a follow-up or independent and if it belongs to the LLMs/NLP domain.

            **Steps:**
            1. **Identify Follow-up Queries:** If the question depends on prior context, merge relevant details into a self-contained query.
            2. **Analyze Retrieved Documents:** Use the retrieved context to determine if the question is relevant.
            3. **Determine Domain Relevance:** If the question is unrelated to LLMs/NLP, return:
                OUT_OF_CONTEXT_QUESTION: " say that you can't response, for example saying that the question is outside your knowledge domain.
            4. **Format Output:**
            - If valid, return only the refined query.
            - If out of context, return "OUT_OF_CONTEXT_QUESTION: <response>".

            **Few-shot Examples:**
            
            **Example 1 - Follow-up Query:**
            **Conversation History:**
            User: How does GPT-4 handle long context?
            Assistant: GPT-4 uses positional embeddings and attention mechanisms to process long contexts efficiently.
            User: Can it handle 10,000 tokens?
            **Rewritten Query:** "Can GPT-4 handle 10,000 tokens given its architecture?"
            
            **Example 2 - Independent Query:**
            **User Question:** "What is zero-shot learning in NLP?"
            **Rewritten Query:** "What is zero-shot learning in NLP?"
            
            **Example 3 - Out of Context Query:**
            **User Question:** "Who won the FIFA World Cup in 2018?"
            **Response:** "OUT_OF_CONTEXT_QUESTION: I'm sorry but I can't provide information about football. I specialize in answering questions related to NLP and LLMs."
            
            **Example 4 - Out of Context Query:**
            **User Question:** "What is the capital of Japan?"
            **Response:** "OUT_OF_CONTEXT_QUESTION: I'm designed to assist with NLP and LLM-related topics. General knowledge queries are outside my domain."
            
            **Example 5 - Out of Context Query:**
            **User Question:** "Can you recommend a good sci-fi book?"
            **Response:** "OUT_OF_CONTEXT_QUESTION: My expertise is in NLP and LLMs. I recommend checking book review platforms for such recommendations."
            
            **Example 6 - Out of Context Query:**
            **User Question:** "Who invented the light bulb?"
            **Response:** "OUT_OF_CONTEXT_QUESTION: This question falls outside my specialized domain of NLP and LLMs."
            
            **Example 7 - Are you sure Query:**
            User: How does GPT-4 handle long context?
            Assistant: GPT-4 uses positional embeddings and attention mechanisms to process long contexts efficiently.
            **User Question:** "Are you sure"
            **Response:** "OUT_OF_CONTEXT_QUESTION: Yes, i'm sure. GPT-4 handle long context using positional embeddings."
            
            **Conversation History:**
            {chat_history}

            **User Question:**
            {question}

            **Retrieved Context:**
            {retrieved_context}
            '''
        )
        prompt = PromptTemplate(template=template, input_variables=["chat_history", "question", "retrieved_context"])
        return LLMChain(llm=self.generation_model1.llm, prompt=prompt)


    def _create_qa_chain(self):
        template = (
            """
            You are an advanced AI assistant using Retrieval-Augmented Generation (RAG). 
            Use the provided knowledge to generate an accurate and coherent response. 
            If you lack sufficient context, say you cannot answer.

            **Context:**
            {context}

            **User Question:**
            {question}

            **Response Format:**
            - If you can answer, provide a well-structured response.
            - If not, respond: "I'm sorry, but I don't have enough information to answer."
            - Generation language: ENGLISH.
            - !IMPORTANT: generate a response in HTML div format !.
            """
        )
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        return LLMChain(
            llm=self.generation_model2.llm,
            prompt=prompt
        )


    
    def ask(self, question: str) -> dict:
        # Retrieve relevant documents for current and prior queries
        retrieved_docs_current = self.retriever.get_relevant_documents(question)
        retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs_current])
        
        # Retrieve context from previous queries if available
        previous_query = self.history[-1]['reformulated_query'] if self.history else ""
        retrieved_docs_previous = self.retriever.get_relevant_documents(previous_query) if previous_query else []
        retrieved_context += "\n" + "\n".join([doc.page_content for doc in retrieved_docs_previous])
        
        # Reformulate the query considering conversation history and retrieved context
        reformulated_query = self.query_handling_chain.invoke({
            "question": question,
            "chat_history": self.get_history_for_prompt(),
            "retrieved_context": retrieved_context
        })
        reformulated_query = reformulated_query["text"].strip()
        
        if "OUT_OF_CONTEXT_QUESTION" in reformulated_query:
            response = self.clarify_response(reformulated_query)
            retrieved_docs = retrieved_docs_current + retrieved_docs_previous

        else:
            # Retrieve relevant documents for reformulated queries
            retrieved_docs_reformulated = self.retriever.get_relevant_documents(reformulated_query)
            retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs_reformulated])
            
            result = self.qa_chain.invoke({"question": reformulated_query, "context": retrieved_context})
            response = result["text"].strip()
            retrieved_docs = retrieved_docs_reformulated
        
        interaction_json = self.log_interaction(question, reformulated_query, response, retrieved_docs)
        self.add_to_history(question, response, reformulated_query)
        return interaction_json

    def add_to_history(self, question: str, answer: str, reformulated_query=None) -> None:
        # Limit history size based on `max_history`
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append({"original_question": question, "final_response": answer, "reformulated_query": reformulated_query})

    def get_history_for_prompt(self) -> str:
        # Generate formatted history for prompt
        return "\n".join(f"User: {entry['original_question']}\nAssistant: {entry['final_response']}" for entry in self.history)

    def get_history(self):
        return self.history    
    
    def clarify_response(self, response: str) -> str:
        # Clean up the response by removing specific markers
        for marker in ["-----END_PROMPT-----", "Response:", "Answer:", "Assistant:", "Reformulated query:", "OUT_OF_CONTEXT_QUESTION:"]:
            if marker in response:
                response = response.split(marker)[-1].strip()
        
        return response
    
    def log_interaction(self, original_question: str, reformulated_query: str, response: str, retrieved_docs: Optional[List[Document]] = None) -> dict:
        # Log the interaction to a file
        entry = {
            "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M"),
            "original_question": original_question,
            "reformulated_query": reformulated_query,
            "final_response": response,
            "generation_model": self.generation_model2.modelName(),
            "embedding_model": self.embedding_model,
            "faiss_index": self.faiss_index,
        }

        if retrieved_docs:
            entry["retrieved_documents"] = [doc.page_content for doc in retrieved_docs]

        log_entries = []
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                log_entries = json.load(f)
                if not isinstance(log_entries, list):  
                    log_entries = []  # If the JSON is not a list, initialize a new one
        except (FileNotFoundError, json.JSONDecodeError):
            log_entries = []  # If the file doesn't exist or has invalid data, start fresh

        log_entries.append(entry)

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, ensure_ascii=False, indent=4)

        return entry
        
    def clear_history(self):
        self.history.clear()
