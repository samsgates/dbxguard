from fastapi.testclient import TestClient
from dbxguard_api.main import app

def test_health():
    with TestClient(app) as client:
        response=client.get("/health/live"); assert response.status_code==200; assert response.json()["status"]=="ok"
def test_inline_sql_analysis():
    with TestClient(app) as client:
        response=client.post("/api/v1/analyses/sql",json={"environment":"production","sql":"ALTER TABLE x.y DROP COLUMN z;","nodes":[{"id":"x.y.z","type":"COLUMN","name":"z"}],"edges":[]}); assert response.status_code==200; assert response.json()["decision"]=="BLOCK"
