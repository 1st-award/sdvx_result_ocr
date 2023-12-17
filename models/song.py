from sqlalchemy import TEXT, Column, VARCHAR
# from pydantic import BaseModel
from database import Base

class Song(Base):
    __tablename__ = "T_SONG"

    TITLE = Column(VARCHAR, primary_key=True)
    AUTHOR = Column(VARCHAR, primary_key=True)
    BPM = Column(VARCHAR)
    DIFFICULTY = Column(TEXT)
