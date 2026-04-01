# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 開発コマンド

### 環境構築
```bash
# 依存関係のインストール
uv sync

# Streamlitアプリケーションの起動
uv run streamlit run src/Home.py
```

### コード品質
```bash
# リンターとフォーマッターの実行
ruff check
ruff format

# 自動修正可能な問題を修正
ruff check --fix
```

## アーキテクチャ概要

DuckDBとS3/MinIOストレージを統合したStreamlitベースのBIツールです。

### 主要コンポーネント

**インフラストラクチャ層 (`src/infrastructure/`)**
- `DuckDB`: データベース接続を管理し、DuckDBのhttpfs拡張を通じてS3/MinIO統合を処理
- `S3Handler`: AWS S3とMinIO両方に対してboto3ベースのファイル一覧機能を提供

**アプリケーション層 (`src/pages/`)**
- `CSV_Upload.py`: CSVファイルのアップロード、データプレビュー、S3ストレージ、SQLクエリ実行を処理
- `s3_file_analyze.py`: ストレージバケットからのファイル選択と分析機能を提供

### 重要なアーキテクチャパターン

**ストレージ抽象化**: 環境ベースの設定を通じてAWS S3とMinIO両方をサポート。DuckDBがデータ操作を処理し、S3Handlerがファイル一覧を管理。

**セッション状態管理**: クエリエリアの表示状態などのUI状態管理にStreamlitのセッション状態を使用。

**マルチページナビゲーション**: `page_link.py`を使用して全ページで一貫したサイドバーナビゲーションを提供。

## 環境設定

ストレージ認証情報を含む`.env`ファイルが必要:
- MinIO: `MINIO_ACCESS_KEY_ID`, `MINIO_SECRET_ACCESS_KEY`, `MINIO_BUCKET`
- AWS S3: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

## 技術スタック

- **フロントエンド**: Streamlit
- **データベース**: DuckDB（httpfs拡張付き）
- **データ処理**: Polars
- **ストレージ**: AWS S3 / MinIO
- **パッケージ管理**: uv
- **コード品質**: Ruff（Python 3.12対象）

## 開発時の重要な注意点

### ストレージ統合の二重アプローチ
アプリケーションはストレージに対して2つの補完的なアプローチを使用:
- **DuckDB + httpfs**: DuckDBのS3統合による直接的なデータ操作（クエリ、アップロード）
- **boto3 + S3Handler**: AWS SDK機能が必要なファイル一覧とメタデータ操作

### Ruff設定
プロジェクトでは`select = ["ALL"]`による包括的なリンティングを使用しているが、フォーマッターと競合するルールは除外。行長は100文字に設定（Blackのデフォルト動作に合わせる）。

### 共通関数パターン
両ページ（CSV_Upload.py、s3_file_analyze.py）で`connect_to_storage`関数を共有しており、ストレージタイプに応じた接続処理を統一している。