from typing import Any, Dict, List, Tuple
from ultralytics import YOLO

class Box:
    """
    Yolov8 감지한 객체 Box Class
    감지한 객체의 이름과 좌표를 저장
    """
    def __init__(self) -> None:
        self._class_nm:str = ""
        self._pos:Tuple[float, float, float, float] = ()
        self._conf: float = 0.0

    @property
    def class_nm(self) -> str:
        return self._class_nm

    @class_nm.setter
    def class_nm(self, class_nm) -> None:
        # OCR시 합성어 분리되어 결과 출력되는 현상 방지 -> 단일어로 변경
        if (class_nm in ["result_perfect", "UC"]):
            class_nm = "result"
        elif(class_nm == "score_detail"):
            class_nm = "detail"
        elif(class_nm == "score_perfect"):
            class_nm = "score"
        elif(class_nm == "score_rate"):
            class_nm = "rate"
        self._class_nm = class_nm

    
    @property
    def pos(self) -> Tuple[float, float, float, float]:
        return self._pos
    
    @pos.setter
    def pos(self, box_pos) -> None:
        self._pos = box_pos
    
    @property
    def conf(self) -> float:
        return self._conf
    
    @conf.setter
    def conf(self, conf) -> None:
        self._conf = conf


class Predict:
    """
    Box class를 담는 Class
    감지한 객체 이름과 Box class를 저장
    """
    def __init__(self) -> None:
        self.objects:Dict[str: Box] = {}

    def __str__(self) -> str:
        return f"Object Length: {len(self.objects)}"

    def __len__(self) -> int:
        return len(self.objects)

    def objects(self) -> tuple[Box]:
        return self.objects
    
    def add(self, box: Box):
        if box.class_nm == "scoreboard":
            return
        if box.class_nm not in self.objects:
            self.objects[box.class_nm] = box
        else:
            old_box = self.objects[box.class_nm]
            if old_box.conf < box.conf:
                self.objects[box.class_nm] = box
    


def predict(model_path: str, source: Any) -> List[Predict]:
    """Yolov8 이미지 예측

    Args:
        model_path (str): Yolov8 model 저장 위치
        source (Any): 이미지

    Returns:
        List[Predict]: 감지된 객체 리스트
    """
    # Load a pretrained YOLOv8n model
    model = YOLO(model_path)
    predict = Predict()

    # Run inference on 'bus.jpg' with arguments
    results = model.predict(source, conf=0.65, save=True, project="images", name="detect", exist_ok=True)

    for result in results:
        # print(result.names)
        for box in result.boxes:
            class_id = result.names[box.cls[0].item()]
            cords = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            # print("Object type:", class_id)
            # print("Coordinates:", cords)
            # print("Probability:", conf)
            box = Box()
            box.class_nm = class_id
            box.pos = cords
            box.conf = conf
            predict.add(box)
    return predict