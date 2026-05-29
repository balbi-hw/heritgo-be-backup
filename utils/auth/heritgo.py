from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


def generate_token(user, token_type):
    now = datetime.now(UTC)

    if token_type == "access":
        exp = now + timedelta(hours=3)
    elif token_type == "refresh":
        exp = now + timedelta(days=1)
    else:
        raise ValueError("Invalid token type")

    payload = {
        "sub": str(user.pk),
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(
        payload,
        settings.JWT_AUTH["JWT_SECRET_KEY"],
        algorithm=settings.JWT_AUTH["JWT_ALGORITHM"],
    )

    return token


def validate(request):

    header = get_authorization_header(request)

    if not header:
        return None

    tokens = header.split()

    if len(tokens) != 2:
        msg = {
            "message": "헤더 형식이 올바르지 않습니다.",
            "code": "JWT_403_INVALID_AUTH_HEADER",
        }
        raise AuthenticationFailed(msg)

    auth, token = tokens

    if auth.lower() != b"bearer":
        raise AuthenticationFailed("잘못된 인증 방식입니다.")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_AUTH["JWT_SECRET_KEY"],
            algorithms=settings.JWT_AUTH["JWT_ALGORITHM"],
            options={
                "require": [
                    "sub",
                    "token_type",
                    "iat",
                    "exp",
                ]
            },
        )

    except jwt.exceptions.MissingRequiredClaimError:
        msg = {
            "message": "토큰에 필수 정보가 없습니다.",
            "code": "JWT_403_MISSING_REQUIRED_CLAIM",
        }
        raise AuthenticationFailed(msg) from None

    except jwt.ExpiredSignatureError:
        msg = {
            "message": "토큰이 만료되었습니다.",
            "code": "JWT_401_EXPIRED_ACCESSTOKEN",
        }
        raise AuthenticationFailed(msg) from None

    except jwt.exceptions.InvalidTokenError:
        msg = {
            "message": "잘못된 토큰입니다.",
            "code": "JWT_403_INVALID_ACCESSTOKEN",
        }
        raise AuthenticationFailed(msg) from None

    if payload["token_type"] != "access":
        msg = {
            "message": "Access Token 이 아닙니다.",
            "code": "JWT_403_NOT_ACCESSTOKEN",
        }
        raise AuthenticationFailed(msg)

    try:
        return int(payload["sub"])
    except ValueError:
        msg = {
            "message": "토큰의 사용자 식별자가 올바르지 않습니다.",
            "code": "JWT_403_INVALID_SUBJECT",
        }
        raise AuthenticationFailed(msg) from None


def check_refresh_token(request):

    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            msg = {
                "message": "refresh_token 이 누락되었습니다.",
                "code": "JWT_400_NOT_FOUND_TOKEN",
            }
            raise AuthenticationFailed(msg)

        decoded = jwt.decode(
            refresh_token,
            settings.JWT_AUTH["JWT_SECRET_KEY"],
            settings.JWT_AUTH["JWT_ALGORITHM"],
        )

        if decoded.get("token_type") != "refresh":
            msg = {
                "message": "토큰에 문제가 있습니다.",
                "code": "JWT_403_INVALID_TOKEN_TYPE",
            }
            raise AuthenticationFailed(msg)

    except jwt.InvalidTokenError:
        msg = {
            "message": "문제가 발생하였습니다. 다시 시도해주세요.",
            "code": " JWT_403_UNDETECTED_ERROR",
        }
        raise AuthenticationFailed(msg) from None
