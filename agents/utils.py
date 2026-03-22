import os

def gather_source_code(target_dir: str, file_type: list | tuple | str = ".py") -> str:
    """Collect source and headers files from the target directory, prioritizing root files."""
    if isinstance(file_type, str):
        file_type = (file_type,)
    elif isinstance(file_type, list):
        file_type = tuple(file_type)

    file_paths = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(file_type) or file == "Makefile":
                full_path = os.path.join(root, file)
                file_paths.append(full_path)
                
    # Sort by directory depth to prioritize root/main files over large subdirectories like libft/
    file_paths.sort(key=lambda p: (os.path.relpath(p, target_dir).count(os.sep), p))

    total_content = ""
    for file_path in file_paths:
        rel_path = os.path.relpath(file_path, target_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                chunk = f"--- File: {rel_path} ---\n{content}\n"
                # Truncate at ~40000 chars total to avoid context window explosion (~10k tokens)
                if len(total_content) + len(chunk) > 40000:
                    total_content += f"--- File: {rel_path} ---\n[TRUNCATED due to maximum context length]\n"
                    continue
                total_content += chunk
        except Exception as e:
            total_content += f"--- File: {rel_path} ---\nError reading file: {e}\n"
                    
    return total_content
