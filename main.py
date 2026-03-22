import sys
import os
import argparse
from rich.console import Console

# Add current directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.subject_context import load_subject_context
from graph import build_review_graph

console = Console()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="42 Multi-Agent Code Review")
    parser.add_argument("--path", type=str, required=True, help="Target directory to review (mounted as /workspace in Docker)")
    parser.add_argument("--type", type=str, nargs='+', default=[".py"], help="File extensions to review (e.g., .c .h)")
    parser.add_argument("--project", type=str, default="", help="Optional project name to load Subject RAG")
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    target_dir = args.path
    file_type = args.type
    project_name = args.project

    if not os.path.exists(target_dir):
        console.print(f"[bold red]Error: Directory '{target_dir}' not found.[/bold red]")
        sys.exit(1)

    console.print(f"[bold green]Starting Code Review for:[/bold green] {target_dir}")
    

    # Subject Context
    subject_text = ""
    if project_name:
        console.print(f"[bold yellow]Loading subject context for {project_name}...[/bold yellow]")
        subject_text = load_subject_context(project_name)

    # 3. Code Review
    console.print("[bold yellow]Initializing AI Review Graph...[/bold yellow]")
    try:
        review_graph, reviewer_chain = build_review_graph()
        
        initial_state = {
            "target_dir": target_dir,
            "file_type": file_type,
            "subject_text": subject_text
        }
        
        # Run graph
        console.print("[bold yellow]Running Agents (Subject -> Analyzer -> Executor)...[/bold yellow]")
        final_state = review_graph.invoke(initial_state)

        console.print("\n[bold cyan]--- AI Code Review Result ---[/bold cyan]\n")
        
        # Stream the final review
        full_review = ""
        for chunk in reviewer_chain.stream(final_state):
            print(chunk, end="", flush=True)
            full_review += chunk
            
        print() # Print a final newline
        output_dir = "output"
        # Save outcome to output folder
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, "review_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(full_review)
        console.print(f"\n[bold green]Report saved to: {report_path}[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]Error during AI code review:[/bold red] {e}")

    console.print("\n[bold blue]Code review complete.[/bold blue]")

if __name__ == "__main__":
    main()
