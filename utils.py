from db import get_transaction_id
from exception import DatabaseSaveError
from models import BankAccount, Transaction, TransactionResponse

"""
Helper functions that do not include database operations are here in this module.
"""

async def format(transaction_pk: str) -> TransactionResponse:
    transaction: Transaction = await get_transaction_id(transaction_pk)

    return TransactionResponse(
        transaction_type=transaction.details.transaction_type,
        timestamp=transaction.details.timestamp,
        amount=transaction.details.amount,
        destination=getattr(transaction.details, 'destination', None),
        origin=getattr(transaction.details, 'origin', None)
    )

async def save_transaction(transaction: Transaction) -> str:
    try:
        transaction.save()
        return transaction.pk
    except Exception as e:
        raise DatabaseSaveError(e)

async def save_balance(bank_account: BankAccount) -> str:
    try:
        bank_account.save()
    except Exception as e:
        raise DatabaseSaveError(e)

async def send(origin: BankAccount, destination: BankAccount, amount: float) -> str:
    send = Transaction.outward_transaction(
        amount = amount,
        destination=destination.pk
    )

    receive = Transaction.incoming_transaction(
        amount = amount,
        origin = origin.pk
    )

    await save_transaction(send)
    await save_transaction(receive)

    origin.balance -= amount
    destination.balance += amount

    if origin.transfer_history is None:
        origin.transfer_history = []
    
    origin.transfer_history.append(send.pk)
    
    if destination.transfer_history is None:
        destination.transfer_history = []
    
    destination.transfer_history.append(receive.pk)

    await save_balance(origin)
    await save_balance(destination)

    return send.pk