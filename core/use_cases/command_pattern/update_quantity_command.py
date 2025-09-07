from typing import Dict, Any, List, Optional
from core.entities import PhysicalQuantity, Law
from core.use_cases.command_pattern.base import Command


class UpdatePhysicalQuantityCommand(Command):
    """Команда редактирования физической величины с сохранением состояния для отмены"""
    
    def __init__(self, app_model, old_quantity: PhysicalQuantity, name: str, symbol: str, unit: str, dimension: str, new_group_id: str):
        super().__init__()
        self.app_model = app_model
        self.old_quantity = old_quantity
        self.name = name
        self.symbol = symbol
        self.unit = unit
        self.dimension = dimension
        self.new_group_id = new_group_id
        
        # Сохраняем состояние для отмены
        self.updated_quantity = None
        self.previous_visible_quantities = {}
        self.previous_alternative_quantities = {}
        self.deleted_laws = []
    
    def execute(self) -> bool:
        """Выполнить редактирование физической величины"""
        if self._executed and not self._undone:
            return False
        
        try:
            # Сохраняем текущее состояние
            self._save_state()
            
            # Выполняем редактирование
            self.updated_quantity = self.app_model.update_physical_quantity(
                old_quantity=self.old_quantity,
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                dimension=self.dimension,
                new_group_id=self.new_group_id
            )
            
            if self.updated_quantity:
                self._executed = True
                self._undone = False
                return True
            else:
                print(f"Ошибка выполнения команды редактирования: Не удалось обновить величину")
                return False
            
        except Exception as e:
            print(f"Ошибка выполнения команды редактирования: {e}")
            return False
    
    def undo(self) -> bool:
        """Отменить редактирование - восстановить старую физическую величину"""
        if not self._executed or self._undone:
            return False
        
        try:
            # Восстанавливаем старую физическую величину
            restored_quantity = self.app_model.update_physical_quantity(
                old_quantity=self.updated_quantity,
                name=self.old_quantity.name,
                symbol=self.old_quantity.symbol,
                unit=self.old_quantity.unit,
                dimension=self.old_quantity.dimension,
                new_group_id=self.old_quantity.group_id
            )
            
            # Устанавливаем восстанавливаемую величину как видимую, чтобы сгенерировать событие для UI
            self.app_model.set_visible_quantity(restored_quantity.L, restored_quantity.T, restored_quantity)
            
            # Восстанавливаем предыдущие видимые величины
            for (L, T), quantity in self.previous_visible_quantities.items():
                if quantity:
                    self.app_model.set_visible_quantity(L, T, quantity)
                else:
                    # Если не было видимой величины, удаляем запись о видимой
                    self.app_model.quantity_manager.quantity_repo.remove_visible_quantity(L, T)
            
            # Восстанавливаем альтернативные величины
            for (L, T), quantities in self.previous_alternative_quantities.items():
                for qty in quantities:
                    self.app_model.create_physical_quantity(
                        name=qty.name,
                        symbol=qty.symbol,
                        unit=qty.unit,
                        dimension=qty.dimension,
                        L=qty.L,
                        T=qty.T,
                        group_id=qty.group_id
                    )
            
            # Восстанавливаем удаленные законы
            for law_data in self.deleted_laws:
                self.app_model.create_law_from_selection(
                    law_data['name'],
                    law_data['formula'],
                    law_data['description'],
                    law_data['variables']
                )
            
            self._undone = True
            return True
            
        except Exception as e:
            print(f"Ошибка отмены команды редактирования: {e}")
            return False
    
    def redo(self) -> bool:
        """Повторить редактирование"""
        if not self._executed or not self._undone:
            return False
        
        try:
            # Повторно выполняем редактирование
            self.updated_quantity = self.app_model.update_physical_quantity(
                old_quantity=self.old_quantity,
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                dimension=self.dimension,
                new_group_id=self.new_group_id
            )
            
            if self.updated_quantity:
                # Устанавливаем обновленную величину как видимую, чтобы сгенерировать событие для UI
                self.app_model.set_visible_quantity(self.updated_quantity.L, self.updated_quantity.T, self.updated_quantity)
                self._undone = False
                return True
            else:
                print(f"Ошибка повтора команды редактирования: Не удалось обновить величину")
                return False
            
        except Exception as e:
            print(f"Ошибка повтора команды редактирования: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Редактирование физической величины '{self.old_quantity.name}' -> '{self.name}'"
    
    def _save_state(self) -> None:
        """Сохранить текущее состояние перед редактированием"""
        # Сохраняем текущие видимые величины в позиции редактирования
        visible_quantities = self.app_model.get_visible_quantities()
        if (self.old_quantity.L, self.old_quantity.T) in visible_quantities:
            self.previous_visible_quantities[(self.old_quantity.L, self.old_quantity.T)] = visible_quantities[(self.old_quantity.L, self.old_quantity.T)]
        else:
            self.previous_visible_quantities[(self.old_quantity.L, self.old_quantity.T)] = None
        
        # Сохраняем альтернативные величины в этой позиции
        alternative_quantities = self.app_model.quantity_manager.get_alternatives_for_cell(
            self.old_quantity.L, self.old_quantity.T, self.old_quantity.group_id
        )
        if alternative_quantities:
            self.previous_alternative_quantities[(self.old_quantity.L, self.old_quantity.T)] = alternative_quantities
        else:
            self.previous_alternative_quantities[(self.old_quantity.L, self.old_quantity.T)] = []
        
        # Сохраняем законы, которые могут быть затронуты при изменении имени
        if self.name != self.old_quantity.name:
            dependencies = self.app_model.check_quantity_dependencies(self.old_quantity.name)
            for law in dependencies:
                self.deleted_laws.append({
                    'id': law.id,
                    'name': law.name,
                    'formula': law.formula,
                    'description': law.description,
                    'variables': law.variables
                })