from graphene import ObjectType, Int, String, Boolean, DateTime, List, Field


class UserObject(ObjectType):
    id = Int()
    username = String()
    email = String()
    full_name = String()
    is_active = Boolean()
    is_admin = Boolean()
    created_at = DateTime()
    last_login = DateTime()
    file_uploads = List(lambda: FileUploadObject)
    ebooks = List(lambda: EBookObject)
    audiobooks = List(lambda: AudiobookObject)

    @staticmethod
    def resolve_file_uploads(root, info):
        return root.file_uploads

    @staticmethod
    def resolve_ebooks(root, info):
        return root.ebooks

    @staticmethod
    def resolve_audiobooks(root, info):
        return root.audiobooks


class FileUploadObject(ObjectType):
    id = Int()
    filename = String()
    file_type = String()
    user_id = Int()
    created_at = DateTime()
    delete_time = DateTime()
    user = Field(lambda: UserObject)
    ebooks = List(lambda: EBookObject)

    @staticmethod
    def resolve_user(root, info):
        return root.user

    @staticmethod
    def resolve_ebooks(root, info):
        return root.ebooks


class EBookObject(ObjectType):
    id = Int()
    title = String()
    author = String()
    summary = String()
    file_upload_id = Int()
    user_id = Int()
    created_at = DateTime()
    delete_time = DateTime()
    file_upload = Field(lambda: FileUploadObject)
    user = Field(lambda: UserObject)
    audiobooks = List(lambda: AudiobookObject)

    @staticmethod
    def resolve_file_upload(root, info):
        return root.file_upload

    @staticmethod
    def resolve_user(root, info):
        return root.user

    @staticmethod
    def resolve_audiobooks(root, info):
        return root.audiobooks


class AudiobookObject(ObjectType):
    id = Int()
    filename = String()
    ebook_id = Int()
    user_id = Int()
    created_at = DateTime()
    delete_time = DateTime()
    ebook = Field(lambda: EBookObject)
    user = Field(lambda: UserObject)

    @staticmethod
    def resolve_ebook(root, info):
        return root.ebook

    @staticmethod
    def resolve_user(root, info):
        return root.user
