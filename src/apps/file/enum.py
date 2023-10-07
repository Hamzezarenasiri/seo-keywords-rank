from enum import Enum


class FileSize413MessageEnum(str, Enum):
    too_large: str = "Filesize is too large"


class FileType415MessageEnum(str, Enum):
    file_type: str = "Provided file format is not supported"


class S3ServiceUnavailableMessageEnum(str, Enum):
    service_unavailable: str = "S3 service is not available"
    file_not_found: str = "File not found"


class FileIsUsedMessageEnum(str, Enum):
    file_is_used: str = "File is used in an other entity"


class FileTypeEnum(str, Enum):
    image: str = "image"
    video: str = "video"
    document: str = "document"


ALL_FILE_TYPES = [i.value for i in FileTypeEnum.__members__.values()]


class FileCategoryEnum(str, Enum):
    gallery: str = "gallery"


ALL_FILE_CATEGORIES = [i.value for i in FileCategoryEnum.__members__.values()]
