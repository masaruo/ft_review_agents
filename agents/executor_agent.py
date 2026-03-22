import sys
import os
import subprocess
import json
from langchain_core.prompts import PromptTemplate

def _generate_commands(state, llm) -> list:
    template = """
あなたは42スクールのコード動的検証スクリプト生成エージェントです。
以下のプロジェクト要件（ルール）とソースコードから、対象プログラムを動的にテストするためのシェルコマンド（ビルド、実行、テスト等）を提案してください。

出力は、JSONフォーマットの文字列配列のみとしてください。それ以外の余計なテキストは一切不要です。
例:
["make re", "valgrind ./a.out arg1", "make fclean"]

【プロジェクト要件】
{extracted_rules}

【ソースコードの一部または概要】
{source_code}
"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    # We truncate the source code to avoid context limits if necessary, though LLM context usually handles it
    source_preview = state.get("source_code", "")[:4000]
    res = chain.invoke({
        "extracted_rules": state.get("extracted_rules", ""),
        "source_code": source_preview
    })
    
    content = res.content if hasattr(res, "content") else str(res)
    # Extract JSON array from LLM response
    import re
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    # Basic fallback
    return ["make", "make test"]

def _summarize_execution(raw_log: str, llm) -> str:
    template = """
あなたは42スクールの動的テスト解析エンジニアです。
以下のシェルコマンドの実行ログから、重要な結果を抽出し、以下のフォーマットでマークダウン要約レポートを作成してください。

#### [致命的]
(コンパイルエラー、SEGV、メモリリーク等)
#### [規約・警告]
(コンパイラのWarning等の細かな問題)
#### [テスト情報]
(正常に完了したテスト・コマンド)

余計な挨拶は不要です。該当する問題がないセクションは「特になし」など簡潔にしてください。

【実行ログ】
{raw_log}
"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    log_preview = raw_log[-12000:]
    res = chain.invoke({"raw_log": log_preview})
    return res.content if hasattr(res, "content") else str(res)

def executor_node(state, llm):
    target_dir = state["target_dir"]
    
    print(f"[Executor Agent] Generating test commands for {target_dir}...")
    commands = _generate_commands(state, llm)
    
    if not commands:
         commands = ["make"]

    results = []
    print(f"[Executor Agent] Planned commands: {commands}")
    for cmd in commands:
        summary = f"--- Executing: {cmd} ---\n"
        print(summary.strip())
        try:
            # We run in the target directory
            # timeout prevents infinite loops in student code
            process = subprocess.run(
                cmd, 
                shell=True, 
                cwd=target_dir, 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            stdout = process.stdout if process.stdout else ""
            stderr = process.stderr if process.stderr else ""
            summary += stdout + "\n"
            summary += stderr + "\n"
            summary += f"Exit status: {process.returncode}\n"
        except subprocess.TimeoutExpired:
            summary += "Command timed out after 15 seconds.\n"
        except Exception as e:
            summary += f"Execution error: {e}\n"
        
        results.append(summary)
    
    execution_results = "\n".join(results)
    print(f"[Executor Agent] Summarizing execution results...")
    summarized_results = _summarize_execution(execution_results, llm)
    
    return {
        "execution_results": summarized_results
    }
