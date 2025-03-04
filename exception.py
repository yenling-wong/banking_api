from redis_om import NotFoundError

class InsufficientBalanceError(Exception):
    def __init__(self, message="Insufficient balance for this transaction"):
        self.message = message
        super().__init__(self.message)

class InvalidAmountError(Exception):
    def __init__(self, message="Invalid amount"):
        self.message = message
        super().__init__(self.message)

class OwnerNotFoundError(NotFoundError):
    """Raised when an owner is not found in the database"""
    pass

class BankAccountNotFoundError(NotFoundError):
    """Raised when a bank account is not found in the database"""
    pass

class DatabaseSaveError(Exception):
    """Raised when a save operation is not successful"""
    pass