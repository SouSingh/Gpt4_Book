from app.database.database import Session
from app.database.model import EBook


def create_ebook(
    title: str,
    author: str,
    summary: str,
    file_upload_id: int,
    user_id: int,
    session: Session,
) -> None:
    ebook = EBook(
        title=title,
        author=author,
        summary=summary,
        file_upload_id=file_upload_id,
        user_id=user_id,
    )

    session.add(ebook)
    session.commit()
    session.refresh(ebook)
