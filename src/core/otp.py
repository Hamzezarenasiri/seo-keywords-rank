import pickle
from enum import Enum
from string import digits
from typing import Optional

from fastapi import HTTPException

from src.apps.auth.enum import AuthOTPTypeEnum
from src.apps.user.models import UserDBReadModel
from src.apps.auth.exception import OTPExpiredOrInvalid
from src.core.common.exceptions import CustomHTTPException
from src.core.utils import get_random_string
from src.main.config import app_settings, test_settings
from src.services import global_services


class OtpRequestType(str, Enum):
    reset_pass: str = "Rest Password"
    verification: str = "Verification"


class OtpExistsError(Exception):
    pass


async def otp_sender(
    user: UserDBReadModel,
    otp_type: AuthOTPTypeEnum,
    otp: str,
    request_type: Optional[OtpRequestType] = OtpRequestType.reset_pass,
) -> str:
    message = app_settings.OTP_TEMPLATE.format(otp=otp)
    if not app_settings.TEST_MODE:
        if otp_type == AuthOTPTypeEnum.sms:
            await global_services.SNS.send_sms(
                phone_number=user.mobile_number, message=message
            )
            # global_services.BROKER.send_task(
            #     name="twilio_send_sms_task_high",
            #     queue="high_priority",
            #     kwargs={"mobile_number": user.mobile_number, "message": message},
            # )
        elif otp_type == AuthOTPTypeEnum.email:
            # global_services.BROKER.send_task(
            #     name="twilio_send_email_task_high",
            #     queue="high_priority",
            #     kwargs={"to_email": user.email, "subject": message, "content": message},
            # )
            if request_type == OtpRequestType.reset_pass:
                global_services.SES.send_otp_rest_pass_email(
                    user.email,
                    otp_code=otp,
                    user_name=f"{user.first_name} {user.last_name}",
                )
            if request_type == OtpRequestType.verification:
                global_services.SES.send_otp_verification_email(
                    user.email,
                    otp_code=otp,
                    user_name=f"{user.first_name} {user.last_name}",
                )
        else:
            raise HTTPException(status_code=406, detail="Invalid otp type")
    return message


async def set_otp(key: str):
    if app_settings.TEST_MODE:
        otp = test_settings.DEFAULT_OTP
        expiry = test_settings.DEFAULT_OTP_TIME
    else:
        otp = make_random_digit_otp(length=app_settings.OTP_LENGTH)
        expiry = app_settings.OTP_TIME
    otp_to_cache = pickle.dumps(otp)
    exist_key = await global_services.CACHE.exists(key=key)
    if exist_key:
        raise OtpExistsError
    await global_services.CACHE.set(key=key, value=otp_to_cache, expiry=expiry)
    return otp


async def set_otp_and_send_message(
    user: UserDBReadModel,
    otp_type: AuthOTPTypeEnum,
    cache_key: Optional[str] = None,
    request_type: Optional[OtpRequestType] = OtpRequestType.reset_pass,
) -> str:
    cache_key = cache_key or str(user.id)
    try:
        otp = await set_otp(cache_key)
    except OtpExistsError as e:
        message = f"{otp_type} has already been sent, try again after the time limit "
        raise CustomHTTPException(
            detail=[message],
            message=message,
            status_code=406,
        ) from e
    message = await otp_sender(user, otp_type, otp, request_type=request_type)
    return message


async def get_otp(key: str) -> Optional[str]:
    cached = await global_services.CACHE.get(key=key)
    if cached:
        return pickle.loads(cached)


async def cache_otp_verification(key: str):
    exist_key = await global_services.CACHE.exists(key=key)
    if exist_key:
        raise OtpExistsError
    if app_settings.TEST_MODE:
        otp = test_settings.DEFAULT_OTP
        expiry = test_settings.DEFAULT_OTP_TIME
    else:
        otp = make_random_digit_otp(length=app_settings.OTP_LENGTH)
        expiry = app_settings.OTP_TIME
    code = ("code", otp)
    retry = ("retry", 1)
    await global_services.CACHE.hmset(key, *code, *retry)
    await global_services.CACHE.expire(key=key, time=expiry)
    return otp


async def send_otp_verification(
    reciever: str,
    otp_code: str,
    otp_type: AuthOTPTypeEnum,
):
    message = app_settings.OTP_TEMPLATE.format(otp=otp_code)
    if otp_type == AuthOTPTypeEnum.sms.value:
        await global_services.SNS.send_sms(phone_number=reciever, message=message)
    elif otp_type == AuthOTPTypeEnum.email.value:
        global_services.SES.send_otp_verification_email(
            reciever, otp_code=otp_code, user_name=f"{reciever}"
        )
    else:
        raise HTTPException(status_code=406, detail="Invalid otp type")


async def verify_otp(
    key: str,
    code: str,
):
    cached_otp = await global_services.CACHE.hgetall(key)
    if not cached_otp:
        raise OTPExpiredOrInvalid
    cached_otp = {
        key.decode("utf-8"): cached_otp[key].decode("utf-8") for key in cached_otp
    }
    retries = int(cached_otp.get("retry"))
    if retries >= 10:
        raise OTPExpiredOrInvalid
    if cached_otp.get("code") != code:
        await global_services.CACHE.hincrby(key, "retry")
        raise OTPExpiredOrInvalid
    await global_services.CACHE.delete(key)


def make_random_digit_otp(length=6, allowed_chars=digits[1:]):
    return get_random_string(length, allowed_chars)
