from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class JSBridge(QObject):
    """Мост для связи между Python и JavaScript"""
    
    # Сигналы для общения с JavaScript
    sendAllCellsToWebView = pyqtSignal()
    showContextMenu = pyqtSignal(int, int, str, int, int)
    save_canvas_image_signal = pyqtSignal(str)
    
    def __init__(self, webView):
        super().__init__()
        self.webView = webView
    
    @pyqtSlot()
    def send_all_cells_to_web_view(self):
        """Отправить все соты в WebView"""
        self.sendAllCellsToWebView.emit()
    
    @pyqtSlot(int, int, str, int, int)
    def show_context_menu(self, L: int, T: int, group_name: str, x: int, y: int):
        """Показать контекстное меню"""
        self.showContextMenu.emit(L, T, group_name, x, y)
    
    @pyqtSlot(str)
    def save_canvas_image(self, base64_data_url: str):
        """Сохранить изображение канваса"""
        # Этот метод будет обработан в MainController
        pass
    
    def create_cell(self, cell_data):
        """Создать ячейку через JavaScript"""
        try:
            js = f"field.createCell({cell_data['L']}, {cell_data['T']}, '{cell_data['name']}', '{cell_data['symbol']}', '{cell_data['value_c']}', '{cell_data['group']['name']}', '{cell_data['group']['color']}');"
            self.webView.page().runJavaScript(js)
            print(f"✅ Создана сота через JSBridge: {cell_data['name']} в ({cell_data['L']}, {cell_data['T']})")
        except Exception as e:
            print(f"❌ Ошибка создания соты через JSBridge: {e}")

    def update_cell(self, cell_data):
        """Обновить ячейку через JavaScript"""
        try:
            js = f"field.updateCell({cell_data['L']}, {cell_data['T']}, '{cell_data['name']}', '{cell_data['symbol']}', '{cell_data['value_c']}', '{cell_data['group']['name']}', '{cell_data['group']['color']}');"
            self.webView.page().runJavaScript(js)
            print(f"✅ Обновлена сота через JSBridge: {cell_data['name']} в ({cell_data['L']}, {cell_data['T']})")
        except Exception as e:
            print(f"❌ Ошибка обновления соты через JSBridge: {e}")

    def remove_cell(self, L: int, T: int):
        """Удалить ячейку через JavaScript"""
        try:
            js = f"field.removeCell({L}, {T});"
            self.webView.page().runJavaScript(js)
            print(f"✅ Удалена сота через JSBridge: ({L}, {T})")
        except Exception as e:
            print(f"❌ Ошибка удаления соты через JSBridge: {e}")
