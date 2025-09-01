import pytest
from core.entities.system_group import SystemGroup
from infrastructure.repositories.system_group_repository import SystemGroupRepositoryImpl


class TestSystemGroupRepositoryImpl:
    """Тесты для SystemGroupRepositoryImpl"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.repo = SystemGroupRepositoryImpl()
        self.test_group = SystemGroup(
            id="group1",
            name="Тестовая группа",
            color="#FF0000",
            G=1,
            k=2
        )
    
    def test_add_group_success(self):
        """Тест успешного добавления группы"""
        # Act
        self.repo.add(self.test_group)
        
        # Assert
        assert len(self.repo.get_all()) == 1
        assert self.repo.get_by_id("group1") == self.test_group
        assert self.repo.get_by_name("Тестовая группа") == self.test_group
        assert self.repo.get_by_gk(1, 2) == self.test_group
    
    def test_add_duplicate_id_raises_error(self):
        """Тест добавления группы с дублирующимся ID"""
        # Arrange
        self.repo.add(self.test_group)
        duplicate_group = SystemGroup(
            id="group1",  # тот же ID
            name="Другая группа",
            color="#00FF00",
            G=3,
            k=4
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'group1' уже существует"):
            self.repo.add(duplicate_group)
    
    def test_add_duplicate_name_raises_error(self):
        """Тест добавления группы с дублирующимся названием"""
        # Arrange
        self.repo.add(self.test_group)
        duplicate_group = SystemGroup(
            id="group2",
            name="Тестовая группа",  # то же название
            color="#00FF00",
            G=3,
            k=4
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа 'Тестовая группа' уже существует"):
            self.repo.add(duplicate_group)
    
    def test_add_duplicate_gk_raises_error(self):
        """Тест добавления группы с дублирующейся комбинацией G,k"""
        # Arrange
        self.repo.add(self.test_group)
        duplicate_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=1,  # тот же G
            k=2   # тот же k
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с G=1, k=2 уже существует"):
            self.repo.add(duplicate_group)
    
    def test_update_group_success(self):
        """Тест успешного обновления группы"""
        # Arrange
        self.repo.add(self.test_group)
        updated_group = SystemGroup(
            id="group1",
            name="Обновленная группа",
            color="#00FF00",
            G=5,
            k=6
        )
        
        # Act
        self.repo.update(updated_group)
        
        # Assert
        assert len(self.repo.get_all()) == 1
        assert self.repo.get_by_id("group1") == updated_group
        assert self.repo.get_by_name("Обновленная группа") == updated_group
        assert self.repo.get_by_gk(5, 6) == updated_group
        assert self.repo.get_by_gk(1, 2) is None
    
    def test_update_nonexistent_group_raises_error(self):
        """Тест обновления несуществующей группы"""
        # Arrange
        nonexistent_group = SystemGroup(
            id="nonexistent",
            name="Несуществующая группа",
            color="#0000FF",
            G=1,
            k=2
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа с ID 'nonexistent' не найдена"):
            self.repo.update(nonexistent_group)
    
    def test_update_duplicate_name_raises_error(self):
        """Тест обновления группы с дублирующимся названием"""
        # Arrange
        self.repo.add(self.test_group)
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=3,
            k=4
        )
        self.repo.add(another_group)
        
        updated_group = SystemGroup(
            id="group1",
            name="Другая группа",  # дублирует название group2
            color="#0000FF",
            G=5,
            k=6
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Системная группа 'Другая группа' уже существует"):
            self.repo.update(updated_group)
    
    def test_remove_group_success(self):
        """Тест успешного удаления группы"""
        # Arrange
        self.repo.add(self.test_group)
        
        # Act
        self.repo.remove("group1")
        
        # Assert
        assert len(self.repo.get_all()) == 0
        assert self.repo.get_by_id("group1") is None
        assert self.repo.get_by_name("Тестовая группа") is None
        assert self.repo.get_by_gk(1, 2) is None
    
    def test_remove_nonexistent_group_no_error(self):
        """Тест удаления несуществующей группы (не должен вызывать ошибку)"""
        # Act
        self.repo.remove("nonexistent")
        
        # Assert
        assert len(self.repo.get_all()) == 0
    
    def test_get_all_groups(self):
        """Тест получения всех групп"""
        # Arrange
        group1 = SystemGroup("group1", "Группа 1", "#FF0000", 1, 1)
        group2 = SystemGroup("group2", "Группа 2", "#00FF00", 2, 2)
        
        # Act
        self.repo.add(group1)
        self.repo.add(group2)
        
        # Assert
        all_groups = self.repo.get_all()
        assert len(all_groups) == 2
        assert group1 in all_groups
        assert group2 in all_groups
    
    def test_clear_all(self):
        """Тест очистки всех данных"""
        # Arrange
        group1 = SystemGroup("group1", "Группа 1", "#FF0000", 1, 1)
        group2 = SystemGroup("group2", "Группа 2", "#00FF00", 2, 2)
        self.repo.add(group1)
        self.repo.add(group2)
        
        # Act
        self.repo.clear_all()
        
        # Assert
        assert len(self.repo.get_all()) == 0
        assert len(self.repo._groups) == 0
        assert len(self.repo._by_name) == 0
        assert len(self.repo._by_gk) == 0