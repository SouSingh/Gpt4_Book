from datetime import timezone, datetime, timedelta

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc), nullable=False)
    last_login = Column(DateTime)

    # relationships
    file_uploads = relationship("FileUpload", back_populates="user", lazy="selectin")
    ebooks = relationship("EBook", back_populates="user", lazy="selectin")
    audiobooks = relationship("Audiobook", back_populates="user", lazy="selectin")


class FileUpload(Base):

    __tablename__ = "file_uploads"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc), nullable=False)
    delete_time = Column(
        DateTime,
        default=datetime.now(tz=timezone.utc) + timedelta(days=30),
        nullable=False,
    )

    # relationships
    user = relationship("User", back_populates="file_uploads", lazy="selectin")
    ebooks = relationship("EBook", back_populates="file_upload", lazy="selectin")


class Audiobook(Base):

    __tablename__ = "audiobooks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    ebook_id = Column(ForeignKey("ebooks.id"), nullable=False, unique=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc), nullable=False)
    delete_time = Column(
        DateTime,
        default=datetime.now(tz=timezone.utc) + timedelta(days=30),
        nullable=False,
    )

    # relationships
    ebook = relationship("EBook", back_populates="audiobooks", lazy="selectin")
    user = relationship("User", back_populates="audiobooks", lazy="selectin")


class EBook(Base):

    __tablename__ = "ebooks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    file_upload_id = Column(ForeignKey("file_uploads.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc), nullable=False)
    last_accessed = Column(DateTime, nullable=True)

    # relationships
    file_upload = relationship("FileUpload", back_populates="ebooks", lazy="selectin")
    audiobooks = relationship("Audiobook", back_populates="ebook", lazy="selectin")
    user = relationship("User", back_populates="ebooks", lazy="selectin")
