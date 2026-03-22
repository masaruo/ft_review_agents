from langchain_core.prompts import PromptTemplate
from agents.utils import gather_source_code

def analyzer_node(state, llm):
    target_dir = state["target_dir"]
    file_type = state["file_type"]
    extracted_rules = state.get("extracted_rules", "")
    
    source_code = gather_source_code(target_dir, file_type)

    template = """
あなたは42スクールのコード解析エージェントです。以下のソースコードにおいて、プロジェクト要件を満たしていない箇所（バグ、メモリリークの可能性、エラー処理漏れ、禁止関数の疑い）だけを簡潔に箇条書きでピックアップしてください。問題がないファイルは無視してください。重複は避けてください。

【プロジェクト要件】
{extracted_rules}

【ソースコード】
{source_code}
"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    res = chain.invoke({
        "extracted_rules": extracted_rules,
        "source_code": source_code
    })
    
    return {
        "source_code": source_code,
        "analysis_results": res.content if hasattr(res, "content") else str(res)
    }
