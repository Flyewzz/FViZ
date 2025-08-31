from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from .physical_quantity import PhysicalQuantity


@dataclass
class SystemGroup:
    """Бизнес-сущность системной группы (этаж)"""
    id: str
    name: str
    color: str
    G: int
    k: int
    
    def __post_init__(self):
        """Валидация при создании"""
        if not self.name.strip():
            raise ValueError("Название группы не может быть пустым")
        if not self.color.startswith('#') or len(self.color) != 7:
            raise ValueError("Цвет должен быть в формате #RRGGBB")
    
    def get_unique_key(self) -> tuple[int, int]:
        """Возвращает уникальную комбинацию G и k"""
        return (self.G, self.k)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "G": self.G,
            "k": self.k
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SystemGroup':
        return cls(
            id=data.get("id", data["name"]),  # backward compatibility
            name=data["name"],
            color=data["color"],
            G=data["G"],
            k=data["k"]
        )
