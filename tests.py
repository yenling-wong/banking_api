import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
from main import Owner, BankAccount  # Import your models

client = TestClient(app)

"""
This module contains 10 test definitions for the API endpoints. They aim to cover 
both valid and invalid inputs, as well as mock dependencies such as database operations.

"""

@pytest.fixture
def mock_save_customer(mocker):
    return mocker.patch('main.save_customer', return_value='owner_id_123')

@pytest.fixture
def mock_create_account(mocker):
    return mocker.patch('main.create_account', return_value='IBAN123')

@pytest.fixture
def mock_get_customer(mocker):
    return mocker.patch('main.get_customer', return_value=Owner(id='owner_id_123', name='John Doe'))

@pytest.fixture
def mock_get_bank_account(mocker):
    return mocker.patch('main.get_bank_account', return_value=BankAccount(id="IBAN123",balance=1000.0))

@pytest.fixture
def mock_transfer(mocker):
    return mocker.patch('main.send', return_value="transfer_pk_123")

def test_new_owner_success(mock_save_customer, mock_create_account):
    response = client.post('/owner/1000.0', json={'owner': {'name': 'John Doe'}, 'amount': 1000.0})
    assert response.status_code == 201
    assert response.json() == {'id': 'owner_id_123', 'iban': 'IBAN123'}

def test_new_owner_invalid_amount():
    response = client.post('/owner/-100.0', json={'owner': {'name': 'John Doe'}, 'amount': -100.0})
    assert response.status_code == 400
    assert 'Amount must be a positive float' in response.json()['detail']

def test_new_account_success(mock_get_customer, mock_create_account):
    response = client.post('/owner/owner_id_123/bank_account/1000.0')
    assert response.status_code == 201
    assert response.json() == {'iban': 'IBAN123'}

def test_new_account_invalid_amount(mock_get_customer):
    response = client.post('/owner/owner_id_123/bank_account/-1000.0')
    assert response.status_code == 400
    assert 'Amount must be a positive float' in response.json()['detail']

def test_transfer_success(mock_get_bank_account, mock_transfer):
    mock_get_bank_account.side_effect = [
        BankAccount(id="IBAN123", balance=950.0),
        BankAccount(id="IBAN456", balance=500.0)
    ]
    response = client.post('/owner/owner_id_123/bank_account/IBAN123/transfer/IBAN456/50.0')
    assert response.json() == {'transaction_reference_number': 'transfer_pk_123', 'account_balance': '950.0'}

def test_transfer_invalid_amount(mock_get_bank_account, mock_transfer):
    mock_get_bank_account.side_effect = [
        BankAccount(id="IBAN123", balance=950.0),
        BankAccount(id="IBAN456", balance=500.0)
    ]
    response = client.post('/owner/owner_id_123/bank_account/IBAN123/transfer/IBAN456/-50.0')
    assert response.status_code == 400
    assert 'Amount must be a positive float' in response.json()['detail']

def test_transfer_insufficient_balance(mock_get_bank_account):
    mock_get_bank_account.return_value = BankAccount(balance=10)
    response = client.post('/owner/owner_id_123/bank_account/IBAN123/transfer/IBAN456/50')
    assert response.status_code == 400
    assert 'Insufficient Balance' in response.json()['detail']

def test_account_balance(mock_get_bank_account):
    response = client.get('/owner/owner_id_123/bank_account/IBAN123/balance')
    assert response.status_code == 200
    assert response.json() == {'account_balance': 1000}

def test_transfer_history_with_transactions(mock_get_bank_account, mocker):
    mock_get_bank_account.return_value = BankAccount(transfer_history=['trans1', 'trans2'])
    mock_format = mocker.patch('main.format', side_effect=[{'id': 'trans1'}, {'id': 'trans2'}])
    response = client.get('/owner/owner_id_123/bank_account/IBAN123/transactions')
    assert response.status_code == 200
    assert response.json() == [{'id': 'trans1'}, {'id': 'trans2'}]

def test_transfer_history_no_transactions(mock_get_bank_account):
    mock_get_bank_account.return_value = BankAccount(transfer_history=None)
    response = client.get('/owner/owner_id_123/bank_account/IBAN123/transactions')
    assert response.status_code == 200
    assert response.json() == []
