from exception import BankAccountNotFoundError, DatabaseSaveError, NotFoundError, OwnerNotFoundError
from models import BankAccount, Owner, Transaction

"""
All CRUD database operations with Redis OM
"""
# new customer
async def save_customer(owner: Owner) -> str:
    try:
        owner.save()
        return owner.pk
    except Exception as e:
        raise DatabaseSaveError(e)

### Retrieve customer object via ID
async def get_customer(pk: str) -> Owner:
    try:
        return Owner.get(pk)
    except NotFoundError:
        raise OwnerNotFoundError

# new bank account for a customer
async def create_account(owner: Owner, amount: float) -> str:
    new_account = BankAccount()
    
    if owner.bank_accounts is None:
        owner.bank_accounts = []
    owner.bank_accounts.append(new_account.pk)
    new_account.balance = amount

    try:
        new_account.save()
    except Exception as e:
        raise DatabaseSaveError(e)
    
    try:
        owner.save()
    except Exception as e:
        raise DatabaseSaveError(e)
    return new_account.pk

### Retrieve bank account object given a pk string
async def get_bank_account(pk: str) -> BankAccount:
    try:
        return BankAccount.get(pk)
    except NotFoundError:
        raise BankAccountNotFoundError

### Retrieve transaction object given an ID
async def get_transaction_id(pk: str) -> Transaction:
    return Transaction.get(pk)
