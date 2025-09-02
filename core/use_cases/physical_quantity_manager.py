from typing import List, Optional, Dict, Tuple
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.system_group import SystemGroup
from core.interfaces.physical_quantity_repository import IPhysicalQuantityRepository
from core.interfaces.system_group_repository import ISystemGroupRepository


class PhysicalQuantityManager:
    """Менеджер физических величин - содержит бизнес-логику"""
    
    def __init__(
        self,
        quantity_repo: IPhysicalQuantityRepository,
        system_group_repo: ISystemGroupRepository
    ):
        self.quantity_repo = quantity_repo
        self.system_group_repo = system_group_repo
    
    def create_quantity(
        self,
        name: str,
        symbol: str,
        unit: str,
        dimension: str,
        L: int,
        T: int,
        group_id: str
    ) -> PhysicalQuantity:
        """Создать новую физическую величину с валидацией"""
        
        # Проверка уникальности названия
        if self.quantity_repo.find_by_name(name):
            raise ValueError(f"Физическая величина с названием '{name}' уже существует")
        
        # Проверка существования группы
        group = self.system_group_repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"Системная группа с ID '{group_id}' не существует")
        
        # Проверка занятости координат в группе
        existing = self.quantity_repo.find_by_position(L, T, group_id)
        if existing:
            raise ValueError(f"Координаты ({L}, {T}) уже заняты в группе {group_id}")
        
        quantity = PhysicalQuantity(
            name=name,
            symbol=symbol,
            unit=unit,
            dimension=dimension,
            L=L,
            T=T,
            group_id=group_id
        )
        
        self.quantity_repo.save(quantity)
        return quantity
    
    def update_quantity(
        self,
        old_quantity: PhysicalQuantity,
        name: str,
        symbol: str,
        unit: str,
        dimension: str,
        new_group_id: str
    ) -> PhysicalQuantity:
        """Обновить существующую физическую величину"""
        
        # Проверка уникальности названия (исключая текущую)
        existing_by_name = self.quantity_repo.find_by_name(name)
        if existing_by_name and existing_by_name != old_quantity:
            raise ValueError(f"Физическая величина с названием '{name}' уже существует")
        
        # Проверка существования новой группы
        new_group = self.system_group_repo.get_by_id(new_group_id)
        if not new_group:
            raise ValueError(f"Системная группа с ID '{new_group_id}' не существует")
        
        # Проверка занятости координат в новой группе (если группа изменилась)
        if new_group_id != old_quantity.group_id:
            existing = self.quantity_repo.find_by_position(old_quantity.L, old_quantity.T, new_group_id)
            if existing:
                raise ValueError(f"Координаты ({old_quantity.L}, {old_quantity.T}) уже заняты в группе {new_group_id}")
        
        # Создаем новую величину
        new_quantity = PhysicalQuantity(
            name=name,
            symbol=symbol,
            unit=unit,
            dimension=dimension,
            L=old_quantity.L,
            T=old_quantity.T,
            group_id=new_group_id
        )
        
        # Обновляем в репозитории
        self.quantity_repo.update(old_quantity, new_quantity)
        return new_quantity
    
    def delete_quantity(self, L: int, T: int, group_id: str) -> None:
        """Удалить физическую величину"""
        quantity = self.quantity_repo.find_by_position(L, T, group_id)
        if not quantity:
            raise ValueError(f"Физическая величина на координатах ({L}, {T}) в группе {group_id} не найдена")
        
        # Проверяем, является ли удаляемая величина видимой
        visible = self.quantity_repo.get_visible_quantity(L, T)
        is_visible = visible and visible == quantity
        
        self.quantity_repo.remove(L, T, group_id)
        
        # Удаляем из видимых если была видимой
        if is_visible:
            # Ищем альтернативную величину для отображения
            alternatives = self.get_alternatives_for_cell(L, T, group_id)
            if alternatives:
                # Установка альтернативной величины как видимой сгенерирует событие обновления
                self.quantity_repo.set_visible_quantity(L, T, alternatives[0])
            else:
                # Удаление видимой величины сгенерирует событие удаления
                self.quantity_repo.remove_visible_quantity(L, T)
    
    def get_alternatives_for_cell(self, L: int, T: int, exclude_group_id: str) -> List[PhysicalQuantity]:
        """Получить альтернативные величины для замены на тех же координатах"""
        alternatives = self.quantity_repo.find_all_by_position(L, T)
        return [q for q in alternatives if q.group_id != exclude_group_id]
    
    def set_visible_quantity(self, L: int, T: int, quantity: PhysicalQuantity) -> None:
        """Установить видимую величину на координатах"""
        self.quantity_repo.set_visible_quantity(L, T, quantity)
    
    def get_visible_quantities(self) -> Dict[Tuple[int, int], PhysicalQuantity]:
        """Получить все видимые величины"""
        return self.quantity_repo.get_all_visible_quantities()
    
    def validate_name_uniqueness(self, name: str, exclude_quantity: Optional[PhysicalQuantity] = None) -> bool:
        """Проверить уникальность названия"""
        existing = self.quantity_repo.find_by_name(name)
        return existing is None or existing == exclude_quantity
    
    def get_quantity_at_position(self, L: int, T: int, group_id: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину в позиции для определенной группы"""
        return self.quantity_repo.find_by_position(L, T, group_id)
    
    def get_used_groups_at_position(self, L: int, T: int) -> List[str]:
        """Получить ID групп, занятые в данной позиции"""
        quantities = self.quantity_repo.find_all_by_position(L, T)
        return [q.group_id for q in quantities]
    
    def get_all_quantities_by_position(self) -> Dict[Tuple[int, int], List[PhysicalQuantity]]:
        """Получить все физические величины, сгруппированные по координатам"""
        return self.quantity_repo.get_all_quantities_by_position()
    
    def clear_all(self) -> None:
        """Очистить все данные"""
        self.quantity_repo.clear_all()
