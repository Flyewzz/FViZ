import json

from PyQt5.QtCore import QVariant, QUrl
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QPushButton, QWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from models.law import Law


class LawDialog(QDialog):
    def __init__(self, backend, selected_items: QVariant, parent=None):
        super().__init__(parent)

        print('selected_items', [it.name for it in selected_items])

        self.setWindowTitle("Добавить закон")
        self.backend = backend
        self.selected_items = selected_items

        layout = QVBoxLayout()

        # --- Название, описание, формула ---
        self.name_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.formula_input = QLineEdit()
        self.formula_view = QWebEngineView(self)
        self.formula_view.setMinimumHeight(200)

        layout.addWidget(QLabel("Название закона:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(QLabel("Формула (в формате KaTeX):"))
        layout.addWidget(self.formula_input)
        layout.addWidget(self.formula_view)

        # --- Параллелограмм: a * b = c * d ---
        a, b, c, d = selected_items  # список из 4 величин
        self.eq_widget = QWidget()
        eq_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel(b.name))
        row1.addWidget(QLabel("*"))
        row1.addWidget(QLabel(d.name))

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("="))

        row3 = QHBoxLayout()
        row3.addWidget(QLabel(a.name))
        row3.addWidget(QLabel("*"))
        row3.addWidget(QLabel(c.name))

        eq_layout.addLayout(row1)
        eq_layout.addLayout(row2)
        eq_layout.addLayout(row3)
        self.eq_widget.setLayout(eq_layout)

        layout.addWidget(QLabel("Выражение:"))
        layout.addWidget(self.eq_widget)

        # --- Группа закона ---
        self.group_selector = QComboBox()
        for group in backend.law_groups:  # предполагаем, что список групп законов доступен здесь
            self.group_selector.addItem(group.name, group)
        layout.addWidget(QLabel("Группа закона"))
        layout.addWidget(self.group_selector)

        # --- Кнопки ---
        button_layout = QHBoxLayout()
        save_btn = QPushButton("✅ Добавить")
        cancel_btn = QPushButton("❌ Отмена")
        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # --- Обновление формулы ---
        self.formula_input.textChanged.connect(self.update_preview)
        self.update_preview()

    def update_preview(self):
        latex = self.formula_input.text()
        escaped = latex.replace("\\", "\\\\").replace('"', '\\"')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="qrc:/res/css/katex.min.css">
            <script src="qrc:/res/js/katex.min.js"></script>
        </head>
        <body>
            <div id="preview_formula" style="text-align:center;font-size:24px;color:black;margin-top:20px;">(загрузка...)</div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    try {{
                        katex.render("{escaped}", document.getElementById("preview_formula"));
                    }} catch (e) {{
                        document.getElementById("preview_formula").innerText = "❌ Ошибка в формуле";
                    }}
                }});
            </script>
        </body>
        </html>
        """

        self.formula_view.setHtml(html)

    def save(self):
        group = self.group_selector.currentData()
        law = Law(
            name=self.name_input.text(),
            description=self.desc_input.text(),
            formula=self.formula_input.text(),
            variables=[q.name for q in self.selected_items],
            group=group
        )
        group.laws.append(law)
        QMessageBox.information(self, "✅", "Закон добавлен!")
        self.accept()