import json
from pathlib import Path

from pydantic import BaseModel


class TRIZPrinciple(BaseModel):
    number: int
    name_en: str
    name_ko: str
    description: str
    matching_score: float | None = None


def load_triz_principles() -> list[TRIZPrinciple]:
    data_path = Path(__file__).parent.parent.parent / "data" / "triz_principles.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    return [TRIZPrinciple(**item) for item in data]
