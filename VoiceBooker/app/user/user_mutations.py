from datetime import datetime, timezone
from typing import Optional

from graphene import Mutation, String, Boolean, Field, Int
from graphql import GraphQLError

from app.database.database import Session
from app.database.model import User
from app.gql.types import UserObject
from app.user.utils.email import is_valid_email
from app.user.utils.jwt import generate_jwt, regenerate_jwt
from app.user.utils.password import is_password_secure, hash_password, verify_password
from app.user.utils.user import get_authenticated_user
from app.utils.decorators import logged_in


class CreateUser(Mutation):
    class Arguments:
        username = String(required=True)
        email = String(required=True)
        password = String(required=True)
        full_name = String(required=True)

    ok = Boolean()
    user = Field(UserObject)

    @staticmethod
    def mutate(root, info, username: str, email: str, password: str, full_name: str):
        with Session() as session:
            is_valid_email(email)

            user = session.query(User).filter(User.email == email).first()

            if user:
                raise GraphQLError("Email already exists")

            user = session.query(User).filter(User.username == username).first()

            if user:
                raise GraphQLError("Username already taken")

            is_password_secure(password)

            user = User(
                username=username,
                email=email,
                password=hash_password(password),
                full_name=full_name,
                is_active=True,
                is_admin=False,
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            return CreateUser(ok=True, user=user)


class LoginUser(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    token = String()
    refresh_token = String()
    user = Field(UserObject)

    @staticmethod
    def mutate(root, info, email: str, password: str):
        with Session() as session:
            user = session.query(User).filter(User.email == email).first()

            if not user:
                raise GraphQLError("Invalid credentials")

            verify_password(user.password, password)

            if not user.is_active:
                raise GraphQLError("User is not active")

            token = generate_jwt(email, "access")
            refresh_token = generate_jwt(email, "refresh")

            user.last_login = datetime.now(timezone.utc)

            session.commit()
            session.refresh(user)

            return LoginUser(token=token, refresh_token=refresh_token, user=user)


class UpdateUser(Mutation):
    class Arguments:
        user_id = Int(required=True)
        username = String()
        email = String()
        password = String()
        old_password = String()
        full_name = String()
        active = Boolean()

    ok = Boolean()
    user = Field(UserObject)

    @staticmethod
    @logged_in
    def mutate(
        root,
        info,
        user_id: int,
        old_password: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        active: Optional[bool] = None,
        full_name: Optional[str] = None,
    ):
        user_token = get_authenticated_user(info.context)

        if user_token:
            user: User = user_token[0]
            verify_password(user.password, old_password)
        else:
            raise GraphQLError("Could not verify user")

        with Session() as session:
            if user_id:
                changed_user = session.query(User).filter(User.id == user_id).first()
                is_user_active = changed_user.is_active

                if not changed_user:
                    raise GraphQLError("User not found")

                if (user_id != user.id) or user.is_admin:
                    if username:
                        is_taken = (
                            session.query(User)
                            .filter(User.username == username)
                            .first()
                        )

                        if is_taken:
                            raise GraphQLError("Username already taken")

                        changed_user.username = username

                    if email:
                        is_valid_email(email)
                        is_taken = (
                            session.query(User).filter(User.email == email).first()
                        )

                        if is_taken:
                            raise GraphQLError("Email already taken")

                        changed_user.email = email

                    if password:
                        is_password_secure(password)
                        changed_user.password = hash_password(password)

                    if active:
                        changed_user.is_active = active

                    if full_name:
                        changed_user.full_name = full_name

                    session.commit()
                    session.refresh(changed_user)

                    return UpdateUser(ok=True, user=changed_user)
                else:
                    raise GraphQLError("You are not allowed to perform this action")


class DeleteUser(Mutation):
    class Arguments:
        user_id = Int(required=True)

    ok = Boolean()

    @staticmethod
    @logged_in
    def mutate(root, info, user_id: int):
        user_token = get_authenticated_user(info.context)

        if user_token:
            user: User = user_token[0]
        else:
            raise GraphQLError("Could not verify user")

        with Session() as session:
            if user_id:
                changed_user = session.query(User).filter(User.id == user_id).first()

                if not changed_user:
                    raise GraphQLError("User not found")

                if (user_id != user.id) or user.is_admin:
                    session.delete(changed_user)
                    session.commit()
                    return DeleteUser(ok=True)
                else:
                    raise GraphQLError("You are not allowed to perform this action")
            else:
                raise GraphQLError("User not found")


class RegenerateJWT(Mutation):
    token = String()
    refresh_token = String()
    user = Field(UserObject)

    @staticmethod
    def mutate(root, info):
        user, token = get_authenticated_user(info.context, regeneration=True)
        tokens = regenerate_jwt(token)
        token = tokens[0]
        refresh_token = tokens[1]

        return RegenerateJWT(token=token, refresh_token=refresh_token, user=user)
