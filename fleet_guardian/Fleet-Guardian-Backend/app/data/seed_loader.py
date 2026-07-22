import pandas as pd
import argparse
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal, engine, Base
from app.models import Asset, BatteryCycle

async def load_csv_into_db_async(csv_path: str):
    df = pd.read_csv(csv_path)
    
    async with AsyncSessionLocal() as session:
        # Get existing assets
        result = await session.execute(select(Asset.battery_id))
        existing_assets = set(result.scalars().all())
        
        unique_batteries = df["battery_id"].unique()
        
        for batt_id in unique_batteries:
            if batt_id not in existing_assets:
                new_asset = Asset(battery_id=batt_id, display_name=batt_id)
                session.add(new_asset)
                existing_assets.add(batt_id)
                
        # Insert cycles
        # We process in batches to avoid overwhelming memory
        batch_size = 1000
        records = df.to_dict("records")
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            for row in batch:
                cycle = BatteryCycle(
                    battery_id=row["battery_id"],
                    cycle=row["cycle"],
                    voltage=row["voltage"],
                    temperature=row["temperature"],
                    capacity=row["capacity"],
                    soh=row["soh"],
                    rul=row["rul"]
                )
                session.add(cycle)
                
        await session.commit()
        print(f"Loaded {len(records)} cycles for {len(unique_batteries)} batteries from {csv_path} into DB.")

def load_csv_into_db(csv_path: str):
    async def run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await load_csv_into_db_async(csv_path)
    
    asyncio.run(run())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to CSV dataset")
    args = parser.parse_args()
    
    load_csv_into_db(args.csv)
