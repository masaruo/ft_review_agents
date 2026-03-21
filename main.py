import sys
import os
import argparse
from rich.console import Console

# Add current directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reviewer import CodeReviewer
from tools.makefile_parser import check_makefile_flags
from rag.subject_context import load_subject_context

console = Console()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="42 Code Review Agent")
    parser.add_argument("--path", type=str, required=True, help="Target directory to review (mounted as /workspace in Docker)")
    parser.add_argument("--type", type=str, default=".py", help="File extension to review (e.g., .c, .py)")
    # parser.add_argument("--project", type=str, default="", help="Optional project name to load Subject RAG")
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    target_dir = args.path
    file_type = args.type
    # project_name = args.project

    if not os.path.exists(target_dir):
        console.print(f"[bold red]Error: Directory '{target_dir}' not found.[/bold red]")
        sys.exit(1)

    console.print(f"[bold green]Starting Code Review for:[/bold green] {target_dir}")
    
    # 1. Check Makefile
    console.print("[bold yellow]Checking Makefile...[/bold yellow]")
    makefile_status = check_makefile_flags(target_dir)
    console.print(makefile_status)

    # 2. Subject Context
    subject_context = ""
    if project_name:
        console.print(f"[bold yellow]Loading subject context for {project_name}...[/bold yellow]")
        subject_context = load_subject_context(project_name)

    # 3. Code Review
    console.print("[bold yellow]Initializing AI Reviewer...[/bold yellow]")
    reviewer = CodeReviewer(target_dir, file_type)
    
    console.print("[bold yellow]Generating Review (Streaming)...[/bold yellow]")
    try:
        console.print("\n[bold cyan]--- AI Code Review Result ---[/bold cyan]\n")
        
        # Stream the output chunk by chunk to prevent the process from looking hung
        for chunk in reviewer.review_stream(subject_context):
            print(chunk, end="", flush=True)
            
        print() # Print a final newlinear
    except Exception as e:
        console.print(f"\n[bold red]Error during AI code review:[/bold red] {e}")

    console.print("\n[bold blue]Code review complete.[/bold blue]")

if __name__ == "__main__":
    main()
