from typing import List, Optional, Dict, Tuple
from core.interfaces.repositories import IPhysicalQuantityRepository
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.system_group import SystemGroup


class PhysicalQuantityRepositoryImpl(IPhysicalQuantityRepository):
    """Реализация репозитория физических величин в памяти"""
    
    def __init__(self):
        # Хранение всех величин по группам
        self._quantities_by_group: Dict[str, Dict[Tuple[int, int], PhysicalQuantity]] = {}
        # Хранение видимых величин
        self._visible_quantities: Dict[Tuple[int, int], PhysicalQuantity] = {}
    
    def save(self, quantity: PhysicalQuantity) -> None:
        """Сохранить физическую величину"""
        group_id = quantity.group_id
        coords = (quantity.L, quantity.T)
        
        if group_id not in self._quantities_by_group:
            self._quantities_by_group[group_id] = {}
        
        self._quantities_by_group[group_id][coords] = quantity
    
    def find_by_position(self, L: int, T: int, group_id: str) -> Optional[PhysicalQuantity]:
        """Найти величину по позиции и группе"""
        if group_id not in self._quantities_by_group:
            return None
        
        return self._quantities_by_group[group_id].get((L, T))
    
    def find_all_by_position(self, L: int, T: int) -> List[PhysicalQuantity]:
        """Найти все величины в данной позиции"""
        result = []
        for group_quantities in self._quantities_by_group.values():
            quantity = group_quantities.get((L, T))
            if quantity:
                result.append(quantity)
        return result
    
    def find_by_name(self, name: str) -> Optional[PhysicalQuantity]:
        """Найти величину по имени"""
        for group_quantities in self._quantities_by_group.values():
            for quantity in group_quantities.values():
                if quantity.name == name:
                    return quantity
        return None
    
    def find_all(self) -> List[PhysicalQuantity]:
        """Получить все величины"""
        result = []
        for group_quantities in self._quantities_by_group.values():
            result.extend(group_quantities.values())
        return result
    
    def remove(self, L: int, T: int, group_id: str) -> None:
        """Удалить физическую величину (реализация интерфейса)"""
        if group_id in self._quantities_by_group:
            coords = (L, T)
            if coords in self._quantities_by_group[group_id]:
                del self._quantities_by_group[group_id][coords]
    
    def find_all_by_group(self, group_id: str) -> List[PhysicalQuantity]:
        """Найти все величины в группе"""
        if group_id not in self._quantities_by_group:
            return []
        
        return list(self._quantities_by_group[group_id].values())
    
    def update(self, old_quantity: PhysicalQuantity, new_quantity: PhysicalQuantity) -> None:
        """Обновить величину"""
        # Удаляем старую
        old_group_id = old_quantity.group_id
        old_coords = (old_quantity.L, old_quantity.T)
        
        if old_group_id in self._quantities_by_group:
            if old_coords in self._quantities_by_group[old_group_id]:
                del self._quantities_by_group[old_group_id][old_coords]
        
        # Добавляем новую
        self.save(new_quantity)
    
    # === Методы для работы с видимыми величинами ===
    
    def set_visible_quantity(self, L: int, T: int, quantity: PhysicalQuantity) -> None:
        """Установить видимую величину"""
        self._visible_quantities[(L, T)] = quantity
    
    def get_visible_quantity(self, L: int, T: int) -> Optional[PhysicalQuantity]:
        """Получить видимую величину"""
        return self._visible_quantities.get((L, T))
    
    def get_all_visible_quantities(self) -> Dict[Tuple[int, int], PhysicalQuantity]:
        """Получить все видимые величины"""
        return self._visible_quantities.copy()
    
    def remove_visible_quantity(self, L: int, T: int) -> None:
        """Удалить видимую величину"""
        coords = (L, T)
        if coords in self._visible_quantities:
            del self._visible_quantities[coords]
    
    def clear_all(self) -> None:
        """Очистить все данные"""
        self._quantities_by_group.clear()
        self._visible_quantities.clear()
    
    def get_all_quantities_by_position(self) -> Dict[Tuple[int, int], List[PhysicalQuantity]]:
        """Получить все величины, сгруппированные по позициям"""
        result = {}
        
        for group_quantities in self._quantities_by_group.values():
            for coords, quantity in group_quantities.items():
                if coords not in result:
                    result[coords] = []
                result[coords].append(quantity)
        
        return result

    # === Реализация методов интерфейса ===
    
    def get_all(self) -> List[PhysicalQuantity]:
        """Получить все физические величины"""
        return self.find_all()
    
    def get_by_id(self, id: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по ID - не поддерживается в текущей реализации"""
        # В текущей модели нет ID, используем name как ID
        return self.find_by_name(id)
    
    def get_by_coordinates(self, L: int, T: int, system_group_id: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по координатам и группе"""
        return self.find_by_position(L, T, system_group_id)
    
    def get_by_name(self, name: str) -> Optional[PhysicalQuantity]:
        """Получить физическую величину по имени"""
        return self.find_by_name(name)
    
    def get_by_group(self, system_group_id: str) -> List[PhysicalQuantity]:
        """Получить все физические величины группы"""
        return self.find_all_by_group(system_group_id)
    
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Проверить существование по имени"""
        quantity = self.find_by_name(name)
        if quantity is None:
            return False
        # Поскольку у нас нет ID, игнорируем exclude_id
        return True
    
    def delete(self, id: str) -> None:
        """Удалить физическую величину по ID - не поддерживается в текущей реализации"""
        raise NotImplementedError("Delete by ID is not supported. Use delete(L, T, group_id) instead.")
