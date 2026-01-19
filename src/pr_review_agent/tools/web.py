from typing import Annotated
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def search_web(query: Annotated[str, "The search query to find command usage or error solutions"]) -> str:
    """
    Search the web for information about how to run commands, fix errors, or understand libraries.
    
    Args:
        query: The search query
        
    Returns:
        Search results summary
    """
    try:
        search = DuckDuckGoSearchRun()
        return search.invoke(query)
    except Exception as e:
        return f"Search failed: {str(e)}"
