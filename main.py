import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session

sql_ddl = 'sqls/contact-ddl.sql'
with open(sql_ddl, 'r') as f:
    sql_init = f.read()

load_dotenv()
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
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(String)
    createdAt = Column(DateTime, default=datetime.now())
    updatedAt = Column(DateTime, default=datetime.now())
    deletedAt = Column(DateTime, default=None)


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


#This is our identify logic to handle queries
@app.post("/identify")
def create_item(contact: InputContact, db: Session = Depends(get_db)):
    existing_emails = db.query(ContactModel).filter(
        contact.email == ContactModel.email
        and ContactModel.linkPrecedence == 'PRIMARY')
    existing_email = existing_emails.first()
    existing_phones = db.query(ContactModel).filter(
        contact.phone == ContactModel.phone
        and ContactModel.linkPrecedence == 'PRIMARY')
    existing_phone = existing_phones.first()
    primary_contact_id = ""
    if not existing_email and not existing_phone:
        db_item = ContactModel(
            email=contact.email,
            phone=contact.phone,
            linkPrecedence='PRIMARY'
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        primary_contact_id = db_item.id
    elif existing_email and not existing_phone:
        primary_contact_id = existing_email.id
        db_item = ContactModel(
            email=contact.email,
            phone=contact.phone,
            linkedId=existing_email.id,
            linkPrecedence='SECONDARY'
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    elif not existing_email and existing_phone:
        primary_contact_id = existing_phone.id
        db_item = ContactModel(
            email=contact.email,
            phone=contact.phone,
            linkedId=existing_phone.id,
            linkPrecedence='SECONDARY'
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    else:
        if existing_phone.id != existing_email.id:
            primary_contact_id = existing_phone.id
            existing_email.linkedId = existing_phone.id
            existing_email.linkPrecedence = 'SECONDARY'
            db.commit()
            db.refresh(existing_email)

    required_rows = db.query(ContactModel).filter(ContactModel.id == primary_contact_id or
                                                  ContactModel.linkedId == primary_contact_id)
    emails = set()
    phones = set()
    secondary_ids = []
    for row in required_rows:
        emails.add(row.email)
        phones.add(row.phone)
        if row.id != primary_contact_id:
            secondary_ids.append(row.id)
    return {
        "contact": {
            "primaryContactId": primary_contact_id,
            "emails": list(emails),
            "phoneNumbers": list(phones),
            "secondaryContactIds": secondary_ids
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
