import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class CodeReviewer:
    def __init__(self, target_dir: str, file_type: str = ".py"):
        self.target_dir = target_dir
        self.file_type = file_type
        
        # Determine LLM usage parameter overrides
        if os.environ.get("OPENAI_API_KEY"):
            # If OPENAI_API_KEY is present, we prefer OpenAI
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        else:
            # Otherwise we use the local Ollama daemon
            # Use `or` to catch empty strings from Makefile
            ollama_host = os.environ.get("OLLAMA_HOST") or "http://host.docker.internal:11434"
            model_name = os.environ.get("OLLAMA_MODEL") or "qwen2.5-coder:7b"
            self.llm = ChatOllama(
                model=model_name, 
                base_url=ollama_host, 
                temperature=0.3,
                num_ctx=8192,
                repeat_penalty=1.1
            )

    def _gather_source_code(self) -> str:
        """Collect source and headers files from the target directory, prioritizing root files."""
        file_paths = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(self.file_type) or file == "Makefile":
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)
                    print(f"[DEBUG] Found file: {full_path}", flush=True)
                    
        # Sort by directory depth to prioritize root/main files over large subdirectories like libft/
        file_paths.sort(key=lambda p: (os.path.relpath(p, self.target_dir).count(os.sep), p))

        total_content = ""
        for file_path in file_paths:
            rel_path = os.path.relpath(file_path, self.target_dir)
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

    def review_stream(self, subject_context: str = ""):
        code_context = self._gather_source_code()
        template = """
あなたは42スクールの経験豊富な「Peer Reviewer」です。
提供されたコードを、42の厳格な基準（The Norm, Memory Management, Efficiency）に基づいて査読してください。

### 1. 評価対象のコンテキスト
- **プロジェクト名/要件**: {subject_context}
- **ファイル名/ソースコード**: {code_context}

### 2. レビューのガイドライン（優先順位順）
以下の順序で、論理的な欠陥がないか確認してください。

1. **Fatal Errors (即失格対象)**:
   - セグメンテーションフォルト、バスエラー、二重解放（Double Free）の可能性。
   - メモリリーク（mallocに対するfreeの不足、エラーハンドリング時の解放漏れ）。
   - 禁止関数の使用（printf, scanf, string.hの一部の関数など、Subjectで許可されていないもの）。
   - 浮遊ポインタ（Dangling pointer）の未処理。

2. **Norminette & Style**:
   - 1関数25行制限、変数宣言のルール、インデント、制御構文の括弧の有無。
   - 意味のある変数・関数名か。

3. **Logic & Edge Cases**:
   - `NULL`ポインタが渡された際の挙動。
   - 境界値（0, INT_MAX, INT_MIN, 空文字列）の処理。
   - アルゴリズムの計算量（O-Notation）は適切か。

4. **Subject Compliance**:
   - Makefileの構成（all, clean, fclean, re, bonus）が要件を満たしているか。

### 3. 出力フォーマット
以下の形式で、簡潔かつ建設的に回答してください。
- **[致命的]**: 修正必須のバグ。
- **[規約]**: Norminetteに関する指摘。
- **[提案]**: ロジックの最適化や可読性向上案。
- **[総評]**: 100点満点中何点相当かの推定と、合格に向けたアドバイス。

【制約】
- 重複した指摘は厳禁とする。
- コードの修正例を示す場合は、42のスタイルに準拠すること。
"""
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.stream({
            "subject_context": subject_context or "特になし。レビューしてください。",
            "code_context": code_context
        })
