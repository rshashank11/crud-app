from pydantic import BaseModel, UUID4, ConfigDict
from typing import List

class AuthorBase(BaseModel):
    name: str
    bio: str | None = None

class AuthorCreate(AuthorBase):
    pass 

class AuthorUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None

class AuthorResponse(AuthorBase):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)

class ReviewBase(BaseModel):
    rating: int
    comment: str | None = None
    
class ReviewCreate(ReviewBase):
    book_id: UUID4

class ReviewResponse(ReviewBase):
    id: UUID4
    book_id: UUID4
    model_config = ConfigDict(from_attributes=True)

class BookBase(BaseModel):
    title: str
    synopsis: str | None = None # Added this here so it's available in Create/Update/Response

class BookCreate(BookBase):
    author_id: UUID4

class BookUpdate(BaseModel):
    title: str | None = None
    author_id: UUID4 | None = None
    synopsis: str | None = None

class BookResponse(BookBase):
    id: UUID4
    author_id: UUID4
    author: AuthorResponse
    reviews: List[ReviewResponse] = []
    model_config = ConfigDict(from_attributes=True)