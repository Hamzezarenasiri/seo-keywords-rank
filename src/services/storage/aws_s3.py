"""
    This file contains an abstract for handling all file system actions.
    Right now it works directly with the os but later it can connect to any
    other modules.

    Environment Variables:
        - AWS_ACCESS_KEY: AWS IAM Access key
        - AWS_SECRET_KEY: AWS IAM Secret key
        - AWS_S3_BUCKET: S3 Bucket Name
        - AWS_S3_PRESIGNED_EXPIRATION: Expiration time for the download link in seconds.
"""
import boto3
from botocore.config import Config
from botocore.errorfactory import ClientError


class ConnectionHandler(object):
    def __init__(
        self, resouce_type: str, access_key: str, secret_key: str, region_name: str
    ):
        self.client = boto3.client(
            resouce_type,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(region_name=region_name),
            endpoint_url=f"https://s3.{region_name}.amazonaws.com",
        )


class S3Handler(ConnectionHandler):
    def __init__(
        self,
        access_key: str,
        secret_access: str,
        region_name: str,
        bucket_name: str,
        presigned_expiration: int = 3600,
    ):
        super(S3Handler, self).__init__(
            "s3",
            access_key=access_key,
            secret_key=secret_access,
            region_name=region_name,
        )
        self.bucket_name = bucket_name
        self.predesigned_expiration = presigned_expiration

    async def get_object(self, key):
        return self.client.get_object(Bucket=self.bucket_name, Key=key)

    async def object_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    async def get_presigned_url(self, key):
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=self.predesigned_expiration,
        )

    async def upload_object(self, local_file, s3_key):
        return self.client.upload_file(local_file, self.bucket_name, s3_key)

    async def upload_object_binary(self, source_file, s3_key, content_type):
        return self.client.put_object(
            Body=source_file,
            Bucket=self.bucket_name,
            Key=s3_key,
            ContentType=content_type,
        )

    async def download_object(self, remote_key, local_file):
        return self.client.download_file(
            Bucket=self.bucket_name,
            Key=remote_key,
            Filename=local_file,
        )

    async def remove_object(self, key):
        return self.client.delete_object(Bucket=self.bucket_name, Key=key)
