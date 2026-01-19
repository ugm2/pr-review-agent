"""Configuration for LangSmith tracing and LangGraph."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class LangSmithConfig:
    """Configuration for LangSmith tracing."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        self.api_key = api_key or os.getenv("LANGSMITH_API_KEY")
        self.project = project or os.getenv("LANGSMITH_PROJECT", "pr-review-agent")
        
        # Enable tracing if API key is present and not explicitly disabled
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = bool(self.api_key) and os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    
    def configure(self):
        """Apply LangSmith configuration to environment."""
        if self.enabled and self.api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.api_key
            os.environ["LANGCHAIN_PROJECT"] = self.project
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
    
    @property
    def is_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled."""
        return self.enabled and bool(self.api_key)


class AgentConfig:
    """Configuration for the PR review agent."""
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        langsmith: Optional[LangSmithConfig] = None
    ):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.langsmith = langsmith or LangSmithConfig()
        self.langsmith.configure()
