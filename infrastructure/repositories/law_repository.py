from typing import List, Optional, Dict
from core.interfaces.law_repository import ILawRepository
from core.entities.law import Law
from core.entities.law_group import LawGroup


class LawRepositoryImpl(ILawRepository):
    """Реализация репозитория законов в памяти"""
    
    def __init__(self):
        self._laws: Dict[str, Law] = {}
        self._law_groups: Dict[str, LawGroup] = {}
        self._laws_by_group: Dict[str, List[Law]] = {}
        
        # Инициализируем базовые группы законов
        self._init_default_law_groups()
    
    def _init_default_law_groups(self):
        """Инициализация групп законов по умолчанию"""
        default_groups = [
            LawGroup("mechanics", "Механика", "#ffaaaa"),
            LawGroup("electrodynamics", "Электродинамика", "#aaffaa"),
            LawGroup("thermodynamics", "Термодинамика", "#aaaaff"),
        ]
        
        for group in default_groups:
            self._law_groups[group.id] = group
            self._laws_by_group[group.id] = []
    
    def save_law(self, law: Law) -> None:
        """Сохранить закон"""
        self._laws[law.id] = law
        
        # Добавляем в группу
        group_id = getattr(law, 'group_id', None) or (law.group.id if hasattr(law, 'group') else None)
        if group_id and group_id not in self._laws_by_group:
            self._laws_by_group[group_id] = []
        
        if group_id and law not in self._laws_by_group[group_id]:
            self._laws_by_group[group_id].append(law)
    
    def find_law_by_id(self, law_id: str) -> Optional[Law]:
        """Найти закон по ID"""
        return self._laws.get(law_id)
    
    def find_laws_by_variables(self, variables: List[str]) -> List[Law]:
        """Найти законы по переменным"""
        result = []
        variable_set = set(variables)
        
        for law in self._laws.values():
            if set(law.variables) == variable_set:
                result.append(law)
        
        return result
    
    def find_all_laws(self) -> List[Law]:
        """Получить все законы"""
        return list(self._laws.values())
    
    def delete_law(self, law_id: str) -> None:
        """Удалить закон"""
        law = self._laws.get(law_id)
        if law:
            del self._laws[law_id]
            
            # Удаляем из группы
            group_id = getattr(law, 'group_id', None) or (law.group.id if hasattr(law, 'group') else None)
            if group_id and group_id in self._laws_by_group and law in self._laws_by_group[group_id]:
                self._laws_by_group[group_id].remove(law)
    
    def save_law_group(self, group: LawGroup) -> None:
        """Сохранить группу законов"""
        self._law_groups[group.id] = group
        if group.id not in self._laws_by_group:
            self._laws_by_group[group.id] = []
    
    def find_law_group_by_id(self, group_id: str) -> Optional[LawGroup]:
        """Найти группу законов по ID"""
        return self._law_groups.get(group_id)
    
    def find_all_law_groups(self) -> List[LawGroup]:
        """Получить все группы законов"""
        return list(self._law_groups.values())
    
    def find_laws_by_group(self, group_id: str) -> List[Law]:
        """Найти законы по группе"""
        return self._laws_by_group.get(group_id, []).copy()
    
    def delete_law_group(self, group_id: str) -> None:
        """Удалить группу законов"""
        # Сначала удаляем все законы в группе
        laws_to_delete = self._laws_by_group.get(group_id, []).copy()
        for law in laws_to_delete:
            self.delete_law(law.id)
        
        # Затем удаляем саму группу
        if group_id in self._law_groups:
            del self._law_groups[group_id]
        if group_id in self._laws_by_group:
            del self._laws_by_group[group_id]
    
    def update_law(self, law: Law) -> None:
        """Обновить закон"""
        old_law = self._laws.get(law.id)
        if old_law:
            old_group_id = getattr(old_law, 'group_id', None) or (old_law.group.id if hasattr(old_law, 'group') else None)
            new_group_id = getattr(law, 'group_id', None) or (law.group.id if hasattr(law, 'group') else None)
            
            if old_group_id and new_group_id and old_group_id != new_group_id:
                # Переместить закон между группами
                if old_group_id in self._laws_by_group and old_law in self._laws_by_group[old_group_id]:
                    self._laws_by_group[old_group_id].remove(old_law)
        
        self.save_law(law)
    
    def clear_all(self) -> None:
        """Очистить все данные"""
        self._laws.clear()
        self._laws_by_group.clear()
        for group_id in list(self._law_groups.keys()):
            if group_id not in ["mechanics", "electrodynamics", "thermodynamics"]:
                del self._law_groups[group_id]
        
        # Очищаем списки законов в базовых группах
        for group_id in self._law_groups.keys():
            self._laws_by_group[group_id] = []

    # === Реализация методов интерфейса ILawRepository ===
    
    def get_all_laws(self) -> List[Law]:
        """Получить все законы"""
        return self.find_all_laws()
    
    def get_law_by_variables(self, variable_names: List[str]) -> Optional[Law]:
        """Найти закон по переменным"""
        laws = self.find_laws_by_variables(variable_names)
        return laws[0] if laws else None
    
    def add_law(self, law: Law) -> None:
        """Добавить закон"""
        self.save_law(law)
    
    def remove_law(self, law: Law) -> None:
        """Удалить закон"""
        self.delete_law(law.id)
    
    def update_law(self, law: Law) -> None:
        """Обновить закон"""
        self.save_law(law)
    
    # === Реализация методов интерфейса ILawGroupRepository ===
    
    def get_all(self) -> List[LawGroup]:
        """Получить все группы законов"""
        return self.find_all_law_groups()
    
    def get_by_id(self, id: str) -> Optional[LawGroup]:
        """Получить группу по ID"""
        return self.find_law_group_by_id(id)
    
    def get_by_name(self, name: str) -> Optional[LawGroup]:
        """Получить группу по имени"""
        for group in self.find_all_law_groups():
            if group.name == name:
                return group
        return None
    
    def add(self, group: LawGroup) -> None:
        """Добавить группу законов"""
        self.save_law_group(group)
    
    def update(self, group: LawGroup) -> None:
        """Обновить группу законов"""
        self.save_law_group(group)
    
    def remove(self, id: str) -> None:
        """Удалить группу законов"""
        self.delete_law_group(id)
    
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Проверить существование по имени"""
        group = self.get_by_name(name)
        return group is not None and (exclude_id is None or group.id != exclude_id)
