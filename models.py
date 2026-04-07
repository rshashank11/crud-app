from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, UUID, Date
from typing import List
from datetime import datetime
import uuid
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase): #Creating a blank copy of the blueprint
    pass # Tell function not to do anything after(no custom data to be passed)


class Author(Base):
    __tablename__ = "authors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    bio = Column(Text)
    embedding = Column(Vector(1536))
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    synopsis = Column(String, nullable=True)
    embedding = Column(Vector(1536))
    author_id = Column(UUID, ForeignKey("authors.id"), index=True)
    author = relationship("Author", back_populates="books") #Here "books" is the variable in Author model
    edition = Column(Date)
    reviews = relationship("Review", back_populates="book")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rating = Column(Integer)
    comment = Column(Text)
    embedding = Column(Vector(1536))
    book_id = Column(UUID, ForeignKey("books.id"), index=True)
    book = relationship("Book", back_populates="reviews")

