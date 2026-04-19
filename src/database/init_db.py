"""
Run this script once to create all tables in the Azure SQL database.

Usage:
    python -m src.database.init_db
"""
from sqlalchemy import text
from src.database.connection import engine
from src.database.models import Base


def init():
    print("Creating schema and tables in Azure SQL Database...")

    # Create the 'boarder' schema if it doesn't already exist
    with engine.connect() as conn:
        conn.execute(text("IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'boarder') EXEC('CREATE SCHEMA boarder')"))
        conn.commit()
    print("Schema 'boarder' ready.")

    # Create all tables under the boarder schema
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created: boarder.users, boarder.products, boarder.inventory, boarder.transactions")


if __name__ == "__main__":
    init()
