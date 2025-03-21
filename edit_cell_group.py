from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QHBoxLayout, QWidget
from PyQt5.QtGui import QColor, QPalette
from physical_value import PhysicalQuantity


class EditCellDialog(QDialog):
    """Диалоговое окно для редактирования соты"""

    def __init__(self, backend, L, T, parent=None, create_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Создание физической величины" if create_mode else "Редактирование физической величины")
        self.backend = backend
        self.L = L
        self.T = T
        self.create_mode = create_mode

        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.cell = None
        # 🔹 Получаем текущие данные соты
        # Вместо self.backend.cells.get((L, T))
        for group in self.backend.system_groups:
            cell = group.get_quantity(L, T)
            if cell:
                self.cell = cell
                break

        if not self.cell and not self.create_mode:
            self.close()
            return

        # 🔹 Поля для ввода данных
        self.name_input = QLineEdit("" if create_mode else self.cell.name)
        self.symbol_input = QLineEdit("" if create_mode else self.cell.symbol)
        self.unit_input = QLineEdit("" if create_mode else self.cell.unit)
        self.value_c_input = QLineEdit("" if create_mode else self.cell.value_c)

        layout.addWidget(QLabel(f"Редактирование соты (L={L}, T={T})"))
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Условное обозначение:"))
        layout.addWidget(self.symbol_input)
        layout.addWidget(QLabel("Единица измерения:"))
        layout.addWidget(self.unit_input)
        layout.addWidget(QLabel("Размерность в СИ:"))
        layout.addWidget(self.value_c_input)

        # 🔹 Выбор системной группы
        self.group_selector = QComboBox()
        self.color_preview = QWidget()  # Виджет для отображения цвета группы

        self.color_preview.setFixedSize(20, 20)

        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("Системная группа:"))
        group_layout.addWidget(self.group_selector)
        group_layout.addWidget(self.color_preview)

        layout.addLayout(group_layout)

        # 🔹 Заполняем селектор
        for group in self.backend.system_groups:
            self.group_selector.addItem(group.name, group)

        # 🔹 Если в режиме редактирования — выбрать текущую группу и показать цвет
        if not self.create_mode and self.cell:
            index = self.group_selector.findData(self.cell.group)
            if index != -1:
                self.group_selector.setCurrentIndex(index)
                self.updateGroupColor(self.cell.group.color)
        else:
            # В режиме создания — выбрать первую группу по умолчанию
            self.group_selector.setCurrentIndex(0)
            self.updateGroupColor(self.group_selector.currentData().color)

        self.group_selector.currentIndexChanged.connect(self.changeGroupColor)
        # 🔹 Кнопка сохранения
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def changeGroupColor(self):
        """Меняет цвет квадратика при смене группы"""
        selected_group = self.group_selector.currentData()
        if selected_group:
            self.updateGroupColor(selected_group.color)

    def updateGroupColor(self, color):
        """Обновляет цвет квадратика рядом с выбором группы"""
        palette = self.color_preview.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.color_preview.setAutoFillBackground(True)
        self.color_preview.setPalette(palette)

    def save_changes(self):
        """Сохранение изменений"""
        selected_group = self.group_selector.currentData()
        new_name = self.name_input.text()
        new_symbol = self.symbol_input.text()
        new_unit = self.unit_input.text()
        new_value_c = self.value_c_input.text()

        if self.create_mode:
            new_cell = PhysicalQuantity(new_name, new_symbol, new_unit, new_value_c, selected_group, self.L, self.T)
            self.backend.cells[(self.L, self.T)] = new_cell
            selected_group.add_quantity(new_cell)
            self.backend.createWebViewCell(self.L, self.T, new_cell)
        else:
            self.backend.applyEditCellChanges(self.L, self.T, new_name, new_symbol, new_unit, new_value_c,
                                              selected_group)

        self.accept()