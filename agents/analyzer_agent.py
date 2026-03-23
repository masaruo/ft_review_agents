from langchain_core.prompts import PromptTemplate
from agents.utils import gather_source_files
import concurrent.futures

def analyzer_node(state, llm):
    target_dir = state["target_dir"]
    file_type = state["file_type"]
    extracted_rules = state.get("extracted_rules", "")
    adhoc_instructions = state.get("adhoc_instructions", "")
    review_folders = state.get("review_folders", [])
    
    source_files = gather_source_files(target_dir, file_type, review_folders)

    template = """
あなたは42スクールのコード解析エージェントです。以下の単一ファイルのソースコードにおいて、プロジェクト要件を満たしていない箇所（バグ、メモリリークの可能性、エラー処理漏れ、禁止関数の疑い）を具体的に箇条書きでピックアップしてください。
指摘する際は「対象のコード・関数」と「なぜ問題なのか（具体的な理由）」をセットで必ず詳細に記述してください。
もし特に指摘する問題がない場合は、必ず「問題なし」という4文字のみを出力してください。それ以外の挨拶や説明は一切不要です。

【重要】
今渡されているのはプロジェクト内の「単一のファイルのみ」です。ヘッダーファイル（.hpp や .h）を解析する際、「関数の実装（中身）がない」という指摘は絶対にしないでください（実装は別の .cppファイル等にあるためです）。

【プロジェクト要件】
{extracted_rules}

【追加の指示 (Adhoc Instructions)】
{adhoc_instructions}

【対象ファイル】
{file_path}

【ソースコード】
{source_code}
"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    analysis_results_list = []
    print(f"[Analyzer Agent] Starting parallel static analysis for {len(source_files)} files...")
    
    def _analyze_file(file_item):
        path, content = file_item
        try:
            res = chain.invoke({
                "extracted_rules": extracted_rules,
                "adhoc_instructions": adhoc_instructions,
                "file_path": path,
                "source_code": content
            })
            out = res.content if hasattr(res, "content") else str(res)
            out_stripped = out.strip()
            
            # 軽微な返答や問題なしをフィルタリング
            if out_stripped != "問題なし" and "特になし" not in out_stripped and len(out_stripped) > 5:
                print(f"  -> [Pointed Out] {path}")
                return f"#### {path}\n{out_stripped}"
            else:
                print(f"  -> [OK] {path}")
                return None
        except Exception as e:
            print(f"  -> [Error] {path}: {e}")
            return None

    # 並列処理でAPIの待機時間を大幅に短縮
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(_analyze_file, source_files.items())
        for r in results:
            if r:
                analysis_results_list.append(r)
            
    final_analysis = "\n\n".join(analysis_results_list) if analysis_results_list else "特になし"
    
    # Store a preview of source_code for the executor agent
    source_preview = "\n".join(f"--- {k} ---\n{v}" for k, v in source_files.items())[:10000]

    return {
        "source_code": source_preview,
        "analysis_results": final_analysis
    }
