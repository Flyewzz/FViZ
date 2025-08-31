from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
from core.entities import PhysicalQuantity


class IPhysicalQuantityRepository(ABC):
    """Интерфейс репозитория физических величин"""
    
    @abstractmethod
    def get_all(self) -> List[PhysicalQuantity]:
        """Получить все физические величины"""
        pass
    
    @abstractmethod
    def get_by_coordinates(self, L: int, T: int, group_id: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по координатам и группе"""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по названию"""
        pass
    
    @abstractmethod
    def get_by_group(self, group_id: str) -> List[PhysicalQuantity]:
        """Получить все физические величины группы"""
        pass
    
    @abstractmethod
    def add(self, quantity: PhysicalQuantity) -> None:
        """Добавить физическую величину"""
        pass
    
    @abstractmethod
    def update(self, quantity: PhysicalQuantity) -> None:
        """Обновить физическую величину"""
        pass
    
    @abstractmethod
    def remove(self, L: int, T: int, group_id: str) -> None:
        """Удалить физическую величину"""
        pass
    
    @abstractmethod
    def get_visible_cells(self) -> Dict[Tuple[int, int], PhysicalQuantity]:
        """Получить видимые ячейки"""
        pass
    
    @abstractmethod
    def set_visible_cell(self, L: int, T: int, quantity: PhysicalQuantity) -> None:
        """Установить видимую ячейку"""
        pass
    
    @abstractmethod
    def remove_visible_cell(self, L: int, T: int) -> None:
        """Удалить видимую ячейку"""
        pass
