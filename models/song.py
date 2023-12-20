from datetime import datetime
from sqlalchemy import TEXT, Column, VARCHAR, DATETIME
from pydantic import BaseModel
# from pydantic import BaseModel
from database import Base

class Song(Base):
    __tablename__ = "T_SONG"

    TITLE = Column(VARCHAR, primary_key=True)
    AUTHOR = Column(VARCHAR, primary_key=True)
    BPM = Column(VARCHAR)
    DIFFICULTY = Column(TEXT)

class Record(Base):
    __tablename__ = "T_RECORD"

    TITLE = Column(VARCHAR, primary_key=True)
    DIFFICULTY = Column(VARCHAR)
    RESULT = Column(VARCHAR)
    SCORE = Column(VARCHAR)
    SCORE_DETAIL = Column(VARCHAR)
    USERNAME = Column(VARCHAR, primary_key=True)
    DT = Column(DATETIME, primary_key=True)


class RecordItem(BaseModel):
     TITLE: str
     DIFFICULTY: str
     RESULT: str
     SCORE: str
     SCORE_DETAIL: str
     USERNAME: str
     DT: datetime