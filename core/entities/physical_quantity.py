from dataclasses import dataclass
from typing import Optional


@dataclass
class PhysicalQuantity:
    """Бизнес-сущность физической величины"""
    name: str
    symbol: str  # условное обозначение
    unit: str    # единица измерения
    dimension: str  # размерность в СИ
    L: int       # координата L
    T: int       # координата T
    group_id: str  # ID системной группы
    
    def __post_init__(self):
        """Валидация при создании"""
        if not self.name.strip():
            raise ValueError("Название не может быть пустым")
        if not self.symbol.strip():
            raise ValueError("Условное обозначение не может быть пустым")
    
    def get_coordinates(self) -> tuple[int, int]:
        """Возвращает координаты (L, T)"""
        return (self.L, self.T)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "unit": self.unit,
            "dimension": self.dimension,
            "L": self.L,
            "T": self.T,
            "group_id": self.group_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PhysicalQuantity':
        return cls(
            name=data["name"],
            symbol=data["symbol"],
            unit=data["unit"],
            dimension=data.get("dimension", data.get("value_c", "")),  # backward compatibility
            L=data["L"],
            T=data["T"],
            group_id=data["group_id"]
        )
