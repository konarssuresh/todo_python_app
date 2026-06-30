from .utils import *
from routers.admin import get_current_user,get_db
from fastapi import status
from models import Todos

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title": "learn to code",
        "description": "need to learn everyday",
        "priority": 5,
        "complete": False,
        "owner_id": 1,
        "id": 1
    }]

def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_admin_todo_not_found(test_todo):
    response = client.delete("admin/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':"Todo not found"}

def test_admin_read_all_users(test_todo,test_user):
    response = client.get("/admin/users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

def test_admin_read_one_user(test_todo,test_user):
    response = client.get("/admin/users/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("username") == 'kingjoffrey'

def test_admin_read_one_user_not_founf(test_todo,test_user):
    response = client.get("/admin/users/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND