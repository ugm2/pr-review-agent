from typing import Dict, Any, List, Optional, Annotated

# NOTE: These tools are deprecated in favor of the dynamic `terminal` and `workspace` tools.
# They are kept here temporarily for reference or potential future utility usage.

def run_pytest(repo_root: Annotated[str, "Root directory of the repository"], timeout: int = 60) -> Dict[str, Any]:
    """Deprecated."""
    return {"error": "Use run_command instead"}

def run_ruff(repo_root: Annotated[str, "Root directory of the repository"], timeout: int = 30) -> Dict[str, Any]:
    """Deprecated."""
    return {"error": "Use run_command instead"}

def run_mypy(repo_root: Annotated[str, "Root directory of the repository"], timeout: int = 60) -> Dict[str, Any]:
    """Deprecated."""
    return {"error": "Use run_command instead"}

def ripgrep(
    repo_root: Annotated[str, "Root directory of the repository"],
    query: Annotated[str, "Search query/pattern to find in code"],
    paths: Optional[List[str]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """Deprecated."""
    return {"error": "Use run_command instead"}

