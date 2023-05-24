from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todo.db'

# once you reload using uvicorn todo.db it will create

"""
# Postgres sql setup:

# create postgres database after you install postgres in your system
# pip install psycopg2-binary

SQLALCHEMY_DATABASE_URL = 'postgresql:://postgres:password@hostname/databasename'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

#reload uvicorn

"""

"""
# Mysql setup:

# create Mysql database after you install mysql in your system
# pip install pymysql

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql:://root:password@127.0.0.1:3306/databasename'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

#reload uvicorn
"""

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
