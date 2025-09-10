from typing import Union
from pydantic import BaseModel

class Transaction(BaseModel):
    date: str  # or datetime if you want to parse automatically
    amount: Union[float, str]  # frontend might send string
    description: str
    tax_category: str
