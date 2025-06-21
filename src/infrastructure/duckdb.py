import os
from typing import TYPE_CHECKING

import duckdb
import polars as pl
import streamlit as st

if TYPE_CHECKING:
    from io import BytesIO


class DuckDB:
    """Represents a DuckDB connection."""

    def __init__(self) -> None:
        """Initialize the DuckDB connection."""
        self.conn = duckdb.connect()
        self._setup_httpfs()

    def _setup_httpfs(self) -> None:
        """Setup DuckDB HTTPFS extension."""
        self.conn.sql("INSTALL httpfs;")
        self.conn.sql("LOAD httpfs;")

    def connect_storage(self, storage_type: str, region: str | None) -> None:
        """Connect to the specified storage.

        Args:
            storage_type: Type of storage ('s3' or 'minio')
            region: AWS region (required for S3, ignored for MinIO)

        Raises:
            ValueError: If required environment variables are not set
        """
        if storage_type == "s3":
            self._setup_aws_secret(region)
        else:
            self._setup_minio_secret()

    def _setup_aws_secret(self, region: str | None) -> None:
        """Setup AWS S3 secret for DuckDB.

        Args:
            region: AWS region

        Raises:
            ValueError: If AWS credentials are not set
        """
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        if not aws_access_key_id or not aws_secret_access_key:
            msg = "AWS credentials are not set in environment variables"
            raise ValueError(msg)

        if not region:
            msg = "AWS region is required for S3 connection"
            raise ValueError(msg)

        self.conn.sql(
            f"""
            CREATE SECRET aws (
                TYPE S3,
                KEY_ID '{aws_access_key_id}',
                SECRET '{aws_secret_access_key}',
                REGION '{region}',
                ENDPOINT 's3.{region}.amazonaws.com'
            )
            """
        )

    def _setup_minio_secret(self) -> None:
        """Setup MinIO secret for DuckDB.

        Raises:
            ValueError: If MinIO credentials are not set
        """
        minio_access_key_id = os.environ.get("MINIO_ACCESS_KEY_ID")
        minio_secret_access_key = os.environ.get("MINIO_SECRET_ACCESS_KEY")

        if not minio_access_key_id or not minio_secret_access_key:
            msg = "MinIO credentials are not set in environment variables"
            raise ValueError(msg)

        self.conn.sql(
            f"""
            CREATE SECRET minio (
                TYPE S3,
                KEY_ID '{minio_access_key_id}',
                SECRET '{minio_secret_access_key}',
                ENDPOINT 'minio:9000',
                URL_STYLE vhost,
                USE_SSL false
            )
            """
        )

    def load_uploaded_csv_file(self, uploaded_file: BytesIO) -> pl.DataFrame:
        """Load the uploaded CSV file and transform to DataFrame.

        Args:
            uploaded_file: CSV file content as BytesIO

        Returns:
            Polars DataFrame containing the CSV data
        """
        return self.conn.read_csv(uploaded_file)

    def upload_data_to_s3(
        self,
        bucket_name: str,
        file_name: str,
        data: pl.DataFrame,  # noqa: ARG002
    ) -> None:
        """Upload data to S3 storage.

        Args:
            bucket_name: S3 bucket name
            file_name: Target file name (without extension)
            data: Data to upload (currently unused due to DuckDB limitation)

        Raises:
            ValueError: If bucket_name or file_name is empty
        """
        if not bucket_name or not file_name:
            msg = "Bucket name and file name must be provided"
            raise ValueError(msg)

        s3_path = f"s3://{bucket_name}/{file_name}.parquet"
        self.conn.sql(f"COPY data TO '{s3_path}';")
        st.success("ファイルをS3にアップロードしました")
