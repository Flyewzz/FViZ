from typing import List, Optional, Dict
from core.entities import SystemGroup
from core.interfaces import ISystemGroupRepository


class SystemGroupRepositoryImpl(ISystemGroupRepository):
    """In-memory реализация репозитория системных групп"""
    
    def __init__(self):
        # Основное хранилище: {id: SystemGroup}
        self._groups: Dict[str, SystemGroup] = {}
        # Индекс по названиям: {name: SystemGroup}
        self._by_name: Dict[str, SystemGroup] = {}
        # Индекс по G,k: {(G, k): SystemGroup}
        self._by_gk: Dict[tuple[int, int], SystemGroup] = {}
    
    def get_all(self) -> List[SystemGroup]:
        """Получить все системные группы"""
        return list(self._groups.values())
    
    def get_by_id(self, id: str) -> Optional[SystemGroup]:
        """Получить группу по ID"""
        return self._groups.get(id)
    
    def get_by_name(self, name: str) -> Optional[SystemGroup]:
        """Получить группу по названию"""
        return self._by_name.get(name)
    
    def get_by_gk(self, G: int, k: int) -> Optional[SystemGroup]:
        """Получить группу по комбинации G и k"""
        return self._by_gk.get((G, k))
    
    def add(self, group: SystemGroup) -> None:
        """Добавить системную группу"""
        # Проверяем уникальность ID
        if group.id in self._groups:
            raise ValueError(f"Системная группа с ID '{group.id}' уже существует")
        
        # Проверяем уникальность названия
        if group.name in self._by_name:
            raise ValueError(f"Системная группа '{group.name}' уже существует")
        
        # Проверяем уникальность G,k
        gk_key = group.get_unique_key()
        if gk_key in self._by_gk:
            raise ValueError(f"Системная группа с G={group.G}, k={group.k} уже существует")
        
        # Добавляем во все индексы
        self._groups[group.id] = group
        self._by_name[group.name] = group
        self._by_gk[gk_key] = group
    
    def update(self, group: SystemGroup) -> None:
        """Обновить системную группу"""
        old_group = self._groups.get(group.id)
        if not old_group:
            raise ValueError(f"Системная группа с ID '{group.id}' не найдена")
        
        # Удаляем старые индексы
        if old_group.name in self._by_name:
            del self._by_name[old_group.name]
        old_gk = old_group.get_unique_key()
        if old_gk in self._by_gk:
            del self._by_gk[old_gk]
        
        # Проверяем уникальность нового названия (если изменилось)
        if group.name != old_group.name and group.name in self._by_name:
            raise ValueError(f"Системная группа '{group.name}' уже существует")
        
        # Проверяем уникальность новой комбинации G,k (если изменилась)
        new_gk = group.get_unique_key()
        if new_gk != old_gk and new_gk in self._by_gk:
            raise ValueError(f"Системная группа с G={group.G}, k={group.k} уже существует")
        
        # Обновляем все индексы
        self._groups[group.id] = group
        self._by_name[group.name] = group
        self._by_gk[new_gk] = group
    
    def remove(self, id: str) -> None:
        """Удалить системную группу"""
        group = self._groups.get(id)
        if not group:
            return
        
        # Удаляем из всех индексов
        del self._groups[id]
        if group.name in self._by_name:
            del self._by_name[group.name]
        gk_key = group.get_unique_key()
        if gk_key in self._by_gk:
            del self._by_gk[gk_key]
    
    def clear_all(self) -> None:
        """Очистить все данные"""
        self._groups.clear()
        self._by_name.clear()
        self._by_gk.clear()
