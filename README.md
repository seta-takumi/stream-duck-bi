# StreamDuck-BI

## 概要

Streamlit+DuckDB を用いた BI ツール

## 環境構築

### 開発環境

1. リポジトリのルートディレクトリに`.env`を作成し、以下を設定

```
# MINIO（ローカル）環境設定
MINIO_ACCESS_KEY_ID=admin
MINIO_SECRET_ACCESS_KEY=password
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password
MINIO_DOMAIN=minio
MINIO_BUCKET=warehouse
TZ=Asia/Tokyo

# S3環境用設定(適宜追加)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

2. Dev Container を起動

[こちら](https://code.visualstudio.com/docs/devcontainers/containers)を参考

2. 依存関係のインストール

```
uv sync
```

## アプリケーション(Streamlit)の起動

### 開発環境

```
uv run streamlit run src/Home.py
```
