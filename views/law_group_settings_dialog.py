from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QListWidget, QListWidgetItem, QWidget, QLabel, QFormLayout, QLineEdit, QColorDialog
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from services.utils import is_group_name_used


class LawGroupSettingsDialog(QDialog):
    def __init__(self, groups, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Параметры группы законов")
        self.setMinimumSize(600, 500)

        self.groups = groups  # список LawGroup
        self.layout = QVBoxLayout(self)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.edit_group_by_item)
        self.layout.addWidget(self.list)

        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить группу")
        self.edit_btn = QPushButton("✏️ Редактировать выбранную")
        self.delete_btn = QPushButton("🗑️ Удалить выбранную")
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(self.btn_layout)

        self.add_btn.clicked.connect(self.add_group)
        self.edit_btn.clicked.connect(self.edit_group)
        self.delete_btn.clicked.connect(self.delete_group)

        self.load_groups()

    def load_groups(self):
        self.list.clear()
        for group in self.groups:
            self.add_group_to_list(group)

    def add_group_to_list(self, group):
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)

        color_box = QLabel()
        color_box.setFixedSize(20, 20)
        color_box.setStyleSheet(f"background-color: {group.color}; border-radius: 10px; border: 1px solid black;")

        name_label = QLabel(group.name)
        name_label.setFont(QFont("Arial", 13, QFont.Bold))

        layout.addWidget(color_box)
        layout.addWidget(name_label)
        layout.addStretch()

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.list.addItem(item)
        self.list.setItemWidget(item, widget)
        item.setData(Qt.UserRole, group)

    def add_group(self):
        self.edit_group_dialog()

    def edit_group(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите группу.")
            return

        group = item.data(Qt.UserRole)
        index = self.groups.index(group)
        self.edit_group_dialog(group, index)

    def edit_group_by_item(self, item):
        group = item.data(Qt.UserRole)
        index = self.groups.index(group)
        self.edit_group_dialog(group, index)

    def edit_group_dialog(self, group=None, index=None):
        from models.law_group import LawGroup

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать группу" if group else "Добавить группу")
        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        name_input = QLineEdit(group.name if group else "")

        color = QColor(group.color if group else "#ffffff")
        color_btn = QPushButton()
        color_btn.setStyleSheet(f"background-color: {color.name()}")
        color_btn.setFixedSize(40, 20)

        def choose_color():
            nonlocal color
            new_color = QColorDialog.getColor(color, self)
            if new_color.isValid():
                color = new_color
                color_btn.setStyleSheet(f"background-color: {color.name()}")

        color_btn.clicked.connect(choose_color)

        color_layout = QHBoxLayout()
        color_layout.addWidget(color_btn)
        color_widget = QWidget()
        color_widget.setLayout(color_layout)

        form_layout.addRow("Название группы:", name_input)
        form_layout.addRow("Цвет:", color_widget)

        layout.addLayout(form_layout)

        btn_save = QPushButton("Сохранить")
        btn_cancel = QPushButton("Отмена")
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

        def validate():
            btn_save.setEnabled(bool(name_input.text().strip()))

        name_input.textChanged.connect(validate)
        validate()

        def save():
            name = name_input.text().strip()
            if not name:
                return

            if is_group_name_used(self.groups, name, exclude=group):
                QMessageBox.warning(dialog, "Ошибка", f"Группа с именем '{name}' уже существует.")
                return

            if group:
                # Обновляем существующую группу
                group.name = name
                group.color = color.name()
                # Сохраняем в модель данных если доступна
                if hasattr(self, 'app_model') and self.app_model:
                    self.app_model.update_law_group(group.id, name, color.name())
                self.load_groups()
            else:
                # Создаем новую группу
                from models.law_group import LawGroup
                import uuid
                new_group = LawGroup(name, color.name())
                new_group.id = str(uuid.uuid4())  # Добавляем ID отдельно
                self.groups.append(new_group)
                # Сохраняем в модель данных если доступна
                if hasattr(self, 'app_model') and self.app_model:
                    self.app_model.create_law_group(new_group.id, name, color.name())
                self.load_groups()

            dialog.accept()

        btn_save.clicked.connect(save)
        btn_cancel.clicked.connect(dialog.reject)
        dialog.exec_()

    def delete_group(self):
        """Удалить выбранную группу законов"""
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите группу для удаления.")
            return

        group = item.data(Qt.UserRole)
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить группу законов '{group.name}'?\n\n"
            "Это действие также удалит все законы, принадлежащие этой группе.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # Удаляем через модель приложения если доступна
            if hasattr(self, 'app_model') and self.app_model:
                self.app_model.delete_law_group(group.id)
                self.groups = self.app_model.get_all_law_groups()
            else:
                # Fallback для старой архитектуры
                self.groups.remove(group)
            
            self.load_groups()
            QMessageBox.information(self, "Успех", f"Группа законов '{group.name}' успешно удалена.")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить группу: {e}")