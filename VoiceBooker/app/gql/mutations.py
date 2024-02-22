from app.file_upload.mutation import FileUploadMutation
from app.user.mutations import UserMutation


class Mutation(UserMutation, FileUploadMutation):
    """A class that serves as the entry point for all GraphQL mutations in the application.

    This class inherits from `UserMutation`, which is the base class for all user mutations. This allows for grouping
    all user-related mutations in one place, which facilitates code management and organization.

    Attributes:
        pass: A placeholder indicating that no additional code needs to be executed.
    """

    pass
