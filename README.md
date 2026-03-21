# 42 Code Review Agent

42スクールのプロジェクト（libft, minishellなど）特化したAIコードレビューツールです。
Dockerを用いて構築されているため、評価者・対象者のMac上で環境依存なく即座に実行可能です。

## 必要要件
- Docker (Docker Desktop等)
- (オプション) Ollama または OpenAI API Key

## セットアップ手順

初回の利用時、またはツールの更新時にDockerイメージをビルドします。

```bash
make build
```

## 使い方

レビュー対象となる42プロジェクト（例：`/Users/username/libft`）のディレクトリを指定して実行します。

### 1. Ollama（ローカルLLM）を使用する場合

デフォルトでは、コマンドを実行するPCのローカルにあるOllama（`http://host.docker.internal:11434`）へ接続を試みます。推奨モデルは `qwen2.5-coder` や `deepseek-coder-v2` 等です。

```bash
make run TARGET_DIR=/Users/username/libft
```

別のホスト上のOllamaを指定することも可能です。
```bash
make run TARGET_DIR=/Users/username/libft OLLAMA_HOST=http://192.168.x.x:11434
```

### 2. OpenAI（API）を使用する場合

より高速・高精度なレビューが必要な場合は、OpenAIのAPIキーを渡すことで実行できます。

```bash
make run TARGET_DIR=/Users/username/libft OPENAI_API_KEY=sk-xxxxxx
```

## プロジェクトSubject（課題要件）の追加
本エージェントは指定されたプロジェクトごとのSubject制約を考慮してレビューを行います。
`subjects/` ディレクトリ配下にPDFファイル（例：`subjects/libft.pdf`）として課題の実ファイル（Subject）を配置しておくと、AIが内容を自動で抽出（RAG）してレビュー精度を大幅に向上させます。
