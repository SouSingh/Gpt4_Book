from graphene import ObjectType

from app.file_download.queries import FileDownloadQuery
from app.user.queries import UserQuery


class Query(UserQuery, FileDownloadQuery):
    """A class that serves as the entry point for all GraphQL queries in the application.

    This class inherits from `UserQuery`, which is the base class for all user queries. This allows for grouping all
    user-related queries in one place, which facilitates code management and organization.

    Attributes:
        pass: A placeholder indicating that no additional code needs to be executed.
    """

    pass
