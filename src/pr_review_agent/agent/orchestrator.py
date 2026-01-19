from ..schemas import AgentState, ReviewRequest, ReviewResponse
from .client import GroqClient
from ..tools import get_changed_files
from .graph import ReviewGraph

class ReviewOrchestrator:
    def __init__(self, request: ReviewRequest, client: GroqClient):
        self.request = request
        self.client = client
        # Initialize state to pass to graph
        self.initial_state = AgentState(
            diff=request.diff,
            changed_files=get_changed_files.invoke({
                "repo_root": request.repo_root, 
                "mode": request.mode, 
                "base_ref": request.base_ref, 
                "head_ref": request.head_ref
            }),
            iteration=0
        )
        self.graph = ReviewGraph(request, client)

    def run(self) -> ReviewResponse:
        """
        Run the full ReAct loop via LangGraph.
        """
        # Execute the graph
        final_state = self.graph.workflow.invoke(self.initial_state)
        
        # Extract the review from the final state
        if final_state.get("review_draft"):
            return final_state["review_draft"]
            
        # Fallback if something went wrong
        return ReviewResponse(
            summary=["Error: No review generated"],
            comments=[]
        )

