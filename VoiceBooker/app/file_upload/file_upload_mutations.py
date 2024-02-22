import threading

from graphene import Mutation, String, Boolean, Field, Int
from graphql import GraphQLError

from app.database.database import Session
from app.database.model import FileUpload
from app.ebook.utils.create_ebook import create_ebook
from app.file_convertion.epub_to_txt import epub_to_txt
from app.file_convertion.pdf_to_txt import pdf_to_txt
from app.gql.types import FileUploadObject
from app.user.utils.user import get_authenticated_user


class CreateFileUpload(Mutation):
    class Arguments:
        filename = String(required=True)
        file_type = String(required=True)
        title = String(required=True)
        author = String(required=True)
        summary = String(required=True)

    ok = Boolean()
    file_upload = Field(FileUploadObject)

    @staticmethod
    def mutate(
        root,
        info,
        filename: str,
        file_type: str,
        title: str,
        author: str,
        summary: str,
    ):
        with Session() as session:
            token_user = get_authenticated_user(info.context)
            user = token_user[0]

            file_upload = FileUpload(
                filename=filename, file_type=file_type, user_id=user.id
            )

            session.add(file_upload)
            session.commit()
            session.refresh(file_upload)

            file_upload_id = file_upload.id

            create_ebook(
                title=title,
                author=author,
                summary=summary,
                file_upload_id=file_upload_id,
                user_id=user.id,
                session=session,
            )

            if file_type == "application/pdf":
                # this is entry point for book to audio conversion
                t1 = threading.Thread(target=pdf_to_txt)
                t1.start()
            elif file_type == "application/epub+zip":
                t1 = threading.Thread(target=epub_to_txt)
                t1.start()

            return CreateFileUpload(ok=True, file_upload=file_upload)


class DeleteFileUpload(Mutation):
    class Arguments:
        id = Int(required=True)

    ok = Boolean()

    @staticmethod
    def mutate(root, info, id: int):
        with Session() as session:
            token_user = get_authenticated_user(info.context)
            user = token_user[0]

            file_upload = session.query(FileUpload).filter(FileUpload.id == id).first()

            if not file_upload:
                raise GraphQLError("FileUpload not found")

            if not (file_upload.user_id == user.id or user.is_admin):
                raise GraphQLError("You are not authorized to delete this file")

            session.delete(file_upload)
            session.commit()

            return DeleteFileUpload(ok=True)
