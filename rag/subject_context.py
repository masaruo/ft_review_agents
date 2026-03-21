import os
from langchain_community.document_loaders import PyPDFLoader

def load_subject_context(project_name: str) -> str:
    """Load subject PDF if it exists in a subjects/ directory."""
    subject_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "subjects", f"{project_name}.pdf")
    
    if os.path.exists(subject_file):
        try:
            loader = PyPDFLoader(subject_file)
            pages = loader.load()
            return "\n".join([page.page_content for page in pages])
        except Exception as e:
            return f"Error loading PDF: {e}"
            
    return ""
