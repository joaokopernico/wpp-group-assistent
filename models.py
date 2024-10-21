# models.py
from pydantic import BaseModel

class SendMessage(BaseModel):
    phone: str
    text: str
