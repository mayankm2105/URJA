import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from scripts.generate_synthetic_dataset import generate_synthetic_data
from app.data.seed_loader import load_csv_into_db_async

# Create async sqlite engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    # Setup the database and seed it
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    generate_synthetic_data()
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "synthetic_battery_dataset.csv")
    
    # Run the seeder logic inside the test db
    import pandas as pd
    from app.models import Asset, BatteryCycle
    df = pd.read_csv(csv_path)
    async with TestingSessionLocal() as session:
        unique_batteries = df["battery_id"].unique()
        for batt_id in unique_batteries:
            session.add(Asset(battery_id=batt_id, display_name=batt_id))
            
        records = df.to_dict("records")
        for row in records:
            session.add(BatteryCycle(
                battery_id=row["battery_id"],
                cycle=row["cycle"],
                voltage=row["voltage"],
                temperature=row["temperature"],
                capacity=row["capacity"],
                soh=row["soh"],
                rul=row["rul"]
            ))
        await session.commit()
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists(csv_path):
        os.remove(csv_path)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_get_assets(client: AsyncClient):
    # 16. GET /assets returns list with exactly 20 entries
    response = await client.get("/assets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20

@pytest.mark.asyncio
async def test_get_asset_health_valid(client: AsyncClient):
    # 17. GET /assets/{valid_battery_id}/health
    response = await client.get("/assets/SYN0001/health")
    assert response.status_code == 200
    data = response.json()
    assert "battery_id" in data
    assert "rul_cycles" in data
    assert "temperature_anomaly" in data

@pytest.mark.asyncio
async def test_get_asset_health_invalid(client: AsyncClient):
    # 18. GET /assets/{invalid_battery_id}/health -> 404
    response = await client.get("/assets/INVALID_ID/health")
    assert response.status_code == 404
    assert "error" not in response.json() # FastAPI default 404 is {"detail": ...} 
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_get_asset_recommendation(client: AsyncClient):
    # 19. GET /assets/{valid_battery_id}/recommendation -> 200, mock Groq
    from unittest.mock import patch, AsyncMock
    with patch("app.routers.assets.generate_explanation", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {
            "explanation": "Test",
            "likely_cause": "Test",
            "recommendation": "Test",
            "urgency": "Low"
        }
        response = await client.get("/assets/SYN0001/recommendation")
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "urgency" in data

@pytest.mark.asyncio
async def test_get_asset_history(client: AsyncClient):
    # 20. GET /assets/{valid_battery_id}/history
    response = await client.get("/assets/SYN0001/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "cycle" in data[0]
    # Check sorted ascending by cycle
    cycles = [item["cycle"] for item in data]
    assert cycles == sorted(cycles)

@pytest.mark.asyncio
async def test_get_fleet_summary(client: AsyncClient):
    # 21. GET /fleet/summary
    response = await client.get("/fleet/summary")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_assets"] == 20
    assert data["healthy_count"] + data["watch_count"] + data["critical_count"] == 20

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    # 22. GET /health-check
    response = await client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
