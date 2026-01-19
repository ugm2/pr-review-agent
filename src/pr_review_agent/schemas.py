from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

# --- Input Schemas ---

class ModelSettings(BaseModel):
    model: str = "qwen/qwen3-32b,llama-3.3-70b-versatile,llama-3.1-8b-instant"
    max_iters: int = 7
    enable_tools: bool = True
    enable_tot: bool = False
    strictness: Literal["low", "med", "high"] = "med"
    verbose: bool = False
    unsafe_mode: bool = False

class ReviewRequest(BaseModel):
    repo_root: str
    mode: Literal["staged", "unstaged", "working-tree", "branch", "commit-range"]
    base_ref: Optional[str] = None
    head_ref: Optional[str] = None
    diff: str
    settings: ModelSettings = Field(default_factory=ModelSettings)

# --- Output Schemas ---

class CommentSeverity(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReviewComment(BaseModel):
    file: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    evidence: Optional[str] = None
    suggestion: Optional[str] = None

class FilePatch(BaseModel):
    file: str
    unified_diff: str

class ReviewResponse(BaseModel):
    summary: List[str]
    comments: List[ReviewComment]
    patches: Optional[List[FilePatch]] = None
    tool_results: Optional[Dict[str, Any]] = None
    reflections: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Agent State ---

class AgentState(BaseModel):
    diff: str
    changed_files: List[str] = Field(default_factory=list)
    repo_facts: Dict[str, Any] = Field(default_factory=dict)
    tool_observations: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    review_draft: Optional[ReviewResponse] = None
    verification_report: Optional[str] = None
    reflections: List[str] = Field(default_factory=list)
    memory_read: List[str] = Field(default_factory=list)
    memory_write: List[str] = Field(default_factory=list)
    iteration: int = 0
