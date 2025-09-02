from typing import Dict, Tuple, List
from PyQt5.QtCore import QObject, pyqtSignal

from core.use_cases.application_model import ApplicationModel
from core.entities.physical_quantity import PhysicalQuantity


class MainPresenter(QObject):
    """Презентер главного окна"""
    
    # Сигналы для обновления View
    cells_updated = pyqtSignal(dict)  # Dict[Tuple[int, int], PhysicalQuantity]
    cell_created = pyqtSignal(int, int, object)  # L, T, PhysicalQuantity
    cell_updated = pyqtSignal(int, int, object)  # L, T, PhysicalQuantity
    cell_removed = pyqtSignal(int, int)  # L, T
    parallelogram_should_be_drawn = pyqtSignal(list, str)  # quantities, color
    parallelogram_should_be_cleared = pyqtSignal()
    
    def __init__(self, application_model: ApplicationModel):
        super().__init__()
        self.app_model = application_model
    
    def get_visible_cells_for_display(self) -> Dict[Tuple[int, int], PhysicalQuantity]:
        """Получить видимые соты для отображения"""
        return self.app_model.get_visible_quantities()
    
    def handle_all_cells_request(self):
        """Обработка запроса всех сот"""
        cells = self.get_visible_cells_for_display()
        self.cells_updated.emit(cells)
    
    def handle_parallelogram_draw(self, quantities: List[PhysicalQuantity], color: str = ""):
        """Обработка запроса отрисовки параллелограмма"""
        self.parallelogram_should_be_drawn.emit(quantities, color)
    
    def handle_parallelogram_clear(self):
        """Обработка запроса очистки параллелограмма"""
        self.parallelogram_should_be_cleared.emit()
    
    def create_physical_quantity(self, name: str, symbol: str, unit: str, dimension: str, 
                               L: int, T: int, group_id: str):
        """Создать физическую величину"""
        try:
            quantity = self.app_model.create_physical_quantity(
                name, symbol, unit, dimension, L, T, group_id
            )
            # Устанавливаем как видимую если это первая в данной позиции
            self.app_model.set_visible_quantity(L, T, quantity)
            self.cell_created.emit(L, T, quantity)
            return quantity
        except Exception as e:
            print(f"Ошибка создания физической величины: {e}")
            return None
    
    def update_physical_quantity(self, old_quantity: PhysicalQuantity, 
                               name: str, symbol: str, unit: str, dimension: str, 
                               new_group_id: str):
        """Обновить физическую величину"""
        try:
            updated_quantity = self.app_model.update_physical_quantity(
                old_quantity, name, symbol, unit, dimension, new_group_id
            )
            # Обновляем видимую величину
            self.app_model.set_visible_quantity(old_quantity.L, old_quantity.T, updated_quantity)
            self.cell_updated.emit(old_quantity.L, old_quantity.T, updated_quantity)
            return updated_quantity
        except Exception as e:
            print(f"Ошибка обновления физической величины: {e}")
            return None
    
    def delete_physical_quantity(self, L: int, T: int, group_id: str):
        """Удалить физическую величину с каскадным удалением"""
        try:
            self.app_model.delete_cell_cascade(L, T, group_id)
            
            # Проверяем, есть ли альтернативные величины в этой позиции
            all_groups = self.app_model.get_all_system_groups()
            alternative_found = False
            
            for group in all_groups:
                if group.id != group_id:
                    # Здесь нужно проверить, есть ли величина в этой группе в данной позиции
                    # Добавим метод в ApplicationModel позже
                    pass
            
            if not alternative_found:
                self.cell_removed.emit(L, T)
                
        except Exception as e:
            print(f"Ошибка удаления физической величины: {e}")
    
    def replace_visible_quantity(self, L: int, T: int, quantity: PhysicalQuantity):
        """Заменить видимую величину"""
        self.app_model.set_visible_quantity(L, T, quantity)
        self.cell_updated.emit(L, T, quantity)
    
    def get_system_groups(self):
        """Получить системные группы"""
        return self.app_model.get_all_system_groups()
    
    def get_law_groups(self):
        """Получить группы законов"""
        return self.app_model.get_all_law_groups()
    
    def validate_quantity_name(self, name: str, exclude_quantity=None) -> bool:
        """Проверить уникальность имени величины"""
        return self.app_model.validate_quantity_name(name, exclude_quantity)
