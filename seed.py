import requests
import random
from database import engine, SessionLocal
from faker import Faker
from models import Author, Book, Review, Base
from openai import OpenAI
import os

from main import get_embedding

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

fake = Faker()

db = SessionLocal()

Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)


def generate_synopsis(title: str, author: str):
    print(f"Writing synopsis for: {title}...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a librarian. Write a 50-word plot summary for the book provided. If it's a generic title, invent a creative fictional plot."},
            {"role": "user", "content": f"Title: {title}, Author: {author}"}
        ]
    )
    
    return response.choices[0].message.content

try:
    url = "https://openlibrary.org/search.json?subject=fiction&limit=1000"
    response = requests.get(url)
    data = response.json()
    docs = data.get("docs", [])

    author_cache = {}
    books_created = 0
    seen_titles = set()

    for doc in docs:
        title = doc.get("title")
        author_names = doc.get("author_name")

        

        if title in seen_titles:
            continue

        if not title or not author_names:
            continue

        seen_titles.add(title)

        primary_author_name = author_names[0]

        if primary_author_name not in author_cache:
            new_author = Author(name=primary_author_name, bio="Data pulled from Open Library.")
            db.add(new_author)
            author_cache[primary_author_name] = new_author
        
        current_author = author_cache[primary_author_name]

        book_synopsis = generate_synopsis(title, primary_author_name)

        text_to_embed = f"Title: {title}. Synopsis: {book_synopsis}"

        book_vector = get_embedding(text_to_embed)

        new_book = Book(title=title, author=current_author, synopsis=book_synopsis, embedding=book_vector)
        db.add(new_book)
        books_created += 1

    db.commit() 
    
    all_books = db.query(Book).all()
    reviews_created = 0

    for book in all_books:
        number_of_reviews = random.randint(0, 5)
        
        for _ in range(number_of_reviews):
            new_review = Review(
                rating=random.randint(1, 5),     
                comment=fake.paragraph(),       
                book_id=book.id                  
            )
            db.add(new_review)
            reviews_created += 1

    db.commit() 


except Exception as e:
    db.rollback()
    print(f"Error occurred: {e}")

finally:
    db.close()