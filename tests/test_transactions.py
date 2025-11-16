from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_transactions_empty():
    """Тест получения пустого списка транзакций"""
    response = client.get("/api/v1/transactions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_transaction():
    """Тест создания транзакции"""
    transaction_data = {
        "title": "Тестовая транзакция",
        "amount": 100.50,
        "description": "Описание",
        "category": "Еда",
        "type": "expense"
    }
    response = client.post("/api/v1/transactions", json=transaction_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == transaction_data["title"]
    assert data["amount"] == transaction_data["amount"]
    assert "id" in data
    assert "created_at" in data


def test_get_transaction_by_id():
    """Тест получения транзакции по ID"""
    # Сначала создаем транзакцию
    transaction_data = {
        "title": "Тест",
        "amount": 50.0,
        "type": "expense"
    }
    create_response = client.post("/api/v1/transactions", json=transaction_data)
    transaction_id = create_response.json()["id"]
    
    # Получаем по ID
    response = client.get(f"/api/v1/transactions/{transaction_id}")
    assert response.status_code == 200
    assert response.json()["id"] == transaction_id


def test_get_balance():
    """Тест получения баланса"""
    response = client.get("/api/v1/transactions/stats/balance")
    assert response.status_code == 200
    assert "balance" in response.json()
    assert "total_income" in response.json()
    assert "total_expenses" in response.json()

