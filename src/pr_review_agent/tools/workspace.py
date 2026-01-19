import os
from typing import Dict, Any, Annotated
from langchain_core.tools import tool

@tool
def explore_workspace(repo_root: Annotated[str, "Root directory of the repository"] = ".") -> Dict[str, Any]:
    """
    List files in the repository root to help identifying the project structure.
    
    Args:
        repo_root: Path to the repository root directory (default: ".")
        
    Returns:
        Dictionary with a list of files and directories in the root.
    """
    try:
        # List all files and directories, including hidden ones (like ls -a)
        # We exclude .git to avoid clutter, but keep other config files.
        entries = os.listdir(repo_root)
        
        # Sort for deterministic output
        entries.sort()
        
        # Separate into files and dirs for better context
        files = []
        dirs = []
        
        for entry in entries:
            if entry == ".git":
                continue
                
            full_path = os.path.join(repo_root, entry)
            if os.path.isdir(full_path):
                dirs.append(entry + "/")
            else:
                files.append(entry)
                
        return {
            "root_contents": dirs + files,
            "message": "Analyze these files to determine the language and tools. You may need to read specific config files using 'run_command' (e.g. 'cat pyproject.toml')."
        }
    except Exception as e:
        return {"error": str(e)}
