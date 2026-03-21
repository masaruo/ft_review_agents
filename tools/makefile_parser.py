import os

def check_makefile_flags(target_dir: str) -> str:
    makefile_path = os.path.join(target_dir, "Makefile")
    if not os.path.exists(makefile_path):
        return "⚠️ Makefileが見つかりません。Cプロジェクトの場合は推奨されません。"
    
    issues = []
    try:
        with open(makefile_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "-Wall" not in content or "-Wextra" not in content or "-Werror" not in content:
                issues.append("⚠️ -Wall -Wextra -Werror のコンパイルフラグが不足している可能性があります。")
            if "re:" not in content:
                issues.append("⚠️ 're' ルールが見つからない可能性があります。")
                
        if not issues:
            return "✅ Makefileの基本的なフラグとルールは記載されています。"
        return "\n".join(issues)
    except Exception as e:
        return f"⚠️ Makefileの読み込み中にエラーが発生しました: {e}"
