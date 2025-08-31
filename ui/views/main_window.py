from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog, QMessageBox
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QIcon, QKeySequence
import os

from core.use_cases.application_model import ApplicationModel
from core.application_factory import ApplicationFactory
from ui.controllers.main_controller import MainController
from ui.presenters.main_presenter import MainPresenter

from views.physical_web_view import PhysicalWebEngineView
from views.law_group_settings_dialog import LawGroupSettingsDialog
from views.system_groups_dialog import SystemGroupsDialog
from services.file_service import FileService
from backend.bridge import JSBridge


class MainWindow(QMainWindow):
    """Главное окно приложения с новой архитектурой"""
    
    def __init__(self, application_model: ApplicationModel):
        super().__init__()
        
        # Модель приложения
        self.app_model = application_model
        
        # Создаем UI компоненты
        self._setup_ui()
        
        # Создаем контроллер и презентер
        self.controller = ApplicationFactory.create_main_controller(self.app_model, self.webView)
        self.presenter = ApplicationFactory.create_main_presenter(self.app_model)
        
        # Настраиваем веб-канал
        self._setup_web_channel()
        
        # Подключаем сигналы
        self._connect_signals()
        
        # Загружаем веб-интерфейс
        self._load_web_interface()
        
        # Настраиваем меню
        self._init_menu()
        
        # Поддержка Drag and Drop
        self.setAcceptDrops(True)
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("FViZ 2.0")
        self.setGeometry(100, 100, 2000, 1400)
        
        # Создаем центральный виджет и layout
        self.container = QWidget()
        self.layout = QVBoxLayout()
        
        # Создаем веб-представление
        self.webView = PhysicalWebEngineView()
        self.layout.addWidget(self.webView)
        
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)
    
    def _setup_web_channel(self):
        """Настройка веб-канала для связи с JS"""
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.controller)
        self.webView.page().setWebChannel(self.channel)
        
        # Создаем мост для JavaScript методов
        self.js_bridge = JSBridge(self.webView)
        self.channel.registerObject("js_bridge", self.js_bridge)
        
        # Подключаем сигналы моста к контроллеру
        self.js_bridge.sendAllCellsToWebView.connect(self.controller.send_all_cells_to_web_view)
        self.js_bridge.showContextMenu.connect(lambda L, T, group_name, x, y: self.controller.show_context_menu(L, T, group_name, x, y))
        self.js_bridge.save_canvas_image_signal.connect(lambda data_url: self.controller.save_canvas_image(data_url))
    
    def _connect_signals(self):
        """Подключение сигналов между компонентами"""
        # Сигналы от контроллера
        self.controller.cell_updated.connect(self.on_cell_updated)
        self.controller.parallelogram_drawn.connect(self.draw_parallelogram)
        self.controller.parallelogram_cleared.connect(self.clear_parallelogram)
        self.controller.all_cells_requested.connect(self.presenter.handle_all_cells_request)
        
        # Сигналы от презентера
        self.presenter.cells_updated.connect(self.send_cells_to_webview)
        self.presenter.cell_created.connect(self.on_cell_created)
        self.presenter.cell_updated.connect(self.on_cell_updated_by_presenter)
        self.presenter.cell_removed.connect(self.on_cell_removed)
        self.presenter.parallelogram_should_be_drawn.connect(self.draw_parallelogram)
        self.presenter.parallelogram_should_be_cleared.connect(self.clear_parallelogram)
    
    def _load_web_interface(self):
        """Загрузка веб-интерфейса"""
        self.webView.setHtml(open("canvas/canvas.html", encoding="utf-8").read())
        self.webView.page().loadFinished.connect(self.init_web_channel)
    
    def _init_menu(self):
        """Инициализация меню"""
        def icon(name):
            return QIcon(os.path.join("res", "icons", f"{name}.png"))
        
        menu_bar = self.menuBar()
        
        # Файл
        file_menu = menu_bar.addMenu("Файл")
        
        open_action = QAction(icon("open"), "Открыть...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.load_json_dialog)
        
        save_action = QAction(icon("save"), "Сохранить", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_json_dialog)
        
        save_as_action = QAction(icon("save_as"), "Сохранить как...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_json_as_dialog)
        
        export_action = QAction(icon("export"), "Экспорт таблицы", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(lambda: self.webView.page().runJavaScript("exportCanvasImage();"))
        
        exit_action = QAction(icon("exit"), "Выйти", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        
        file_menu.addActions([open_action, save_action, save_as_action, export_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Правка
        edit_menu = menu_bar.addMenu("Правка")
        
        undo_action = QAction("Отменить", self)
        undo_action.setShortcut(QKeySequence.Undo)
        
        redo_action = QAction("Повторить", self)
        redo_action.setShortcut(QKeySequence.Redo)
        
        edit_menu.addActions([undo_action, redo_action])
        
        # Вид
        view_menu = menu_bar.addMenu("Вид")
        
        laws_action = QAction("Список законов", self)
        laws_action.setShortcut("Ctrl+L")
        
        zoom_in_action = QAction("Приблизить", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        
        zoom_out_action = QAction("Отдалить", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_out_action.triggered.connect(self.zoom_out)
        
        view_menu.addActions([laws_action, zoom_in_action, zoom_out_action])
        
        # Параметры
        settings_menu = menu_bar.addMenu("Параметры")
        
        group_action = QAction("Системные группы ФВ", self)
        group_action.triggered.connect(self.open_group_dialog)
        
        lawgroup_action = QAction("Параметры группы законов", self)
        lawgroup_action.triggered.connect(self.open_law_group_dialog)
        
        settings_menu.addActions([group_action, lawgroup_action])
        
        # Справка
        help_menu = menu_bar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(about_action)
    
    # === Обработчики сигналов ===
    
    def init_web_channel(self):
        """Инициализация веб-канала после загрузки страницы"""
        self.webView.page().runJavaScript("""
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyqtObject = channel.objects.backend;
                window.jsBridge = channel.objects.js_bridge;
                console.log("✅ QWebChannel успешно создан в MainWindow");
                
                // Отправляем все ячейки на веб-страницу после инициализации
                setTimeout(function() {
                    if (window.jsBridge && window.jsBridge.send_all_cells_to_web_view) {
                        window.jsBridge.send_all_cells_to_web_view();
                    } else {
                        console.error("❌ Метод send_all_cells_to_web_view не найден в jsBridge");
                    }
                }, 500); // Небольшая задержка для гарантии полной инициализации
            });
        """)
    
    def on_cell_updated(self, message):
        """Обработка обновления соты"""
        print(f"Cell updated: {message}")
    
    def send_cells_to_webview(self, cells):
        """Отправка сот в WebView"""
        print(f"📡 Отправляем {len(cells)} сот в WebView")
        
        # Сначала очищаем все соты
        self.webView.page().runJavaScript("ensureFieldExists(() => { field.clearAll(); });")
        
        # Затем создаем новые
        for (L, T), cell in cells.items():
            group_name = self._get_group_name(cell.group_id)
            group_color = self._get_group_color(cell.group_id)
            
            # Экранируем кавычки в названиях
            safe_name = cell.name.replace("'", "\\'").replace('"', '\\"')
            safe_symbol = cell.symbol.replace("'", "\\'").replace('"', '\\"')
            safe_dimension = cell.dimension.replace("'", "\\'").replace('"', '\\"')  # Используем dimension вместо unit
            safe_group_name = group_name.replace("'", "\\'").replace('"', '\\"')
            
            script = f"field.createCell({L}, {T}, '{safe_name}', '{safe_symbol}', '{safe_dimension}', '{safe_group_name}', '{group_color}');"
            self.webView.page().runJavaScript(f"ensureFieldExists(() => {{ {script} }});")
            
            print(f"✅ Создана сота: {safe_name} в ({L}, {T})")
    
    def _get_group_name(self, group_id: str) -> str:
        """Получить название группы по ID"""
        group = self.app_model.get_system_group_by_id(group_id)
        return group.name if group else "Неизвестная группа"
    
    def _get_group_color(self, group_id: str) -> str:
        """Получить цвет группы по ID"""
        group = self.app_model.get_system_group_by_id(group_id)
        return group.color if group else "#73ecfa"
    
    def on_cell_created(self, L, T, quantity):
        """Обработка создания новой соты"""
        # Используем мост для создания соты
        group = self.app_model.get_system_group_by_id(quantity.group_id)
        cell_data = {
            'L': L,
            'T': T,
            'name': quantity.name,
            'symbol': quantity.symbol,
            'value_c': quantity.unit,
            'group': {
                'name': group.name if group else "Неизвестная группа",
                'color': group.color if group else "#73ecfa"
            }
        }
        self.js_bridge.create_cell(cell_data)
        
        # Принудительно обновляем все соты для гарантии корректного отображения
        self.presenter.handle_all_cells_request()
    
    def on_cell_updated_by_presenter(self, L, T, quantity):
        """Обработка обновления соты презентером"""
        # Используем мост для обновления соты
        group = self.app_model.get_system_group_by_id(quantity.group_id)
        cell_data = {
            'L': L,
            'T': T,
            'name': quantity.name,
            'symbol': quantity.symbol,
            'value_c': quantity.unit,
            'group': {
                'name': group.name if group else "Неизвестная группа",
                'color': group.color if group else "#73ecfa"
            }
        }
        self.js_bridge.update_cell(cell_data)
        
        # Принудительно обновляем все соты для гарантии корректного отображения
        self.presenter.handle_all_cells_request()
    
    def on_cell_removed(self, L, T):
        """Обработка удаления соты"""
        self.js_bridge.remove_cell(L, T)
        
        # Принудительно обновляем все соты для гарантии корректного отображения
        self.presenter.handle_all_cells_request()
    
    def draw_parallelogram(self, quantities, color=""):
        """Отрисовка параллелограмма"""
        js_array = "[" + ", ".join(
            f"{{L: {q.L}, T: {q.T}}}" for q in quantities
        ) + "]"
        
        if color:
            self.webView.page().runJavaScript(f"field.drawParallelogram({js_array}, '{color}');")
        else:
            self.webView.page().runJavaScript(f"field.drawParallelogram({js_array});")
    
    def clear_parallelogram(self):
        """Очистка параллелограмма"""
        self.webView.page().runJavaScript("field.clearParallelogram();")
    
    def _block_field_operations(self, blocked: bool):
        """Блокировка/разблокировка операций с полем"""
        if blocked:
            self.webView.page().runJavaScript("window.fieldOperationsBlocked = true;")
        else:
            self.webView.page().runJavaScript("window.fieldOperationsBlocked = false;")
    
    # === Обработчики меню ===
    
    def open_group_dialog(self):
        """Открыть диалог системных групп"""
        # Блокируем операции с полем
        self._block_field_operations(True)
        
        # Получаем группы напрямую из модели приложения
        groups = self.app_model.get_all_system_groups()
        dialog = SystemGroupsDialog(groups, self)
        # Передаем ссылку на модель приложения для сохранения изменений
        dialog.app_model = self.app_model
        
        try:
            result = dialog.exec_()
            # После закрытия диалога обновляем отображение сот
            if result == dialog.Accepted:
                self.presenter.handle_all_cells_request()
        finally:
            # Разблокируем операции с полем
            self._block_field_operations(False)
    
    def open_law_group_dialog(self):
        """Открыть диалог групп законов"""
        # Блокируем операции с полем
        self._block_field_operations(True)
        
        try:
            # Получаем группы законов напрямую из модели приложения
            law_groups = self.app_model.get_all_law_groups()
            dialog = LawGroupSettingsDialog(law_groups, self)
            # Передаем ссылку на модель приложения для сохранения изменений
            dialog.app_model = self.app_model
            dialog.exec_()
        finally:
            # Разблокируем операции с полем
            self._block_field_operations(False)
    
    def load_json_dialog(self):
        """Загрузить JSON проект"""
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить JSON проект", "", "JSON (*.json)")
        if path:
            # Создаем временный сервис для совместимости
            class TempService:
                def __init__(self, app_model):
                    self.app_model = app_model
                
                @property
                def system_groups(self):
                    return self.app_model.get_all_system_groups()
                
                @property
                def law_groups(self):
                    return self.app_model.get_all_law_groups()
            
            temp_service = TempService(self.app_model)
            file_service = FileService(temp_service, temp_service.law_groups)
            file_service.load_json_file(path, parent=self)
    
    def save_json_dialog(self):
        """Сохранить JSON проект"""
        class TempService:
            def __init__(self, app_model):
                self.app_model = app_model
            
            @property
            def system_groups(self):
                return self.app_model.get_all_system_groups()
            
            @property
            def law_groups(self):
                return self.app_model.get_all_law_groups()
        
        temp_service = TempService(self.app_model)
        file_service = FileService(temp_service, temp_service.law_groups)
        file_service.save_to_file(parent=self)
    
    def save_json_as_dialog(self):
        """Сохранить как JSON проект"""
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "JSON (*.json)")
        if path:
            class TempService:
                def __init__(self, app_model):
                    self.app_model = app_model
                
                @property
                def system_groups(self):
                    return self.app_model.get_all_system_groups()
                
                @property
                def law_groups(self):
                    return self.app_model.get_all_law_groups()
            
            temp_service = TempService(self.app_model)
            file_service = FileService(temp_service, temp_service.law_groups)
            file_service.save_to_file(path, parent=self)
    
    def zoom_in(self):
        """Приблизить"""
        self.adjust_zoom(1.1)
    
    def zoom_out(self):
        """Отдалить"""
        self.adjust_zoom(0.9)
    
    def adjust_zoom(self, factor):
        """Настроить масштаб"""
        self.webView.page().runJavaScript("""
            (function() {
                let current = field.getZoom();
                let updated = Math.min(Math.max(current * %f, 0.3), 5.0);
                field.setZoom(updated);
            })();
        """ % factor)
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.information(self, "О программе",
                                """
                    <b>Система "Физические Величины и Закономерности" (ФВиЗ)</b><br>
                    © 2024–2025<br><br>
                    Разработка: <b>Вайсман И.И.</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Email: dentalon599@gmail.com<br>
                    Автор ФВиЗ: <b>Чуев В.М.</b> &nbsp;&nbsp;&nbsp;&nbsp; Email: chuev@mail.ru<br><br>
                    Программа — <b>ФВиЗ 2.0 (FViZ 2.0)</b>
                    """)
    
    # === Drag and Drop ===
    
    def dragEnterEvent(self, event):
        """Обработка начала перетаскивания"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.json'):
                    event.accept()
                    return
        event.ignore()
    
    def dropEvent(self, event):
        """Обработка завершения перетаскивания"""
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.json'):
                class TempService:
                    def __init__(self, app_model):
                        self.app_model = app_model
                    
                    @property
                    def system_groups(self):
                        return self.app_model.get_all_system_groups()
                    
                    @property
                    def law_groups(self):
                        return self.app_model.get_all_law_groups()
                
                temp_service = TempService(self.app_model)
                file_service = FileService(temp_service, temp_service.law_groups)
                file_service.load_json_file(path, parent=self)
                return
