import pytest
from unittest.mock import Mock, MagicMock
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.law import Law
from core.entities.law_group import LawGroup
from core.use_cases.law_manager import LawManager, LawGroupManager, ParallelogramLogic


class TestLawManager:
    """Тесты для LawManager"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок репозиториев
        self.mock_law_repo = Mock()
        self.mock_law_group_repo = Mock()
        self.mock_quantity_repo = Mock()
        self.manager = LawManager(self.mock_law_repo, self.mock_law_group_repo, self.mock_quantity_repo)
        
        # Тестовые данные
        self.test_law_group = LawGroup(
            id="law_group1",
            name="Механика",
            color="#FF0000"
        )
        
        self.test_quantity1 = PhysicalQuantity(
            name="Длина",
            symbol="L",
            unit="м",
            dimension="L",
            L=1,
            T=0,
            group_id="group1"
        )
        
        self.test_quantity2 = PhysicalQuantity(
            name="Время",
            symbol="t",
            unit="с",
            dimension="T",
            L=0,
            T=1,
            group_id="group1"
        )
        
        self.test_quantity3 = PhysicalQuantity(
            name="Масса",
            symbol="m",
            unit="кг",
            dimension="M",
            L=0,
            T=0,
            group_id="group1"
        )
        
        self.test_quantity4 = PhysicalQuantity(
            name="Ускорение",
            symbol="a",
            unit="м/с²",
            dimension="LT⁻²",
            L=1,
            T=-2,
            group_id="group1"
        )
        
        self.test_law = Law(
            name="Закон движения",
            formula="s = v*t",
            description="Закон равномерного движения",
            variables=["Длина", "Время", "Скорость", "Ускорение"],
            group_id="law_group1"
        )
    
    def test_create_law_success(self):
        """Тест успешного создания закона"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # Группа существует
        self.mock_quantity_repo.get_by_name.side_effect = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]  # Все величины существуют
        self.mock_law_repo.get_law_by_variables.return_value = None  # Закон с такими переменными не существует
        
        # Act
        result = self.manager.create_law(
            name="Закон движения",
            formula="s = v*t",
            description="Закон равномерного движения",
            variables=["Длина", "Время", "Скорость", "Ускорение"],
            group_id="law_group1"
        )
        
        # Assert
        assert result.name == "Закон движения"
        assert result.formula == "s = v*t"
        assert result.description == "Закон равномерного движения"
        assert result.variables == ["Длина", "Время", "Скорость", "Ускорение"]
        assert result.group_id == "law_group1"
        
        # Проверяем, что репозитории были вызваны правильно
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_quantity_repo.get_by_name.assert_any_call("Длина")
        self.mock_quantity_repo.get_by_name.assert_any_call("Время")
        self.mock_quantity_repo.get_by_name.assert_any_call("Ускорение")
        self.mock_law_repo.get_law_by_variables.assert_called_once_with(["Длина", "Время", "Скорость", "Ускорение"])
        self.mock_law_repo.add_law.assert_called_once()
    
    def test_create_law_nonexistent_group_raises_error(self):
        """Тест создания закона в несуществующей группе"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None  # Группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Группа законов с ID 'nonexistent' не существует"):
            self.manager.create_law(
                name="Закон движения",
                formula="s = v*t",
                description="Закон равномерного движения",
                variables=["Длина", "Время", "Скорость", "Ускорение"],
                group_id="nonexistent"
            )
        
        # Проверяем, что другие проверки не вызывались
        self.mock_quantity_repo.get_by_name.assert_not_called()
        self.mock_law_repo.get_law_by_variables.assert_not_called()
        self.mock_law_repo.add_law.assert_not_called()
    
    def test_create_law_nonexistent_variable_raises_error(self):
        """Тест создания закона с несуществующей величиной"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # Группа существует
        self.mock_quantity_repo.get_by_name.side_effect = [self.test_quantity1, None, self.test_quantity3, self.test_quantity4]  # Вторая величина не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Физическая величина 'Время' не найдена"):
            self.manager.create_law(
                name="Закон движения",
                formula="s = v*t",
                description="Закон равномерного движения",
                variables=["Длина", "Время", "Скорость", "Ускорение"],
                group_id="law_group1"
            )
        
        # Проверяем, что проверки вызывались в правильном порядке
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_quantity_repo.get_by_name.assert_any_call("Длина")
        self.mock_quantity_repo.get_by_name.assert_any_call("Время")
        
        # Проверяем, что get_by_name был вызван ровно 2 раза (для "Длина" и "Время")
        # и что остальные вызовы не происходили
        calls = self.mock_quantity_repo.get_by_name.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == "Длина"
        assert calls[1][0][0] == "Время"
        
        self.mock_law_repo.get_law_by_variables.assert_not_called()
        self.mock_law_repo.add_law.assert_not_called()
    
    def test_create_law_duplicate_variables_raises_error(self):
        """Тест создания закона с дублирующимися переменными"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # Группа существует
        self.mock_quantity_repo.get_by_name.side_effect = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]  # Все величины существуют
        self.mock_law_repo.get_law_by_variables.return_value = self.test_law  # Закон с такими переменными существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Закон с такими переменными уже существует: Закон движения"):
            self.manager.create_law(
                name="Новый закон",
                formula="f = m*a",
                description="Закон Ньютона",
                variables=["Длина", "Время", "Скорость", "Ускорение"],
                group_id="law_group1"
            )
        
        # Проверяем, что все проверки вызывались
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_quantity_repo.get_by_name.assert_any_call("Длина")
        self.mock_quantity_repo.get_by_name.assert_any_call("Время")
        self.mock_quantity_repo.get_by_name.assert_any_call("Скорость")
        self.mock_law_repo.get_law_by_variables.assert_called_once_with(["Длина", "Время", "Скорость", "Ускорение"])
        self.mock_law_repo.add_law.assert_not_called()
    
    def test_update_law_success(self):
        """Тест успешного обновления закона"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # Новая группа существует
        
        # Act
        result = self.manager.update_law(
            existing_law=self.test_law,
            name="Обновленный закон движения",
            formula="s = v*t + a*t²/2",
            description="Закон равноускоренного движения",
            group_id="law_group1"
        )
        
        # Assert
        assert result.name == "Обновленный закон движения"
        assert result.formula == "s = v*t + a*t²/2"
        assert result.description == "Закон равноускоренного движения"
        assert result.variables == ["Длина", "Время", "Скорость", "Ускорение"]  # Переменные не меняются
        assert result.group_id == "law_group1"
        
        # Проверяем, что репозитории были вызваны правильно
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_law_repo.update_law.assert_called_once()
    
    def test_update_law_nonexistent_group_raises_error(self):
        """Тест обновления закона в несуществующей группе"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None  # Новая группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Группа законов с ID 'nonexistent' не существует"):
            self.manager.update_law(
                existing_law=self.test_law,
                name="Обновленный закон",
                formula="s = v*t",
                description="Описание",
                group_id="nonexistent"
            )
        
        # Проверяем, что обновление не вызывалось
        self.mock_law_repo.update_law.assert_not_called()
    
    def test_find_law_by_quantities_success(self):
        """Тест поиска закона по величинам (успешный)"""
        # Arrange
        quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]
        self.mock_law_repo.get_law_by_variables.return_value = self.test_law
        
        # Act
        result = self.manager.find_law_by_quantities(quantities)
        
        # Assert
        assert result == self.test_law
        self.mock_law_repo.get_law_by_variables.assert_called_once_with(["Длина", "Время", "Масса", "Ускорение"])
    
    def test_find_law_by_quantities_wrong_count(self):
        """Тест поиска закона по величинам (неверное количество)"""
        # Arrange
        quantities = [self.test_quantity1, self.test_quantity2]  # Только 2 величины
        
        # Act
        result = self.manager.find_law_by_quantities(quantities)
        
        # Assert
        assert result is None
        self.mock_law_repo.get_law_by_variables.assert_not_called()
    
    def test_find_law_by_quantities_not_found(self):
        """Тест поиска закона по величинам (не найден)"""
        # Arrange
        quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]
        self.mock_law_repo.get_law_by_variables.return_value = None
        
        # Act
        result = self.manager.find_law_by_quantities(quantities)
        
        # Assert
        assert result is None
        self.mock_law_repo.get_law_by_variables.assert_called_once_with(["Длина", "Время", "Масса", "Ускорение"])
    
    def test_get_law_group_color_success(self):
        """Тест получения цвета группы закона (успешный)"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group
        
        # Act
        result = self.manager.get_law_group_color(self.test_law)
        
        # Assert
        assert result == "#FF0000"
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
    
    def test_get_law_group_color_not_found(self):
        """Тест получения цвета группы закона (группа не найдена)"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None
        
        # Act
        result = self.manager.get_law_group_color(self.test_law)
        
        # Assert
        assert result == "#000000"
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")


class TestLawGroupManager:
    """Тесты для LawGroupManager"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок репозитория
        self.mock_law_group_repo = Mock()
        self.manager = LawGroupManager(self.mock_law_group_repo)
        
        # Тестовые данные
        self.test_law_group = LawGroup(
            id="law_group1",
            name="Механика",
            color="#FF0000"
        )
    
    def test_create_group_success(self):
        """Тест успешного создания группы законов"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None  # ID не существует
        
        # Act
        result = self.manager.create_group(
            id="law_group1",
            name="Механика",
            color="#FF0000"
        )
        
        # Assert
        assert result.id == "law_group1"
        assert result.name == "Механика"
        assert result.color == "#FF0000"
        
        # Проверяем, что репозиторий был вызван правильно
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_law_group_repo.add.assert_called_once()
    
    def test_create_group_duplicate_id_raises_error(self):
        """Тест создания группы законов с дублирующимся ID"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # ID существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Группа законов с ID 'law_group1' уже существует"):
            self.manager.create_group(
                id="law_group1",
                name="Термодинамика",
                color="#00FF00"
            )
        
        # Проверяем, что добавление не вызывалось
        self.mock_law_group_repo.add.assert_not_called()
    
    def test_update_group_success(self):
        """Тест успешного обновления группы законов"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # Группа существует
        
        # Act
        result = self.manager.update_group(
            group_id="law_group1",
            name="Обновленная механика",
            color="#00FF00"
        )
        
        # Assert
        assert result.id == "law_group1"
        assert result.name == "Обновленная механика"
        assert result.color == "#00FF00"
        
        # Проверяем, что репозиторий был вызван правильно
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_law_group_repo.update.assert_called_once()
    
    def test_update_group_not_found_raises_error(self):
        """Тест обновления несуществующей группы законов"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None  # Группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Группа законов с ID 'nonexistent' не найдена"):
            self.manager.update_group(
                group_id="nonexistent",
                name="Название",
                color="#FFFFFF"
            )
        
        # Проверяем, что обновление не вызывалось
        self.mock_law_group_repo.update.assert_not_called()
    
    def test_get_all_groups(self):
        """Тест получения всех групп законов"""
        # Arrange
        groups = [
            LawGroup("group1", "Механика", "#FF0000"),
            LawGroup("group2", "Термодинамика", "#00FF00")
        ]
        self.mock_law_group_repo.get_all.return_value = groups
        
        # Act
        result = self.manager.get_all_groups()
        
        # Assert
        assert result == groups
        self.mock_law_group_repo.get_all.assert_called_once()
    
    def test_get_group_by_id_found(self):
        """Тест получения группы законов по ID (найдено)"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group
        
        # Act
        result = self.manager.get_group_by_id("law_group1")
        
        # Assert
        assert result == self.test_law_group
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
    
    def test_get_group_by_id_not_found(self):
        """Тест получения группы законов по ID (не найдено)"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None
        
        # Act
        result = self.manager.get_group_by_id("nonexistent")
        
        # Assert
        assert result is None
        self.mock_law_group_repo.get_by_id.assert_called_once_with("nonexistent")
    
    def test_delete_group_success(self):
        """Тест успешного удаления группы законов"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = self.test_law_group  # Группа существует
        
        # Act
        self.manager.delete_group("law_group1")
        
        # Assert
        self.mock_law_group_repo.get_by_id.assert_called_once_with("law_group1")
        self.mock_law_group_repo.remove.assert_called_once_with("law_group1")
    
    def test_delete_group_not_found_raises_error(self):
        """Тест удаления несуществующей группы законов"""
        # Arrange
        self.mock_law_group_repo.get_by_id.return_value = None  # Группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Группа законов с ID 'nonexistent' не найдена"):
            self.manager.delete_group("nonexistent")
        
        # Проверяем, что удаление не вызывалось
        self.mock_law_group_repo.remove.assert_not_called()


# class TestParallelogramLogic:
#     """Тесты для ParallelogramLogic"""
    
#     def setup_method(self):
#         """Настройка перед каждым тестом"""
#         # Создаем мок репозитория
#         self.mock_quantity_repo = Mock()
#         self.logic = ParallelogramLogic(self.mock_quantity_repo)
        
#         # Создаем мок для system_group_repo
#         self.mock_system_group_repo = Mock()
#         self.logic.system_group_repo = self.mock_system_group_repo
        
#         # Тестовые данные
#         self.test_group = Mock()
#         self.test_group.G = 1
#         self.test_group.k = 2
        
#         self.test_quantity1 = PhysicalQuantity(
#             name="Длина1",
#             symbol="L1",
#             unit="м",
#             dimension="L",
#             L=2,
#             T=1,
#             group_id="group1"
#         )
        
#         self.test_quantity2 = PhysicalQuantity(
#             name="Длина2",
#             symbol="L2",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=2,
#             group_id="group1"
#         )
        
#         self.test_quantity3 = PhysicalQuantity(
#             name="Длина3",
#             symbol="L3",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=1,
#             group_id="group1"
#         )
        
#         self.test_quantity4 = PhysicalQuantity(
#             name="Длина4",
#             symbol="L4",
#             unit="м",
#             dimension="L",
#             L=2,
#             T=0,
#             group_id="group1"
#         )
    
#     def test_check_parallelogram_success_4_points(self):
#         """Тест проверки параллелограмма с 4 точками (успешный)"""
#         # Arrange
#         quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]
#         self.mock_system_group_repo.get_by_id.return_value = self.test_group
        
#         # Act
#         result = self.logic.check_parallelogram(quantities)
        
#         # Assert
#         assert result is not None
#         assert len(result) == 4
#         # Проверяем, что результат содержит те же элементы, но в другом порядке
#         assert len(result) == len(quantities)
#         for item in quantities:
#             assert item in result
    
#     def test_check_parallelogram_success_3_points(self):
#         """Тест проверки параллелограмма с 3 точками (успешный)"""
#         # Arrange
#         quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3]
#         self.mock_system_group_repo.get_by_id.return_value = self.test_group
        
#         # Act
#         result = self.logic.check_parallelogram(quantities)
        
#         # Assert
#         assert result is not None
#         assert len(result) == 4
#         # Проверяем, что результат содержит те же элементы, но с удвоенной центральной точкой
#         assert result.count(self.test_quantity3) == 2  # Центральная точка должна быть удвоена
    
#     def test_check_parallelogram_wrong_count(self):
#         """Тест проверки параллелограмма с неверным количеством точек"""
#         # Arrange
#         quantities = [self.test_quantity1, self.test_quantity2]  # Только 2 точки
        
#         # Act
#         result = self.logic.check_parallelogram(quantities)
        
#         # Assert
#         assert result is None
    
#     def test_check_parallelogram_conditions_not_met(self):
#         """Тест проверки параллелограмма (условия не выполнены)"""
#         # Arrange
#         # Создаем величины, которые не удовлетворяют условиям параллелограмма
#         quantity_bad1 = PhysicalQuantity(
#             name="Bad1",
#             symbol="B1",
#             unit="м",
#             dimension="L",
#             L=3,
#             T=3,
#             group_id="group1"
#         )
#         quantity_bad2 = PhysicalQuantity(
#             name="Bad2",
#             symbol="B2",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=1,
#             group_id="group1"
#         )
#         quantity_bad3 = PhysicalQuantity(
#             name="Bad3",
#             symbol="B3",
#             unit="м",
#             dimension="L",
#             L=2,
#             T=2,
#             group_id="group1"
#         )
#         quantity_bad4 = PhysicalQuantity(
#             name="Bad4",
#             symbol="B4",
#             unit="м",
#             dimension="L",
#             L=0,
#             T=0,
#             group_id="group1"
#         )
        
#         quantities = [quantity_bad1, quantity_bad2, quantity_bad3, quantity_bad4]
#         self.mock_system_group_repo.get_by_id.return_value = self.test_group
        
#         # Act
#         result = self.logic.check_parallelogram(quantities)
        
#         # Assert
#         assert result is None
    
#     def test_check_parallelogram_no_system_group_repo(self):
#         """Тест проверки параллелограмма без system_group_repo"""
#         # Arrange
#         self.logic.system_group_repo = None
#         quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]
        
#         # Act
#         result = self.logic.check_parallelogram(quantities)
        
#         # Assert
#         assert result is None
    
#     def test_check_parallelogram_exception_handling(self):
#         """Тест проверки параллелограмма с обработкой исключений"""
#         # Arrange
#         quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]
#         self.mock_system_group_repo.get_by_id.side_effect = Exception("Test exception")
        
#         # Act
#         result = self.logic.check_parallelogram(quantities)
        
#         # Assert
#         assert result is None
    
#     def test_check_linear_parallelogram_vertical(self):
#         """Тест проверки линейного параллелограмма (вертикальная линия)"""
#         # Arrange
#         # Создаем точки на вертикальной линии (одинаковый L)
#         quantity_v1 = PhysicalQuantity(
#             name="V1",
#             symbol="V1",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=0,
#             group_id="group1"
#         )
#         quantity_v2 = PhysicalQuantity(
#             name="V2",
#             symbol="V2",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=1,
#             group_id="group1"
#         )
#         quantity_v3 = PhysicalQuantity(
#             name="V3",
#             symbol="V3",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=2,
#             group_id="group1"
#         )
        
#         quantities = [quantity_v1, quantity_v2, quantity_v3]
        
#         # Act
#         result = self.logic._check_linear_parallelogram(quantities)
        
#         # Assert
#         assert result is not None
#         assert len(result) == 4
#         assert result[0] == quantity_v1
#         assert result[3] == quantity_v3
#         assert result[1] == result[2] == quantity_v2  # Центральная точка удваивается
    
#     def test_check_linear_parallelogram_horizontal(self):
#         """Тест проверки линейного параллелограмма (горизонтальная линия)"""
#         # Arrange
#         # Создаем точки на горизонтальной линии (одинаковый T)
#         quantity_h1 = PhysicalQuantity(
#             name="H1",
#             symbol="H1",
#             unit="м",
#             dimension="L",
#             L=0,
#             T=1,
#             group_id="group1"
#         )
#         quantity_h2 = PhysicalQuantity(
#             name="H2",
#             symbol="H2",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=1,
#             group_id="group1"
#         )
#         quantity_h3 = PhysicalQuantity(
#             name="H3",
#             symbol="H3",
#             unit="м",
#             dimension="L",
#             L=2,
#             T=1,
#             group_id="group1"
#         )
        
#         quantities = [quantity_h1, quantity_h2, quantity_h3]
        
#         # Act
#         result = self.logic._check_linear_parallelogram(quantities)
        
#         # Assert
#         assert result is not None
#         assert len(result) == 4
#         assert result[0] == quantity_h1
#         assert result[3] == quantity_h3
#         assert result[1] == result[2] == quantity_h2  # Центральная точка удваивается
    
#     def test_check_linear_parallelogram_not_linear(self):
#         """Тест проверки линейного параллелограмма (не линейные точки)"""
#         # Arrange
#         quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3]
        
#         # Act
#         result = self.logic._check_linear_parallelogram(quantities)
        
#         # Assert
#         assert result is None
    
#     def test_check_full_parallelogram_success(self):
#         """Тест проверки полного параллелограмма (успешный)"""
#         # Arrange
#         quantities = [self.test_quantity1, self.test_quantity2, self.test_quantity3, self.test_quantity4]
        
#         # Act
#         result = self.logic._check_full_parallelogram(quantities)
        
#         # Assert
#         assert result is not None
#         assert len(result) == 4
#         # Проверяем, что результат содержит те же элементы, но в другом порядке
#         assert len(result) == len(quantities)
#         for item in quantities:
#             assert item in result
    
#     def test_check_full_parallelogram_insufficient_points(self):
#         """Тест проверки полного параллелограмма (недостаточно точек)"""
#         # Arrange
#         quantities = [self.test_quantity1]  # Только 1 точка
        
#         # Act
#         result = self.logic._check_full_parallelogram(quantities)
        
#         # Assert
#         assert result is None
    
#     def test_check_full_parallelogram_conditions_not_met(self):
#         """Тест проверки полного параллелограмма (условия не выполнены)"""
#         # Arrange
#         # Создаем величины, которые не удовлетворяют условиям
#         quantity_bad1 = PhysicalQuantity(
#             name="Bad1",
#             symbol="B1",
#             unit="м",
#             dimension="L",
#             L=3,
#             T=3,
#             group_id="group1"
#         )
#         quantity_bad2 = PhysicalQuantity(
#             name="Bad2",
#             symbol="B2",
#             unit="м",
#             dimension="L",
#             L=1,
#             T=1,
#             group_id="group1"
#         )
#         quantity_bad3 = PhysicalQuantity(
#             name="Bad3",
#             symbol="B3",
#             unit="м",
#             dimension="L",
#             L=2,
#             T=2,
#             group_id="group1"
#         )
#         quantity_bad4 = PhysicalQuantity(
#             name="Bad4",
#             symbol="B4",
#             unit="м",
#             dimension="L",
#             L=0,
#             T=0,
#             group_id="group1"
#         )
        
#         quantities = [quantity_bad1, quantity_bad2, quantity_bad3, quantity_bad4]
        
#         # Act
#         result = self.logic._check_full_parallelogram(quantities)
        
#         # Assert
#         assert result is None