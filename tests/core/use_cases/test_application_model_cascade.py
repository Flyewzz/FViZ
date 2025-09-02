import pytest
from core.entities import PhysicalQuantity, SystemGroup, Law, LawGroup
from core.use_cases.application_model import ApplicationModel
from core.use_cases.physical_quantity_manager import PhysicalQuantityManager
from core.use_cases.system_group_manager import SystemGroupManager
from core.use_cases.law_manager import LawManager, LawGroupManager
from core.use_cases.law_manager import ParallelogramLogic
from infrastructure.repositories.physical_quantity_repository import PhysicalQuantityRepositoryImpl
from infrastructure.repositories.system_group_repository import SystemGroupRepositoryImpl
from infrastructure.repositories.law_repository import LawRepositoryImpl


class TestApplicationModelCascade:
    """Тесты каскадного удаления и проверки зависимостей в ApplicationModel"""
    
    def setup_method(self):
        """Настройка тестовой среды"""
        # Создаем репозитории
        self.quantity_repo = PhysicalQuantityRepositoryImpl()
        self.group_repo = SystemGroupRepositoryImpl()
        self.law_repo = LawRepositoryImpl()
        
        # Создаем менеджеры
        self.quantity_manager = PhysicalQuantityManager(self.quantity_repo, self.group_repo)
        self.group_manager = SystemGroupManager(self.group_repo)
        self.law_manager = LawManager(self.law_repo, self.law_repo, self.quantity_repo)
        self.law_group_manager = LawGroupManager(self.law_repo)
        self.parallelogram_logic = ParallelogramLogic(self.quantity_repo)
        
        # Создаем ApplicationModel
        self.app_model = ApplicationModel(
            self.quantity_manager,
            self.group_manager,
            self.law_manager,
            self.law_group_manager,
            self.parallelogram_logic
        )
        
        # Создаем тестовые данные
        self._create_test_data()
    
    def _create_test_data(self):
        """Создание тестовых данных"""
        # Создаем системные группы
        self.group1 = self.group_manager.create_group("group1", "Группа 1", "#ff0000", 1, 1)
        self.group2 = self.group_manager.create_group("group2", "Группа 2", "#00ff00", 2, 2)
        
        # Создаем физические величины
        self.quantity1 = self.quantity_manager.create_quantity("Сила", "F", "Н", "MLT⁻²", 1, 1, "group1")
        self.quantity2 = self.quantity_manager.create_quantity("Масса", "m", "кг", "M", 1, 2, "group1")
        self.quantity3 = self.quantity_manager.create_quantity("Ускорение", "a", "м/с²", "LT⁻²", 2, 1, "group1")
        self.quantity4 = self.quantity_manager.create_quantity("Время", "t", "с", "T", 2, 2, "group1")
        
        # Создаем дополнительные величины для тестов
        self.quantity5 = self.quantity_manager.create_quantity("Скорость", "v", "м/с", "LT⁻¹", 3, 1, "group1")
        self.quantity6 = self.quantity_manager.create_quantity("Импульс", "p", "кг·м/с", "MLT⁻¹", 3, 2, "group1")
        self.quantity7 = self.quantity_manager.create_quantity("Площадь", "S", "м²", "L²", 3, 3, "group1")
        self.quantity8 = self.quantity_manager.create_quantity("Давление", "P", "Па", "ML⁻¹T⁻²", 3, 4, "group1")
        
        # Создаем альтернативные величины в другой группе
        self.quantity1_alt = self.quantity_manager.create_quantity("Сила (альтернатива)", "F", "Н", "MLT⁻²", 1, 1, "group2")
        
        # Создаем закон
        self.law = self.law_manager.create_law(
            "Закон Ньютона", 
            "F = m * a", 
            "Второй закон Ньютона", 
            ["Сила", "Масса", "Ускорение", "Время"], 
            "mechanics"
        )
    
    def test_check_quantity_dependencies(self):
        """Тест проверки зависимостей физической величины"""
        # Проверяем зависимости для "Сила"
        dependencies = self.app_model.check_quantity_dependencies("Сила")
        
        assert len(dependencies) == 1
        assert dependencies[0].name == "Закон Ньютона"
        assert "Сила" in dependencies[0].variables
    
    def test_check_quantity_dependencies_by_entity(self):
        """Тест проверки зависимостей по сущности"""
        dependencies = self.app_model.check_quantity_dependencies_by_entity(self.quantity1)
        
        assert len(dependencies) == 1
        assert dependencies[0].name == "Закон Ньютона"
    
    def test_check_group_dependencies(self):
        """Тест проверки зависимостей системной группы"""
        dependencies = self.app_model.check_group_dependencies("group1")
        
        assert len(dependencies['quantities']) == 8
        assert len(dependencies['laws']) == 1
    
    def test_check_cell_dependencies(self):
        """Тест проверки зависимостей конкретной соты"""
        dependencies = self.app_model.check_cell_dependencies(1, 1, "group1")
        
        assert not dependencies['is_empty']
        assert dependencies['quantity'].name == "Сила"
        assert len(dependencies['laws']) == 1
    
    def test_check_empty_cell_dependencies(self):
        """Тест проверки зависимостей пустой соты"""
        dependencies = self.app_model.check_cell_dependencies(5, 5, "group1")
        
        assert dependencies['is_empty']
        assert dependencies['quantity'] is None
        assert len(dependencies['laws']) == 0
    
    def test_check_law_dependencies(self):
        """Тест проверки зависимостей закона"""
        dependencies = self.app_model.check_law_dependencies(self.law)
        
        assert len(dependencies['quantities']) == 4
        assert len(dependencies['related_laws']) == 0
    
    # def test_check_cyclic_dependencies(self):
    #     """Тест проверки циклических зависимостей"""
    #     # Создаем второй закон, который использует другие переменные
    #     law2 = self.law_manager.create_law(
    #         "Закон импульса",
    #         "p = m * v",
    #         "Закон сохранения импульса",
    #         ["Масса", "Скорость", "Импульс", "Время"],
    #         "mechanics"
    #     )
        
    #     # Проверяем циклические зависимости
    #     cyclic_deps = self.app_model.check_cyclic_dependencies()
        
    #     # В данном случае циклов быть не должно, так как законы используют одни и те же переменные
    #     assert len(cyclic_deps) == 0
    
    def test_detect_orphan_laws(self):
        """Тест обнаружения осиротевших законов"""
        # Создаем закон с несуществующей величиной (пропуская проверку)
        # Создаем закон с существующими величинами, но одна из них будет удалена
        # Создаем закон с несуществующей величиной напрямую через репозиторий
        orphan_law = Law(
            name="Осиротевший закон",
            formula="X = Y * Z",
            description="Закон, который станет осиротевшим",
            variables=["Сила", "Масса", "Несуществующая", "Время"],
            group_id="mechanics"
        )
        self.law_repo.add_law(orphan_law)
        
        orphan_laws = self.app_model.detect_orphan_laws()
        
        assert len(orphan_laws) == 1
        assert orphan_laws[0].name == "Осиротевший закон"
    
    def test_delete_cell_cascade_empty(self):
        """Тест каскадного удаления пустой соты"""
        # Используем пустую соту (5, 5)
        result = self.app_model.delete_cell_cascade(5, 5, "group1")
        
        assert result['success'] is True
        assert result['deleted_quantity'] is None
        assert len(result['deleted_laws']) == 0
        assert result['message'] in ['Пустая сота успешно удалена', 'Пустая сота успешно удалена (не было записи)']
    
    def test_delete_cell_cascade_with_quantity(self):
        """Тест каскадного удаления соты с величиной"""
        result = self.app_model.delete_cell_cascade(1, 1, "group1")
        
        assert result['success'] is True
        assert result['deleted_quantity']['name'] == "Сила"
        assert len(result['deleted_laws']) == 1
        assert result['deleted_laws'][0]['name'] == "Закон Ньютона"
        assert "Сила" in result['deleted_laws'][0]['variables']
    
    def test_delete_quantity_cascade(self):
        """Тест каскадного удаления физической величины по имени"""
        # Создаем величину "Сила" в группе 2 с другими координатами
        self.quantity_manager.create_quantity("Сила (группа 2)", "F", "Н", "MLT⁻²", 4, 4, "group2")
        
        result = self.app_model.delete_quantity_cascade("Сила")
        
        assert result['success'] is True
        assert len(result['deleted_quantities']) == 1  # Только в группе 1
        assert len(result['deleted_laws']) == 1
        assert result['deleted_laws'][0]['name'] == "Закон Ньютона"
    
    def test_delete_system_group_cascade(self):
        """Тест каскадного удаления системной группы"""
        result = self.app_model.delete_system_group_cascade("group1")
        
        assert result['success'] is True
        assert len(result['deleted_quantities']) == 8
        assert len(result['deleted_laws']) == 1
        assert result['deleted_laws'][0]['name'] == "Закон Ньютона"
    
    def test_delete_law_cascade(self):
        """Тест удаления закона с проверкой зависимостей"""
        result = self.app_model.delete_law_cascade(self.law.id)
        
        assert result['success'] is True
        assert result['deleted_law']['name'] == "Закон Ньютона"
        assert "Сила" in result['deleted_law']['variables']
    
    
    def test_delete_cell_cascade_error_handling(self):
        """Тест обработки ошибок при каскадном удалении"""
        # Попытка удаления несуществующей соты
        result = self.app_model.delete_cell_cascade(999, 999, "nonexistent_group")
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "не существует" in result['error']
    
    def test_delete_quantity_cascade_error_handling(self):
        """Тест обработки ошибок при удалении величины"""
        # Попытка удаления несуществующей величины
        result = self.app_model.delete_quantity_cascade("НесуществующаяВеличина")
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "не найдена" in result['error']
    
    def test_delete_system_group_cascade_error_handling(self):
        """Тест обработки ошибок при удалении системной группы"""
        # Попытка удаления несуществующей группы
        result = self.app_model.delete_system_group_cascade("nonexistent_group")
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "не найдена" in result['error']
    
    def test_delete_law_cascade_error_handling(self):
        """Тест обработки ошибок при удалении закона"""
        # Попытка удаления несуществующего закона
        result = self.app_model.delete_law_cascade("nonexistent_law_id")
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "не найден" in result['error']
    
    def test_multiple_laws_same_quantity(self):
        """Тест удаления величины, используемой в нескольких законах"""
        # Создаем второй закон, использующую ту же величину, но с другими переменными
        law2 = self.law_manager.create_law(
            "Закон давления",
            "P = F / S",
            "Закон давления",
            ["Сила", "Площадь", "Давление", "Время"],
            "mechanics"
        )
        
        # Удаляем величину
        result = self.app_model.delete_quantity_cascade("Сила")
        
        assert result['success'] is True
        assert len(result['deleted_laws']) == 2  # Оба закона должны быть удалены
        law_names = [law['name'] for law in result['deleted_laws']]
        assert "Закон Ньютона" in law_names
        assert "Закон давления" in law_names
    
    def test_cross_group_dependencies(self):
        """Тест зависимостей"""
        # Создаем величину в группе 2
        quantity5 = self.quantity_manager.create_quantity("Энергия", "E", "Дж", "ML²T⁻²", 1, 3, "group2")
        
        # Создаем закон, использующий величины из разных групп
        law3 = self.law_manager.create_law(
            "跨组 закон", 
            "E = F * s", 
            "Закон, использующий величины из разных групп", 
            ["Энергия", "Сила", "Масса", "Ускорение"], 
            "mechanics"
        )
        
        # Удаляем системную группу 1
        result = self.app_model.delete_system_group_cascade("group1")
        
        assert result['success'] is True
        assert len(result['deleted_quantities']) == 8  # Все величины из группы 1
        assert len(result['deleted_laws']) == 2  # Оба закона используют величины из группы 1
        
        # Проверяем, что величина в группе 2 осталась
        remaining_quantity = self.quantity_manager.get_quantity_at_position(1, 3, "group2")
        assert remaining_quantity is not None
        assert remaining_quantity.name == "Энергия"