import os

import streamlit as st
from infrastructure.duckdb import DuckDB
from infrastructure.s3_handler import S3Handler
from page_link import page_link


def connect_to_storage(storage: str, db: DuckDB) -> str:
    """Connect to the storage and returns the bucket name.

    Args:
        storage: The type of storage ('s3' or 'minio')
        db: The DuckDB instance

    Returns:
        The bucket name
    Raises:
        ValueError: If MinIO bucket name is not configured
    """
    if storage == "s3":
        bucket_name = st.text_input("Bucket Name", value="warehouse")
        region = st.text_input("Region", value="ap-northeast-1")
        db.connect_storage(storage, region)
        return bucket_name

    bucket_name = os.environ.get("MINIO_BUCKET")
    if not bucket_name:
        msg = "MINIO_BUCKET environment variable is not set"
        raise ValueError(msg)

    db.connect_storage(storage, None)
    return bucket_name


def s3_file_analyze() -> None:
    """Display the contents of the selected file from the storage."""
    # サイドバーにページリンクを表示
    page_link()

    # Streamlitアプリの設定
    st.title("ストレージ内の分析")

    # データベース接続
    try:
        db = DuckDB()
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return

    storage = st.selectbox("Storage", ["minio", "s3"])

    # 指定したストレージごとの設定と接続
    try:
        s3 = S3Handler(storage)
        bucket_name = connect_to_storage(storage, db)
    except Exception as e:
        st.error(f"ストレージ接続エラー: {e}")
        return

    # バケット内のファイル一覧を取得
    try:
        files = s3.list_files(bucket_name)
        if not files:
            st.info("バケットにファイルがありません")
            return

        selected_file = st.selectbox("Select a file", files)

        # ファイルの内容を表示
        if selected_file:
            try:
                # TODO: load_data_from_s3メソッドが存在しないため、実装が必要
                st.info(f"選択されたファイル: {selected_file}")
                st.warning("ファイル読み込み機能は未実装です")
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")

    except Exception as e:
        st.error(f"ファイル一覧取得エラー: {e}")


if __name__ == "__main__":
    s3_file_analyze()
