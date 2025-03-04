from typing import List
from utils import format, send
from redis_om import get_redis_connection

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import create_account, get_bank_account, get_customer, save_customer
from models import Owner, TransactionResponse, BankAccount

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:8000'],
    allow_methods=['*']
)

"""
Creates a new bank account for a new customer with an initial deposit. The endpoint returns a unique identification
number
The request object should look like this:
{
  "owner": {
    "name": "John Doe"
  },
  "amount": 300.0
}

The successful response object should look like this:
{
  "id": "01JN1MAZP9M9KCJYMBZS6V5YNN",
  "iban": "01JN1MAZPDZNP6P3CSZR4S6ME9"
}
"""
@app.post('/owner/{amount}', status_code=201)
async def new_owner(data: dict) -> dict[str, str]:
    owner = Owner(**data['owner'])
    owner_id = await save_customer(owner)
    amount = data['amount']
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be a positive float")
    iban = await create_account(owner, amount)
    return {
        "id" : owner_id,
        "iban": iban
    }

"""
IBAN acts as the pk or id of a bank account to uniquely identify it. This endpoint creates
an account for an existing customer

Response:
{
  "iban": "01JN1ME3R55EB343J7G1S792JV"
}
"""
@app.post('/owner/{id}/bank_account/{amount}', status_code=201)
async def new_account(id: str, amount: float) -> dict[str, str]:
    owner = await get_customer(id)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be a positive float")
    iban = await create_account(owner, amount)
    return {
        "iban": iban
    }

"""
Returns a unique identification when a transaction is performed, as well as the balance remained.

Response:
{
  "transaction_reference_number": "01JN1MJDG6ZTWHHPVA8N6RYMF9",
  "account_balance": "423.65"
}
"""
@app.post('/owner/{id}/bank_account/{bank_account_iban}/transfer/{recipient_iban}/{amount}', status_code=201)
async def transfer(amount: float, id: str, bank_account_iban: str, recipient_iban: str) -> dict[str, str]:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be a positive float")
    origin = await get_bank_account(bank_account_iban)
    if origin.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient Balance")
    destination = await get_bank_account(recipient_iban)

    transfer_pk = await send(origin=origin, destination=destination, amount=amount)

    return {
        "transaction_reference_number": transfer_pk,
        "account_balance": origin.balance
    }

"""
Returns balance remaining in an account.

Response:
{
  "account_balance": 423.65
}
"""
@app.get('/owner/{id}/bank_account/{bank_account_iban}/balance', status_code=200)
async def account_balance(id: str, bank_account_iban: str) -> dict[str, float]:
    bank_account = await get_bank_account(bank_account_iban)

    return {
        "account_balance": bank_account.balance
    }

"""
Returns list of transactions in chronological order
[
  {
    "transaction_type": "TRANSFER",
    "timestamp": "2025-02-26T18:23:46.310933",
    "amount": 76.35,
    "origin": null,
    "destination": "01JN1MAZPDZNP6P3CSZR4S6ME9"
  },
  {
    "transaction_type": "TRANSFER",
    "timestamp": "2025-02-26T18:27:43.468005",
    "amount": 26.09,
    "origin": null,
    "destination": "01JN1MAZPDZNP6P3CSZR4S6ME9"
  },
  {
    "transaction_type": "TRANSFER",
    "timestamp": "2025-02-26T18:28:10.406067",
    "amount": 38.94,
    "origin": null,
    "destination": "01JN1MAZPDZNP6P3CSZR4S6ME9"
  }
]
"""
@app.get('/owner/{id}/bank_account/{bank_account_iban}/transactions', status_code=200)
async def transfer_history(bank_account_iban: str):
    bank_account = await get_bank_account(bank_account_iban)
    transaction_ids: List[str] = bank_account.transfer_history

    if transaction_ids is None:
        return []

    transfer_history: List[TransactionResponse] = [await format(transaction_id) for transaction_id in transaction_ids]

    return transfer_history