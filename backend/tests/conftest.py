import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import app.models  # load models

# Use a test database or sqlite memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We need to create vector type workaround for sqlite in tests, but for MVP we skip vector ops in pricing test
# SQLite doesn't support pgvector, so if we query models with Vector, it might fail. 
# We'll use a mocked vector or replace the engine with a local test postgres if available.
# Since we have postgres locally, let's use it for tests.
TEST_DB_URL = "postgresql://localhost/packagepro" # in real life use packagepro_test
real_engine = create_engine(TEST_DB_URL)
RealTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=real_engine)

@pytest.fixture(scope="function")
def db_session():
    # Use real DB but rollback after test
    # In a real setup, you'd create a template DB or truncate tables
    connection = real_engine.connect()
    transaction = connection.begin()
    session = RealTestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
