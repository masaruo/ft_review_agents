from langchain_core.prompts import PromptTemplate

def subject_node(state, llm):
    subject_text = state.get("subject_text", "")
    if not subject_text:
        return {"extracted_rules": "No subject provided. Proceed with general 42 programming guidelines."}
        
    template = """
以下の42プロジェクトの要件（Subject）から、「絶対に守るべき必須要件」「禁止関数リスト」「その他特別な制約」だけを箇条書きで抽出してください。余計な挨拶や解説は不要です。

{subject_text}
"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    res = chain.invoke({"subject_text": subject_text})
    
    return {"extracted_rules": res.content if hasattr(res, "content") else str(res)}
