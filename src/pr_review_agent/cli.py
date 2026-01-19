import typer
import os
from rich.console import Console
from rich.panel import Panel
from typing import Optional, cast, Any
from .schemas import ReviewRequest, ModelSettings
from .agent.client import GroqClient
from .agent.orchestrator import ReviewOrchestrator
from .tools.git import git_diff

app = typer.Typer()
console = Console()

@app.command()
def review(
    repo_root: str = typer.Option(os.getcwd(), help="Root directory of the repository"),
    mode: str = typer.Option("staged", help="Diff mode: staged, unstaged, working-tree, branch, commit-range"),
    base_ref: Optional[str] = typer.Option(None, help="Base reference for diff"),
    head_ref: Optional[str] = typer.Option(None, help="Head reference for diff"),
    model: str = typer.Option("qwen/qwen3-32b,llama-3.3-70b-versatile,llama-3.1-8b-instant", help="Comma-separated list of Groq models for fallback priority"),
    max_iters: int = typer.Option(7, help="Maximum number of ReAct iterations"),
    format: str = typer.Option("markdown", help="Output format: markdown, json"),
    trace: bool = typer.Option(False, "--trace", help="Enable LangSmith tracing"),
    project: str = typer.Option("pr-review-agent", "--project", help="LangSmith project name"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging"),
    unsafe: bool = typer.Option(False, "--unsafe", help="Disable security checks (DANGEROUS)"),
):
    """
    Run the PR Review Agent on a local diff.
    """
    # Configure LangSmith
    if trace:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = project
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = project
    
    try:
        # 1. Get the diff
        diff = git_diff.invoke({
            "repo_root": repo_root,
            "mode": mode,
            "base_ref": base_ref,
            "head_ref": head_ref
        })
        if not diff:
            console.print("[yellow]No changes detected.[/yellow]")
            return

        # 2. Prepare the request
        settings = ModelSettings(model=model, max_iters=max_iters, verbose=verbose, unsafe_mode=unsafe)
        request = ReviewRequest(
            repo_root=repo_root,
            mode=cast(Any, mode),
            base_ref=base_ref,
            head_ref=head_ref,
            diff=diff,
            settings=settings
        )

        # 3. Initialize Agent
        client = GroqClient(model=model)
        orchestrator = ReviewOrchestrator(request, client)

        # 4. Run Review
        with console.status("[bold green]Agent is reviewing the PR..."):
            response = orchestrator.run()

        # 5. Output results
        if format == "json":
            console.print(response.model_dump_json(indent=2))
        else:
            _render_markdown(response)
            
        # 6. Show trace info
        if trace:
            console.print(f"\n[dim]View trace at: https://smith.langchain.com/o/{os.getenv('LANGCHAIN_ORG_ID', 'default')}/projects/p/{project}[/dim]")


    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(code=1)

def _render_markdown(response):
    console.print(Panel("[bold]PR Review Summary[/bold]", style="cyan"))
    for s in response.summary:
        console.print(f"• {s}")
    console.print()

    if response.comments:
        console.print("[bold magenta]Review Comments[/bold magenta]")
        
        for comment in response.comments:
            severity_color = {
                "low": "blue",
                "medium": "yellow",
                "high": "red",
                "critical": "bold red reversed"
            }.get(comment.severity, "white")

            # Build the content of the panel
            content_parts = []
            
            # Message
            content_parts.append(f"[bold]{comment.message}[/bold]\n")
            
            # Evidence (if any)
            if comment.evidence:
                content_parts.append(f"[dim]Evidence:[/dim]\n[italic]{comment.evidence}[/italic]\n")
            
            # Suggestion (if any)
            if comment.suggestion:
                # Basic heuristic to detect language from suggestion or file extension
                # Ideally, we'd guess from file path, but keeping it simple for now or defaulting to python/text
                content_parts.append("[green]Suggestion:[/green]")
                content_parts.append(f"```\n{comment.suggestion}\n```")

            # Final assembly
            panel_content = "\n".join(content_parts)
            
            title = f"{comment.file}"
            if comment.start_line:
                title += f":{comment.start_line}"
                if comment.end_line and comment.end_line != comment.start_line:
                    title += f"-{comment.end_line}"

            console.print(Panel(
                panel_content,
                title=f"[{severity_color}] {comment.severity.upper()} [/] | {title}",
                border_style=severity_color.split(" ")[-1] if " " not in severity_color else "white", # simple fallback
                expand=False
            ))
            console.print() # spacer

if __name__ == "__main__":
    app()
