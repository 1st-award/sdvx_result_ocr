from typing import Any, Dict, List, Tuple
from ultralytics import YOLO

class Box:
    def __init__(self) -> None:
        self._class_nm:str = ""
        self._pos:Tuple[float, float, float, float] = ()
        self._conf: float = 0.0

    @property
    def class_nm(self) -> str:
        return self._class_nm

    @class_nm.setter
    def class_nm(self, class_nm) -> None:
        self._class_nm = class_nm.replace("_", "")
    
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