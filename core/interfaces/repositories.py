from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
from ..entities.physical_quantity import PhysicalQuantity
from ..entities.system_group import SystemGroup
from ..entities.law import Law
from ..entities.law_group import LawGroup


class IPhysicalQuantityRepository(ABC):
    """Интерфейс репозитория для физических величин"""
    
    @abstractmethod
    def get_all(self) -> List[PhysicalQuantity]:
        """Получить все физические величины"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по ID"""
        pass
    
    @abstractmethod
    def get_by_coordinates(self, L: int, T: int, system_group_id: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по координатам и группе"""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по имени"""
        pass
    
    @abstractmethod
    def get_by_group(self, system_group_id: str) -> List[PhysicalQuantity]:
        """Получить все физические величины группы"""
        pass
    
    @abstractmethod
    def save(self, quantity: PhysicalQuantity) -> None:
        """Сохранить физическую величину"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> None:
        """Удалить физическую величину"""
        pass
    
    @abstractmethod
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Проверить существование по имени"""
        pass


class ISystemGroupRepository(ABC):
    """Интерфейс репозитория для системных групп"""
    
    @abstractmethod
    def get_all(self) -> List[SystemGroup]:
        """Получить все системные группы"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[SystemGroup]:
        """Получить системную группу по ID"""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[SystemGroup]:
        """Получить системную группу по имени"""
        pass
    
    @abstractmethod
    def save(self, group: SystemGroup) -> None:
        """Сохранить системную группу"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> None:
        """Удалить системную группу"""
        pass
    
    @abstractmethod
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Проверить существование по имени"""
        pass
    
    @abstractmethod
    def exists_by_gk_pair(self, G: int, k: int, exclude_id: Optional[str] = None) -> bool:
        """Проверить существование пары (G, k)"""
        pass


class ILawRepository(ABC):
    """Интерфейс репозитория для законов"""
    
    @abstractmethod
    def get_all(self) -> List[Law]:
        """Получить все законы"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Law]:
        """Получить закон по ID"""
        pass
    
    @abstractmethod
    def get_by_variables(self, variable_names: List[str]) -> Optional[Law]:
        """Найти закон по именам переменных"""
        pass
    
    @abstractmethod
    def get_by_group(self, law_group_id: str) -> List[Law]:
        """Получить законы группы"""
        pass
    
    @abstractmethod
    def save(self, law: Law) -> None:
        """Сохранить закон"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> None:
        """Удалить закон"""
        pass


class ILawGroupRepository(ABC):
    """Интерфейс репозитория для групп законов"""
    
    @abstractmethod
    def get_all(self) -> List[LawGroup]:
        """Получить все группы законов"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[LawGroup]:
        """Получить группу законов по ID"""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[LawGroup]:
        """Получить группу законов по имени"""
        pass
    
    @abstractmethod
    def save(self, group: LawGroup) -> None:
        """Сохранить группу законов"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> None:
        """Удалить группу законов"""
        pass
    
    @abstractmethod
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Проверить существование по имени"""
        pass


class IDataPersistenceService(ABC):
    """Интерфейс сервиса сохранения/загрузки данных"""
    
    @abstractmethod
    def save_project(self, file_path: str, data: Dict) -> None:
        """Сохранить проект в файл"""
        pass
    
    @abstractmethod
    def load_project(self, file_path: str) -> Dict:
        """Загрузить проект из файла"""
        pass


class IUINotificationService(ABC):
    """Интерфейс для уведомлений UI"""
    
    @abstractmethod
    def show_info(self, title: str, message: str) -> None:
        """Показать информационное сообщение"""
        pass
    
    @abstractmethod
    def show_warning(self, title: str, message: str) -> None:
        """Показать предупреждение"""
        pass
    
    @abstractmethod
    def show_error(self, title: str, message: str) -> None:
        """Показать ошибку"""
        pass
    
    @abstractmethod
    def ask_confirmation(self, title: str, message: str) -> bool:
        """Запросить подтверждение"""
        pass
