
class GoogleGemini():
    def __init__(self, api_key, model="gemini-2.0-flash", temperature=0.5, top_p=1.0, 
                 max_tokens=2048, frequency_penalty=0.0, presence_penalty=0.0):
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            api_key=api_key
        )
    
    def modelName(self):
        return self.llm.model
    
    

##------------------------------------------------------------------------------------------
class Cohere():
    def __init__(self, api_key, model="command-r-plus-04-2024", temperature=0.5, top_p=1.0, 
                 max_tokens=2048, frequency_penalty=0.0, presence_penalty=0.0):
        from langchain_cohere.chat_models import ChatCohere
        self.llm = ChatCohere(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            cohere_api_key=api_key
        )
    
    def modelName(self):
        return self.llm.model

##------------------------------------------------------------------------------------------
class Anthropic():
    def __init__(self, api_key, model="claude-3-7-sonnet-20250219", temperature=0.2, top_p=1.0, 
                 max_tokens=2048, frequency_penalty=0.0, presence_penalty=0.0):
        from langchain_anthropic import ChatAnthropic
        self.llm = ChatAnthropic(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            anthropic_api_key=api_key
        )
    
    def modelName(self):
        return self.llm.model

##------------------------------------------------------------------------------------------
class HuggingFaceModel():
    def __init__(self, model_name, api_key, temperature=0.2, top_p=1.0, max_tokens=2048, 
                 frequency_penalty=0.0, presence_penalty=0.0):
        from langchain_huggingface import ChatHuggingFace
        self.llm = ChatHuggingFace(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            huggingface_api_key=api_key
        )
        self.model_name = model_name
    
    def modelName(self):
        return self.model_name