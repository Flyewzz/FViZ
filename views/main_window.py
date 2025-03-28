from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog
from PyQt5.QtWebChannel import QWebChannel
from views.physical_web_view import PhysicalWebEngineView
from backend.controller import Backend


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt WebView + Konva")
        self.setGeometry(100, 100, 2000, 1400)

        self.container = QWidget()
        self.layout = QVBoxLayout()

        self.webView = PhysicalWebEngineView()
        self.layout.addWidget(self.webView)

        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Создание backend-контроллера и канала
        self.backend = Backend(self.webView)

        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        self.webView.page().setWebChannel(self.channel)

        # Загружаем HTML
        self.webView.setHtml(open("canvas/canvas.html", encoding="utf-8").read())

        # Устанавливаем канал после загрузки страницы
        self.webView.page().loadFinished.connect(self.initWebChannel)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")

        load_json_action = QAction("Импортировать JSON", self)
        load_json_action.triggered.connect(self.load_json_dialog)
        file_menu.addAction(load_json_action)

        settings_menu = menu_bar.addMenu("Настройки")
        group_action = QAction("Системные группы ФВ", self)
        group_action.triggered.connect(self.open_group_dialog)
        settings_menu.addAction(group_action)

    def open_group_dialog(self):
        from views.system_groups_dialog import SystemGroupsDialog
        dialog = SystemGroupsDialog(self.backend.service.system_groups, self)
        dialog.exec_()

    def initWebChannel(self):
        self.webView.page().runJavaScript("""
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyqtObject = channel.objects.backend;
            });
        """)

        self.backend.updateCell.connect(self.sendToJS)

    def sendToJS(self, message):
        self.webView.page().runJavaScript(f'alert("{message}");')

    def load_json_dialog(self):
        from services.file_service import FileService
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить JSON проект", "", "JSON (*.json)")
        if path:
            service = FileService(self.backend.service, self.backend.service.law_groups)
            service.load_json_file(path, parent=self)