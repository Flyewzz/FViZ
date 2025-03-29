# services/file_service.py
import json
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from models.physical_value import PhysicalQuantity
from models.system_group import SystemGroup
from models.law import Law
from models.law_group import LawGroup


class FileService:
    def __init__(self, cell_service, law_groups):
        self.cell_service = cell_service
        self.law_groups = law_groups

    def save_to_file(self, path, parent=None):
        if not path:
            return

        all_cells = self.cell_service.get_all_cells()
        visible_set = {(q.L, q.T, q.group.name) for q in self.cell_service.get_visible_cells().values()}

        data = {
            "cells": [
                q.to_dict(visible=(q.L, q.T, q.group.name) in visible_set)
                for q in all_cells.values()
            ],
            "system_groups": [g.to_dict() for g in self.cell_service.get_all_groups()],
            "law_groups": [g.to_dict() for g in self.law_groups]
        }

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(parent, "✅", "Проект успешно сохранен!")
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_json_file(self, path, parent=None):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.cell_service.clear_all()
            self.law_groups.clear()

            groups_by_name = {}
            for g_data in data.get("system_groups", []):
                g = SystemGroup.from_dict(g_data)
                self.cell_service.add_group(g)
                groups_by_name[g.name] = g

            for q_data in data.get("cells", []):
                g_name = q_data.get("group")
                if g_name == '':
                    continue
                group = groups_by_name.get(g_name)
                if not group:
                    print(f"⚠️ Группа {g_name} не найдена.")
                    continue

                cell = PhysicalQuantity.from_dict(q_data, group)
                visible = q_data.get("visible", False)
                self.cell_service.create_cell(cell, group, visible=visible)

            for lg_data in data.get("law_groups", []):
                group = LawGroup.from_dict(lg_data)
                self.law_groups.append(group)

            self.cell_service.send_all_to_webview()

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось загрузить JSON: {str(e)}")