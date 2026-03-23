import os

def gather_source_files(target_dir: str, file_type: list | tuple | str = ".py", review_folders: list = None) -> dict[str, str]:
    """Collect source and headers files from the target directory and return a dictionary of {rel_path: content}."""
    if isinstance(file_type, str):
        file_type = (file_type,)
    elif isinstance(file_type, list):
        file_type = tuple(file_type)

    if not review_folders:
        directories_to_scan = [target_dir]
    else:
        directories_to_scan = [os.path.join(target_dir, f) for f in review_folders]

    file_paths = []
    for scan_dir in directories_to_scan:
        if not os.path.exists(scan_dir):
            continue
        if os.path.isfile(scan_dir):
            if scan_dir.endswith(file_type) or os.path.basename(scan_dir) == "Makefile":
                file_paths.append(scan_dir)
            continue
            
        for root, _, files in os.walk(scan_dir):
            for file in files:
                if file.endswith(file_type) or file == "Makefile":
                    full_path = os.path.join(root, file)
                    if full_path not in file_paths:
                        file_paths.append(full_path)
                
    # Sort by directory depth to prioritize root/main files over large subdirectories like libft/
    file_paths.sort(key=lambda p: (os.path.relpath(p, target_dir).count(os.sep), p))

    file_contents = {}
    for file_path in file_paths:
        rel_path = os.path.relpath(file_path, target_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_contents[rel_path] = content
        except Exception as e:
            file_contents[rel_path] = f"Error reading file: {e}"
                    
    return file_contents
