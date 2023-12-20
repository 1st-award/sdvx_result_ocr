import hashlib
import os
import yolov8.image as image
from dotenv import load_dotenv
from io import BytesIO
from models.song import Song, Record, RecordItem
from PIL import Image
from sqlalchemy.orm import Session
from typing import Tuple
from yolov8.ocr import req_OCR_data
from yolov8.predict import predict, Predict
load_dotenv()
DETECT_DIR_PATH = os.environ.get("DETECT_DIR_PATH")
OCR_READY_DIR_PATH = os.environ.get("OCR_READY_DIR_PATH")
THUMBNAIL_DIR_PATH = os.environ.get("THUMBNAIL_DIR_PATH")
UPLOAD_DIR_PATH = os.environ.get("UPLOAD_DIR_PATH")
YOLO_MODEL_PATH = os.environ.get("YOLO_MODEL_PATH")

def get_song_information(title:str, db:Session):
    """
    곡 제목을 통해 곡 정보(제목, 작곡자, 난이도, BPM) return
    """
    # SELECT_QUERY = "SELECT T_SONG.TITLE FROM T_SONG;"
    return db.query(Song).filter(Song.TITLE == title).first()

def get_song_thumbnail(title:str, difficulty:str):
    title = hashlib.sha256(title.encode()).hexdigest()
    image_path = f"{THUMBNAIL_DIR_PATH}\\{title}\\{difficulty}.jpg"
    return title, image_path


def image_predict(img_path) -> Tuple[Image.Image, Predict]:
    # 이미지 열기
    img = Image.open(img_path)
    # 이미지에서 필요한 정보 좌표 가져오기
    result = predict(YOLO_MODEL_PATH, img)
    return img, result


async def create_image_to_data(img:Image, result: Predict, image_name: str):
    # 필요한 정보 자르기
    cutted_img = {}
    for _, box in result.objects.items():
        cutted_img[box.class_nm] = image.cut(img, box)
    # 정보 이어붙히기
    ocr_ready_image_size = image.calc_size(cutted_img)
    ocr_ready_image = image.merge(cutted_img, ocr_ready_image_size)
    ocr_ready_byte_image = BytesIO()
    ocr_ready_image.save(ocr_ready_byte_image, "jpeg")
    ocr_ready_image.save(f"{OCR_READY_DIR_PATH}\\{image_name}.jpg", "jpeg")
    data = req_OCR_data(ocr_ready_byte_image, image_name)
    return data

def remove_detect_image(image_name: str, image_format: str):
    os.remove(f'{UPLOAD_DIR_PATH}\\{image_name}.{image_format}')
    os.remove(f'{DETECT_DIR_PATH}\\{image_name}.{image_format}')

def create_record(data: RecordItem, db: Session):
    record = Record(**data.dict())
    db.add(record)
    db.commit()

def get_record(user_name: str, db: Session):
    result = db.query(Record).filter(Record.USERNAME == user_name).order_by(Record.SCORE.desc(), Record.TITLE.desc(), Record.DT.desc()).all()
    return result
