import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from db_model import ContactModel
from input_model import InputContact
from fetch_db_url import postgres_url

app = FastAPI()
load_dotenv()

postgres_prod_url = postgres_url()
engine = create_engine(postgres_prod_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# This is our identify logic to handle queries
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
    primary_row = db.query(ContactModel).filter(ContactModel.id == primary_contact_id).first()
    secondary_rows = db.query(ContactModel).filter(ContactModel.linkedId == primary_contact_id)
    emails = {primary_row.email}
    phones = {primary_row.phone}
    secondary_ids = []
    for s_row in secondary_rows:
        emails.add(s_row.email)
        phones.add(s_row.phone)
        secondary_ids.append(s_row.id)

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
