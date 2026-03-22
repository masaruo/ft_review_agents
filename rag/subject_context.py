import os
from langchain_community.document_loaders import PyPDFLoader

def load_subject_context(project_or_path: str) -> str:
    """Load subject PDF from absolute/relative path or from subjects/ directory."""
    if os.path.isfile(project_or_path):
        subject_file = project_or_path

    if os.path.exists(subject_file):
        try:
            loader = PyPDFLoader(subject_file)
            pages = loader.load()
            print(f"loading {subject_file}")
            return "\n".join([page.page_content for page in pages])
        except Exception as e:
            return f"Error loading PDF: {e}"
            
    return ""
