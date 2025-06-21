import os

import polars as pl
import streamlit as st
from infrastructure.duckdb import DuckDB
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
    else:
        bucket_name = os.environ.get("MINIO_BUCKET")
        db.connect_storage(storage, None)
    return bucket_name


def upload_file_process(
    uploaded_data: pl.DataFrame, bucket_name: str, file_name: str, db: DuckDB
) -> None:
    """Process the uploaded file and save it to an S3 or Minio bucket.

    Display the uploaded data and allow the user to choose whether to save 
    the data to S3 or create an SQL query.

    Args:
        uploaded_data: The uploaded data as a polars DataFrame
        bucket_name: The name of the bucket to save the data
        file_name: The name of the file to save
        db: The DuckDB instance
    """
    st.write("アップロードされたデータ:")
    st.dataframe(uploaded_data.pl(), hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("S3に保存", key="upload_data", use_container_width=True):
            try:
                db.upload_data_to_s3(bucket_name, file_name, uploaded_data)
            except Exception as e:
                st.error(f"S3への保存中にエラーが発生しました: {e}")

    with col2:
        if st.button("SQLを作成", use_container_width=True):
            st.session_state["show_query_area"] = not st.session_state.get(
                "show_query_area", False
            )


def execute_query_process(
    uploaded_data: pl.DataFrame, table_name: str, bucket_name: str, db: DuckDB
) -> None:
    """Execute a SQL query and performs actions based on the query result.

    Args:
        uploaded_data: The uploaded data as a polars DataFrame
        table_name: The name of the table to create from the uploaded data
        bucket_name: The name of the S3 bucket to upload the query result to
        db: The DuckDB instance
    """
    if not table_name.strip():
        st.error("テーブル名を入力してください")
        return

    try:
        uploaded_data.create(table_name)
    except Exception as e:
        st.error(f"テーブルの作成中にエラーが発生しました: {e}")
        return

    query = st.text_area("SQLクエリを入力してください")
    if not query.strip():
        return

    try:
        result = db.conn.execute(query).fetchdf()
        result_pl = pl.from_pandas(result)
        st.write("クエリ結果:")
        st.dataframe(result_pl, hide_index=True)

        col3, col4 = st.columns(2)
        with col3:
            if st.button("S3に保存", key="query_result", use_container_width=True):
                try:
                    db.upload_data_to_s3(bucket_name, table_name, result_pl)
                except Exception as e:
                    st.error(f"S3への保存中にエラーが発生しました: {e}")

        with col4:
            try:
                csv = result_pl.write_csv()
                st.download_button(
                    label="CSVファイルとしてダウンロード",
                    data=csv,
                    file_name="query_result.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"CSVの生成中にエラーが発生しました: {e}")

    except Exception as e:
        st.error(f"クエリの実行中にエラーが発生しました: {e}")


def csv_upload() -> None:
    """Perform CSV upload, save to storage and query execution."""
    # サイドバーにページリンクを表示
    page_link()

    # Streamlitアプリの設定
    st.title("CSVアップロードとクエリ実行")

    # データベース接続
    try:
        db = DuckDB()
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return

    storage = st.selectbox("Storage", ["minio", "s3"])

    # 指定したストレージごとの設定と接続
    try:
        bucket_name = connect_to_storage(storage, db)
    except Exception as e:
        st.error(f"ストレージ接続エラー: {e}")
        return

    # セッション状態の初期化
    if "show_query_area" not in st.session_state:
        st.session_state["show_query_area"] = False

    # ファイルアップロードセクション
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
    if uploaded_file is not None:
        try:
            uploaded_data = db.load_uploaded_csv_file(uploaded_file)
            file_name = uploaded_file.name.split(".")[0]
            upload_file_process(uploaded_data, bucket_name, file_name, db)

            # クエリ実行セクション
            if st.session_state.get("show_query_area", False):
                table_name = st.text_input(
                    "SQLを作成する際のテーブル名を入力してください", key="table_name"
                )
                if table_name.strip():
                    execute_query_process(uploaded_data, table_name, bucket_name, db)

        except Exception as e:
            st.error(f"ファイル処理エラー: {e}")


if __name__ == "__main__":
    csv_upload()
