from typing import List, Optional
from PyQt5.QtWidgets import QWidget

from core.use_cases.application_model import ApplicationModel
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.law import Law


class LawDialogPresenter:
    """Презентер для диалога законов"""
    
    def __init__(self, application_model: ApplicationModel, 
                 quantities: List[PhysicalQuantity], 
                 existing_law: Optional[Law] = None,
                 parent: Optional[QWidget] = None):
        self.app_model = application_model
        self.quantities = quantities
        self.existing_law = existing_law
        self.parent = parent
    
    def show(self):
        """Показать диалог закона"""
        from views.laws_dialog import LawDialog
        
        # Создаем временный сервис для совместимости со старым кодом
        class TempService:
            def __init__(self, app_model):
                self.app_model = app_model
            
            @property
            def law_groups(self):
                return self.app_model.get_all_law_groups()
        
        temp_service = TempService(self.app_model)
        
        dialog = LawDialog(
            temp_service,
            self.quantities,
            self.existing_law,
            parent=self.parent
        )
        dialog.show()
    
    def get_law_groups(self):
        """Получить группы законов"""
        return self.app_model.get_all_law_groups()
    
    def create_law(self, name: str, formula: str, description: str, group_id: str) -> bool:
        """Создать закон из выделенных величин"""
        try:
            law = self.app_model.create_law_from_selection(name, formula, description, group_id)
            return law is not None
        except Exception as e:
            print(f"Ошибка создания закона: {e}")
            return False
    
    def update_law(self, law: Law, name: str, formula: str, description: str, group_id: str) -> bool:
        """Обновить существующий закон"""
        try:
            # Здесь нужно будет добавить метод в ApplicationModel для обновления законов
            # law.name = name
            # law.formula = formula
            # law.description = description
            # и т.д.
            return True
        except Exception as e:
            print(f"Ошибка обновления закона: {e}")
            return False
    
    def get_quantity_names(self) -> List[str]:
        """Получить имена величин"""
        return [q.name for q in self.quantities]
    
    def validate_law_variables(self, variables: List[str]) -> bool:
        """Проверить соответствие переменных закона выделенным величинам"""
        quantity_names = set(self.get_quantity_names())
        variable_names = set(variables)
        return quantity_names == variable_names
