from typing import Dict, Any, List, Optional
from core.entities import PhysicalQuantity, Law
from core.use_cases.command_pattern.base import Command


class DeletePhysicalQuantityCommand(Command):
    """Команда удаления физической величины с каскадным удалением"""
    
    def __init__(self, app_model, L: int, T: int, group_id: str):
        super().__init__()
        self.app_model = app_model
        self.L = L
        self.T = T
        self.group_id = group_id
        
        # Сохраняем состояние для отмены
        self.deleted_quantity = None
        self.deleted_laws = []
        self.previous_visible_quantity = None
        self.alternative_quantities = []
    
    def execute(self) -> bool:
        """Выполнить удаление с каскадным эффектом"""
        if self._executed and not self._undone:
            return False
        
        try:
            # Сохраняем текущее состояние
            self._save_state()
            
            # Выполняем каскадное удаление
            result = self.app_model.delete_cell_cascade(self.L, self.T, self.group_id)
            
            if result['success']:
                self._executed = True
                self._undone = False
                return True
            else:
                print(f"Ошибка выполнения команды удаления: {result['error']}")
                return False
            
        except Exception as e:
            print(f"Ошибка выполнения команды удаления: {e}")
            return False
    
    def undo(self) -> bool:
        """Отменить удаление - восстановить все удаленные объекты"""
        if not self._executed or self._undone:
            return False
        
        try:
            # Восстанавливаем физическую величину
            if self.deleted_quantity:
                self.app_model.create_physical_quantity(
                    name=self.deleted_quantity.name,
                    symbol=self.deleted_quantity.symbol,
                    unit=self.deleted_quantity.unit,
                    dimension=self.deleted_quantity.dimension,
                    L=self.deleted_quantity.L,
                    T=self.deleted_quantity.T,
                    group_id=self.deleted_quantity.group_id
                )
            
            # Восстанавливаем законы
            for law_data in self.deleted_laws:
                self.app_model.create_law_from_selection(
                    law_data['name'],
                    law_data['formula'],
                    law_data['description'],
                    law_data['variables']
                )
            
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
            print(f"Ошибка отмены команды удаления: {e}")
            return False
    
    def redo(self) -> bool:
        """Повторить удаление"""
        if not self._executed or not self._undone:
            return False
        
        try:
            # Повторно выполняем удаление
            result = self.app_model.delete_cell_cascade(self.L, self.T, self.group_id)
            
            if result['success']:
                self._undone = False
                return True
            else:
                print(f"Ошибка повтора команды удаления: {result['error']}")
                return False
            
        except Exception as e:
            print(f"Ошибка повтора команды удаления: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Удаление физической величины в позиции ({self.L}, {self.T})"
    
    def _save_state(self) -> None:
        """Сохранить текущее состояние перед удалением"""
        # Сохраняем удаляемую величину
        quantity = self.app_model.quantity_manager.get_quantity_at_position(self.L, self.T, self.group_id)
        if quantity:
            self.deleted_quantity = quantity
        
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
        
        # Сохраняем законы, которые будут удалены каскадно
        dependencies = self.app_model.check_cell_dependencies(self.L, self.T, self.group_id)
        if dependencies['laws']:
            for law in dependencies['laws']:
                self.deleted_laws.append({
                    'id': law.id,
                    'name': law.name,
                    'formula': law.formula,
                    'description': law.description,
                    'variables': law.variables
                })