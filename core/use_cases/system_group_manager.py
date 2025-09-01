from typing import List, Optional
from core.entities import SystemGroup
from core.interfaces import ISystemGroupRepository


class SystemGroupManager:
    """Менеджер системных групп - содержит бизнес-логику"""
    
    def __init__(self, system_group_repo: ISystemGroupRepository):
        self.system_group_repo = system_group_repo
    
    def create_group(self, id: str, name: str, color: str, G: int, k: int) -> SystemGroup:
        """Создать новую системную группу с валидацией"""
        
        # Проверка уникальности ID
        if self.system_group_repo.get_by_id(id):
            raise ValueError(f"Системная группа с ID '{id}' уже существует")
        
        # Проверка уникальности названия
        if self.system_group_repo.get_by_name(name):
            raise ValueError(f"Системная группа с названием '{name}' уже существует")
        
        # Проверка уникальности комбинации G и k
        if self.system_group_repo.get_by_gk(G, k):
            raise ValueError(f"Системная группа с комбинацией G={G}, k={k} уже существует")
        
        group = SystemGroup(
            id=id,
            name=name,
            color=color,
            G=G,
            k=k
        )
        
        self.system_group_repo.add(group)
        return group
    
    def update_group(
        self,
        group_id: str,
        name: str,
        color: str,
        G: int,
        k: int
    ) -> SystemGroup:
        """Обновить существующую системную группу"""
        
        group = self.system_group_repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"Системная группа с ID '{group_id}' не найдена")
        
        # Проверка уникальности названия (исключая текущую)
        existing_by_name = self.system_group_repo.get_by_name(name)
        if existing_by_name and existing_by_name.id != group_id:
            raise ValueError(f"Системная группа с названием '{name}' уже существует")
        
        # Проверка уникальности комбинации G и k (исключая текущую)
        existing_by_gk = self.system_group_repo.get_by_gk(G, k)
        if existing_by_gk and existing_by_gk.id != group_id:
            raise ValueError(f"Системная группа с комбинацией G={G}, k={k} уже существует")
        
        updated_group = SystemGroup(
            id=group_id,
            name=name,
            color=color,
            G=G,
            k=k
        )
        
        self.system_group_repo.update(updated_group)
        return updated_group
    
    def delete_group(self, group_id: str) -> None:
        """Удалить системную группу"""
        group = self.system_group_repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"Системная группа с ID '{group_id}' не найдена")
        
        self.system_group_repo.remove(group_id)
    
    def get_all_groups(self) -> List[SystemGroup]:
        """Получить все системные группы"""
        return self.system_group_repo.get_all()
    
    def get_group_by_id(self, group_id: str) -> Optional[SystemGroup]:
        """Получить группу по ID"""
        return self.system_group_repo.get_by_id(group_id)
    
    def validate_name_uniqueness(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Проверить уникальность названия"""
        existing = self.system_group_repo.get_by_name(name)
        if existing is None:
            return True
        if exclude_id and existing.id == exclude_id:
            return True
        return False
    
    def validate_gk_uniqueness(self, G: int, k: int, exclude_id: Optional[str] = None) -> bool:
        """Проверить уникальность комбинации G и k"""
        existing = self.system_group_repo.get_by_gk(G, k)
        if existing is None:
            return True
        if exclude_id and existing.id == exclude_id:
            return True
        return False
