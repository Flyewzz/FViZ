from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QHBoxLayout, QWidget
from PyQt5.QtGui import QColor, QPalette


class EditCellDialog(QDialog):
    """Диалоговое окно для редактирования соты"""

    def __init__(self, backend, L, T, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать соту")
        self.backend = backend
        self.L = L
        self.T = T

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

        print(self.cell)
        if not self.cell:
            self.close()
            return

        # print(self.cell)
        # 🔹 Поля для ввода данных
        self.name_input = QLineEdit(self.cell.name)
        self.symbol_input = QLineEdit(self.cell.symbol)
        self.unit_input = QLineEdit(self.cell.unit)
        self.value_c_input = QLineEdit(self.cell.value_c)

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
        self.updateGroupColor(self.cell.group.color)

        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("Системная группа:"))
        group_layout.addWidget(self.group_selector)
        group_layout.addWidget(self.color_preview)

        layout.addLayout(group_layout)

        for group in self.backend.system_groups:
            self.group_selector.addItem(group.name, group)
            if group == self.cell.group:
                self.group_selector.setCurrentIndex(self.group_selector.count() - 1)

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

        # 🔹 Отправляем изменения в Backend
        self.backend.applyEditCellChanges(self.L, self.T, new_name, new_symbol, new_unit, new_value_c, selected_group)
        self.accept()