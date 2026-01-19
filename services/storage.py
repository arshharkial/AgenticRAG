import boto3
from botocore.exceptions import ClientError
from core.config import settings

class StorageService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket = settings.S3_BUCKET

    def upload_file(self, file_content, object_name: str):
        # Tenant isolation via prefix
        tenant_path = f"{self.tenant_id}/{object_name}"
        try:
            self.s3.put_object(Bucket=self.bucket, Key=tenant_path, Body=file_content)
            return f"{settings.CLOUDFRONT_URL}/{tenant_path}" if settings.CLOUDFRONT_URL else f"s3://{self.bucket}/{tenant_path}"
        except ClientError as e:
            # Log error (placeholder)
            print(f"S3 upload error: {e}")
            return None

    def delete_file(self, object_name: str):
        tenant_path = f"{self.tenant_id}/{object_name}"
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=tenant_path)
            return True
        except ClientError as e:
            print(f"S3 delete error: {e}")
            return False
