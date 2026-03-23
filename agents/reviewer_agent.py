from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_reviewer_chain(llm):
    template = """
あなたは42スクールの経験豊富な「Peer Reviewer」です。
提供された解析結果と要件に基づき、最終的なレビューレポートを生成してください。

### 1. 評価コンテキスト
- **プロジェクト要件**:
{extracted_rules}

- **追加の指示 (Adhoc Instructions)**:
{adhoc_instructions}

### 2. 解析結果（Analyzer Agentの出力: 静的解析）
{analysis_results}

### 3. 動的テスト実行結果（Executor Agentの出力）
{execution_results}

### 4. 出力フォーマット
以下の形式で、簡潔かつ建設的に回答してください。
なお、各指摘事項には、それがどちらの解析で見つかった問題かが分かるよう `(静的解析より)` または `(動的テストより)` と明記してください。

- **[致命的]**: 修正必須のバグ、メモリリーク、禁止関数、または実行時エラーやコンパイルエラー。
- **[規約]**: StyleやNorminetteに関する指摘。
- **[提案]**: ロジックの最適化や可読性向上案。
- **[総評]**: 合格に向けたアドバイス。

【制約】
- 重複した指摘は厳禁とする。
- 解析結果や実行結果に問題がないと書かれている領域については指摘しないこと。
- 実行時に成功しているテストについては、過剰に問題視しないこと。
- 【重要】問題を指摘する際、単にファイル名だけを羅列するのではなく、静的解析や動的テストで報告された「どの関数でどのような処理が抜けているか」「なぜメモリリークが発生しうるか」などの**具体的な理由やコードの詳細**を必ず出力に含めてください。
"""
    prompt = PromptTemplate.from_template(template)
    return prompt | llm | StrOutputParser()
