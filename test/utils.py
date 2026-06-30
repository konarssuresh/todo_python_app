import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine,text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from models import Todos,Users
from routers.auth import bcrypt_context



SQLALCHEMY_DATABASE_URI = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    print("override_get_db")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    print("override_get_current_user")
    return {'username':"kingjoffrey",'id':1,'user_role':'Admin'}



client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="learn to code",
        description="need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="kingjoffrey",
        email="joffrey@gmail.com",
        hashed_password=bcrypt_context.hash("Joffrey123"),
        first_name="king",
        last_name="joffrey",
        role="Admin"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()