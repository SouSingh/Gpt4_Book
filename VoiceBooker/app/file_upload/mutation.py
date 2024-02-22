from graphene import ObjectType

from app.file_upload.file_upload_mutations import CreateFileUpload, DeleteFileUpload


class FileUploadMutation(ObjectType):
    create_file_upload = CreateFileUpload.Field()
    delete_file_upload = DeleteFileUpload.Field()
