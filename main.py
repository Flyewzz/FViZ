from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QPoint
from PyQt5.QtGui import QCursor
from physical_web_view import PhysicalWebEngineView
from system_group import SystemGroup
from edit_cell_group import EditCellDialog
from physical_value import PhysicalQuantity
import sys
import res

class Backend(QObject):
    """ Класс для обработки событий из WebView в PyQt """

    updateCell = pyqtSignal(str)  # Сигнал, отправляющий данные в WebView

    def __init__(self, webView):
        super().__init__()
        self.webView = webView  # Store a reference to the webView

        # 🔹 Создаем тестовые системные группы
        self.system_groups = [
            SystemGroup("Группа 1", "#73ecfa", G=1, k=1),
            SystemGroup("Группа 2", "#fa73ec", G=2, k=2),
            SystemGroup("Группа 3", "#ecfa73", G=3, k=3)
        ]

        # 🔹 Заполняем сотами (примерные тестовые данные)
        self.cells = {
            (-2, -2): PhysicalQuantity("Частота", "f", "Гц", "T^{-1}", self.system_groups[0], -2, -2),
            (-2, -1): PhysicalQuantity("Ускорение", "a", "м/с²", "L T^{-2}", self.system_groups[0], -2, -1),
            (-2, 0): PhysicalQuantity("Давление", "p", "Па", "M L^{-1} T^{-2}", self.system_groups[0], -2, 0),
            (-2, 1): PhysicalQuantity("Мощность", "P", "Вт", "M L^2 T^{-3}", self.system_groups[0], -2, 1),
            (-2, 2): PhysicalQuantity("Магнитный поток", "Φ", "Вб", "M L^2 T^{-2} A^{-1}", self.system_groups[0], -2,
                                      2),

            (-1, -2): PhysicalQuantity("Вязкость", "η", "Па·с", "M L^{-1} T^{-1}", self.system_groups[0], -1, -2),
            (-1, -1): PhysicalQuantity("Сила", "F", "Н", "M L T^{-2}", self.system_groups[0], -1, -1),
            (-1, 0): PhysicalQuantity("Плотность", "ρ", "кг/м³", "M L^{-3}", self.system_groups[0], -1, 0),
            (-1, 1): PhysicalQuantity("Работа", "A", "Дж", "M L^2 T^{-2}", self.system_groups[0], -1, 1),
            (-1, 2): PhysicalQuantity("Поток энергии", "q", "Вт/м²", "M T^{-3}", self.system_groups[0], -1, 2),

            (0, -2): PhysicalQuantity("Скорость", "v", "м/с", "L T^{-1}", self.system_groups[1], 0, -2),
            (0, -1): PhysicalQuantity("Угловая скорость", "ω", "рад/с", "T^{-1}", self.system_groups[1], 0, -1),
            (0, 0): PhysicalQuantity("Масса", "m", "кг", "M", self.system_groups[1], 0, 0),
            (0, 1): PhysicalQuantity("Энергия", "E", "Дж", "M L^2 T^{-2}", self.system_groups[1], 0, 1),
            (0, 2): PhysicalQuantity("Сила тока", "I", "А", "I", self.system_groups[1], 0, 2),

            (1, -2): PhysicalQuantity("Импульс", "p", "кг·м/с", "M L T^{-1}", self.system_groups[2], 1, -2),
            (1, -1): PhysicalQuantity("Момент импульса", "L", "кг·м²/с", "M L^2 T^{-1}", self.system_groups[2], 1, -1),
            (1, 0): PhysicalQuantity("Объём", "V", "м³", "L^3", self.system_groups[2], 1, 0),
            (1, 1): PhysicalQuantity("Эл. напряжение", "U", "В", "M L^2 T^{-3} A^{-1}", self.system_groups[2], 1, 1),
            (1, 2): PhysicalQuantity("Электр. заряд", "q", "Кл", "A T", self.system_groups[2], 1, 2),

            (2, -2): PhysicalQuantity("Сопротивление", "R", "Ом", "M L^2 T^{-3} A^{-2}", self.system_groups[2], 2, -2),
            (2, -1): PhysicalQuantity("Электр. ёмкость", "C", "Ф", "M^{-1} L^{-2} T^4 A^2", self.system_groups[2], 2,
                                      -1),
            (2, 0): PhysicalQuantity("Длина", "l", "м", "L", self.system_groups[2], 2, 0),
            (2, 1): PhysicalQuantity("Температура", "T", "K", "Θ", self.system_groups[2], 2, 1),
            (2, 2): PhysicalQuantity("Кол-во вещества", "n", "моль", "N", self.system_groups[2], 2, 2),
        }

        for coords, cell in self.cells.items():
            cell.group.add_quantity(cell)

        self.sendAllCellsToWebView()

    @pyqtSlot(str)
    def handleCellClick(self, cellData):
        print(f"Клик по соте: {cellData}")  # Выводим в консоль
        self.updateCell.emit(f"Выбрана сота {cellData}")  # Отправляем обратно в WebView

    @pyqtSlot(int, int, int, int)
    def showContextMenu(self, L, T, x, y):
        """ Метод вызывается при ПКМ на соте """
        print(f"ПКМ на соте с координатами: L={L}, T={T}, позиция: x={x}, y={y}")

        # Показываем контекстное меню
        menu = QMenu()
        edit_action = QAction("Редактировать", menu)
        delete_action = QAction("Удалить", menu)
        replace_action = QAction("Заменить", menu)

        edit_action.triggered.connect(lambda: self.editCell(L, T))
        delete_action.triggered.connect(lambda: self.deleteCell(L, T))
        replace_action.triggered.connect(lambda: self.replaceCell(L, T))

        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.addAction(replace_action)

        # 🔹 Adjust final menu position
        adjusted_x = x  # `x` is already in global coordinates
        adjusted_y = y  # `y` is already in global coordinates

        # # 🔹 Convert web page (x, y) to **global** screen coordinates
        # webView_offset = self.webView.mapToGlobal(QPoint(0, 0))  # Top-left corner of WebView
        # adjusted_x = webView_offset.x() + x
        # adjusted_y = webView_offset.y() + y

        print(f"Adjusted global position: x={adjusted_x}, y={adjusted_y}")

        # 🖱 Show the menu at the **exact** right-click position
        menu.exec_(QPoint(adjusted_x, adjusted_y))

    @pyqtSlot(int, int)
    def editCell(self, L, T):
        """Открывает диалог редактирования соты"""
        print(f"Редактируем соту: L={L}, T={T}")

        app = QApplication.instance()
        dialog = EditCellDialog(self, L, T, parent=app.activeWindow())
        dialog.exec_()

    @pyqtSlot(int, int)
    def deleteCell(self, L, T):
        """Удаляет физическую величину и заменяет её другой (если возможно)"""
        print(f"Удаляем физ. величину на соте: L={L}, T={T}")

        # 🔹 Найти текущую физ. величину
        current_quantity = None
        current_group = None

        for group in self.system_groups:
            current_quantity = group.get_quantity(L, T)
            if current_quantity:
                current_group = group
                break

        if not current_quantity:
            print("❌ Не найдено физ. величины для удаления")
            return

        # 🔹 Удалить из группы
        current_group.remove_quantity(L, T)

        # 🔹 Найти замену в той же группе
        new_quantity = current_group.get_next_quantity(L, T)

        if new_quantity:
            print(f"🔄 Заменяем удаленную величину на: {new_quantity.name}")
            self.updateWebViewCell(L, T, new_quantity)
        else:
            print("🗑 Полностью удаляем соту")
            self.removeWebViewCell(L, T)

    @pyqtSlot(int, int)
    def replaceCell(self, L, T):
        """Заменяет физическую величину в данных и обновляет WebView"""
        print(f"Заменяем физ. величину на соте: L={L}, T={T}")

        # 🔹 Найти текущую физическую величину
        current_quantity = None
        current_group = None

        for group in self.system_groups:
            current_quantity = group.get_quantity(L, T)
            if current_quantity:
                current_group = group
                break

        if not current_quantity:
            print("❌ Не найдено физ. величины для замены")
            return

        # 🔹 Найти замену среди других системных групп
        for group in self.system_groups:
            if group != current_group:
                new_quantity = group.get_quantity(L, T)
                if new_quantity:
                    break
        else:
            print("❌ Нет заменяемых величин")
            return

        # 🔹 Обновить данные
        current_group.remove_quantity(L, T)
        new_quantity.group.add_quantity(new_quantity)

        # 🔹 Обновить WebView
        self.updateWebViewCell(L, T, new_quantity)

    @pyqtSlot()
    def sendAllCellsToWebView(self):
        print("📡 JS запросил отправку сот")

        script = "\n".join(
            [
                f"field.createCell({L}, {T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.color}');"
                for (L, T), cell in self.cells.items()
            ]
        )

        self.webView.page().runJavaScript(f"""
                ensureFieldExists(() => {{
                    {script}
                }});
            """)

    def applyEditCellChanges(self, L, T, new_name, new_symbol, new_unit, new_value_c, new_group):
        """Обновляет данные соты или перемещает её в новую системную группу"""
        if (L, T) not in self.cells:
            print(f"❌ Сота (L={L}, T={T}) не найдена")
            return

        current_cell = self.cells[L, T]

        # 🔹 Если группа изменилась, перемещаем соту
        if current_cell.group != new_group:
            print(f"🔄 Перемещаем соту (L={L}, T={T}) в {new_group.name}")
            del self.cells[(L, T)]
            new_cell = PhysicalQuantity(new_name, new_symbol, new_unit, new_value_c, new_group, L, T)
            self.cells[(L, T)] = new_cell
        else:
            print(f"✏ Обновляем данные соты (L={L}, T={T}) в {new_group.name}")
            current_cell.name = new_name
            current_cell.symbol = new_symbol
            current_cell.unit = new_unit
            current_cell.value_c = new_value_c

        # 🔹 Обновляем WebView
        self.updateWebViewCell(L, T, self.cells[(L, T)])

    def createWebViewCell(self, L, T, cell):
        """Создает соту в WebView"""
        self.webView.page().runJavaScript(f"""
            window.field.createCell({L}, {T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.color}');
        """)

    def updateWebViewCell(self, L, T, cell):
        """Обновляет соту в WebView"""
        self.webView.page().runJavaScript(f"""
            window.field.updateCell({L}, {T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.color}');
        """)

    def removeWebViewCell(self, L, T):
        """Удаляет соту из WebView"""
        self.webView.page().runJavaScript(f"field.removeCell({L}, {T});")



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



        self.backend = Backend(self.webView)

        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        self.webView.page().setWebChannel(self.channel)

        # Загружаем HTML-файл
        self.webView.setHtml(open("canvas/canvas.html", encoding="utf-8").read())

        # self.webView.setUrl(QUrl("qrc:///qwebchannel.js"))

        # self.webView.setContextMenuPolicy(Qt.NoContextMenu)

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