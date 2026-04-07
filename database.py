from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

import os
from dotenv import load_dotenv

load_dotenv()

postgresql_url = f"postgresql://postgres.dewstjfniopxeazoueqj:{os.environ.get('DB_PASSWORD')}@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"

engine = create_engine(postgresql_url)

SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



