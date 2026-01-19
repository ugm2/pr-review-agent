import subprocess
from typing import Optional, Annotated
from langchain_core.tools import tool

@tool
def git_diff(
    repo_root: Annotated[str, "Root directory of the repository"],
    mode: Annotated[str, "Diff mode: staged, unstaged, working-tree, branch, commit-range"] = "staged",
    base_ref: Annotated[Optional[str], "Base reference for diff (branch or commit)"] = None,
    head_ref: Annotated[Optional[str], "Head reference for diff (required for commit-range)"] = None
) -> str:
    """
    Get git diff based on the specified mode.
    
    Modes:
    - staged: Only staged changes (git diff --cached)
    - unstaged: Only unstaged changes (git diff)
    - working-tree: All uncommitted changes, staged + unstaged (git diff HEAD)
    - branch: Changes compared to a branch
    - commit-range: Changes between two commits
    """
    cmd = ["git", "-C", repo_root, "diff"]
    
    if mode == "staged":
        cmd.append("--cached")
    elif mode == "unstaged":
        # Default git diff shows unstaged changes
        pass
    elif mode == "working-tree":
        # Compare working tree to HEAD (all uncommitted changes)
        cmd.append("HEAD")
    elif mode == "branch":
        if not base_ref:
            base_ref = "main" # default
        cmd.append(base_ref)
    elif mode == "commit-range":
        if not base_ref or not head_ref:
            raise ValueError("base_ref and head_ref are required for commit-range mode")
        cmd.append(f"{base_ref}..{head_ref}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout

@tool
def get_changed_files(
    repo_root: Annotated[str, "Root directory of the repository"],
    mode: Annotated[str, "Diff mode: staged, unstaged, working-tree, branch, commit-range"] = "staged",
    base_ref: Annotated[Optional[str], "Base reference for diff"] = None,
    head_ref: Annotated[Optional[str], "Head reference for diff"] = None
) -> list[str]:
    """
    Get a list of changed files.
    """
    cmd = ["git", "-C", repo_root, "diff", "--name-only"]
    
    if mode == "staged":
        cmd.append("--cached")
    elif mode == "unstaged":
        # Default git diff shows unstaged changes
        pass
    elif mode == "working-tree":
        # Compare working tree to HEAD (all uncommitted changes)
        cmd.append("HEAD")
    elif mode == "branch":
        if not base_ref:
            base_ref = "main"
        cmd.append(base_ref)
    elif mode == "commit-range":
        cmd.append(f"{base_ref}..{head_ref}")
        
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [f for f in result.stdout.split("\n") if f.strip()]
