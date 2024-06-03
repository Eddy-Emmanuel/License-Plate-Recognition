from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sys
sys.path.append("./")
from backend_config.config import Configurations

CONFIG = Configurations()

engine = create_engine(url=CONFIG.engine_url,
                       connect_args={CONFIG.connect_args:False})

session = sessionmaker(bind=engine,
                       autoflush=False,
                       autocommit=False)

Base = declarative_base()

def GetDatabase():
    db = session()
    try:
        yield db
    finally:
        db.close()
        
