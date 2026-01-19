import subprocess
from typing import Dict, Any, Annotated
from langchain_core.tools import tool

@tool
def run_command(
    command: Annotated[str, "The shell command to execute"], 
    repo_root: Annotated[str, "Root directory of the repository"] = ".",
    timeout: int = 120,
    unsafe_mode: bool = False
) -> Dict[str, Any]:
    """
    Execute a shell command in the repository.
    
    Args:
        command: The full command string to execute (e.g. "pytest -v", "npm test")
        repo_root: Path to the repository root directory (default: ".")
        timeout: Maximum execution time in seconds
        unsafe_mode: If True, bypass security checks (default: False)
        
    Returns:
        Dictionary with exit_code, stdout, and stderr
    """
    try:
        # Security Check
        if not unsafe_mode:
            is_valid, reason = SecurityManager.validate(command)
            if not is_valid:
                return {"error": f"Security Error: {reason}. Use --unsafe to override if you are sure."}

        result = subprocess.run(
            command, 
            cwd=repo_root, 
            shell=True,
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out. Hint: Interactive prompt detected? Try adding '--yes' or '-y' to automatically confirm prompts."}
    except Exception as e:
        return {"error": str(e)}

class SecurityManager:
    DENIED_PATTERNS = [
        ">", "|", ";", "&", # Shell operators
        "rm ", "mv ", "sudo", "chmod", "chown", "dd ", ":(){:|:&};:" # Harmful commands
    ]

    @staticmethod
    def validate(command: str) -> tuple[bool, str]:
        cmd_str = command.strip()
        
        # 1. Check for denied patterns
        for pattern in SecurityManager.DENIED_PATTERNS:
            if pattern in cmd_str:
                return False, f"Forbidden pattern '{pattern}' detected"
             
        return True, "OK"
