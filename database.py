from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL="postgresql://root:RZj0cnZNYg3QbvhaRyceEna1H3btB9rQ@dpg-d91ohtpo3t8c73ee7tn0-a.singapore-postgres.render.com/todoapplicationdatabase_iu5e"

# SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:test1234!@127.0.0.1:3306/TodoApplicationDatabase"


engine= create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()