import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.subject_agent import subject_node
from agents.analyzer_agent import analyzer_node
from agents.executor_agent import executor_node
from agents.reviewer_agent import get_reviewer_chain

class ReviewState(TypedDict):
    target_dir: str
    file_type: list
    subject_text: str
    extracted_rules: str
    source_code: str
    analysis_results: str
    execution_results: str
    adhoc_instructions: str
    review_folders: list

def get_llm():
    if os.environ.get("OPENAI_API_KEY"):
        print("using OPENAI")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    else:
        print("using Ollama")
        from langchain_ollama import ChatOllama
        ollama_host = os.environ.get("OLLAMA_HOST") or "http://host.docker.internal:11434"
        model_name = os.environ.get("OLLAMA_MODEL") or "qwen2.5-coder:7b"
        return ChatOllama(
            model=model_name, 
            base_url=ollama_host, 
            temperature=0.3,
            num_ctx=8192,
            repeat_penalty=1.1
        )

def build_review_graph():
    llm = get_llm()
    
    # Wrap nodes with the initialized LLM
    def s_node(state): return subject_node(state, llm)
    def a_node(state): return analyzer_node(state, llm)
    def e_node(state): return executor_node(state, llm)
    
    graph = StateGraph(ReviewState)
    graph.add_node("subject", s_node)
    graph.add_node("analyzer", a_node)
    graph.add_node("executor", e_node)
    
    graph.set_entry_point("subject")
    
    # 順番実行 (Sequential)
    graph.add_edge("subject", "analyzer")
    graph.add_edge("analyzer", "executor")
    graph.add_edge("executor", END)
    
    compiled = graph.compile()
    reviewer_chain = get_reviewer_chain(llm)
    return compiled, reviewer_chain
