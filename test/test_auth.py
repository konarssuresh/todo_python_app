from fastapi import status
from .utils import *

from routers.auth import get_current_user, get_db,bcrypt_context

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_user(test_user):
    response = client.get("/auth/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("username") == "kingjoffrey"

def test_create_user(test_user):
    request_data = {
    "username":"Suresh1",
    "email":"suresh1@gmail.com",
    "first_name":"Suresh",
    "last_name":"Konar",
    "password":"Suresh@123",
    "role":"Admin",
    "phone_number":"123123123"
    }
    response = client.post("/auth/",json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.username == 'Suresh1').first()
    assert user.username == "Suresh1"
    assert user.email == "suresh1@gmail.com"
    assert user.first_name == "Suresh"

def test_change_password(test_user):
    request_data = {
    "old_password":"Joffrey123",
    "new_password":"Suresh@1234"
    }

    response = client.post("/auth/change_password/",json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_authenticate_user(test_user):
    request_data = {
        "username":"kingjoffrey",
        "password":"Joffrey123"
    }
    response = client.post("/auth/token/", data=request_data)
    assert response.status_code == 200

def test_unauthenticated_user(test_user):
    request_data = {
        "username": "kingjoffrey",
        "password": "Joffrey1234"
    }
    response = client.post("/auth/token/", data=request_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_phone_number(test_user):
    request_data = {
        "phone_number":"123123123"
    }
    response = client.put("/auth/change_phone_number/",json=request_data)
    assert response.status_code == status.HTTP_202_ACCEPTED