import base64
import database
import difflib
import json
import os
import re
import requests
import uuid
from dotenv import load_dotenv
from io import BytesIO
from typing import Dict, List, Optional
load_dotenv()
CLASS_JOB: Dict[str, bool] = {"difficulty": False, "result": False,"score": False, "detail": False, "rate": False, "title": False}
CLASS_LIST: List[str] = ["difficulty", "result", "score", "detail","rate", "title"]
DETAIL_LIST: List[str] = ["ERROR", "NEAR", "CRITICAL", "S_CRITICAL"]
DIFFICULTY_LIST: List[str] = ["NOV", "ADV", "EXH", "MXM", "INF", "GRV", "HVN", "VVD", "XCD"]
RESULT_LIST: List[str] = ["CRASH", "COMPLETE", "PERFECT", "ULTIMATECHAIN"]
RATE_LIST: List[str] = ["EFFECTIVE RATE", "EXCESSIVE RATE"]
SONG_LIST: List[str] = database.get_song_title()
JSON_DIR_PATH = os.environ.get("JSON_DIR_PATH")
OCR_API_URL = os.environ.get("OCR_API_URL")
OCR_TOKEN = os.environ.get("OCR_TOKEN")

def sequence_matcher(target: str, template: List[str], target_conf: Optional[float]=None) -> str:
    """OCR 처리 후, 원본 단어와 가장 유사한 단어를 계산하는 함수 (https://shorturl.at/lvT17)

    Args:
        target (str): OCR 결과 단어
        template (List[str]): 원본 단어 List
        target_conf (Optional[float], optional): 목표 유사도. Defaults to None.

    Returns:
        str: OCR 결과와 가장 유사한 단어
    """
    input_bytes = bytes(target, 'utf-8')
    input_bytes_list = list(input_bytes)
    best_ratio = -1
    best_template:str|None = None
    for temp in template:
        answer_bytes = bytes(temp, 'utf-8')
        answer_bytes_list = list(answer_bytes)
        sm = difflib.SequenceMatcher(None, answer_bytes_list, input_bytes_list)
        similar = sm.ratio()
        if best_ratio < similar:
            if target_conf is not None and target_conf > similar:
                    # 목표 정확도보다 예측치가 작은경우 pass
                    continue
            best_ratio = similar
            best_template = temp
    # print(best_ratio, best_template)
    return best_template

def post_process(current_job: str, ocr_value: list|str, dup_switch: bool) -> list|str:
    """OCR 결과 값 보정 함수

     Args:
        current_job (str): 현재 작업
        ocr_value (list | str): 보정할 OCR 결과 값
        dup_switch (bool): score_detail label 중복 입력 확인 변수

    Returns:
        list|str: 보정된 OCR 결과 값
    """
    if current_job == "title":
            ocr_value = sequence_matcher(ocr_value, SONG_LIST)
    elif current_job == "score":
        # 숫자만 남게
        ocr_value = re.sub(r'[^0-9]', '', ocr_value)
        if list(ocr_value)[0] == "0":
            # 0XXXXXX -> XXXXXX로 보정
            ocr_value = ocr_value[1:]
    elif current_job == "difficulty":
        # 문자만 남게
        ocr_value = re.sub(r'\d', '', ocr_value).strip()
        ocr_value = sequence_matcher(ocr_value, DIFFICULTY_LIST)
    elif current_job == "rate":
        ocr_value = ocr_value.split()
        ocr_value[-1] = re.sub(r'[^\d, ., %]', '', ocr_value[-1])
        ocr_value = ' '.join(ocr_value)
    elif current_job == "detail":
        # 문자 -> 숫자
        for idx in range(len(ocr_value)):
            # print(ocr_value[idx])
            if ocr_value[idx] in ["O", "o"]:
                ocr_value[idx] = "0"
            elif ocr_value[idx] in ["I", "i"]:
                ocr_value[idx] = "1"
            elif not ocr_value[idx].isdigit():
                ocr_value[idx] = "-1"
        if dup_switch is True:
            ocr_value.append("-1")
    elif current_job == "result":
        ocr_value = sequence_matcher(ocr_value, RESULT_LIST)
    return ocr_value

