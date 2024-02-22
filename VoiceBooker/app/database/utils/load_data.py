from app.database.database import Base, engine, Session
from app.database.model import User, FileUpload
from app.ebook.utils.create_ebook import create_ebook
from app.file_upload.utils.create_audiobook import create_audiobook
from app.user.utils.password import hash_password


def create_database() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    user = User(
        username="admin",
        email="admin@admin.com",
        password=hash_password("admin"),
        full_name="admin",
        is_active=True,
        is_admin=True,
    )

    file_upload = FileUpload(
        filename="test.pdf",
        file_type="application/pdf",
        user_id=1,
    )

    with Session() as session:
        session.add(user)
        session.add(file_upload)
        session.commit()
        create_ebook(
            title="test",
            author="test",
            summary="test",
            file_upload_id=1,
            user_id=1,
            session=Session(),
        )
        audiobook = create_audiobook(
            filename="test.mp3",
            ebook_id=1,
            user_id=1,
        )
        session.close()
        print("Database created and user added")
