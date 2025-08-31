from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities import SystemGroup


class ISystemGroupRepository(ABC):
    """Интерфейс репозитория системных групп"""
    
    @abstractmethod
    def get_all(self) -> List[SystemGroup]:
        """Получить все системные группы"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[SystemGroup]:
        """Получить группу по ID"""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[SystemGroup]:
        """Получить группу по названию"""
        pass
    
    @abstractmethod
    def get_by_gk(self, G: int, k: int) -> Optional[SystemGroup]:
        """Получить группу по комбинации G и k"""
        pass
    
    @abstractmethod
    def add(self, group: SystemGroup) -> None:
        """Добавить системную группу"""
        pass
    
    @abstractmethod
    def update(self, group: SystemGroup) -> None:
        """Обновить системную группу"""
        pass
    
    @abstractmethod
    def remove(self, id: str) -> None:
        """Удалить системную группу"""
        pass
