from pydantic import BaseModel


class InputContact(BaseModel):
    email: str
    phone: str
