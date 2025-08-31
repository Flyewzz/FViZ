from dataclasses import dataclass
from typing import List, Dict
from .law import Law


@dataclass
class LawGroup:
    """Бизнес-сущность группы законов"""
    id: str
    name: str
    color: str
    
    def __post_init__(self):
        """Валидация при создании"""
        if not self.name.strip():
            raise ValueError("Название группы законов не может быть пустым")
        if not self.color.startswith('#') or len(self.color) != 7:
            raise ValueError("Цвет должен быть в формате #RRGGBB")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LawGroup':
        return cls(
            id=data.get("id", data["name"]),  # backward compatibility
            name=data["name"],
            color=data["color"]
        )
