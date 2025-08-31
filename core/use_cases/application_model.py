from typing import List, Dict, Tuple
from core.entities import PhysicalQuantity, SystemGroup
from core.use_cases.physical_quantity_manager import PhysicalQuantityManager
from core.use_cases.system_group_manager import SystemGroupManager
from core.use_cases.law_manager import LawManager, LawGroupManager, ParallelogramLogic


class ApplicationModel:
    """Главная модель приложения - фасад для всех операций Core слоя"""
    
    def __init__(
        self,
        quantity_manager: PhysicalQuantityManager,
        system_group_manager: SystemGroupManager,
        law_manager: LawManager,
        law_group_manager: LawGroupManager,
        parallelogram_logic: ParallelogramLogic
    ):
        self.quantity_manager = quantity_manager
        self.system_group_manager = system_group_manager
        self.law_manager = law_manager
        self.law_group_manager = law_group_manager
        self.parallelogram_logic = parallelogram_logic
        
        self._selected_quantities: List[PhysicalQuantity] = []
    
    # === Операции с физическими величинами ===
    
    def create_physical_quantity(
        self,
        name: str,
        symbol: str,
        unit: str,
        dimension: str,
        L: int,
        T: int,
        group_id: str
    ) -> PhysicalQuantity:
        """Создать физическую величину"""
        return self.quantity_manager.create_quantity(name, symbol, unit, dimension, L, T, group_id)
    
    def update_physical_quantity(
        self,
        old_quantity: PhysicalQuantity,
        name: str,
        symbol: str,
        unit: str,
        dimension: str,
        new_group_id: str
    ) -> PhysicalQuantity:
        """Обновить физическую величину"""
        return self.quantity_manager.update_quantity(old_quantity, name, symbol, unit, dimension, new_group_id)
    
    def delete_physical_quantity(self, L: int, T: int, group_id: str) -> None:
        """Удалить физическую величину"""
        self.quantity_manager.delete_quantity(L, T, group_id)
    
    def get_alternative_quantities(self, L: int, T: int, exclude_group_id: str) -> List[PhysicalQuantity]:
        """Получить альтернативные величины для замены"""
        return self.quantity_manager.get_alternatives_for_cell(L, T, exclude_group_id)
    
    def set_visible_quantity(self, L: int, T: int, quantity: PhysicalQuantity) -> None:
        """Установить видимую величину"""
        self.quantity_manager.set_visible_quantity(L, T, quantity)
    
    def get_visible_quantities(self) -> Dict[Tuple[int, int], PhysicalQuantity]:
        """Получить видимые величины"""
        return self.quantity_manager.get_visible_quantities()
    
    # === Операции с системными группами ===
    
    def create_system_group(self, id: str, name: str, color: str, G: int, k: int) -> SystemGroup:
        """Создать системную группу"""
        return self.system_group_manager.create_group(id, name, color, G, k)
    
    def update_system_group(self, group_id: str, name: str, color: str, G: int, k: int) -> SystemGroup:
        """Обновить системную группу"""
        return self.system_group_manager.update_group(group_id, name, color, G, k)
    
    def get_all_system_groups(self) -> List[SystemGroup]:
        """Получить все системные группы"""
        return self.system_group_manager.get_all_groups()
    
    def get_system_group_by_id(self, group_id: str) -> SystemGroup:
        """Получить системную группу по ID"""
        return self.system_group_manager.get_group_by_id(group_id)
    
    def update_group_properties(self, group_id: str, properties: Dict) -> SystemGroup:
        """Обновить свойства группы"""
        group = self.get_system_group_by_id(group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")
        
        # Обновляем свойства
        if 'name' in properties:
            group.name = properties['name']
        if 'color' in properties:
            group.color = properties['color']
        if 'G' in properties:
            group.G = properties['G']
        if 'k' in properties:
            group.k = properties['k']
        
        # Сохраняем изменения
        return self.system_group_manager.update_group(group_id, group.name, group.color, group.G, group.k)
    
    # === Операции с выделением и параллелограммами ===
    
    def toggle_quantity_selection(self, quantity: PhysicalQuantity) -> None:
        """Переключить выделение величины"""
        if quantity in self._selected_quantities:
            self._selected_quantities.remove(quantity)
        else:
            self._selected_quantities.append(quantity)
    
    def get_selected_quantities(self) -> List[PhysicalQuantity]:
        """Получить выделенные величины"""
        return self._selected_quantities.copy()
    
    def clear_selection(self) -> None:
        """Очистить выделение"""
        self._selected_quantities.clear()
    
    def check_parallelogram(self) -> List[PhysicalQuantity]:
        """Проверить параллелограмм из выделенных величин"""
        if len(self._selected_quantities) not in (3, 4):
            return None
        
        return self.parallelogram_logic.check_parallelogram(self._selected_quantities)
    
    # === Операции с законами ===
    
    def find_law_for_selection(self) -> 'Law':
        """Найти закон для текущего выделения"""
        parallelogram = self.check_parallelogram()
        if not parallelogram:
            return None
        
        return self.law_manager.find_law_by_quantities(parallelogram)
    
    def create_law_from_selection(self, name: str, formula: str, description: str, group_id: str) -> 'Law':
        """Создать закон из выделенных величин"""
        parallelogram = self.check_parallelogram()
        if not parallelogram:
            raise ValueError("Выделенные величины не образуют параллелограмм")
        
        variables = [q.name for q in parallelogram]
        return self.law_manager.create_law(name, formula, description, variables, group_id)
    
    def get_all_law_groups(self) -> List['LawGroup']:
        """Получить все группы законов"""
        return self.law_group_manager.get_all_groups()
    
    def get_law_group_by_id(self, group_id: str) -> 'LawGroup':
        """Получить группу законов по ID"""
        return self.law_group_manager.get_group_by_id(group_id)
    
    def create_law_group(self, id: str, name: str, color: str) -> 'LawGroup':
        """Создать группу законов"""
        return self.law_group_manager.create_group(id, name, color)
    
    def update_law_group(self, group_id: str, name: str, color: str) -> 'LawGroup':
        """Обновить группу законов"""
        return self.law_group_manager.update_group(group_id, name, color)
    
    def delete_law_group(self, group_id: str) -> None:
        """Удалить группу законов"""
        self.law_group_manager.delete_group(group_id)
    
    # === Валидация ===
    
    def validate_quantity_name(self, name: str, exclude_quantity: PhysicalQuantity = None) -> bool:
        """Проверить уникальность названия величины"""
        return self.quantity_manager.validate_name_uniqueness(name, exclude_quantity)
    
    def validate_group_name(self, name: str, exclude_id: str = None) -> bool:
        """Проверить уникальность названия группы"""
        return self.system_group_manager.validate_name_uniqueness(name, exclude_id)
    
    def validate_group_gk(self, G: int, k: int, exclude_id: str = None) -> bool:
        """Проверить уникальность комбинации G и k"""
        return self.system_group_manager.validate_gk_uniqueness(G, k, exclude_id)
    
    # === Дополнительные методы ===
    
    def get_quantity_at_position(self, L: int, T: int, group_id: str) -> PhysicalQuantity:
        """Получить физическую величину в позиции для определенной группы"""
        return self.quantity_manager.get_quantity_at_position(L, T, group_id)
    
    def get_used_groups_at_position(self, L: int, T: int) -> List[SystemGroup]:
        """Получить группы, занятые в данной позиции"""
        return self.quantity_manager.get_used_groups_at_position(L, T)
    
    def get_all_quantities(self) -> Dict[Tuple[int, int], List[PhysicalQuantity]]:
        """Получить все физические величины, сгруппированные по координатам"""
        return self.quantity_manager.get_all_quantities_by_position()
    
    def clear_all_data(self) -> None:
        """Очистить все данные приложения"""
        self.quantity_manager.clear_all()
        self._selected_quantities.clear()
