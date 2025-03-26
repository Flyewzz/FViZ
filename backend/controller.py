# backend/controller.py

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QPoint, QVariant
from PyQt5.QtWidgets import QApplication, QAction, QMenu
from views.cell_edit_dialog import EditCellDialog
from services.cell_service import CellService
from views.laws_dialog import LawDialog


class Backend(QObject):
    updateCell = pyqtSignal(str)

    def __init__(self, webView):
        super().__init__()
        self.webView = webView
        self.service = CellService(webView)

    @pyqtSlot(str)
    def handleCellClick(self, cellData):
        print(f"Клик по соте: {cellData}")
        self.updateCell.emit(f"Выбрана сота {cellData}")

    @pyqtSlot(int, int, QVariant, int, int)
    def showContextMenu(self, L, T, group_name, x, y):
        print(f"ПКМ на соте: L={L}, T={T}, group={group_name}, x={x}, y={y}")
        menu = QMenu()

        if group_name is not None:
            other = self.service.find_quantities_in_other_groups(L, T, group_name)
            if other:
                sub = QMenu("Заменить", menu)
                for q in other:
                    action = QAction(q.name, sub)
                    action.triggered.connect(lambda _, q=q: self.service.replace_cell(L, T, q))
                    sub.addAction(action)
                menu.addMenu(sub)

            edit = QAction("Редактировать", menu)
            delete = QAction("Удалить", menu)
            edit.triggered.connect(lambda: self.editCell(L, T))
            delete.triggered.connect(lambda: self.service.delete_cell(L, T, group_name))
            menu.addAction(edit)
            menu.addAction(delete)

        # Вычисляем, какие группы уже заняты на этих координатах
        used_groups = [
            group
            for group in self.service.get_all_groups()
            if group.get_quantity(L, T) is not None
        ]

        all_groups = self.service.get_all_groups()
        if len(used_groups) != len(all_groups):
            create = QAction("Создать", menu)
            create.triggered.connect(lambda: self.createCellDialog(L, T, used_groups))
            menu.addAction(create)
        menu.exec_(QPoint(x, y))

    @pyqtSlot(int, int, str)
    def onCellSelected(self, L, T, group_name):
        quantity = self.service.get_cell_by_coords(L, T, group_name)
        if quantity:
            self.service.toggle_selection(quantity)
            selected_quantities = self.service.check_parallelogram()
            if selected_quantities:
                self.draw_parallelogram(selected_quantities)
                self.openLawDialog(selected_quantities)

    @pyqtSlot(list)
    def openLawDialog(self, quantities):
        # теперь отображаем форму в Python
        app = QApplication.instance()
        dialog = LawDialog(self.service, quantities, parent=app.activeWindow())
        dialog.show()

    @pyqtSlot(list)
    def draw_parallelogram(self, quantities):
        js_array = "[" + ", ".join(
            f"{{L: {q.L}, T: {q.T}}}" for q in quantities
        ) + "]"

        self.webView.page().runJavaScript(f"field.drawParallelogram({js_array});")

    def createCellDialog(self, L, T, exclude_groups):
        print(f"Создание соты: L={L}, T={T}")
        app = QApplication.instance()

        dialog = EditCellDialog(
            self.service,
            L,
            T,
            parent=app.activeWindow(),
            create_mode=True,
            exclude_groups=exclude_groups,
        )
        dialog.exec_()

    def editCell(self, L, T):
        app = QApplication.instance()
        dialog = EditCellDialog(self.service, L, T, parent=app.activeWindow())
        dialog.exec_()

    @pyqtSlot()
    def sendAllCellsToWebView(self):  # <- Это важно
        print("📡 JS запросил отправку сот")
        cells = self.service.get_all_cells()
        script = "\n".join(
            [
                f"field.createCell({L}, {T}, '{c.name}', '{c.symbol}', '{c.value_c}', '{c.group.name}', '{c.group.color}');"
                for (L, T), c in cells.items()
            ]
        )
        self.webView.page().runJavaScript(f"ensureFieldExists(() => {{ {script} }});")

