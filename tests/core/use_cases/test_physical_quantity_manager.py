import pytest
from unittest.mock import Mock, MagicMock
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.system_group import SystemGroup
from core.use_cases.physical_quantity_manager import PhysicalQuantityManager


class TestPhysicalQuantityManager:
    """Тесты для PhysicalQuantityManager"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок репозиториев
        self.mock_quantity_repo = Mock()
        self.mock_system_group_repo = Mock()
        self.manager = PhysicalQuantityManager(self.mock_quantity_repo, self.mock_system_group_repo)
        
        # Тестовые данные
        self.test_group = SystemGroup(
            id="group1",
            name="Тестовая группа",
            color="#FF0000",
            G=1,
            k=2
        )
        
        self.test_quantity = PhysicalQuantity(
            name="Длина",
            symbol="L",
            unit="м",
            dimension="L",
            L=1,
            T=0,
            group_id="group1"
        )
        
        self.another_quantity = PhysicalQuantity(
            name="Время",
            symbol="t",
            unit="с",
            dimension="T",
            L=0,
            T=1,
            group_id="group1"
        )
    
    def test_create_quantity_success(self):
        """Тест успешного создания физической величины"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = None  # Название не существует
        self.mock_system_group_repo.get_by_id.return_value = self.test_group  # Группа существует
        self.mock_quantity_repo.find_by_position.return_value = None  # Координаты свободны
        
        # Act
        result = self.manager.create_quantity(
            name="Длина",
            symbol="L",
            unit="м",
            dimension="L",
            L=1,
            T=0,
            group_id="group1"
        )
        
        # Assert
        assert result.name == "Длина"
        assert result.symbol == "L"
        assert result.unit == "м"
        assert result.dimension == "L"
        assert result.L == 1
        assert result.T == 0
        assert result.group_id == "group1"
        
        # Проверяем, что репозитории были вызваны правильно
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("group1")
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group1")
        self.mock_quantity_repo.save.assert_called_once()
    
    def test_create_quantity_duplicate_name_raises_error(self):
        """Тест создания физической величины с дублирующимся названием"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = self.test_quantity  # Название существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Физическая величина с названием 'Длина' уже существует"):
            self.manager.create_quantity(
                name="Длина",
                symbol="L",
                unit="м",
                dimension="L",
                L=1,
                T=0,
                group_id="group1"
            )
        
        # Проверяем, что другие проверки не вызывались
        self.mock_system_group_repo.get_by_id.assert_not_called()
        self.mock_quantity_repo.find_by_position.assert_not_called()
        self.mock_quantity_repo.save.assert_not_called()
    
    def test_create_quantity_nonexistent_group_raises_error(self):
        """Тест создания физической величины в несуществующей группе"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = None  # Название не существует
        self.mock_system_group_repo.get_by_id.return_value = None  # Группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'nonexistent' не существует"):
            self.manager.create_quantity(
                name="Длина",
                symbol="L",
                unit="м",
                dimension="L",
                L=1,
                T=0,
                group_id="nonexistent"
            )
        
        # Проверяем, что проверки вызывались в правильном порядке
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("nonexistent")
        self.mock_quantity_repo.find_by_position.assert_not_called()
        self.mock_quantity_repo.save.assert_not_called()
    
    def test_create_quantity_position_occupied_raises_error(self):
        """Тест создания физической величины в занятых координатах"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = None  # Название не существует
        self.mock_system_group_repo.get_by_id.return_value = self.test_group  # Группа существует
        self.mock_quantity_repo.find_by_position.return_value = self.test_quantity  # Координаты заняты
        
        # Act & Assert
        with pytest.raises(ValueError, match="Координаты \\(1, 0\\) уже заняты в группе group1"):
            self.manager.create_quantity(
                name="Длина",
                symbol="L",
                unit="м",
                dimension="L",
                L=1,
                T=0,
                group_id="group1"
            )
        
        # Проверяем, что все проверки вызывались
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("group1")
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group1")
        self.mock_quantity_repo.save.assert_not_called()
    
    def test_update_quantity_success(self):
        """Тест успешного обновления физической величины"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = None  # Новое название не существует
        self.mock_system_group_repo.get_by_id.return_value = self.test_group  # Новая группа существует
        # Позиция в новой группе свободна - не нужно мокировать, т.к. группа не меняется
        
        # Act
        result = self.manager.update_quantity(
            old_quantity=self.test_quantity,
            name="Обновленная длина",
            symbol="L'",
            unit="м",
            dimension="L",
            new_group_id="group1"
        )
        
        # Assert
        assert result.name == "Обновленная длина"
        assert result.symbol == "L'"
        assert result.unit == "м"
        assert result.dimension == "L"
        assert result.L == 1  # То же L
        assert result.T == 0  # То же T
        assert result.group_id == "group1"  # Та же группа
        
        # Проверяем, что репозитории были вызваны правильно
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Обновленная длина")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("group1")
        self.mock_quantity_repo.update.assert_called_once()
    
    def test_update_quantity_different_group_success(self):
        """Тест успешного обновления физической величины с изменением группы"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=2,
            k=3
        )
        self.mock_quantity_repo.find_by_name.return_value = None  # Новое название не существует
        self.mock_system_group_repo.get_by_id.return_value = another_group  # Новая группа существует
        self.mock_quantity_repo.find_by_position.return_value = None  # Позиция в новой группе свободна
        
        # Act
        result = self.manager.update_quantity(
            old_quantity=self.test_quantity,
            name="Длина в другой группе",
            symbol="L",
            unit="м",
            dimension="L",
            new_group_id="group2"
        )
        
        # Assert
        assert result.name == "Длина в другой группе"
        assert result.symbol == "L"
        assert result.unit == "м"
        assert result.dimension == "L"
        assert result.L == 1  # То же L
        assert result.T == 0  # То же T
        assert result.group_id == "group2"  # Новая группа
        
        # Проверяем, что репозитории были вызваны правильно
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина в другой группе")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("group2")
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group2")
        self.mock_quantity_repo.update.assert_called_once()
    
    def test_update_quantity_duplicate_name_raises_error(self):
        """Тест обновления физической величины с дублирующимся названием (другая величина)"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = self.another_quantity  # Название существует (у другой величины)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Физическая величина с названием 'Время' уже существует"):
            self.manager.update_quantity(
                old_quantity=self.test_quantity,
                name="Время",
                symbol="L",
                unit="м",
                dimension="L",
                new_group_id="group1"
            )
        
        # Проверяем, что проверки вызывались
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Время")
        self.mock_system_group_repo.get_by_id.assert_not_called()
        self.mock_quantity_repo.update.assert_not_called()
    
    def test_update_quantity_nonexistent_group_raises_error(self):
        """Тест обновления физической величины в несуществующую группу"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = None  # Новое название не существует
        self.mock_system_group_repo.get_by_id.return_value = None  # Новая группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'nonexistent' не существует"):
            self.manager.update_quantity(
                old_quantity=self.test_quantity,
                name="Обновленная длина",
                symbol="L'",
                unit="м",
                dimension="L",
                new_group_id="nonexistent"
            )
        
        # Проверяем, что проверки вызывались в правильном порядке
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Обновленная длина")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("nonexistent")
        self.mock_quantity_repo.update.assert_not_called()
    
    def test_update_quantity_position_occupied_raises_error(self):
        """Тест обновления физической величины в занятые координаты другой группы"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=2,
            k=3
        )
        self.mock_quantity_repo.find_by_name.return_value = None  # Новое название не существует
        self.mock_system_group_repo.get_by_id.return_value = another_group  # Новая группа существует
        self.mock_quantity_repo.find_by_position.return_value = self.another_quantity  # Позиция занята
        
        # Act & Assert
        with pytest.raises(ValueError, match="Координаты \\(1, 0\\) уже заняты в группе group2"):
            self.manager.update_quantity(
                old_quantity=self.test_quantity,
                name="Длина в другой группе",
                symbol="L",
                unit="м",
                dimension="L",
                new_group_id="group2"
            )
        
        # Проверяем, что проверки вызывались
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина в другой группе")
        self.mock_system_group_repo.get_by_id.assert_called_once_with("group2")
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group2")
        self.mock_quantity_repo.update.assert_not_called()
    
    def test_update_quantity_same_name_allowed(self):
        """Тест обновления физической величины с тем же названием (должно разрешаться)"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = self.test_quantity  # То же название (у той же величины)
        
        # Act
        result = self.manager.update_quantity(
            old_quantity=self.test_quantity,
            name="Длина",  # то же название
            symbol="L'",
            unit="м",
            dimension="L",
            new_group_id="group1"
        )
        
        # Assert
        assert result.name == "Длина"
        assert result.symbol == "L'"
        assert result.unit == "м"
        assert result.dimension == "L"
        
        # Проверяем, что репозитории были вызваны правильно
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
        self.mock_quantity_repo.update.assert_called_once()
    
    def test_delete_quantity_success(self):
        """Тест успешного удаления физической величины"""
        # Arrange
        self.mock_quantity_repo.find_by_position.return_value = self.test_quantity
        
        # Act
        self.manager.delete_quantity(L=1, T=0, group_id="group1")
        
        # Assert
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group1")
        self.mock_quantity_repo.remove.assert_called_once_with(1, 0, "group1")
        # Проверяем, что get_visible_quantity был вызван
        self.mock_quantity_repo.get_visible_quantity.assert_called_once_with(1, 0)
    
    def test_delete_quantity_not_found_raises_error(self):
        """Тест удаления несуществующей физической величины"""
        # Arrange
        self.mock_quantity_repo.find_by_position.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Физическая величина на координатах \\(1, 0\\) в группе group1 не найдена"):
            self.manager.delete_quantity(L=1, T=0, group_id="group1")
        
        # Проверяем, что удаление не вызывалось
        self.mock_quantity_repo.remove.assert_not_called()
    
    def test_delete_quantity_with_visible_replacement(self):
        """Тест удаления физической величины с заменой видимой"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=2,
            k=3
        )
        another_quantity_different_group = PhysicalQuantity(
            name="Масса",
            symbol="m",
            unit="кг",
            dimension="M",
            L=1,
            T=0,
            group_id="group2"
        )
        self.mock_quantity_repo.find_by_position.return_value = self.test_quantity
        self.mock_quantity_repo.get_visible_quantity.return_value = self.test_quantity
        self.mock_quantity_repo.find_all_by_position.return_value = [self.test_quantity, another_quantity_different_group]
        
        # Act
        self.manager.delete_quantity(L=1, T=0, group_id="group1")
        
        # Assert
        self.mock_quantity_repo.set_visible_quantity.assert_called_once_with(1, 0, another_quantity_different_group)
    
    def test_delete_quantity_with_no_alternatives(self):
        """Тест удаления физической величины без альтернатив"""
        # Arrange
        self.mock_quantity_repo.find_by_position.return_value = self.test_quantity
        self.mock_quantity_repo.get_visible_quantity.return_value = self.test_quantity
        self.mock_quantity_repo.find_all_by_position.return_value = [self.test_quantity]
        
        # Act
        self.manager.delete_quantity(L=1, T=0, group_id="group1")
        
        # Assert
        self.mock_quantity_repo.remove_visible_quantity.assert_called_once_with(1, 0)
    
    def test_delete_quantity_with_different_visible(self):
        """Тест удаления физической величины, когда видимая другая"""
        # Arrange
        self.mock_quantity_repo.find_by_position.return_value = self.test_quantity
        self.mock_quantity_repo.get_visible_quantity.return_value = self.another_quantity
        
        # Act
        self.manager.delete_quantity(L=1, T=0, group_id="group1")
        
        # Assert
        self.mock_quantity_repo.set_visible_quantity.assert_not_called()
        self.mock_quantity_repo.remove_visible_quantity.assert_not_called()
    
    def test_get_alternatives_for_cell(self):
        """Тест получения альтернатив для ячейки"""
        # Arrange
        alternatives = [self.test_quantity, self.another_quantity]
        self.mock_quantity_repo.find_all_by_position.return_value = alternatives
        
        # Act
        result = self.manager.get_alternatives_for_cell(L=1, T=0, exclude_group_id="group1")
        
        # Assert
        assert result == []
        self.mock_quantity_repo.find_all_by_position.assert_called_once_with(1, 0)
    
    def test_get_alternatives_for_cell_with_different_group(self):
        """Тест получения альтернатив для ячейки с другой группой"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=2,
            k=3
        )
        another_quantity = PhysicalQuantity(
            name="Масса",
            symbol="m",
            unit="кг",
            dimension="M",
            L=1,
            T=0,
            group_id="group2"
        )
        alternatives = [self.test_quantity, another_quantity]
        self.mock_quantity_repo.find_all_by_position.return_value = alternatives
        
        # Act
        result = self.manager.get_alternatives_for_cell(L=1, T=0, exclude_group_id="group1")
        
        # Assert
        assert result == [another_quantity]
        self.mock_quantity_repo.find_all_by_position.assert_called_once_with(1, 0)
    
    def test_set_visible_quantity(self):
        """Тест установки видимой величины"""
        # Act
        self.manager.set_visible_quantity(L=1, T=0, quantity=self.test_quantity)
        
        # Assert
        self.mock_quantity_repo.set_visible_quantity.assert_called_once_with(1, 0, self.test_quantity)
    
    def test_get_visible_quantities(self):
        """Тест получения всех видимых величин"""
        # Arrange
        visible_quantities = {
            (1, 0): self.test_quantity,
            (0, 1): self.another_quantity
        }
        self.mock_quantity_repo.get_all_visible_quantities.return_value = visible_quantities
        
        # Act
        result = self.manager.get_visible_quantities()
        
        # Assert
        assert result == visible_quantities
        self.mock_quantity_repo.get_all_visible_quantities.assert_called_once()
    
    def test_validate_name_uniqueness_true(self):
        """Тест проверки уникальности названия (уникально)"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = None
        
        # Act
        result = self.manager.validate_name_uniqueness("Уникальное название")
        
        # Assert
        assert result is True
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Уникальное название")
    
    def test_validate_name_uniqueness_false(self):
        """Тест проверки уникальности названия (не уникально)"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = self.test_quantity
        
        # Act
        result = self.manager.validate_name_uniqueness("Длина")
        
        # Assert
        assert result is False
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
    
    def test_validate_name_uniqueness_with_exclude_quantity(self):
        """Тест проверки уникальности названия с исключением величины"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = self.test_quantity
        
        # Act
        result = self.manager.validate_name_uniqueness(
            "Длина",
            exclude_quantity=self.test_quantity
        )
        
        # Assert
        assert result is True  # Должно разрешаться, так как это та же величина
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
    
    def test_validate_name_uniqueness_with_exclude_different_quantity(self):
        """Тест проверки уникальности названия с исключением другой величины"""
        # Arrange
        self.mock_quantity_repo.find_by_name.return_value = self.test_quantity
        
        # Act
        result = self.manager.validate_name_uniqueness(
            "Длина",
            exclude_quantity=self.another_quantity
        )
        
        # Assert
        assert result is False  # Должно запрещаться, так как это другая величина
        self.mock_quantity_repo.find_by_name.assert_called_once_with("Длина")
    
    def test_get_quantity_at_position_found(self):
        """Тест получения физической величины в позиции (найдено)"""
        # Arrange
        self.mock_quantity_repo.find_by_position.return_value = self.test_quantity
        
        # Act
        result = self.manager.get_quantity_at_position(L=1, T=0, group_id="group1")
        
        # Assert
        assert result == self.test_quantity
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group1")
    
    def test_get_quantity_at_position_not_found(self):
        """Тест получения физической величины в позиции (не найдено)"""
        # Arrange
        self.mock_quantity_repo.find_by_position.return_value = None
        
        # Act
        result = self.manager.get_quantity_at_position(L=1, T=0, group_id="group1")
        
        # Assert
        assert result is None
        self.mock_quantity_repo.find_by_position.assert_called_once_with(1, 0, "group1")
    
    def test_get_used_groups_at_position(self):
        """Тест получения занятых групп в позиции"""
        # Arrange
        quantities = [self.test_quantity]  # Две одинаковые величины с одной группой
        self.mock_quantity_repo.find_all_by_position.return_value = quantities
        
        # Act
        result = self.manager.get_used_groups_at_position(L=1, T=0)
        
        # Assert
        assert result == ["group1"]
        self.mock_quantity_repo.find_all_by_position.assert_called_once_with(1, 0)
    
    def test_get_used_groups_at_position_multiple_groups(self):
        """Тест получения занятых групп в позиции с несколькими группами"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=2,
            k=3
        )
        another_quantity = PhysicalQuantity(
            name="Масса",
            symbol="m",
            unit="кг",
            dimension="M",
            L=1,
            T=0,
            group_id="group2"
        )
        quantities = [self.test_quantity, another_quantity]
        self.mock_quantity_repo.find_all_by_position.return_value = quantities
        
        # Act
        result = self.manager.get_used_groups_at_position(L=1, T=0)
        
        # Assert
        assert result == ["group1", "group2"]
        self.mock_quantity_repo.find_all_by_position.assert_called_once_with(1, 0)
    
    def test_get_all_quantities_by_position(self):
        """Тест получения всех физических величин по позициям"""
        # Arrange
        quantities_by_position = {
            (1, 0): [self.test_quantity],
            (0, 1): [self.another_quantity]
        }
        self.mock_quantity_repo.get_all_quantities_by_position.return_value = quantities_by_position
        
        # Act
        result = self.manager.get_all_quantities_by_position()
        
        # Assert
        assert result == quantities_by_position
        self.mock_quantity_repo.get_all_quantities_by_position.assert_called_once()
    
    def test_clear_all(self):
        """Тест очистки всех данных"""
        # Act
        self.manager.clear_all()
        
        # Assert
        self.mock_quantity_repo.clear_all.assert_called_once()