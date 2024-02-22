from fastapi import HTTPException

from app.database.database import Session
from app.database.model import User


def get_user(email: str) -> User:
    with Session() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
