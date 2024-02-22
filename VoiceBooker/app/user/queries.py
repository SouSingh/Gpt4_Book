from graphene import ObjectType, Field, String

from app.database.database import Session
from app.database.model import User
from app.gql.types import UserObject


class UserQuery(ObjectType):
    get_user = Field(UserObject, username=String(required=True))

    @staticmethod
    def resolve_get_user(root, info, username: str):
        return Session.query(User).filter(User.username == username).first()
