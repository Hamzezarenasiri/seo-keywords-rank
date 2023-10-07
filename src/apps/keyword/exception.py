from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from . import enum, messages

KeywordNotFound = CustomHTTPException(
    detail=enum.KeywordNotFoundErrorDetailEnum.not_found,
    message=messages.KeywordErrorMessageEnum.not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)

InvalidQuantity = CustomHTTPException(
    detail=enum.KeywordErrorDetailEnum.invalid_quantity,
    message=messages.KeywordErrorMessageEnum.invalid_quantity,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)
