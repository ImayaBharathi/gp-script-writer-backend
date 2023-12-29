#### Python Modules Import
from urllib.parse import quote_plus as urlquote

#### Third party Modules Import
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://backend:%s@localhost/candi_dev" % urlquote('Maha@123')
# ASYNC_SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://backend:%s@localhost/candi_dev" % urlquote('Maha@123')

# postgresql+psycopg2://postgres:Support123@database-1.cfjvcebreqo3.us-west-2.rds.amazonaws.com/candi_dev
# postgresql+psycopg2://postgres:Support123@database-2.cfjvcebreqo3.us-west-2.rds.amazonaws.com/candigate_test

# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://backendtest:Support123@localhost/candigate_test"
# ASYNC_SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://backendtest:Support123@localhost/candigate_test"

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost/gp_dev_db"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c timezone=utc"}, future=True)

    
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
)

Base = declarative_base()

# DB Utilities
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()