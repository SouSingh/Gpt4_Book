from graphene import ObjectType

from app.user.user_mutations import (
    CreateUser,
    LoginUser,
    UpdateUser,
    DeleteUser,
    RegenerateJWT,
)


class UserMutation(ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    refresh_token = RegenerateJWT.Field()
