from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import gradio as gr
from database import get_session
from models import Book, Author, Review
import schemas
from openai import OpenAI
import os
from dotenv import load_dotenv
from frontend import demo

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "online"}

@app.post("/authors", response_model=schemas.AuthorResponse, status_code=201)
def create_author(author_data: schemas.AuthorCreate, db: Session = Depends(get_session)):
    new_author = Author(name=author_data.name, bio=author_data.bio)
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

@app.get("/authors", response_model=List[schemas.AuthorResponse])
def get_all_authors(db: Session = Depends(get_session)):
    return db.query(Author).all()

@app.get("/authors/search", response_model=List[schemas.AuthorResponse])
def search_authors(q: str, db: Session = Depends(get_session)):
    authors = db.query(Author).filter(Author.name.ilike(f"%{q}%")).limit(20).all()
    return authors

@app.put("/authors/{author_id}", response_model=schemas.AuthorResponse)
def update_author(author_id: UUID, author_data: schemas.AuthorUpdate, db: Session = Depends(get_session)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if author_data.name is not None:
        author.name = author_data.name
    if author_data.bio is not None:
        author.bio = author_data.bio
    db.commit()
    db.refresh(author)
    return author

@app.delete("/authors/{author_id}", status_code=204)
def delete_author(author_id: UUID, db: Session = Depends(get_session)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(author)
    db.commit()

@app.get("/books", response_model=List[schemas.BookResponse])
def get_all_books(db: Session = Depends(get_session)):
    books = db.query(Book).all()
    return books

@app.get("/books/search", response_model=List[schemas.BookResponse])
def search_books(q: str, db: Session = Depends(get_session)):
    books = db.query(Book).filter(Book.title.ilike(f"%{q}%")).all()
    return books

@app.get("/books/semantic-search", response_model=List[schemas.BookResponse])
def semantic_search(q: str, db: Session = Depends(get_session)):
    search_vector = get_embedding(q)
    closest_books = db.query(Book).order_by(Book.embedding.cosine_distance(search_vector)).limit(10).all()
    return closest_books

@app.get("/books/rag-search")
def rag_search(q: str, db: Session = Depends(get_session)):
    search_vector = get_embedding(q)
    results = db.query(Book).order_by(
        Book.embedding.cosine_distance(search_vector)
    ).limit(10).all()
    context_text = "\n".join([
        f"Title: {b.title}, Synopsis: {b.synopsis}"
        for b in results
    ])
    prompt = f"Use the following context to answer: {context_text}\n\nQuestion: {q}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "answer": response.choices[0].message.content,
        "sources": [b.title for b in results]
    }

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_specific_book(book_id: UUID, db: Session = Depends(get_session)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=schemas.BookResponse, status_code=201)
def create_book(book_data: schemas.BookCreate, db: Session = Depends(get_session)):
    author = db.query(Author).filter(Author.id == book_data.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author ID does not exist")
    new_book = Book(title=book_data.title, author_id=book_data.author_id, synopsis=book_data.synopsis)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: UUID, book_data: schemas.BookUpdate, db: Session = Depends(get_session)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book_data.title is not None:
        book.title = book_data.title
    if book_data.author_id is not None:
        book.author_id = book_data.author_id
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: UUID, db: Session = Depends(get_session)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()

@app.get("/reviews", response_model=List[schemas.ReviewResponse])
def get_all_reviews(db: Session = Depends(get_session)):
    return db.query(Review).all()

@app.post("/books/{book_id}/reviews", response_model=schemas.ReviewResponse)
def create_review(book_id: UUID, review_data: schemas.ReviewCreate, db: Session = Depends(get_session)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    new_review = Review(rating=review_data.rating, comment=review_data.comment, book_id=book_id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@app.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: UUID, db: Session = Depends(get_session)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()

def get_embedding(text:str):
    response = client.embeddings.create(input=[text], model='text-embedding-3-small')
    return response.data[0].embedding

@app.get("/authors/semantic-search")
def semantic_author_search(q: str, db: Session = Depends(get_session)):
    search_vector = get_embedding(q)
    authors = db.query(Author).order_by(Author.embedding.cosine_distance(search_vector)).limit(3).all()
    return [{"id": str(a.id), "name": a.name, "bio": a.bio} for a in authors]

@app.get("/reviews/semantic-search")
def semantic_review_search(sentiment: str, db: Session = Depends(get_session)):
    search_vector = get_embedding(sentiment)
    reviews = db.query(Review).order_by(Review.embedding.cosine_distance(search_vector)).limit(5).all()
    return [{"id": str(r.id), "comment": r.comment, "rating": r.rating, "book": {"title": r.book.title}} for r in reviews]

app = gr.mount_gradio_app(app, demo, path="/")