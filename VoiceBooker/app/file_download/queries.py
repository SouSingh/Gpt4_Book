from graphene import ObjectType, Field, String, Int

from app.database.database import Session
from app.database.model import Audiobook
from app.utils.decorators import logged_in


class FileDownloadQuery(ObjectType):
    get_audiobook_filename = Field(String, ebook_id=Int(required=True))

    @staticmethod
    @logged_in
    def resolve_get_audiobook_filename(root, info, ebook_id: int):
        with Session() as session:
            audiobook = session.query(Audiobook).filter_by(ebook_id=ebook_id).first()
            filename = audiobook.filename
            return filename
