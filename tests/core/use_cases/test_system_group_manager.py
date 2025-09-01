import pytest
from unittest.mock import Mock, MagicMock
from core.entities.system_group import SystemGroup
from core.use_cases.system_group_manager import SystemGroupManager


class TestSystemGroupManager:
    """Тесты для SystemGroupManager"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок репозитория
        self.mock_repo = Mock()
        self.manager = SystemGroupManager(self.mock_repo)
        
        # Тестовые данные
        self.test_group = SystemGroup(
            id="group1",
            name="Тестовая группа",
            color="#FF0000",
            G=1,
            k=2
        )
    
    def test_create_group_success(self):
        """Тест успешного создания группы"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None  # ID не существует
        self.mock_repo.get_by_name.return_value = None  # Название не существует
        self.mock_repo.get_by_gk.return_value = None  # G,k не существует
        
        # Act
        result = self.manager.create_group(
            id="group1",
            name="Тестовая группа",
            color="#FF0000",
            G=1,
            k=2
        )
        
        # Assert
        assert result.id == "group1"
        assert result.name == "Тестовая группа"
        assert result.color == "#FF0000"
        assert result.G == 1
        assert result.k == 2
        
        # Проверяем, что репозиторий был вызван правильно
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.get_by_name.assert_called_once_with("Тестовая группа")
        self.mock_repo.get_by_gk.assert_called_once_with(1, 2)
        self.mock_repo.add.assert_called_once()
    
    def test_create_group_duplicate_id_raises_error(self):
        """Тест создания группы с дублирующимся ID"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # ID существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'group1' уже существует"):
            self.manager.create_group(
                id="group1",
                name="Тестовая группа",
                color="#FF0000",
                G=1,
                k=2
            )
        
        # Проверяем, что другие проверки не вызывались
        self.mock_repo.get_by_name.assert_not_called()
        self.mock_repo.get_by_gk.assert_not_called()
        self.mock_repo.add.assert_not_called()
    
    def test_create_group_duplicate_name_raises_error(self):
        """Тест создания группы с дублирующимся названием"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None  # ID не существует
        self.mock_repo.get_by_name.return_value = self.test_group  # Название существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с названием 'Тестовая группа' уже существует"):
            self.manager.create_group(
                id="group1",
                name="Тестовая группа",
                color="#FF0000",
                G=1,
                k=2
            )
        
        # Проверяем, что проверки вызывались в правильном порядке
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.get_by_name.assert_called_once_with("Тестовая группа")
        self.mock_repo.get_by_gk.assert_not_called()
        self.mock_repo.add.assert_not_called()
    
    def test_create_group_duplicate_gk_raises_error(self):
        """Тест создания группы с дублирующейся комбинацией G,k"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None  # ID не существует
        self.mock_repo.get_by_name.return_value = None  # Название не существует
        self.mock_repo.get_by_gk.return_value = self.test_group  # G,k существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с комбинацией G=1, k=2 уже существует"):
            self.manager.create_group(
                id="group1",
                name="Тестовая группа",
                color="#FF0000",
                G=1,
                k=2
            )
        
        # Проверяем, что все проверки вызывались
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.get_by_name.assert_called_once_with("Тестовая группа")
        self.mock_repo.get_by_gk.assert_called_once_with(1, 2)
        self.mock_repo.add.assert_not_called()
    
    def test_update_group_success(self):
        """Тест успешного обновления группы"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # Группа существует
        self.mock_repo.get_by_name.return_value = None  # Новое название не существует
        self.mock_repo.get_by_gk.return_value = None  # Новые G,k не существуют
        
        # Act
        result = self.manager.update_group(
            group_id="group1",
            name="Обновленная группа",
            color="#00FF00",
            G=3,
            k=4
        )
        
        # Assert
        assert result.id == "group1"
        assert result.name == "Обновленная группа"
        assert result.color == "#00FF00"
        assert result.G == 3
        assert result.k == 4
        
        # Проверяем, что репозиторий был вызван правильно
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.get_by_name.assert_called_once_with("Обновленная группа")
        self.mock_repo.get_by_gk.assert_called_once_with(3, 4)
        self.mock_repo.update.assert_called_once()
    
    def test_update_group_not_found_raises_error(self):
        """Тест обновления несуществующей группы"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None  # Группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'nonexistent' не найдена"):
            self.manager.update_group(
                group_id="nonexistent",
                name="Обновленная группа",
                color="#00FF00",
                G=3,
                k=4
            )
        
        # Проверяем, что другие проверки не вызывались
        self.mock_repo.get_by_name.assert_not_called()
        self.mock_repo.get_by_gk.assert_not_called()
        self.mock_repo.update.assert_not_called()
    
    def test_update_group_duplicate_name_raises_error(self):
        """Тест обновления группы с дублирующимся названием (другая группа)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # Группа существует
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#0000FF",
            G=5,
            k=6
        )
        self.mock_repo.get_by_name.return_value = another_group  # Название существует (у другой группы)
        # Новые G,k не существуют - не нужно мокировать, т.к. метод не вызывается
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с названием 'Другая группа' уже существует"):
            self.manager.update_group(
                group_id="group1",
                name="Другая группа",
                color="#00FF00",
                G=3,
                k=4
            )
        
        # Проверяем, что проверки вызывались
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.get_by_name.assert_called_once_with("Другая группа")
        # Проверяем, что get_by_gk не вызывался, т.к. ошибка произошла раньше
        self.mock_repo.get_by_gk.assert_not_called()
        self.mock_repo.update.assert_not_called()
    
    def test_update_group_duplicate_gk_raises_error(self):
        """Тест обновления группы с дублирующейся комбинацией G,k (другая группа)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # Группа существует
        self.mock_repo.get_by_name.return_value = None  # Новое название не существует
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#0000FF",
            G=3,
            k=4
        )
        self.mock_repo.get_by_gk.return_value = another_group  # G,k существует (у другой группы)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с комбинацией G=3, k=4 уже существует"):
            self.manager.update_group(
                group_id="group1",
                name="Обновленная группа",
                color="#00FF00",
                G=3,
                k=4
            )
        
        # Проверяем, что проверки вызывались
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.get_by_name.assert_called_once_with("Обновленная группа")
        self.mock_repo.get_by_gk.assert_called_once_with(3, 4)
        self.mock_repo.update.assert_not_called()
    
    def test_update_group_same_name_allowed(self):
        """Тест обновления группы с тем же названием (должно разрешаться)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # Группа существует
        self.mock_repo.get_by_name.return_value = self.test_group  # То же название (у той же группы)
        self.mock_repo.get_by_gk.return_value = None  # Новые G,k не существуют
        
        # Act
        result = self.manager.update_group(
            group_id="group1",
            name="Тестовая группа",  # то же название
            color="#00FF00",
            G=3,
            k=4
        )
        
        # Assert
        assert result.name == "Тестовая группа"
        assert result.color == "#00FF00"
        assert result.G == 3
        assert result.k == 4
        
        # Проверяем, что репозиторий был вызван правильно
        self.mock_repo.update.assert_called_once()
    
    def test_update_group_same_gk_allowed(self):
        """Тест обновления группы с теми же G,k (должно разрешаться)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # Группа существует
        self.mock_repo.get_by_name.return_value = None  # Новое название не существует
        self.mock_repo.get_by_gk.return_value = self.test_group  # Те же G,k (у той же группы)
        
        # Act
        result = self.manager.update_group(
            group_id="group1",
            name="Обновленная группа",
            color="#00FF00",
            G=1,  # те же G
            k=2   # те же k
        )
        
        # Assert
        assert result.name == "Обновленная группа"
        assert result.color == "#00FF00"
        assert result.G == 1
        assert result.k == 2
        
        # Проверяем, что репозиторий был вызван правильно
        self.mock_repo.update.assert_called_once()
    
    def test_delete_group_success(self):
        """Тест успешного удаления группы"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group  # Группа существует
        
        # Act
        self.manager.delete_group("group1")
        
        # Assert
        self.mock_repo.get_by_id.assert_called_once_with("group1")
        self.mock_repo.remove.assert_called_once_with("group1")
    
    def test_delete_group_not_found_raises_error(self):
        """Тест удаления несуществующей группы"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None  # Группа не существует
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'nonexistent' не найдена"):
            self.manager.delete_group("nonexistent")
        
        # Проверяем, что удаление не вызывалось
        self.mock_repo.remove.assert_not_called()
    
    def test_get_all_groups(self):
        """Тест получения всех групп"""
        # Arrange
        groups = [
            SystemGroup("group1", "Группа 1", "#FF0000", 1, 1),
            SystemGroup("group2", "Группа 2", "#00FF00", 2, 2)
        ]
        self.mock_repo.get_all.return_value = groups
        
        # Act
        result = self.manager.get_all_groups()
        
        # Assert
        assert result == groups
        self.mock_repo.get_all.assert_called_once()
    
    def test_get_group_by_id_found(self):
        """Тест получения группы по ID (найдено)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = self.test_group
        
        # Act
        result = self.manager.get_group_by_id("group1")
        
        # Assert
        assert result == self.test_group
        self.mock_repo.get_by_id.assert_called_once_with("group1")
    
    def test_get_group_by_id_not_found(self):
        """Тест получения группы по ID (не найдено)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = self.manager.get_group_by_id("nonexistent")
        
        # Assert
        assert result is None
        self.mock_repo.get_by_id.assert_called_once_with("nonexistent")
    
    def test_validate_name_uniqueness_true(self):
        """Тест проверки уникальности названия (уникально)"""
        # Arrange
        self.mock_repo.get_by_name.return_value = None
        
        # Act
        result = self.manager.validate_name_uniqueness("Уникальное название")
        
        # Assert
        assert result is True
        self.mock_repo.get_by_name.assert_called_once_with("Уникальное название")
    
    def test_validate_name_uniqueness_false(self):
        """Тест проверки уникальности названия (не уникально)"""
        # Arrange
        self.mock_repo.get_by_name.return_value = self.test_group
    
        # Act
        result = self.manager.validate_name_uniqueness("Тестовая группа")
    
        # Assert
        assert result is False
        self.mock_repo.get_by_name.assert_called_once_with("Тестовая группа")
    
    def test_validate_name_uniqueness_with_exclude_id(self):
        """Тест проверки уникальности названия с исключением ID"""
        # Arrange
        self.mock_repo.get_by_name.return_value = self.test_group
        
        # Act
        result = self.manager.validate_name_uniqueness(
            "Тестовая группа",
            exclude_id="group1"
        )
        
        # Assert
        assert result is True  # Должно разрешаться, так как это та же группа
        self.mock_repo.get_by_name.assert_called_once_with("Тестовая группа")
    
    def test_validate_name_uniqueness_with_exclude_id_different(self):
        """Тест проверки уникальности названия с исключением другого ID"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Тестовая группа",
            color="#0000FF",
            G=3,
            k=4
        )
        self.mock_repo.get_by_name.return_value = another_group
        
        # Act
        result = self.manager.validate_name_uniqueness(
            "Тестовая группа",
            exclude_id="group1"
        )
        
        # Assert
        assert result is False  # Должно запрещаться, так как это другая группа
        self.mock_repo.get_by_name.assert_called_once_with("Тестовая группа")
    
    def test_validate_gk_uniqueness_true(self):
        """Тест проверки уникальности комбинации G,k (уникально)"""
        # Arrange
        self.mock_repo.get_by_gk.return_value = None
        
        # Act
        result = self.manager.validate_gk_uniqueness(5, 6)
        
        # Assert
        assert result is True
        self.mock_repo.get_by_gk.assert_called_once_with(5, 6)
    
    def test_validate_gk_uniqueness_false(self):
        """Тест проверки уникальности комбинации G,k (не уникально)"""
        # Arrange
        self.mock_repo.get_by_gk.return_value = self.test_group
        
        # Act
        result = self.manager.validate_gk_uniqueness(1, 2)
        
        # Assert
        assert result is False
        self.mock_repo.get_by_gk.assert_called_once_with(1, 2)
    
    def test_validate_gk_uniqueness_with_exclude_id(self):
        """Тест проверки уникальности комбинации G,k с исключением ID"""
        # Arrange
        self.mock_repo.get_by_gk.return_value = self.test_group
        
        # Act
        result = self.manager.validate_gk_uniqueness(
            1,
            2,
            exclude_id="group1"
        )
        
        # Assert
        assert result is True  # Должно разрешаться, так как это та же группа
        self.mock_repo.get_by_gk.assert_called_once_with(1, 2)
    
    def test_validate_gk_uniqueness_with_exclude_id_different(self):
        """Тест проверки уникальности комбинации G,k с исключением другого ID"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#0000FF",
            G=1,
            k=2
        )
        self.mock_repo.get_by_gk.return_value = another_group
        
        # Act
        result = self.manager.validate_gk_uniqueness(
            1,
            2,
            exclude_id="group1"
        )
        
        # Assert
        assert result is False  # Должно запрещаться, так как это другая группа
        self.mock_repo.get_by_gk.assert_called_once_with(1, 2)