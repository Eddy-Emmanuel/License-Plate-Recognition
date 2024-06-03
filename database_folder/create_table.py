import sys
sys.path.append("./")

from database_folder.create_session import Base

from sqlalchemy import Integer, Column, String

class DataBaseTable(Base):
    __tablename__ = "DataBaseTable"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    institute = Column(String, index=True)