from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities import Law, LawGroup


class ILawRepository(ABC):
    """Интерфейс репозитория законов"""
    
    @abstractmethod
    def get_all_laws(self) -> List[Law]:
        """Получить все законы"""
        pass
    
    @abstractmethod
    def get_law_by_variables(self, variables: List[str]) -> Optional[Law]:
        """Найти закон по переменным"""
        pass
    
    @abstractmethod
    def get_laws_by_variable(self, variable_name: str) -> List[Law]:
        """Найти все законы, использующие конкретную переменную"""
        pass
    
    @abstractmethod
    def add_law(self, law: Law) -> None:
        """Добавить закон"""
        pass
    
    @abstractmethod
    def update_law(self, law: Law) -> None:
        """Обновить закон"""
        pass
    
    @abstractmethod
    def remove_law(self, law: Law) -> None:
        """Удалить закон"""
        pass


class ILawGroupRepository(ABC):
    """Интерфейс репозитория групп законов"""
    
    @abstractmethod
    def get_all(self) -> List[LawGroup]:
        """Получить все группы законов"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[LawGroup]:
        """Получить группу по ID"""
        pass
    
    @abstractmethod
    def add(self, group: LawGroup) -> None:
        """Добавить группу законов"""
        pass
    
    @abstractmethod
    def update(self, group: LawGroup) -> None:
        """Обновить группу законов"""
        pass
    
    @abstractmethod
    def remove(self, id: str) -> None:
        """Удалить группу законов"""
        pass
