from pydantic import BaseModel, ConfigDict
from redis_om import Field, JsonModel
from typing import List, Optional
from enum import Enum
import datetime

"""
The relationship between a parent class (ex. Owner) and child class (ex. Bank Account) is 
represented by the storing of child IDs in the parent class to maintain a flattened structure 
(no nesting).
"""

class TransactionType(str, Enum):
    transfer = "TRANSFER"
    receive = "RECEIVE"

class BaseTransaction(JsonModel):
    transaction_type: TransactionType
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    amount: float

    model_config = ConfigDict(arbitrary_types_allowed=True)

class OutwardTransaction(BaseTransaction):
    destination: str

class IncomingTransaction(BaseTransaction):
    origin: str

class Transaction(JsonModel):
    details: BaseTransaction
    
    @classmethod
    def outward_transaction(cls, destination: str, amount: float):
        return cls(details=OutwardTransaction(transaction_type=TransactionType.transfer, destination=destination, amount=amount))

    @classmethod
    def incoming_transaction(cls, origin: str, amount: float):
        return cls(details=IncomingTransaction(transaction_type=TransactionType.receive, origin=origin, amount=amount))

class TransactionResponse(BaseModel):
    transaction_type: TransactionType
    timestamp: datetime.datetime
    amount: float
    origin: Optional[str] = None
    destination: Optional[str] = None

class TransactionHistoryResponse(BaseModel):
    transaction_history: List[TransactionResponse]
    
class BankAccount(JsonModel):
    transfer_history: Optional[List[str]] = None
    balance: float = 0

class Owner(JsonModel):
    name: str = Field(index=True)
    bank_accounts: Optional[List[str]] = None