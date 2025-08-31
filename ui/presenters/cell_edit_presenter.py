from typing import List, Optional
from PyQt5.QtWidgets import QDialog, QWidget

from core.use_cases.application_model import ApplicationModel
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.system_group import SystemGroup


class CellEditPresenter:
    """Презентер для редактирования/создания сот"""
    
    def __init__(self, application_model: ApplicationModel, L: int, T: int, 
                 parent: Optional[QWidget] = None, create_mode: bool = False,
                 exclude_groups: Optional[List[SystemGroup]] = None):
        self.app_model = application_model
        self.L = L
        self.T = T
        self.parent = parent
        self.create_mode = create_mode
        self.exclude_groups = exclude_groups or []
        
        # Получаем текущую величину для редактирования
        self.current_quantity = None
        if not create_mode:
            # Получаем видимую величину в данной позиции
            visible_quantities = self.app_model.get_visible_quantities()
            self.current_quantity = visible_quantities.get((L, T))
    
    def show(self):
        """Показать диалог редактирования"""
        # Импортируем здесь чтобы избежать циклических импортов
        from views.cell_edit_dialog import EditCellDialog
        
        dialog = EditCellDialog(
            self,
            self.L,
            self.T,
            parent=self.parent,
            create_mode=self.create_mode,
            exclude_groups=self.exclude_groups
        )
        dialog.exec_()
    
    def get_current_quantity(self) -> Optional[PhysicalQuantity]:
        """Получить текущую физическую величину"""
        return self.current_quantity
    
    def get_available_groups(self) -> List[SystemGroup]:
        """Получить доступные группы"""
        all_groups = self.app_model.get_all_system_groups()
        
        if self.create_mode:
            # Исключаем уже занятые группы
            exclude_ids = {group.id for group in self.exclude_groups}
            return [group for group in all_groups if group.id not in exclude_ids]
        
        return all_groups
    
    def validate_name(self, name: str) -> bool:
        """Проверить уникальность имени"""
        return self.app_model.validate_quantity_name(name, self.current_quantity)
    
    def save_quantity(self, name: str, symbol: str, unit: str, dimension: str, group_id: str) -> bool:
        """Сохранить физическую величину"""
        try:
            if self.create_mode:
                # Создаем новую величину
                quantity = self.app_model.create_physical_quantity(
                    name, symbol, unit, dimension, self.L, self.T, group_id
                )
                
                # Устанавливаем как видимую
                self.app_model.set_visible_quantity(self.L, self.T, quantity)
                
                print(f"✅ Создана новая сота: {name} в позиции ({self.L}, {self.T})")
                
                # Отправляем сигнал об обновлении UI через существующий презентер
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                main_window = app.activeWindow()
                
                # Используем презентер из главного окна
                if hasattr(main_window, 'presenter'):
                    main_window.presenter.cell_created.emit(self.L, self.T, quantity)
                    # Принудительно обновляем все соты
                    main_window.presenter.handle_all_cells_request()
                
            else:
                # Обновляем существующую
                if not self.current_quantity:
                    return False
                
                updated_quantity = self.app_model.update_physical_quantity(
                    self.current_quantity, name, symbol, unit, dimension, group_id
                )
                
                # Обновляем видимую величину
                self.app_model.set_visible_quantity(self.L, self.T, updated_quantity)
                
                print(f"✅ Обновлена сота: {name} в позиции ({self.L}, {self.T})")
                
                # Отправляем сигнал об обновлении UI через главный презентер
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                main_window = app.activeWindow()
                
                if hasattr(main_window, 'presenter'):
                    main_window.presenter.cell_updated.emit(self.L, self.T, updated_quantity)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения величины: {e}")
            return False
    
    def get_alternatives_for_replacement(self) -> List[PhysicalQuantity]:
        """Получить альтернативные величины для замены"""
        if not self.current_quantity:
            return []
        
        return self.app_model.get_alternative_quantities(
            self.L, self.T, self.current_quantity.group.id
        )
