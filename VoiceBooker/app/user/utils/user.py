from typing import Tuple, Dict

from graphql import GraphQLError

from app.database.database import Session
from app.database.model import User
from app.user.utils.jwt import verify_jwt, verify_refresh_jwt


def get_authenticated_user(
    context: Dict, regeneration: bool = False
) -> Tuple[User, str]:
    request = context.get("request")
    if request is None:
        raise GraphQLError("Missing request object in context")

    auth_header: str = request.headers.get("Authorization")

    token = [None]

    if auth_header and "Bearer" in auth_header:
        token = auth_header.split(" ")

    if token and len(token) == 2:
        token = token[1]

        try:
            is_verified, payload = verify_jwt(token)
        except GraphQLError:
            if regeneration:
                is_verified, payload = verify_refresh_jwt(token)
            else:
                raise GraphQLError("Invalid token")

        with Session() as session:
            user: User = (
                session.query(User).filter(User.email == payload.get("sub")).first()
            )

            if not user:
                raise GraphQLError("User not found")

            return user, token
    else:
        raise GraphQLError("Missing authentication token")
