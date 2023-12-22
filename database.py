from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = f'sqlite:///./sound_voltex.db'
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_song_title():
    db = SessionLocal()
    SELECT_QUERY = "SELECT DISTINCT T_SONG.TITLE FROM T_SONG"
    result = db.execute(text(SELECT_QUERY)).all()
    title_list = []
    for title in result:
        title_list.append(title[0])
    db.close()
    return title_list

Base = declarative_base()