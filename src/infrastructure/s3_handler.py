import os
from typing import Any

import boto3


class S3Handler:
    """Handler for S3 and MinIO storage operations."""

    def __init__(self, storage_type: str) -> None:
        """Initialize the S3Handler object.

        Args:
            storage_type: Type of storage ('s3' or 'minio')

        Raises:
            ValueError: If required environment variables are not set
        """
        self.storage_type = storage_type
        self.s3 = self._create_client()

    def _create_client(self) -> Any:
        """Create S3 client based on storage type.

        Returns:
            Configured S3 client

        Raises:
            ValueError: If required credentials are not set
        """
        if self.storage_type == "s3":
            return self._create_aws_client()
        return self._create_minio_client()

    def _create_aws_client(self) -> Any:
        """Create AWS S3 client.

        Returns:
            AWS S3 client

        Raises:
            ValueError: If AWS credentials are not set
        """
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        # AWS資格情報がないことをチェックするだけ
        if not aws_access_key_id or not aws_secret_access_key:
            pass

        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def _create_minio_client(self) -> Any:
        """Create MinIO client.

        Returns:
            MinIO S3-compatible client

        Raises:
            ValueError: If MinIO credentials are not set
        """
        minio_access_key_id = os.environ.get("MINIO_ACCESS_KEY_ID")
        minio_secret_access_key = os.environ.get("MINIO_SECRET_ACCESS_KEY")

        if not minio_access_key_id or not minio_secret_access_key:
            msg = "MinIO credentials are not set in environment variables"
            raise ValueError(msg)

        return boto3.client(
            "s3",
            endpoint_url="http://minio:9000",
            aws_access_key_id=minio_access_key_id,
            aws_secret_access_key=minio_secret_access_key,
            verify=False,
        )

    def list_files(self, bucket_name: str) -> list[str]:
        """List all files in the S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket

        Returns:
            List of file names (keys) in the bucket

        Raises:
            ValueError: If bucket_name is empty
        """
        if not bucket_name:
            msg = "Bucket name must be provided"
            raise ValueError(msg)

        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            s3_files = response.get("Contents", [])
            return [file["Key"] for file in s3_files]
        except Exception as e:
            msg = f"Failed to list files in bucket {bucket_name}: {e}"
            raise RuntimeError(msg) from e
