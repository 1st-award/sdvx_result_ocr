import os
import uuid
import crud.default as crud
from database import get_db, get_song_title
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from models.song import RecordItem
from sqlalchemy.orm import Session
# Create routing method
router = APIRouter()
load_dotenv()
UPLOAD_DIR_PATH = os.environ.get("UPLOAD_DIR_PATH")


@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.get("/{title}/info")
def read_song_information(title: str, db:Session = Depends(get_db)):
    try:
        result = crud.get_song_information(title, db)
        # print(result)
        return {"success": True, "data": result}
    except Exception as err:
         raise HTTPException(status_code=500, detail=str(err))
    
@router.get("/title/all")
def read_all_song_title():
     result = get_song_title()
     print(len(result))
     return {"succsess": True, "data": result}
         

@router.get("/{title}/img/{difficulty}")
def read_song_image(title: str, difficulty: str):
    title, image_path = crud.get_song_thumbnail(title, difficulty)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Not found file")
    return FileResponse(image_path)

@router.post("/upload")
async def create_image_to_data(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    image = await file.read()
    image_type = file.filename.split(".")[-1]
    image_name = str(uuid.uuid4())
    image_path = f"{UPLOAD_DIR_PATH}\\{image_name}.{image_type}"
    with open(image_path, "wb") as reader:
        reader.write(image)
    image, predict = crud.image_predict(image_path)
    if len(predict) < 5:
            crud.remove_detect_image(image_name, image_type)
            raise HTTPException(status_code=400, detail="Not enough detect data")
    result = await crud.create_image_to_data(image, predict, image_name)
    return {"success": True, "data": result}

@router.post("/record")
async def create_record(data: RecordItem, db: Session=Depends(get_db)):
     crud.create_record(data, db)
     return {"success": True}

@router.get("/record/{user_name}")
async def get_record(user_name: str, db: Session=Depends(get_db)):
     result = crud.get_record(user_name, db)
     if len(result) == 0:
          raise HTTPException(status_code=404, detail="No data")
     return {"success": True, "data": result}