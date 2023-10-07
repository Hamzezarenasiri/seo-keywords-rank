import asyncio
import os
from abc import ABC, abstractmethod
from functools import cache
from logging import getLogger
from pathlib import Path
from urllib.parse import quote as url_encode

import boto3
from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl

logger = getLogger(__name__)


class FileData(BaseModel):
    """
    Represents the result of an upload operation
    Attributes:
        file (Bytes): File saved to memory
        path (Path | str): Path to file in local storage
        url (HttpUrl | str): A URL for accessing the object.
        size (int): Size of the file in bytes.
        filename (str): Name of the file.
        status (bool): True if the upload is successful else False.
        error (str): Error message for failed upload.
        message: Response Message
    """

    file: bytes = b""
    path: Path | str = ""
    url: HttpUrl | str = ""
    size: int = 0
    filename: str = ""
    content_type: str = ""
    status: bool = True
    error: str = ""
    message: str = ""


class CloudUpload(ABC):
    """
    Methods:
        upload: Uploads a single object to the cloud
        multi_upload: Upload multiple objects to the cloud
    Attributes:
        config: A config dict
    """

    def __init__(self, config: dict | None = None):
        """
        Keyword Args:
            config (dict): A dictionary of config settings
        """
        self.config = config or {}

    async def __call__(
        self, file: UploadFile | None = None, files: list[UploadFile] | None = None
    ) -> FileData | list[FileData]:
        try:
            if file:
                return await self.upload(file=file)

            elif files:
                return await self.multi_upload(files=files)
            else:
                return FileData(
                    status=False,
                    error="No file or files provided",
                    message="No file or files provided",
                )
        except Exception as err:
            return FileData(
                status=False, error=str(err), message="File upload was unsuccessful"
            )

    @abstractmethod
    async def upload(self, *, file: UploadFile) -> FileData:
        """"""

    @abstractmethod
    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        """"""


class Local(CloudUpload):
    """
    Local storage for FastAPI.
    """

    async def upload(self, *, file: UploadFile) -> FileData:
        """
        Upload a file to the destination.
        Args:
            file UploadFile: File to upload
        Returns:
            FileData: Result of file upload
        """
        try:
            dest = (
                f"{self.config.get('dest')}/{file.filename}"
                or Path("uploads") / f"{file.filename}"
            )
            file_object = await file.read()
            with open(f"{dest}", "wb") as fh:
                fh.write(file_object)
            await file.close()
            return FileData(
                path=dest,
                message=f"{file.filename} saved successfully",
                content_type=file.content_type,
                size=file.size,
                filename=file.filename,
            )
        except Exception as err:
            logger.error(f"Error uploading file: {err} in {self.__class__.__name__}")
            return FileData(status=False, error=str(err), message="Unable to save file")

    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        """
        Upload multiple files to the destination.
        Args:
            files (list[tuple[str, UploadFile]]): A list of tuples of field name and the file to upload.
        Returns:
            list[FileData]: A list of uploaded file data
        """
        res = await asyncio.gather(*[self.upload(file=file) for file in files])
        return list(res)


"""
Memory storage for FastStore. This storage is used to store files in memory.
"""


class Memory(CloudUpload):
    """
    Memory storage for FastAPI.
    This storage is used to store files in memory and returned as bytes.
    """

    async def upload(self, *, file: UploadFile) -> FileData:
        try:
            file_object = await file.read()
            return FileData(
                size=file.size,
                filename=file.filename,
                content_type=file.content_type,
                file=file_object,
                message=f"{file.filename} saved successfully",
            )
        except Exception as err:
            logger.error(f"Error uploading file: {err} in {self.__class__.__name__}")
            return FileData(status=False, error=str(err), message="Unable to save file")

    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        return list(await asyncio.gather(*[self.upload(file=file) for file in files]))


class S3(CloudUpload):
    @property
    @cache
    def client(self):
        key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        region_name = self.config.get("region") or os.environ.get("AWS_DEFAULT_REGION")
        return boto3.client(
            "s3",
            region_name=region_name,
            aws_access_key_id=key_id,
            aws_secret_access_key=access_key,
        )

    async def upload(self, *, file: UploadFile) -> FileData:
        try:
            extra_args = self.config.get("extra_args", {})
            bucket = self.config.get("bucket") or os.environ.get("AWS_BUCKET_NAME")
            region = self.config.get("region") or os.environ.get("AWS_DEFAULT_REGION")
            await asyncio.to_thread(
                self.client.upload_fileobj,
                file.file,
                bucket,
                file.filename,
                ExtraArgs=extra_args,
            )
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{url_encode(file.filename.encode('utf8'))}"
            return FileData(
                url=url,
                message=f"{file.filename} uploaded successfully",
                filename=file.filename,
                content_type=file.content_type,
                size=file.size,
            )
        except Exception as err:
            logger.error(err)
            return FileData(
                status=False, error=str(err), message="File upload was unsuccessful"
            )

    async def multi_upload(self, *, files: list[UploadFile]):
        tasks = [asyncio.create_task(self.upload(file=file)) for file in files]
        return await asyncio.gather(*tasks)
