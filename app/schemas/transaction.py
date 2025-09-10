# app/schemas/transaction.py
from pydantic import BaseModel
from typing import Union

class Transaction(BaseModel):
    date: str  # ISO string from frontend
    amount: float
    description: str
    tax_category: str
