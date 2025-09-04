from typing import Dict, Any, Optional
from PyQt5.QtWebEngineWidgets import QWebEngineView


class UIUpdateService:
    """Сервис для точечных обновлений UI на основе событий из репозитория"""
    
    def __init__(self, web_view: QWebEngineView, application_model=None):
        self.web_view = web_view
        self.application_model = application_model
        self.repository = None
        self.system_groups = {}  # cache for system groups
    
    def set_repository(self, repository):
        """Установить репозиторий и подписаться на события"""
        self.repository = repository
        repository.add_callback('quantity_created', self._on_quantity_created)
        repository.add_callback('quantity_updated', self._on_quantity_updated)
        repository.add_callback('quantity_replaced', self._on_quantity_replaced)
        repository.add_callback('quantity_deleted', self._on_quantity_deleted)
    
    def set_application_model(self, application_model):
        """Установить ApplicationModel для доступа к группам"""
        self.application_model = application_model
    
    def _get_group_info(self, group_id: str) -> tuple:
        """Получить имя и цвет группы по ID"""
        if group_id in self.system_groups:
            return self.system_groups[group_id]
        
        # Если есть ApplicationModel, пробуем получить реальные данные о группе
        if self.application_model:
            try:
                groups = self.application_model.get_all_system_groups()
                for group in groups:
                    if group.id == group_id:
                        group_name = group.name
                        group_color = group.color
                        self.system_groups[group_id] = (group_name, group_color)
                        return group_name, group_color
            except Exception as e:
                print(f"Ошибка при получении группы {group_id}: {e}")
        
        # Если не удалось получить реальные данные, используем заглушки
        group_name = group_id
        group_color = "#73ecfa"  # цвет по умолчанию (голубой)
        self.system_groups[group_id] = (group_name, group_color)
        return group_name, group_color
    
    def _on_quantity_created(self, data: Dict[str, Any]):
        """Обработчик создания новой видимой величины"""
        L, T = data['L'], data['T']
        quantity = data['quantity']
        
        # Вызываем createCell только для новой видимой соты
        group_name, group_color = self._get_group_info(quantity.group_id)
        self.web_view.page().runJavaScript(
            f"field.createCell({L}, {T}, '{quantity.name}', "
            f"'{quantity.symbol}', '{quantity.dimension}', "
            f"'{group_name}', '{group_color}');"
        )
    
    def _on_quantity_updated(self, data: Dict[str, Any]):
        """Обработчик обновления свойств величины в той же группе"""
        L, T = data['L'], data['T']
        new_quantity = data['new_quantity']
        
        # Вызываем updateCell для обновления свойств
        group_name, group_color = self._get_group_info(new_quantity.group_id)
        self.web_view.page().runJavaScript(
            f"field.updateCell({L}, {T}, '{new_quantity.name}', "
            f"'{new_quantity.symbol}', '{new_quantity.dimension}', "
            f"'{group_name}', '{group_color}');"
        )
    
    def _on_quantity_replaced(self, data: Dict[str, Any]):
        """Обработчик замены группы в тех же координатах"""
        L, T = data['L'], data['T']
        new_quantity = data['new_quantity']
        
        # Вызываем updateCell для замены группы
        group_name, group_color = self._get_group_info(new_quantity.group_id)
        self.web_view.page().runJavaScript(
            f"field.updateCell({L}, {T}, '{new_quantity.name}', "
            f"'{new_quantity.symbol}', '{new_quantity.dimension}', "
            f"'{group_name}', '{group_color}');"
        )
    
    def _on_quantity_deleted(self, data: Dict[str, Any]):
        """Обработчик удаления видимой величины"""
        L, T = data['L'], data['T']
        group_name = data['group_name']
        
        # Вызываем removeCell с указанием группы
        self.web_view.page().runJavaScript(
            f"field.removeCell({L}, {T}, '{group_name}');"
        )
    
    def draw_parallelogram(self, quantities, color=None):
        """Отрисовать параллелограмм на холсте"""
        js_array = "[" + ", ".join(
            f"{{L: {q.L}, T: {q.T}}}" for q in quantities
        ) + "]"

        if color:
            self.web_view.page().runJavaScript(f"field.drawParallelogram({js_array}, '{color}');")
        else:
            self.web_view.page().runJavaScript(f"field.drawParallelogram({js_array});")
    
    def clear_parallelogram(self):
        """Очистить параллелограмм с холста"""
        self.web_view.page().runJavaScript("field.clearParallelogram();")