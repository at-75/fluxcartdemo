import os
from datetime import datetime

import psycopg2
from os import getenv
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session

sql_ddl = 'sqls/contact-ddl.sql'
with open(sql_ddl, 'r') as f:
    sql_init = f.read()

load_dotenv()
# conn = psycopg2.connect(database=getenv('PGDATABASE'),
#                         user=getenv('PGUSER'),
#                         host=getenv('PGHOST'),
#                         password=getenv('PGPASSWORD'),
#                         port=5432)

app = FastAPI()

DB_USER = os.getenv('PGUSER')
DB_PASSWORD = os.getenv('PGPASSWORD')
DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ContactModel(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    linkedId = Column(Integer,nullable=True)
    linkPrecedence = Column(String)
    createdAt = Column(DateTime, default=datetime.now())
    updatedAt = Column(DateTime, default=datetime.now())
    deletedAt = Column(DateTime, default=datetime.now())


class InputContact(BaseModel):
    email: str
    phone: str


Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/identify")
def create_item(contact: InputContact, db: Session = Depends(get_db)):

    #if doesnt exists create one
    #if only email exists -secondary
    #if only phone exists -secondary
    #if both exists

    db_item = ContactModel(
        email=contact.email,
        phone=contact.phone
    )
    print(db_item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Item created successfully", "item_id": db_item.id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
