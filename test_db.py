from database import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print("✅ Connected to the database successfully!")
except Exception as e:
    print("❌ Connection failed:")
    print(e)