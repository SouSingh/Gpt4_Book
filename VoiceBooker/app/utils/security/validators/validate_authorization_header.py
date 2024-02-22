from fastapi import Header, HTTPException

from app.user.utils.jwt import verify_jwt


def validate_authorization_header(authorization: str = Header(None)) -> None:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer":
            is_valid, payload = verify_jwt(token)
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid token")
        else:
            raise HTTPException(status_code=401, detail="Invalid scheme")
    else:
        raise HTTPException(status_code=401, detail="No authorization header")
