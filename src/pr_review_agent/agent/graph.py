import json
from rich import print
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from ..schemas import AgentState, ReviewResponse, ReviewRequest
from ..agent.client import GroqClient
from ..prompts import PLANNING_PROMPT, REVIEW_PROMPT
from ..tools.workspace import explore_workspace
from ..tools.web import search_web
from ..tools.terminal import run_command
from ..tools.git import git_diff

class ReviewGraph:
    def __init__(self, request: ReviewRequest, client: GroqClient):
        self.request = request
        self.client = client
        self.workflow = self._build_graph()
        
    def _build_graph(self) -> Any:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("plan", self.plan_step)
        workflow.add_node("execute_tools", self.execute_tools_step)
        workflow.add_node("review", self.review_step)
        
        # Set entry point
        workflow.set_entry_point("plan")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "plan",
            self.should_continue,
            {
                "tools": "execute_tools",
                "review": "review"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_tools",
            self.check_iteration,
            {
                "continue": "plan",
                "end": "review"
            }
        )
        
        workflow.add_edge("review", END)
        
        return workflow.compile()

    def compile(self):
        return self.workflow

    def plan_step(self, state: AgentState) -> Dict[str, Any]:
        """
        Planning step: decide what to do next.
        """
        if self.request.settings.verbose:
            print("\n[bold cyan]─── Planning ───[/bold cyan]")
            
        prompt = PLANNING_PROMPT.format(
            diff=state.diff,
            changed_files=state.changed_files,
            repo_facts=state.repo_facts,
            observations=state.tool_observations
        )
        response_str = self.client.chat_completion(
            [{"role": "user", "content": prompt}]
        )
        plan = json.loads(response_str)
        
        if self.request.settings.verbose:
            print(f"[dim]Hypotheses:[/dim] {plan.get('hypotheses', [])}")
            print(f"[dim]Tools:[/dim] {json.dumps(plan.get('tools', []), indent=2)}")
        
        updates: Dict[str, Any] = {
            "hypotheses": plan.get("hypotheses", []),
            "candidates": plan.get("tools", []) 
        }
        return updates

    def execute_tools_step(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute selected tools.
        """
        tools_to_run = state.candidates
        new_observations = []
        
        if self.request.settings.verbose:
            print(f"\n[bold cyan]─── Executing {len(tools_to_run)} Tool(s) ───[/bold cyan]")
        
        for tool_call in tools_to_run:
            name = tool_call["name"]
            args = tool_call.get("args", {})
            
            if self.request.settings.verbose:
                print(f"[bold] Running:[/bold] {name} {args}")
            
            observation = {"tool": name, "args": args}
            
            try:
                result = None
                if name == "explore_workspace":
                    result = explore_workspace.invoke(args)
                elif name == "search_web":
                    result = search_web.invoke(args)
                elif name == "run_command":
                    # Inject unsafe_mode from settings
                    args["unsafe_mode"] = self.request.settings.unsafe_mode
                    result = run_command.invoke(args)
                elif name == "git_diff":
                    result = git_diff.invoke(args)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                observation["result"] = result
                
                if self.request.settings.verbose:
                    # Truncate long outputs for readability
                    res_str = str(result)
                    if len(res_str) > 500:
                        res_str = res_str[:500] + "... [truncated]"
                    print(f"[green] Result:[/green] {res_str}")
                    
            except Exception as e:
                observation["result"] = {"error": str(e)}
                if self.request.settings.verbose:
                    print(f"[red] Error:[/red] {str(e)}")
                
            new_observations.append(observation)
        
        return {
            "tool_observations": state.tool_observations + new_observations,
            "iteration": state.iteration + 1
        }

    def review_step(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate final review.
        """
        if self.request.settings.verbose:
            print("\n[bold cyan]─── Generating Review ───[/bold cyan]")
            
        prompt = REVIEW_PROMPT.format(
            diff=state.diff,
            observations=state.tool_observations,
            reflections=state.reflections
        )
        response_str = self.client.chat_completion(
            [{"role": "user", "content": prompt}]
        )
        data = json.loads(response_str)
        review = ReviewResponse(**data)
        
        if self.request.settings.verbose:
            print(f"[dim]Generated {len(review.comments)} comments.[/dim]")
        
        return {"review_draft": review}

    def should_continue(self, state: AgentState) -> Literal["tools", "review"]:
        """
        Determine if we should run tools or go to review.
        """
        if state.candidates:  # logic: if plan has tools
            return "tools"
        return "review"

    def check_iteration(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Check if we exceeded max iterations.
        """
        if state.iteration < self.request.settings.max_iters:
            return "continue"
        
        if self.request.settings.verbose:
            print("[yellow]Max iterations reached. Proceeding to review.[/yellow]")
        return "end"
