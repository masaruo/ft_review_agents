import sys
import os
import argparse
from rich.console import Console
from pathlib import Path

# Add current directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.subject_context import load_subject_context
from graph import build_review_graph

console = Console()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="42 Multi-Agent Code Review")
    # parser.add_argument("--path", type=str, default="", help="Target directory to review (mounted as /workspace in Docker)")
    parser.add_argument("--type", type=str, nargs='+', default=[".py"], help="File extensions to review (e.g., .c .h)")
    parser.add_argument("--folders", type=str, nargs='*', default=[], help="Specific subdirectories to review (e.g., srcs includes)")
    # parser.add_argument("--project", type=str, default="", help="Optional project name to load Subject RAG")
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    # import shutil

    host_dir: Path = Path("target")
    if not host_dir.exists():
        console.print(f"[bold red]Error: Directory '{host_dir}' not found.[/bold red]")
        sys.exit(1)

    file_type: list[str] = args.type
    folders: list[Path] = [Path(dir) for dir in args.folders]

    console.print(f"[bold green]Starting Code Review for:[/bold green] {host_dir} ")

    # Copy files to internal sandbox to avoid macOS bind mount privilege issues during dynamic updates
    # target_dir = "/sandbox"
    # console.print(f"[bold yellow]Copying files to internal sandbox to bypass macOS/Docker privilege issues...[/bold yellow]")
    # if os.path.exists(target_dir):
    #     shutil.rmtree(target_dir)
    # try:
    #     shutil.copytree(host_dir, target_dir, ignore=shutil.ignore_patterns(".git", "output"))
    # except Exception as e:
    #     console.print(f"[bold red]Error copying files to sandbox: {e}[/bold red]")
    #     sys.exit(1)

    # Subject Context
    subject_text = ""
    project_name = getattr(args, "project", None)
    if project_name:
        console.print(f"[bold yellow]Loading subject context for {project_name}...[/bold yellow]")
        subject_text = load_subject_context(project_name)

    # Adhoc Instructions
    adhoc_instructions = ""
    agent_root = os.path.dirname(os.path.abspath(__file__))
    instructions_path = os.path.join(agent_root, "instructions.md")
    if os.path.exists(instructions_path):
        console.print(f"[bold yellow]Loading adhoc instructions from {instructions_path}...[/bold yellow]")
        with open(instructions_path, "r", encoding="utf-8") as f:
            adhoc_instructions = f.read()

    # 3. Code Review
    console.print("[bold yellow]Initializing AI Review Graph...[/bold yellow]")
    try:
        review_graph, reviewer_chain = build_review_graph()

        initial_state = {
            "target_dir": str(host_dir),
            "file_type": file_type,
            "subject_text": subject_text,
            "adhoc_instructions": adhoc_instructions,
            "review_folders": args.folders
        }

        # Run graph
        console.print("[bold yellow]Running Agents (Subject -> Analyzer -> Executor)...[/bold yellow]")
        final_state = review_graph.invoke(initial_state)

        console.print(f"\n[bold magenta]--- [DEBUG] Static Analysis Output Length: {len(final_state.get('analysis_results', ''))} chars ---[/bold magenta]")
        console.print(f"[bold magenta]--- [DEBUG] Dynamic Analysis Output Length: {len(final_state.get('execution_results', ''))} chars ---[/bold magenta]\n")

        console.print("\n[bold cyan]--- AI Code Review Result ---[/bold cyan]\n")

        # Stream the final review
        full_review = ""
        for chunk in reviewer_chain.stream(final_state):
            print(chunk, end="", flush=True)
            full_review += chunk

        print() # Print a final newline
        # Save outcome to output folder on the host machine so it persists
        # Save outcome to output folder on the host machine so it persists
        output_dir = os.path.join(host_dir, "output")

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
