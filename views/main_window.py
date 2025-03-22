from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
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

    def initWebChannel(self):
        self.webView.page().runJavaScript("""
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyqtObject = channel.objects.backend;
            });
        """)

        self.backend.updateCell.connect(self.sendToJS)

    def sendToJS(self, message):
        self.webView.page().runJavaScript(f'alert("{message}");')
