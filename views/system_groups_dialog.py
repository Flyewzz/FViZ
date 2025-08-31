from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QListWidget, QListWidgetItem, QWidget, QLabel, QFormLayout, QLineEdit, QColorDialog
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from services.utils import is_group_name_used


class SystemGroupsDialog(QDialog):
    def __init__(self, groups, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Системные группы ФВ")
        self.setMinimumSize(600, 500)

        self.groups = groups  # список SystemGroup
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
        info_label = QLabel(f"G = {group.G},   k = {group.k}")
        info_label.setFont(QFont("Arial", 11))
        info_label.setStyleSheet("color: gray")

        text_layout = QVBoxLayout()
        text_layout.addWidget(name_label)
        text_layout.addWidget(info_label)

        layout.addWidget(color_box)
        layout.addLayout(text_layout)
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
        from models.system_group import SystemGroup
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать группу" if group else "Добавить группу")
        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        name_input = QLineEdit(group.name if group else "")
        G_input = QLineEdit(str(group.G if group else ""))
        k_input = QLineEdit(str(group.k if group else ""))

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
        form_layout.addRow("G:", G_input)
        form_layout.addRow("k:", k_input)

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

            try:
                G = int(G_input.text())
                k = int(k_input.text())
            except Exception:
                QMessageBox.warning(dialog, "Ошибка", "G и k должны быть целыми числами")
                return

            if is_group_name_used(self.groups, name, exclude=group):
                QMessageBox.warning(dialog, "Ошибка", f"Системная группа с именем '{name}' уже существует.")
                return

            color_changed = False

            if group:
                color_changed = group.color != color.name()
                group.name = name
                group.color = color.name()
                group.G = G
                group.k = k
                self.load_groups()

                # 🔁 Обновляем цвет сот, если цвет изменился
                if color_changed and hasattr(self.parent(), 'backend'):
                    for (L, T), cell in self.parent().backend.service.get_visible_cells().items():
                        if cell.group == group:
                            self.parent().backend.service.update_web_cell(L, T, cell)
            else:
                new_group = SystemGroup(name, color.name(), G, k)
                self.groups.append(new_group)
                self.load_groups()

            dialog.accept()

        def save_and_update_backend():
            name = name_input.text().strip()
            if not name:
                return

            try:
                G = int(G_input.text())
                k = int(k_input.text())
            except Exception:
                QMessageBox.warning(dialog, "Ошибка", "G и k должны быть целыми числами")
                return

            if is_group_name_used(self.groups, name, exclude=group):
                QMessageBox.warning(dialog, "Ошибка", f"Системная группа с именем '{name}' уже существует.")
                return

            try:
                if group:
                    # Обновляем существующую группу
                    if hasattr(self.parent(), 'app_model'):
                        # Обновляем через модель приложения
                        self.parent().app_model.update_group_properties(
                            group.id, {'name': name, 'color': color.name(), 'G': G, 'k': k}
                        )
                    group.name = name
                    group.color = color.name()
                    group.G = G
                    group.k = k
                    self.groups = self.parent().app_model.get_all_system_groups() if hasattr(self.parent(), 'app_model') else self.groups
                else:
                    # Создаем новую группу через модель приложения
                    if hasattr(self.parent(), 'app_model'):
                        new_id = f"group_{len(self.groups) + 1}"
                        self.parent().app_model.create_system_group(new_id, name, color.name(), G, k)
                        self.groups = self.parent().app_model.get_all_system_groups()
                    else:
                        new_group = SystemGroup(name, color.name(), G, k)
                        self.groups.append(new_group)
            except ValueError as e:
                QMessageBox.warning(dialog, "Ошибка", str(e))
                return

            self.load_groups()
            dialog.accept()

        # Заменяем save на save_and_update_backend
        btn_save.clicked.connect(save_and_update_backend)
        btn_cancel.clicked.connect(dialog.reject)
        dialog.exec_()

    def delete_group(self):
        """Удалить выбранную группу"""
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите группу для удаления.")
            return

        group = item.data(Qt.UserRole)
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить группу '{group.name}'?\n\n"
            "Это действие также удалит все физические величины, принадлежащие этой группе.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # Удаляем через модель приложения если доступна
            if hasattr(self.parent(), 'app_model'):
                # Сначала удаляем все физические величины этой группы
                all_quantities = self.parent().app_model.get_all_quantities()
                quantities_to_delete = []
                
                for (L, T), quantities_list in all_quantities.items():
                    for quantity in quantities_list:
                        if quantity.group_id == group.id:
                            quantities_to_delete.append((L, T, group.id))
                
                # Удаляем физические величины
                for L, T, group_id in quantities_to_delete:
                    try:
                        self.parent().app_model.delete_physical_quantity(L, T, group_id)
                    except Exception as e:
                        print(f"Ошибка удаления физической величины: {e}")
                
                # Удаляем саму группу
                self.parent().app_model.system_group_manager.delete_group(group.id)
                self.groups = self.parent().app_model.get_all_system_groups()
            else:
                # Fallback для старой архитектуры
                self.groups.remove(group)
            
            self.load_groups()
            QMessageBox.information(self, "Успех", f"Группа '{group.name}' успешно удалена.")
            
            # Обновляем отображение на поле
            if hasattr(self.parent(), 'presenter') and self.parent().presenter:
                self.parent().presenter.handle_all_cells_request()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить группу: {e}")
