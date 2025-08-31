# backend/bridge.py
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class JSBridge(QObject):
    """Мост для связи между Python и JavaScript"""
    
    # Сигналы для общения с JavaScript
    sendAllCellsToWebView = pyqtSignal()
    showContextMenu = pyqtSignal(int, int, str, int, int)
    
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
    
    # Сигнал для сохранения изображения
    save_canvas_image_signal = pyqtSignal(str)

    def create_cell(self, cell):
        js = f"field.createCell({cell.L}, {cell.T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.name}', '{cell.group.color}');"
        self.webView.page().runJavaScript(js)

    def update_cell(self, cell):
        js = f"field.updateCell({cell.L}, {cell.T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.name}', '{cell.group.color}');"
        self.webView.page().runJavaScript(js)
