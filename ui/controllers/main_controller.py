from typing import List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QPoint, QVariant
from PyQt5.QtWidgets import QApplication, QAction, QMenu, QMessageBox, QFileDialog
from PyQt5.QtGui import QImage
import base64

from core.use_cases.application_model import ApplicationModel
from core.use_cases.application_model_with_commands import ApplicationModelWithCommands
from core.entities.physical_quantity import PhysicalQuantity
from services.ui_update_service import UIUpdateService


class MainController(QObject):
    """Основной контроллер приложения"""
    
    # Сигналы для обновления UI
    cell_updated = pyqtSignal(str)
    parallelogram_drawn = pyqtSignal(list, str)  # quantities, color
    parallelogram_cleared = pyqtSignal()
    all_cells_requested = pyqtSignal()
    
    # Сигналы для управления состоянием undo/redo
    can_undo_changed = pyqtSignal()
    can_redo_changed = pyqtSignal()
    
    def __init__(self, application_model: ApplicationModel, web_view):
        super().__init__()
        # Проверяем, является ли модель моделью с поддержкой команд
        if isinstance(application_model, ApplicationModelWithCommands):
            self.app_model = application_model
            self.commands_enabled = True
        else:
            # Если нет, создаем обертку с поддержкой команд
            self.app_model = ApplicationModelWithCommands(
                quantity_manager=application_model.quantity_manager,
                system_group_manager=application_model.system_group_manager,
                law_manager=application_model.law_manager,
                law_group_manager=application_model.law_group_manager,
                parallelogram_logic=application_model.parallelogram_logic
            )
            self.commands_enabled = False
        
        self.web_view = web_view
        
        # Создаем сервис для точечных обновлений UI
        self.ui_update_service = UIUpdateService(web_view, self.app_model)
        
        # Получаем репозиторий из ApplicationModel и подключаем UI сервис
        quantity_repository = self.app_model.quantity_manager.quantity_repo
        self.ui_update_service.set_repository(quantity_repository)
        self.ui_update_service.set_application_model(self.app_model)
        
        # Подключаем сигналы параллелограмма
        self.parallelogram_drawn.connect(self.ui_update_service.draw_parallelogram)
        self.parallelogram_cleared.connect(self.ui_update_service.clear_parallelogram)
    
    # === Обработка взаимодействий с сотами ===
    
    @pyqtSlot(str)
    def handle_cell_click(self, cell_data: str):
        """Обработка клика по соте"""
        # Очищаем выделение при любом клике по полю
        self.app_model.clear_selection()
        self.parallelogram_cleared.emit()
        
        print(f"Клик по соте: {cell_data}")
        self.cell_updated.emit(f"Выбрана сота {cell_data}")
    
    @pyqtSlot(int, int, QVariant, int, int)
    def show_context_menu(self, L: int, T: int, group_name: str, x: int, y: int):
        """Показать контекстное меню для соты"""
        print(f"ПКМ на соте: L={L}, T={T}, group={group_name}, x={x}, y={y}")
        
        menu = QMenu()
        
        # Показываем пункты редактирования/удаления только если есть группа (сотка существует)
        if group_name and group_name.strip():
            # Получаем альтернативные величины (исключая текущую группу)
            alternatives = self.app_model.get_alternative_quantities(L, T, group_name)
            
            # Фильтруем альтернативы, чтобы исключить текущую соту
            current_quantity = self._get_quantity_at_position(L, T, group_name)
            alternatives = [q for q in alternatives if q != current_quantity]
            
            if alternatives:
                sub_menu = QMenu("Заменить", menu)
                for alt_quantity in alternatives:
                    action = QAction(alt_quantity.name, sub_menu)
                    action.triggered.connect(
                        lambda _, q=alt_quantity: self._replace_and_suppress(L, T, q)
                    )
                    sub_menu.addAction(action)
                menu.addMenu(sub_menu)
            
            # Редактировать и удалить
            edit_action = QAction("Редактировать", menu)
            delete_action = QAction("Удалить", menu)
            
            edit_action.triggered.connect(lambda: self._edit_and_suppress(L, T))
            delete_action.triggered.connect(lambda: self._delete_and_suppress(L, T, group_name))
            
            menu.addAction(edit_action)
            menu.addAction(delete_action)
        
        # Создать новую сотку если есть свободные группы
        used_groups = self._get_used_groups_at_position(L, T)
        all_groups = self.app_model.get_all_system_groups()
        
        if len(used_groups) < len(all_groups):
            create_action = QAction("Создать", menu)
            create_action.triggered.connect(
                lambda: self._create_and_suppress(L, T, used_groups)
            )
            menu.addAction(create_action)
        
        menu.exec_(QPoint(x, y))
    
    @pyqtSlot(int, int, str)
    def on_cell_selected(self, L: int, T: int, group_name: str):
        """Обработка выделения соты"""
        # Получаем физическую величину
        quantity = self._get_quantity_at_position(L, T, group_name)
        
        if not quantity:
            return
        
        # Переключаем выделение только для текущей соты
        # Не очищаем выделение у всех сот - это нарушает пользовательский опыт
        self.app_model.toggle_quantity_selection(quantity)
        
        # Проверяем параллелограмм
        parallelogram = self.app_model.check_parallelogram()
        
        if parallelogram:
            # Ищем существующий закон
            existing_law = self.app_model.find_law_for_selection()
            
            if existing_law:
                # Получаем цвет группы законов
                law_group = self.app_model.get_law_group_by_id(existing_law.group_id)
                color = law_group.color if law_group else "#ff0000"
                print(f"🎨 Найден существующий закон '{existing_law.name}', цвет группы: {color}")
                self.parallelogram_drawn.emit(parallelogram, color)
                self._open_law_dialog(parallelogram, existing_law)
            else:
                print("🔴 Новый параллелограмм, цвет по умолчанию: красный")
                self.parallelogram_drawn.emit(parallelogram, "#ff0000")
                self._open_law_dialog(parallelogram, None)
        else:
            print("🧹 Параллелограмм не найден, очищаем")
            self.parallelogram_cleared.emit()
    
    @pyqtSlot(int, int, str)
    def onCellSelected(self, L: int, T: int, group_name: str):
        """Альтернативное имя метода для совместимости с JS"""
        self.on_cell_selected(L, T, group_name)
    
    @pyqtSlot(int, int, str, int, int)
    def showContextMenu(self, L: int, T: int, group_name: str, x: int, y: int):
        """Альтернативное имя метода для совместимости с JS"""
        self.show_context_menu(L, T, group_name, x, y)
    
    @pyqtSlot()
    def send_all_cells_to_web_view(self):
        """Отправить все соты в WebView"""
        print("📡 JS запросил отправку сот")
        self.all_cells_requested.emit()
    
    @pyqtSlot(str)
    def save_canvas_image(self, base64_data_url: str):
        """Сохранить изображение канваса"""
        try:
            base64_data = base64_data_url.split(',')[1]
            image_data = base64.b64decode(base64_data)
            
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Сохранить изображение",
                "",
                "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)"
            )
            
            if not file_path:
                return
            
            image = QImage()
            image.loadFromData(image_data)
            
            fmt = 'PNG' if file_path.lower().endswith('.png') else 'JPEG'
            image.save(file_path, fmt)
            
            QMessageBox.information(None, "Экспорт", "Изображение успешно сохранено.")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось сохранить изображение:\n{e}")
    
    # === Приватные методы ===
    
    def _replace_and_suppress(self, L: int, T: int, quantity: PhysicalQuantity):
        """Заменить сотку и подавить следующий клик"""
        # Очищаем выделение перед заменой
        self.app_model.clear_selection()
        self.parallelogram_cleared.emit()
        
        self.app_model.set_visible_quantity(L, T, quantity)
        # Событие будет обработано UIUpdateService автоматически
        self._suppress_next_click()
    
    def _edit_and_suppress(self, L: int, T: int):
        """Редактировать сотку и подавить следующий клик"""
        # Очищаем выделение перед редактированием
        self.app_model.clear_selection()
        self.parallelogram_cleared.emit()
        
        from ui.presenters.cell_edit_presenter import CellEditPresenter
        app = QApplication.instance()
        main_window = app.activeWindow()
        
        # Блокируем операции с полем
        if hasattr(main_window, '_block_field_operations'):
            main_window._block_field_operations(True)
        
        try:
            presenter = CellEditPresenter(self.app_model, L, T, parent=main_window)
            presenter.show()
        finally:
            # Разблокируем операции с полем
            if hasattr(main_window, '_block_field_operations'):
                main_window._block_field_operations(False)
            
        self._suppress_next_click()
    
    def _delete_and_suppress(self, L: int, T: int, group_name: str):
        """Удалить соту и подавить следующий клик с каскадным удалением"""
        # Очищаем выделение перед удалением
        self.app_model.clear_selection()
        self.parallelogram_cleared.emit()
        
        # Найдем группу по имени
        groups = self.app_model.get_all_system_groups()
        group_id = None
        for group in groups:
            if group.name == group_name:
                group_id = group.id
                break
        
        if group_id:
            try:
                # Используем каскадное удаление с поддержкой команд
                if self.commands_enabled:
                    # Удаляем с поддержкой отмены/повтора
                    success = self.app_model.delete_physical_quantity_with_command(L, T, group_id)
                    if success:
                        print(f"✅ Удалена сота в позиции ({L}, {T}) из группы {group_name} с каскадным удалением зависимостей (с поддержкой отмены)")
                        # Уведомляем об изменении состояния undo/redo
                        self._notify_state_changed()
                    else:
                        print(f"❌ Не удалось удалить соту в позиции ({L}, {T}) из группы {group_name}")
                else:
                    # Удаляем без поддержки команд (старый режим)
                    self.app_model.delete_cell_cascade(L, T, group_id)
                    print(f"✅ Удалена сота в позиции ({L}, {T}) из группы {group_name} с каскадным удалением зависимостей")
                
                # Событие удаления будет обработано UIUpdateService автоматически
            except ValueError as e:
                print(f"Ошибка каскадного удаления: {e}")
                # Не прерываем выполнение, просто логируем ошибку
        else:
            print(f"❌ Группа {group_name} не найдена")
        
        self._suppress_next_click()
    
    def _create_and_suppress(self, L: int, T: int, used_groups: List):
        """Создать сотку и подавить следующий клик"""
        # Очищаем выделение перед созданием
        self.app_model.clear_selection()
        self.parallelogram_cleared.emit()
        
        from ui.presenters.cell_edit_presenter import CellEditPresenter
        app = QApplication.instance()
        main_window = app.activeWindow()
        
        # Блокируем операции с полем
        if hasattr(main_window, '_block_field_operations'):
            main_window._block_field_operations(True)
        
        try:
            presenter = CellEditPresenter(
                self.app_model, L, T,
                create_mode=True,
                exclude_groups=used_groups,
                parent=main_window
            )
            presenter.show()
        finally:
            # Разблокируем операции с полем
            if hasattr(main_window, '_block_field_operations'):
                main_window._block_field_operations(False)
            
        self._suppress_next_click()
    
    def _get_used_groups_at_position(self, L: int, T: int) -> List[str]:
        """Получить занятые группы в позиции"""
        # Получаем ID занятых групп
        group_ids = self.app_model.get_used_groups_at_position(L, T)
        # Преобразуем ID в объекты групп
        all_groups = self.app_model.get_all_system_groups()
        return [group for group in all_groups if group.id in group_ids]
    
    def _get_quantity_at_position(self, L: int, T: int, group_name: str) -> Optional[PhysicalQuantity]:
        """Получить величину в позиции"""
        # Найдем группу по имени
        groups = self.app_model.get_all_system_groups()
        for group in groups:
            if group.name == group_name:
                # Получаем величину из группы
                return self.app_model.get_quantity_at_position(L, T, group.id)
        return None
    
    def _open_law_dialog(self, quantities: List[PhysicalQuantity], existing_law=None):
        """Открыть диалог закона"""
        # НЕ очищаем выделение и параллелограмм при открытии диалога закона
        # Они должны оставаться видимыми для пользователя
        
        from ui.presenters.law_dialog_presenter import LawDialogPresenter
        app = QApplication.instance()
        main_window = app.activeWindow()
        
        # Блокируем операции с полем
        if hasattr(main_window, '_block_field_operations'):
            main_window._block_field_operations(True)
        
        try:
            presenter = LawDialogPresenter(
                self.app_model, quantities, existing_law,
                parent=main_window
            )
            presenter.show()
        finally:
            # Разблокируем операции с полем
            if hasattr(main_window, '_block_field_operations'):
                main_window._block_field_operations(False)
    
    def _suppress_next_click(self):
        """Подавить следующий клик в WebView"""
        self.web_view.page().runJavaScript("window.suppressNextClick = true;")
    
    def _notify_state_changed(self):
        """Уведомить об изменении состояния undo/redo"""
        print(f"🔔 Уведомление об изменении состояния. Can undo: {self.app_model.can_undo()}, Can redo: {self.app_model.can_redo()}")
        self.can_undo_changed.emit()
        self.can_redo_changed.emit()
    
    def can_undo(self):
        """Проверить возможность отмены"""
        if self.commands_enabled:
            return self.app_model.can_undo()
        return False
    
    def can_redo(self):
        """Проверить возможность повтора"""
        if self.commands_enabled:
            return self.app_model.can_redo()
        return False
    
    def get_undo_description(self):
        """Получить описание действия для отмены"""
        if self.commands_enabled:
            return self.app_model.get_undo_description()
        return ""
    
    def get_redo_description(self):
        """Получить описание действия для повтора"""
        if self.commands_enabled:
            return self.app_model.get_redo_description()
        return ""
    
    def undo_last_action(self):
        """Выполнить отмену последнего действия"""
        if self.commands_enabled:
            print(f"🔄 Попытка отмены действия. Can undo: {self.app_model.can_undo()}, Can redo: {self.app_model.can_redo()}")
            success = self.app_model.undo_last_action()
            if success:
                print("✅ Действие успешно отменено")
                print(f"🔄 После отмены. Can undo: {self.app_model.can_undo()}, Can redo: {self.app_model.can_redo()}")
                # Уведомляем об изменении состояния undo/redo
                self._notify_state_changed()
            else:
                print("❌ Не удалось отменить действие")
            return success
        return False
    
    def redo_last_action(self):
        """Выполнить повтор последнего действия"""
        if self.commands_enabled:
            print(f"🔄 Попытка повтора действия. Can undo: {self.app_model.can_undo()}, Can redo: {self.app_model.can_redo()}")
            success = self.app_model.redo_last_action()
            if success:
                print("✅ Действие успешно повторено")
                print(f"🔄 После повтора. Can undo: {self.app_model.can_undo()}, Can redo: {self.app_model.can_redo()}")
                # Уведомляем об изменении состояния undo/redo
                self._notify_state_changed()
            else:
                print("❌ Не удалось повторить действие")
            return success
        return False
