JV_HF_TOKEN = "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"
RS_HF_TOKEN = "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"
HF_TOKEN = RS_HF_TOKEN


JV_GEMINI_TOKEN = "AIzaSyArDcTFUTzztpgCIlogXSYQwBhUieZxv7Y"
RS_GEMINI_TOKEN = "AIzaSyAS0kVBJkyFyosoCwqAQyJM0ElyKEzrmgM"
VM_GEMINI_TOKEN = "AIzaSyD22Kr3nfSrvkE45KJlbIZHLuTA_cYuBYM"
GEMINI_TOKEN = VM_GEMINI_TOKEN


JV_COHERE_TOKEN = "XjJ6nkqZabaMHpq4aehIfyyksudq5LSm80QvUqcV"
COHERE_TOKEN = JV_COHERE_TOKEN

##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------------
class GoogleGemini:
    def __init__(self, api_key=GEMINI_TOKEN):
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            api_key=api_key
        )
    
    def modelName(self):
        return "gemini-2.0-flash"
##------------------------------------------------------------------------------------------
class CohereCommandRPlus:
    def __init__(self, api_key):
        from langchain_cohere.chat_models import ChatCohere
        self.llm = ChatCohere(
            model="command-r-plus-04-2024",
            temperature=0.7,
            cohere_api_key=api_key
        )
    
    def modelName(self):
        return "command-r-plus-04-2024"
##------------------------------------------------------------------------------------------
class AnthropicClaude:
    def __init__(self, api_key):
        from langchain_anthropic import ChatAnthropic
        self.llm = ChatAnthropic(
            model="claude-3-7-sonnet-20250219",
            temperature=0.5,
            anthropic_api_key=api_key
        )
    
    def modelName(self):
        return "claude-3-7-sonnet-20250219"
##------------------------------------------------------------------------------------------
class HuggingFaceModel:
    def __init__(self, model_name, api_key):
        from langchain_huggingface import ChatHuggingFace
        self.llm = ChatHuggingFace(
            model=model_name,
            temperature=0.7,
            huggingface_api_key=api_key
        )
        self.model_name = model_name
    
    def modelName(self):
        return self.model_name
##------------------------------------------------------------------------------------------