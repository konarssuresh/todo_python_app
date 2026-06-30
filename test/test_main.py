import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main
from fastapi.testclient import TestClient
from fastapi import status

client = TestClient(main.app)

def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status":"Healthy"}