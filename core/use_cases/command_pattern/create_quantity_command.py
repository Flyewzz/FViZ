from typing import Dict, Any, List, Optional
from core.entities import PhysicalQuantity, Law
from core.use_cases.command_pattern.base import Command


class CreatePhysicalQuantityCommand(Command):
    """Команда создания физической величины с сохранением состояния для отмены"""
    
    def __init__(self, app_model, name: str, symbol: str, unit: str, dimension: str, L: int, T: int, group_id: str):
        super().__init__()
        self.app_model = app_model
        self.name = name
        self.symbol = symbol
        self.unit = unit
        self.dimension = dimension
        self.L = L
        self.T = T
        self.group_id = group_id
        
        # Сохраняем состояние для отмены
        self.created_quantity = None
        self.previous_visible_quantity = None
        self.alternative_quantities = []
    
    def execute(self) -> bool:
        """Выполнить создание физической величины"""
        if self._executed and not self._undone:
            return False
        
        try:
            # Сохраняем текущее состояние
            self._save_state()
            
            # Выполняем создание
            self.created_quantity = self.app_model.create_physical_quantity(
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                dimension=self.dimension,
                L=self.L,
                T=self.T,
                group_id=self.group_id
            )
            
            if self.created_quantity:
                # Устанавливаем созданную величину как видимую
                self.app_model.set_visible_quantity(self.L, self.T, self.created_quantity)
                self._executed = True
                self._undone = False
                return True
            else:
                print(f"Ошибка выполнения команды создания: Не удалось создать величину")
                return False
            
        except Exception as e:
            print(f"Ошибка выполнения команды создания: {e}")
            return False
    
    def undo(self) -> bool:
        """Отменить создание - удалить созданную физическую величину"""
        if not self._executed or self._undone:
            return False
        
        try:
            # Удаляем созданную величину
            if self.created_quantity:
                self.app_model.delete_physical_quantity(self.created_quantity.L, self.created_quantity.T, self.created_quantity.group_id)
            
            # Восстанавливаем видимую величину
            if self.previous_visible_quantity:
                self.app_model.quantity_manager.set_visible_quantity(
                    self.previous_visible_quantity.L,
                    self.previous_visible_quantity.T,
                    self.previous_visible_quantity
                )
            
            # Восстанавливаем альтернативные величины
            for qty in self.alternative_quantities:
                self.app_model.quantity_manager.create_quantity(
                    name=qty.name,
                    symbol=qty.symbol,
                    unit=qty.unit,
                    dimension=qty.dimension,
                    L=qty.L,
                    T=qty.T,
                    group_id=qty.group_id
                )
            
            self._undone = True
            return True
            
        except Exception as e:
            print(f"Ошибка отмены команды создания: {e}")
            return False
    
    def redo(self) -> bool:
        """Повторить создание"""
        if not self._executed or not self._undone:
            return False
        
        try:
            # Повторно выполняем создание
            self.created_quantity = self.app_model.create_physical_quantity(
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                dimension=self.dimension,
                L=self.L,
                T=self.T,
                group_id=self.group_id
            )
            
            if self.created_quantity:
                # Устанавливаем созданную величину как видимую
                self.app_model.set_visible_quantity(self.L, self.T, self.created_quantity)
                self._undone = False
                return True
            else:
                print(f"Ошибка повтора команды создания: Не удалось создать величину")
                return False
            
        except Exception as e:
            print(f"Ошибка повтора команды создания: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Создание физической величины '{self.name}' в позиции ({self.L}, {self.T})"
    
    def _save_state(self) -> None:
        """Сохранить текущее состояние перед созданием"""
        # Сохраняем текущую видимую величину
        visible_quantities = self.app_model.quantity_manager.get_visible_quantities()
        self.previous_visible_quantity = visible_quantities.get((self.L, self.T))
        
        # Сохраняем альтернативные величины в этой позиции
        alternative_quantities = self.app_model.quantity_manager.get_used_groups_at_position(self.L, self.T)
        for group_id in alternative_quantities:
            if group_id != self.group_id:
                qty = self.app_model.quantity_manager.get_quantity_at_position(self.L, self.T, group_id)
                if qty:
                    self.alternative_quantities.append(qty)