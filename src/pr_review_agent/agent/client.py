from typing import List, Dict
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from dotenv import load_dotenv
from ..config import AgentConfig

load_dotenv()

class GroqClient:
    def __init__(self, model: str = "qwen/qwen3-32b,llama-3.3-70b-versatile,llama-3.1-8b-instant"):
        self.config = AgentConfig()
        # Parse comma-separated models
        self.models = [m.strip() for m in model.split(",")]
        self.current_model_index = 0
        # Initialize with the first model
        self.model = self.models[0]

    def _get_llm(self, model: str, temperature: float = 0.1):
        return ChatGroq(
            model=model,
            api_key=SecretStr(self.config.groq_api_key) if self.config.groq_api_key else None,
            temperature=temperature
        )

    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        json_mode: bool = True,
        temperature: float = 0.1
    ) -> str:
        """
        Send a chat completion request to Groq using LangChain with fallback.
        """
        lc_messages: List[BaseMessage] = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        
        # Try models in order starting from the current preference
        # We don't reset index on every call to avoid "flapping", 
        # but if we wanted to always try best model first, we would iter from 0.
        # Logic: iterate from 0 to end. If 0 fails, we try 1. 
        # Note: If we want to prioritize the *best* model, we should always start from 0.
        # User request: "tries the next model" implies fallback chain for THIS request.
        
        errors = []
        for model in self.models:
            try:
                llm = self._get_llm(model, temperature)
                chain = llm
                
                if json_mode:
                    chain = chain.bind(response_format={"type": "json_object"})
                    
                response = chain.invoke(lc_messages)
                return str(response.content)
                
            except Exception as e:
                error_str = str(e)
                # Check for rate limit indicators
                is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower() or "too many requests" in error_str.lower()
                
                if is_rate_limit:
                    print(f"⚠️ Rate limit hit for {model}. Trying next model...")
                    errors.append(f"{model}: {error_str}")
                    continue
                else:
                    # Non-rate-limit error (e.g. context length, invalid request) -> Raise immediately
                    raise e
        
        # If we get here, all models failed
        raise Exception(f"All models failed due to rate limits. Errors: {errors}")

