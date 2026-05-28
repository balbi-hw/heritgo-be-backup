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