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
            
            # Формируем данные для сохранения в новом формате
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
                        "color": g.color,
                        "laws": [
                            {
                                "id": law.id,
                                "name": law.name,
                                "formula": law.formula,
                                "description": law.description,
                                "variables": law.variables
                            } for law in all_laws if law.group_id == g.id
                        ]
                    } for g in law_groups
                ],
                "quantities": []
            }
            
            # Добавляем все физические величины с visible полем
            for (L, T), quantities_list in all_quantities.items():
                for quantity in quantities_list:
                    # Проверяем, является ли величина видимой
                    is_visible = False
                    for (vis_L, vis_T), vis_quantity in visible_quantities.items():
                        if vis_quantity.id == quantity.id:
                            is_visible = True
                            break
                    
                    quantity_dict = quantity.to_dict()
                    # Добавляем поле "visible"
                    quantity_dict["visible"] = is_visible
                    # Добавляем поле "group" для backward compatibility
                    system_group = app_model.get_system_group_by_id(quantity.group_id)
                    if system_group:
                        quantity_dict["group"] = system_group.name
                    data["quantities"].append(quantity_dict)
            
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
            
            print("🔍 Начало загрузки новой архитектуры")
            print(f"📄 Загружаемые данные: {len(data.get('system_groups', []))} групп, {len(data.get('law_groups', []))} групп законов, {len(data.get('quantities', []))} величин")
            
            # Очищаем все данные
            app_model.clear_all_data()
            print("🧹 Очищены все данные")
            
            # Загружаем системные группы
            system_groups = data.get("system_groups", [])
            print(f"📁 Загрузка {len(system_groups)} системных групп")
            for i, g_data in enumerate(system_groups):
                try:
                    print(f"  📋 Обработка группы {i+1}/{len(system_groups)}: {g_data.get('name', 'Без имени')}")
                    # Если ID нет, используем имя как ID
                    group_id = g_data.get("id")
                    if not group_id:
                        group_id = g_data["name"]
                        print(f"    ⚠️ ID не найден, используется имя: {group_id}")
                    
                    app_model.create_system_group(
                        group_id,
                        g_data["name"],
                        g_data["color"],
                        g_data["G"],
                        g_data["k"]
                    )
                    print(f"    ✅ Группа создана: {g_data['name']} (ID: {group_id})")
                except Exception as e:
                    print(f"    ❌ Ошибка создания системной группы: {e}")
            
            # Загружаем группы законов с законами внутри
            law_groups = data.get("law_groups", [])
            print(f"📚 Загрузка {len(law_groups)} групп законов")
            for i, lg_data in enumerate(law_groups):
                try:
                    print(f"  📖 Обработка группы законов {i+1}/{len(law_groups)}: {lg_data.get('name', 'Без имени')}")
                    # Если ID нет, используем имя как ID
                    law_group_id = lg_data.get("id")
                    if not law_group_id:
                        law_group_id = lg_data["name"]
                        print(f"    ⚠️ ID не найден, используется имя: {law_group_id}")
                    
                    app_model.create_law_group(
                        law_group_id,
                        lg_data["name"],
                        lg_data["color"]
                    )
                    print(f"    ✅ Группа законов создана: {lg_data['name']}")
                    
                    # Загружаем законы внутри группы
                    laws = lg_data.get("laws", [])
                    print(f"    📝 Загрузка {len(laws)} законов")
                    for j, law_data in enumerate(laws):
                        try:
                            from core.entities.law import Law
                            law = Law(
                                name=law_data["name"],
                                formula=law_data["formula"],
                                description=law_data["description"],
                                variables=law_data["variables"],
                                group_id=law_group_id
                            )
                            law.id = law_data.get("id")  # Устанавливаем ID отдельно
                            app_model.law_manager.law_repo.add_law(law)
                            print(f"      ✅ Закон создан: {law_data['name']}")
                        except Exception as e:
                            print(f"      ❌ Ошибка создания закона: {e}")
                            
                except Exception as e:
                    print(f"    ❌ Ошибка создания группы законов: {e}")
            
            # Загружаем физические величины
            quantities = data.get("quantities", [])
            print(f"🔬 Загрузка {len(quantities)} физических величин")
            visible_count = 0
            visible_quantities = {}  # Инициализируем словарь для видимых величин
            
            for i, q_data in enumerate(quantities):
                try:
                    print(f"  ⚛️ Обработка величины {i+1}/{len(quantities)}: {q_data.get('name', 'Без имени')}")
                    # Получаем group_id из нового формата или из backward compatibility
                    group_id = q_data.get("group_id")
                    if not group_id and "group" in q_data:
                        # Ищем группу по имени для backward compatibility
                        group_name = q_data["group"]
                        print(f"    🔍 Поиск группы по имени: {group_name}")
                        for group in app_model.get_all_system_groups():
                            if group.name == group_name:
                                group_id = group.id
                                print(f"    ✅ Найдена группа: {group_name} (ID: {group_id})")
                                break
                    
                    if group_id:
                        quantity = app_model.create_physical_quantity(
                            q_data["name"],
                            q_data["symbol"],
                            q_data["unit"],
                            q_data["dimension"],
                            q_data["L"],
                            q_data["T"],
                            group_id
                        )
                        
                        # Устанавливаем видимость напрямую
                        is_visible = q_data.get("visible", False)
                        if is_visible:
                            visible_count += 1
                            app_model.set_visible_quantity(q_data["L"], q_data["T"], quantity)
                            print(f"    👁️ Величина видима: {q_data['name']} (L={q_data['L']}, T={q_data['T']})")
                        else:
                            print(f"    👁️ Величина скрыта: {q_data['name']} (L={q_data['L']}, T={q_data['T']})")
                    else:
                        print(f"    ❌ Не удалось найти группу для величины: {q_data['name']}")
                        
                except Exception as e:
                    print(f"    ❌ Ошибка создания физической величины: {e}")
            
            print(f"📊 Статистика: {len(quantities)} величин загружено, {visible_count} видимых")
            
            # Проверка загруженных данных
            loaded_groups = app_model.get_all_system_groups()
            loaded_quantities = app_model.get_all_quantities()
            loaded_visible = app_model.get_visible_quantities()
            
            print(f"📈 Итоговая статистика:")
            print(f"  📁 Системных групп: {len(loaded_groups)}")
            print(f"  ⚛️ Физических величин: {sum(len(q_list) for q_list in loaded_quantities.values())}")
            print(f"  👁️ Видимых величин: {len(loaded_visible)}")
            
            QMessageBox.information(parent, "✅", "Проект успешно загружен!")
            
        except Exception as e:
            print(f"❌ Критическая ошибка загрузки: {str(e)}")
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