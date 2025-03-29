from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog, QMessageBox, QMenu
from PyQt5.QtWebChannel import QWebChannel
from views.physical_web_view import PhysicalWebEngineView
from backend.controller import Backend
from PyQt5.QtGui import QIcon, QKeySequence
# from views.law_group_settings_dialog import LawGroupSettingsDialog
from views.system_groups_dialog import SystemGroupsDialog
from services.file_service import FileService
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        super().__init__()

        self.setWindowTitle("FViZ 2.0")
        self.setGeometry(100, 100, 2000, 1400)

        self.container = QWidget()
        self.layout = QVBoxLayout()

        self.webView = PhysicalWebEngineView()
        self.layout.addWidget(self.webView)

        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Backend
        self.backend = Backend(self.webView)
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)
        self.webView.page().setWebChannel(self.channel)

        self.webView.setHtml(open("canvas/canvas.html", encoding="utf-8").read())
        self.webView.page().loadFinished.connect(self.initWebChannel)

        self.backend.updateCell.connect(self.sendToJS)

        self.init_menu()

        # Drag and Drop поддержка
        self.setAcceptDrops(True)

    def initWebChannel(self):
        self.webView.page().runJavaScript("""
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyqtObject = channel.objects.backend;
            });
        """)

    def sendToJS(self, message):
        self.webView.page().runJavaScript(f'alert("{message}");')

    def init_menu(self):
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
        # export_action.triggered.connect(lambda: self.webView.page().runJavaScript("exportVisibleCanvasImage();"))
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

    def open_group_dialog(self):
        dialog = SystemGroupsDialog(self.backend.service.system_groups, self)
        dialog.exec_()

    def open_law_group_dialog(self):
        pass
        # dialog = LawGroupSettingsDialog(self.backend.service.law_groups, self)
        # dialog.exec_()

    def load_json_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить JSON проект", "", "JSON (*.json)")
        if path:
            service = FileService(self.backend.service, self.backend.service.law_groups)
            service.load_json_file(path, parent=self)

    def save_json_dialog(self):
        service = FileService(self.backend.service, self.backend.service.law_groups)
        service.save_to_file(parent=self)

    def zoom_in(self):
        self.adjust_zoom(1.1)

    def zoom_out(self):
        self.adjust_zoom(0.9)

    def adjust_zoom(self, factor):
        self.webView.page().runJavaScript("""
            (function() {
                let current = field.getZoom();
                let updated = Math.min(Math.max(current * %f, 0.3), 5.0);
                field.setZoom(updated);
            })();
        """ % factor)

    def show_about(self):
        QMessageBox.information(self, "О программе",
                                """
                    <b>Система "Физические Величины и Закономерности" (ФВиЗ)</b><br>
                    © 2024–2025<br><br>
                    Разработка: <b>Вайсман И.И.</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Email: dentalon599@gmail.com<br>
                    Автор ФВиЗ: <b>Чуев В.М.</b> &nbsp;&nbsp;&nbsp;&nbsp; Email: chuev@mail.ru<br><br>
                    Программа — <b>ФВиЗ 2.0 (FViZ 2.0)</b>
                    """)

    def save_json_as_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "JSON (*.json)")
        if path:
            service = FileService(self.backend.service, self.backend.service.law_groups)
            service.save_to_file(path, parent=self)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.json'):
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.json'):
                service = FileService(self.backend.service, self.backend.service.law_groups)
                service.load_json_file(path, parent=self)
                return