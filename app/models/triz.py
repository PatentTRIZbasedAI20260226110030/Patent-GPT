import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

DATA_DIR = Path(__file__).parent.parent.parent / "data"


class TRIZPrinciple(BaseModel):
    number: int
    name_en: str
    name_ko: str
    description: str
    matching_score: float | None = None


class EngineeringParameter(BaseModel):
    id: int
    name_en: str
    name_ko: str


class ContradictionMatrix(BaseModel):
    parameters: list[EngineeringParameter]
    matrix: dict[str, dict[str, list[int]]]

    def lookup(self, improving: int, worsening: int) -> list[int]:
        """Return recommended principle numbers for a contradiction pair."""
        return self.matrix.get(str(improving), {}).get(str(worsening), [])

    def get_parameter_names(self) -> list[str]:
        """Return formatted parameter list for prompt injection."""
        return [f"{p.id}. {p.name_ko} ({p.name_en})" for p in self.parameters]


@lru_cache(maxsize=1)
def load_triz_principles() -> tuple[TRIZPrinciple, ...]:
    data_path = DATA_DIR / "triz_principles.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    return tuple(TRIZPrinciple(**item) for item in data)


@lru_cache(maxsize=1)
def load_contradiction_matrix() -> ContradictionMatrix:
    data_path = DATA_DIR / "triz_contradiction_matrix.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    return ContradictionMatrix(**data)
