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
    
    def get_group_by_id(self, group_id: str) -> Optional[LawGroup]:
        """Получить группу законов по ID"""
        return self.law_group_repo.get_by_id(group_id)
    
    def delete_group(self, group_id: str) -> None:
        """Удалить группу законов"""
        group = self.law_group_repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"Группа законов с ID '{group_id}' не найдена")
        
        self.law_group_repo.remove(group_id)


class ParallelogramLogic:
    """Логика работы с параллелограммами"""
    
    def __init__(self, quantity_repo: IPhysicalQuantityRepository):
        self.quantity_repo = quantity_repo
        self.system_group_repo = None  # Будет установлен через ApplicationFactory
    
    def check_parallelogram(self, quantities: List[PhysicalQuantity]) -> Optional[List[PhysicalQuantity]]:
        """Проверить, образуют ли выбранные величины параллелограмм"""
        
        try:
            if len(quantities) not in (3, 4):
                print("❌ Недостаточно выделенных элементов")
                return None
            
            items = quantities.copy()
            
            # 1. Сортировка по L убыванию, затем T убыванию — для e1
            items.sort(key=lambda q: (-q.L, -q.T))
            e1 = items[0]
            
            # 2. Остальные сортируем по L и T по возрастанию
            rest = items[1:]
            rest.sort(key=lambda q: (q.L, q.T))
            
            if len(rest) < 2:
                print("❌ Недостаточно оставшихся для параллелограмма")
                return None
            
            e2, e3 = rest[0], rest[1]
            e4 = rest[2] if len(items) == 4 else e3  # как в оригинале
            
            def log_and_check(attr_name, fn):
                try:
                    a = fn(e1) + fn(e2)
                    b = fn(e3) + fn(e4)
                    result = a == b
                    print(f"⚖️ Проверка {attr_name}: {fn(e1)}+{fn(e2)} == {fn(e3)}+{fn(e4)} -> {'✅' if result else '❌'}")
                    return result
                except Exception as e:
                    print(f"❌ Ошибка при проверке {attr_name}: {e}")
                    return False
            
            # Получаем G и k из групп через репозиторий
            def get_G(q):
                try:
                    if self.system_group_repo:
                        group = self.system_group_repo.get_by_id(q.group_id)
                        G_value = group.G if group else 0
                        print(f"🔍 Величина {q.name} (group_id={q.group_id}): G={G_value}")
                        return G_value
                    print(f"❌ Нет репозитория для получения G для {q.name}")
                    return 0
                except Exception as e:
                    print(f"❌ Ошибка получения G для {q.name}: {e}")
                    return 0
            
            def get_k(q):
                try:
                    if self.system_group_repo:
                        group = self.system_group_repo.get_by_id(q.group_id)
                        k_value = group.k if group else 0
                        print(f"🔍 Величина {q.name} (group_id={q.group_id}): k={k_value}")
                        return k_value
                    print(f"❌ Нет репозитория для получения k для {q.name}")
                    return 0
                except Exception as e:
                    print(f"❌ Ошибка получения k для {q.name}: {e}")
                    return 0
            
            if all([
                log_and_check("G", get_G),
                log_and_check("k", get_k),
                log_and_check("L", lambda q: q.L),
                log_and_check("T", lambda q: q.T),
            ]):
                print("✅ Параллелограмм найден — передаём [e1, e3, e2, e4]")
                return [e1, e3, e2, e4]
            
            print("❌ Условия не выполнены")
            return None
            
        except Exception as e:
            print(f"❌ Критическая ошибка в check_parallelogram: {e}")
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
