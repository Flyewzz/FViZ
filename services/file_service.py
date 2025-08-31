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

    def save_to_file(self, path=None, parent=None):
        if not path:
            path, _ = QFileDialog.getSaveFileName(parent, "Сохранить проект", "", "JSON (*.json)")
            if not path:
                return

        # Поддержка новой архитектуры
        if hasattr(self.cell_service, 'app_model'):
            self._save_new_architecture(path, parent)
        else:
            self._save_old_architecture(path, parent)

    def _save_new_architecture(self, path, parent):
        """Сохранение для новой архитектуры"""
        try:
            app_model = self.cell_service.app_model
            
            # Получаем все данные из модели приложения
            system_groups = app_model.get_all_system_groups()
            law_groups = app_model.get_all_law_groups()
            visible_quantities = app_model.get_visible_quantities()
            all_quantities = app_model.get_all_quantities()
            all_laws = app_model.law_manager.law_repo.get_all_laws()
            
            # Формируем данные для сохранения
            data = {
                "system_groups": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "color": g.color,
                        "G": g.G,
                        "k": g.k
                    } for g in system_groups
                ],
                "law_groups": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "color": g.color
                    } for g in law_groups
                ],
                "laws": [
                    {
                        "id": law.id,
                        "name": law.name,
                        "formula": law.formula,
                        "description": law.description,
                        "variables": law.variables,
                        "group_id": law.group_id
                    } for law in all_laws
                ],
                "quantities": [],
                "visible_quantities": []
            }
            
            # Добавляем все физические величины
            for (L, T), quantities_list in all_quantities.items():
                for quantity in quantities_list:
                    data["quantities"].append(quantity.to_dict())
            
            # Добавляем видимые величины (координаты и group_id достаточно для идентификации)
            for (L, T), quantity in visible_quantities.items():
                data["visible_quantities"].append({
                    "L": L,
                    "T": T,
                    "group_id": quantity.group_id
                })
            
            # Сохраняем в файл
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(parent, "✅", "Проект успешно сохранен!")
            
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def _save_old_architecture(self, path, parent):
        """Сохранение для старой архитектуры"""
        try:
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

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(parent, "✅", "Проект успешно сохранен!")
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_json_file(self, path, parent=None):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Поддержка новой архитектуры
            if hasattr(self.cell_service, 'app_model'):
                self._load_new_architecture(data, parent)
            else:
                self._load_old_architecture(data, parent)

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось загрузить JSON: {str(e)}")

    def _load_new_architecture(self, data, parent):
        """Загрузка для новой архитектуры"""
        try:
            app_model = self.cell_service.app_model
            
            # Очищаем все данные
            app_model.clear_all_data()
            
            # Загружаем системные группы
            for g_data in data.get("system_groups", []):
                try:
                    app_model.create_system_group(
                        g_data["id"],
                        g_data["name"],
                        g_data["color"],
                        g_data["G"],
                        g_data["k"]
                    )
                except Exception as e:
                    print(f"Ошибка создания системной группы: {e}")
            
            # Загружаем группы законов
            for lg_data in data.get("law_groups", []):
                try:
                    app_model.create_law_group(
                        lg_data["id"],
                        lg_data["name"],
                        lg_data["color"]
                    )
                except Exception as e:
                    print(f"Ошибка создания группы законов: {e}")
            
            # Загружаем физические величины
            for q_data in data.get("quantities", []):
                try:
                    quantity = app_model.create_physical_quantity(
                        q_data["name"],
                        q_data["symbol"],
                        q_data["unit"],
                        q_data["dimension"],
                        q_data["L"],
                        q_data["T"],
                        q_data["group_id"]
                    )
                except Exception as e:
                    print(f"Ошибка создания физической величины: {e}")
            
            # Загружаем законы
            for law_data in data.get("laws", []):
                try:
                    from core.entities.law import Law
                    law = Law(
                        name=law_data["name"],
                        formula=law_data["formula"],
                        description=law_data["description"],
                        variables=law_data["variables"],
                        group_id=law_data["group_id"]
                    )
                    law.id = law_data.get("id")  # Устанавливаем ID отдельно
                    app_model.law_manager.law_repo.add_law(law)
                except Exception as e:
                    print(f"Ошибка создания закона: {e}")
            
            # Устанавливаем видимые величины
            for vq_data in data.get("visible_quantities", []):
                try:
                    quantity = app_model.get_quantity_at_position(
                        vq_data["L"],
                        vq_data["T"],
                        vq_data["group_id"]
                    )
                    if quantity:
                        app_model.set_visible_quantity(vq_data["L"], vq_data["T"], quantity)
                except Exception as e:
                    print(f"Ошибка установки видимой величины: {e}")
            
            QMessageBox.information(parent, "✅", "Проект успешно загружен!")
            
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка загрузки новой архитектуры: {str(e)}")

    def _load_old_architecture(self, data, parent):
        """Загрузка для старой архитектуры"""
        try:
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
            QMessageBox.critical(parent, "Ошибка", f"Ошибка загрузки старой архитектуры: {str(e)}")