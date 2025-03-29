# views/edit_cell_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QHBoxLayout, QWidget, \
    QMessageBox
from PyQt5.QtGui import QColor, QPalette
from services.utils import is_quantity_name_used


class EditCellDialog(QDialog):
    """Диалоговое окно для редактирования или создания соты"""

    def __init__(self, backend, L, T, parent=None, create_mode=False, exclude_groups=[]):
        super().__init__(parent)
        self.setWindowTitle("Создать соту" if create_mode else "Редактировать соту")
        self.backend = backend
        self.L = L
        self.T = T
        self.create_mode = create_mode
        self.exclude_groups = exclude_groups

        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.cell = None

        if not self.create_mode:
            self.cell = self.backend.visible_cells.get((L, T))
            if not self.cell:
                self.close()
                return

        self.name_input = QLineEdit("" if self.create_mode else self.cell.name)
        self.symbol_input = QLineEdit("" if self.create_mode else self.cell.symbol)
        self.unit_input = QLineEdit("" if self.create_mode else self.cell.unit)
        self.value_c_input = QLineEdit("" if self.create_mode else self.cell.value_c)

        layout.addWidget(QLabel(f"{'Создание' if create_mode else 'Редактирование'} соты (L={L}, T={T})"))
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Условное обозначение:"))
        layout.addWidget(self.symbol_input)
        layout.addWidget(QLabel("Единица измерения:"))
        layout.addWidget(self.unit_input)
        layout.addWidget(QLabel("Размерность в СИ:"))
        layout.addWidget(self.value_c_input)

        self.group_selector = QComboBox()
        self.color_preview = QWidget()
        self.color_preview.setFixedSize(20, 20)

        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("Системная группа:"))
        group_layout.addWidget(self.group_selector)
        group_layout.addWidget(self.color_preview)
        layout.addLayout(group_layout)

        for group in self.backend.system_groups:
            if len(self.exclude_groups) > 0:
                if group.name.lower() in [
                    g.name.lower() for g in self.exclude_groups
                ]:
                    continue
            self.group_selector.addItem(group.name, group)
            if not create_mode and group == self.cell.group:
                self.group_selector.setCurrentIndex(self.group_selector.count() - 1)

        self.group_selector.currentIndexChanged.connect(self.changeGroupColor)

        # Задать начальный цвет
        self.changeGroupColor()

        save_button = QPushButton("Создать" if self.create_mode else "Сохранить")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def changeGroupColor(self):
        selected_group = self.group_selector.currentData()
        if selected_group:
            palette = self.color_preview.palette()
            palette.setColor(QPalette.Window, QColor(selected_group.color))
            self.color_preview.setAutoFillBackground(True)
            self.color_preview.setPalette(palette)

    def save_changes(self):
        group = self.group_selector.currentData()
        name = self.name_input.text()
        symbol = self.symbol_input.text()
        unit = self.unit_input.text()
        value_c = self.value_c_input.text()

        if is_quantity_name_used(self.backend, name, self.cell if not self.create_mode else None):
            QMessageBox.warning(self, "Ошибка", f"Физическая величина с именем '{name}' уже существует.")
            return

        if self.create_mode:
            from models.physical_value import PhysicalQuantity
            new_cell = PhysicalQuantity(name, symbol, unit, value_c, group, self.L, self.T)
            self.backend.create_cell(new_cell, group, True)
        else:
            self.backend.apply_edit(self.L, self.T, name, symbol, unit, value_c, group)

        self.accept()