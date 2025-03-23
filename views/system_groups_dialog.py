from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QColorDialog, QLineEdit, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class SystemGroupsDialog(QDialog):
    def __init__(self, groups, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Системные группы ФВ")
        self.setMinimumSize(500, 400)

        self.groups = groups  # список SystemGroup
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Название", "Цвет", "G", "k"])
        self.layout.addWidget(self.table)

        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить")
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)

        self.layout.addLayout(self.btn_layout)

        self.add_btn.clicked.connect(self.add_group)
        self.edit_btn.clicked.connect(self.edit_group)

        self.load_groups()

    def load_groups(self):
        self.table.setRowCount(0)
        for group in self.groups:
            self.add_group_to_table(group)

    def add_group_to_table(self, group):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(group.name))
        self.table.setItem(row, 1, QTableWidgetItem(group.color))
        self.table.setItem(row, 2, QTableWidgetItem(str(group.G)))
        self.table.setItem(row, 3, QTableWidgetItem(str(group.k)))

    def add_group(self):
        self.edit_group_dialog()

    def edit_group(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите группу.")
            return

        group = self.groups[row]
        self.edit_group_dialog(group, row)

    def edit_group_dialog(self, group=None, index=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать группу" if group else "Добавить группу")
        layout = QVBoxLayout(dialog)

        name_input = QLineEdit(group.name if group else "")
        color_btn = QPushButton()
        G_input = QLineEdit(str(group.G if group else ""))
        k_input = QLineEdit(str(group.k if group else ""))

        color_btn.setStyleSheet(f"background-color: {group.color}" if group else "")
        color = QColor(group.color if group else "#ffffff")

        def choose_color():
            nonlocal color
            new_color = QColorDialog.getColor(color, self)
            if new_color.isValid():
                color = new_color
                color_btn.setStyleSheet(f"background-color: {color.name()}")

        color_btn.clicked.connect(choose_color)

        layout.addWidget(QLabel("Название:"))
        layout.addWidget(name_input)
        layout.addWidget(QLabel("Цвет:"))
        layout.addWidget(color_btn)
        layout.addWidget(QLabel("G:"))
        layout.addWidget(G_input)
        layout.addWidget(QLabel("k:"))
        layout.addWidget(k_input)

        btn_save = QPushButton("Сохранить")
        layout.addWidget(btn_save)

        def save():
            try:
                G = int(G_input.text())
                k = int(k_input.text())
                name = name_input.text()
                if not name:
                    raise ValueError("Название не может быть пустым")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))
                return

            if group:
                group.name = name
                group.color = color.name()
                group.G = G
                group.k = k
                self.update_table_row(index, group)
            else:
                from models.system_group import SystemGroup
                new_group = SystemGroup(name, color.name(), G, k)
                self.groups.append(new_group)
                self.add_group_to_table(new_group)

            dialog.accept()

        btn_save.clicked.connect(save)
        dialog.exec_()

    def update_table_row(self, row, group):
        self.table.setItem(row, 0, QTableWidgetItem(group.name))
        self.table.setItem(row, 1, QTableWidgetItem(group.color))
        self.table.setItem(row, 2, QTableWidgetItem(str(group.G)))
        self.table.setItem(row, 3, QTableWidgetItem(str(group.k)))