def req_OCR_data(image: BytesIO, image_name: str) -> List[dict]:
    """OCR 요청 함수

    Args:
        image (BytesIO): OCR 이미지
        image_name (str): OCR 이미지 이름 (uuid)

    Returns:
        List[dict]: OCR 결과 List
    """
    # OCR 한글 요청하기
    url = OCR_API_URL
    header = {
        "Content-Type": "application/json",
        "X-OCR-SECRET": OCR_TOKEN
        }
    data = {
        "version": "V2",
        "requestId": str(uuid.uuid4()),
        "lang": "ja",
        "timestamp": 0,
        "images": [{"format": "jpg", "name": "result", "data": base64.b64encode(image.getvalue()).decode('utf-8')}]
    }
    res = requests.post(url=url, headers=header, data=json.dumps(data))
    result = json.loads(res.text.encode('utf8'))
    with open(f"{JSON_DIR_PATH}\\{image_name}.json", 'w', encoding='utf-8') as file:
        json.dump(result, file)
    current_job = None
    dup_switch: bool =  False
    ocr_result_list: List[dict] = []
    ocr_result = {}
    ocr_value: list|str|None
    for image in result['images']:
        for field in image["fields"]:
            value = field["inferText"]
            title = sequence_matcher(value, CLASS_LIST, 0.9)
            job_list = list(CLASS_JOB.values())
            if (title is not None and True in job_list) or len(set(job_list)) == 1:
                # job_list 모두 false이거나, title이 들어왔는데 job_list에 True가 있을 때
                # current_job을 교체하여 다음에 수행할 작업을 변경함
                if current_job is None:
                    current_job = title
                    CLASS_JOB[title] = True
                else:
                    # print(current_job, ocr_value)
                    CLASS_JOB[current_job] = False
                    CLASS_JOB[title] = True
                    ocr_value = post_process(current_job, ocr_value, dup_switch)
                    ocr_result[current_job] = ocr_value
                    current_job = title
                    
                if current_job == "detail":
                    # "score_detail"
                    # 리스트로 초기화
                    ocr_value = []
                else:
                    # "result", "result_perfect", "UC", "score", "score_perfect", "score_rate", "title", "difficulty"
                    # 문자열로 초기화
                    ocr_value = ""
                continue
            # 데이터 정제하기
            # print(current_job, ocr_value)
            if current_job == "result":
                # SUCCESS, CRASH, PERFECT, ULTIMATE CHAIN
                ocr_value += sequence_matcher(value, RESULT_LIST)
            elif current_job == "detail":
                # ERROR, NEAR, CRITICAL, S-CRITICAL
                result = sequence_matcher(value, DETAIL_LIST, 0.35)
                if result is None:
                    ocr_value.append(value)
                    dup_switch = False
                elif result is not None and dup_switch is True:
                    ocr_value.append("-1")
                else:
                    dup_switch = True
            elif current_job == "score":
                # 0 ~ 100000
                # print(f"currentjob: {result}")
                ocr_value += value
            elif current_job == "rate":
                # EFFECTIVE RATE, EXCESSIVE RATE
                result = sequence_matcher(value, RATE_LIST, 0.45)
                # print(f"scorerate: {result}")
                if result is None:
                    ocr_value += value 
                else:
                    ocr_value += result + " "
            elif current_job == "title":
                # song title
                ocr_value += value
            elif current_job == "difficulty":
                # difficulty
                ocr_value += value + " "
        ocr_value = post_process(current_job, ocr_value, dup_switch)
        ocr_result[current_job] = ocr_value
        ocr_result_list.append(ocr_result)
        # 변수 초기화
        current_job = None
        dup_switch = False
        ocr_result = {}
        ocr_value = None
    return ocr_result_list

                
# print(sequence_matcher("ERMFAL", DETAIL_LIST))
# print(req_OCR())