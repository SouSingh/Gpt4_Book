from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

import jwt
from graphql import GraphQLError

from app.utils.load_env import getenv

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = int(getenv("TOKEN_EXPIRE_MINUTES"))
TOKEN_EXPIRE_REFRESH_MINUTES = int(getenv("TOKEN_EXPIRE_REFRESH_MINUTES"))


def generate_jwt(email: str, token_type: str) -> str:
    if token_type == "access":
        expiration = get_expiration_date(TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        expiration = get_expiration_date(TOKEN_EXPIRE_REFRESH_MINUTES)
    else:
        raise GraphQLError("Invalid token type")

    payload = {"sub": email, "type": token_type, "exp": expiration}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_expiration_date(expire_minutes: int) -> datetime:
    return datetime.utcnow() + timedelta(minutes=expire_minutes)


def verify_jwt(token: str) -> Tuple[bool, Dict]:
    try:
        payload: Dict = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        if datetime.now(timezone.utc) > datetime.fromtimestamp(
            payload.get("exp"), tz=timezone.utc
        ):
            raise GraphQLError("Token has expired")

        if payload.get("type") != "access":
            raise GraphQLError("Invalid token type")

        return True, payload
    except jwt.exceptions.PyJWTError:
        raise GraphQLError("Invalid token")


def verify_refresh_jwt(token: str) -> Tuple[bool, Dict]:
    try:
        payload: Dict = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        if datetime.now(timezone.utc) > datetime.fromtimestamp(
            payload.get("exp"), tz=timezone.utc
        ):
            raise GraphQLError("Token has expired")

        if payload.get("type") != "refresh":
            raise GraphQLError("Invalid token type")

        return True, payload
    except jwt.exceptions.PyJWTError:
        raise GraphQLError("Invalid token")


def regenerate_jwt(token: str) -> Tuple[str, str]:

    valid, payload = verify_refresh_jwt(token)

    if valid:
        token = generate_jwt(payload.get("sub"), "access")
        refresh_token = generate_jwt(payload.get("sub"), "refresh")

        return token, refresh_token
    else:
        raise GraphQLError("Invalid token")
