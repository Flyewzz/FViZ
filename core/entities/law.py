from dataclasses import dataclass
from typing import List
import uuid


@dataclass
class Law:
    """Бизнес-сущность закона физики"""
    name: str
    formula: str
    description: str
    variables: List[str]  # названия физических величин
    group_id: str  # ID группы законов
    id: str = None  # ID закона
    
    def __post_init__(self):
        """Валидация при создании"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.name.strip():
            raise ValueError("Название закона не может быть пустым")
        if len(self.variables) != 4:
            raise ValueError("Закон должен содержать ровно 4 переменные")
    
    def get_sorted_variables(self) -> List[str]:
        """Возвращает отсортированный список переменных для сравнения"""
        return sorted(self.variables)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "formula": self.formula,
            "description": self.description,
            "variables": self.variables,
            "group_id": self.group_id
        }
    
    @classmethod
    def from_dict(cls, data: dict, group_id: str = None) -> 'Law':
        return cls(
            id=data.get("id"),
            name=data["name"],
            formula=data.get("formula", ""),
            description=data.get("description", ""),
            variables=data.get("variables", []),
            group_id=group_id or data.get("group_id")
        )