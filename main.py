from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl
import sys
import res

class Backend(QObject):
    """ Класс для обработки событий из WebView в PyQt """

    updateCell = pyqtSignal(str)  # Сигнал, отправляющий данные в WebView

    @pyqtSlot(str)
    def handleCellClick(self, cellData):
        print(f"Клик по соте: {cellData}")  # Выводим в консоль
        self.updateCell.emit(f"Выбрана сота {cellData}")  # Отправляем обратно в WebView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt WebView + Konva")
        self.setGeometry(100, 100, 1200, 800)

        self.container = QWidget()
        self.layout = QVBoxLayout()

        self.webView = QWebEngineView()
        self.layout.addWidget(self.webView)

        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.channel = QWebChannel()
        self.backend = Backend()
        self.channel.registerObject("backend", self.backend)

        self.webView.page().setWebChannel(self.channel)

        # Загружаем HTML-файл
        self.webView.setHtml(open("canvas/canvas.html", encoding="utf-8").read())

        # self.webView.setUrl(QUrl("qrc:///qwebchannel.js"))

        # Ждём загрузки страницы и подключаем канал
        self.webView.page().loadFinished.connect(self.initWebChannel)

    def initWebChannel(self):
        self.webView.page().runJavaScript("""
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyqtObject = channel.objects.backend;
            });
        """)

        # Подключаем сигнал, чтобы отправлять данные в JS
        self.backend.updateCell.connect(self.sendToJS)

    def sendToJS(self, message):
        """ Отправка данных из Python в WebView (JS) """
        self.webView.page().runJavaScript(f'alert("{message}");')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())