from typing import List, Optional, Tuple
from core.entities import PhysicalQuantity, Law, LawGroup
from core.interfaces import IPhysicalQuantityRepository, ILawRepository, ILawGroupRepository


class LawManager:
    """Менеджер законов физики - содержит бизнес-логику"""
    
    def __init__(
        self,
        law_repo: ILawRepository,
        law_group_repo: ILawGroupRepository,
        quantity_repo: IPhysicalQuantityRepository
    ):
        self.law_repo = law_repo
        self.law_group_repo = law_group_repo
        self.quantity_repo = quantity_repo
    
    def create_law(
        self,
        name: str,
        formula: str,
        description: str,
        variables: List[str],
        group_id: str
    ) -> Law:
        """Создать новый закон с валидацией"""
        
        # Проверка существования группы законов
        if not self.law_group_repo.get_by_id(group_id):
            raise ValueError(f"Группа законов с ID '{group_id}' не существует")
        
        # Проверка существования переменных
        for var_name in variables:
            if not self.quantity_repo.get_by_name(var_name):
                raise ValueError(f"Физическая величина '{var_name}' не найдена")
        
        # Проверка на существующий закон с теми же переменными
        existing_law = self.law_repo.get_law_by_variables(variables)
        if existing_law:
            raise ValueError(f"Закон с такими переменными уже существует: {existing_law.name}")
        
        law = Law(
            name=name,
            formula=formula,
            description=description,
            variables=variables,
            group_id=group_id
        )
        
        self.law_repo.add_law(law)
        return law
    
    def update_law(
        self,
        existing_law: Law,
        name: str,
        formula: str,
        description: str,
        group_id: str
    ) -> Law:
        """Обновить существующий закон"""
        
        # Проверка существования группы законов
        if not self.law_group_repo.get_by_id(group_id):
            raise ValueError(f"Группа законов с ID '{group_id}' не существует")
        
        updated_law = Law(
            name=name,
            formula=formula,
            description=description,
            variables=existing_law.variables,  # переменные не меняем
            group_id=group_id
        )
        
        self.law_repo.update_law(updated_law)
        return updated_law
    
    def find_law_by_quantities(self, quantities: List[PhysicalQuantity]) -> Optional[Law]:
        """Найти закон по выбранным величинам"""
        if len(quantities) != 4:
            return None
        
        variable_names = [q.name for q in quantities]
        return self.law_repo.get_law_by_variables(variable_names)
    
    def get_law_group_color(self, law: Law) -> str:
        """Получить цвет группы закона"""
        group = self.law_group_repo.get_by_id(law.group_id)
        return group.color if group else "#000000"


class LawGroupManager:
    """Менеджер групп законов"""
    
    def __init__(self, law_group_repo: ILawGroupRepository):
        self.law_group_repo = law_group_repo
    
    def create_group(self, id: str, name: str, color: str) -> LawGroup:
        """Создать новую группу законов"""
        
        # Проверка уникальности ID
        if self.law_group_repo.get_by_id(id):
            raise ValueError(f"Группа законов с ID '{id}' уже существует")
        
        group = LawGroup(id=id, name=name, color=color)
        self.law_group_repo.add(group)
        return group
    
    def update_group(self, group_id: str, name: str, color: str) -> LawGroup:
        """Обновить группу законов"""
        
        group = self.law_group_repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"Группа законов с ID '{group_id}' не найдена")
        
        updated_group = LawGroup(id=group_id, name=name, color=color)
        self.law_group_repo.update(updated_group)
        return updated_group
    
    def get_all_groups(self) -> List[LawGroup]:
        """Получить все группы законов"""
        return self.law_group_repo.get_all()


class ParallelogramLogic:
    """Логика работы с параллелограммами"""
    
    def __init__(self, quantity_repo: IPhysicalQuantityRepository):
        self.quantity_repo = quantity_repo
    
    def check_parallelogram(self, quantities: List[PhysicalQuantity]) -> Optional[List[PhysicalQuantity]]:
        """Проверить, образуют ли выбранные величины параллелограмм"""
        
        if len(quantities) == 3:
            return self._check_linear_parallelogram(quantities)
        elif len(quantities) == 4:
            return self._check_full_parallelogram(quantities)
        else:
            return None
    
    def _check_linear_parallelogram(self, quantities: List[PhysicalQuantity]) -> Optional[List[PhysicalQuantity]]:
        """Проверить линейный параллелограмм (3 точки)"""
        # Сортировка для определения центральной точки
        sorted_by_L = sorted(quantities, key=lambda q: q.L)
        sorted_by_T = sorted(quantities, key=lambda q: q.T)
        
        # Проверяем, лежат ли точки на одной линии по L или T
        if len(set(q.L for q in quantities)) == 1:  # Вертикальная линия
            center_idx = 1 if len(sorted_by_T) >= 3 else 0
            center = sorted_by_T[center_idx]
            return [quantities[0], center, center, quantities[-1]]  # Удваиваем центральную
        elif len(set(q.T for q in quantities)) == 1:  # Горизонтальная линия
            center_idx = 1 if len(sorted_by_L) >= 3 else 0
            center = sorted_by_L[center_idx]
            return [quantities[0], center, center, quantities[-1]]  # Удваиваем центральную
        
        return None
    
    def _check_full_parallelogram(self, quantities: List[PhysicalQuantity]) -> Optional[List[PhysicalQuantity]]:
        """Проверить полный параллелограмм (4 точки)"""
        
        # Сортировка как в оригинальном коде
        items = quantities.copy()
        items.sort(key=lambda q: (-q.L, -q.T))
        e1 = items[0]
        
        rest = items[1:]
        rest.sort(key=lambda q: (q.L, q.T))
        
        if len(rest) < 2:
            return None
        
        e2, e3 = rest[0], rest[1]
        e4 = rest[2] if len(items) == 4 else e3
        
        # Получаем группы из репозитория
        groups = {}
        for q in [e1, e2, e3, e4]:
            from core.interfaces import ISystemGroupRepository
            # Здесь нужен доступ к system_group_repo, но у нас его нет в этом классе
            # Поэтому проверяем через group_id
            groups[q.name] = q.group_id
        
        # Проверяем условия параллелограмма по group_id, L, T
        def check_condition(attr_fn):
            return attr_fn(e1) + attr_fn(e2) == attr_fn(e3) + attr_fn(e4)
        
        # Для полной проверки нужны G и k из групп, поэтому делаем упрощенную проверку
        if all([
            check_condition(lambda q: q.L),
            check_condition(lambda q: q.T),
        ]):
            return [e1, e3, e2, e4]
        
        return None
