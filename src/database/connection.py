from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Azure SQL connection string components
AZURE_SQL_SERVER   = os.getenv("AZURE_SQL_SERVER")
AZURE_SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
AZURE_SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME")
AZURE_SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
AZURE_SQL_DRIVER   = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server")

# Use URL.create() to safely handle special characters in credentials (e.g. @ or ! in password)
DATABASE_URL = URL.create(
    drivername="mssql+pyodbc",
    username=AZURE_SQL_USERNAME,
    password=AZURE_SQL_PASSWORD,
    host=AZURE_SQL_SERVER,
    port=1433,
    database=AZURE_SQL_DATABASE,
    query={
        "driver": AZURE_SQL_DRIVER,
        "Encrypt": "yes",
        "TrustServerCertificate": "no",
        "MultipleActiveResultSets": "False",
        "Connection Timeout": "30",
    }
)


engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,       # 👈 VERY IMPORTANT (fixes hanging connections)
    pool_recycle=1800,        # avoids stale Azure connections
    pool_size=5,
    max_overflow=10,
    connect_args={
        "timeout": 30,
        "login_timeout": 30
    }
)


# engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
