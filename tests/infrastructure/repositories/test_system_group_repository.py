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
    
    def test_update_group_with_gk_change_success(self):
        """Тест обновления группы с изменением G,k без конфликта"""
        # Arrange
        self.repo.add(self.test_group)
        updated_group = SystemGroup(
            id="group1",
            name="Обновленная группа",
            color="#00FF00",
            G=5,  # измененный G
            k=6   # измененный k
        )
        
        # Act
        self.repo.update(updated_group)
        
        # Assert
        assert len(self.repo.get_all()) == 1
        assert self.repo.get_by_id("group1") == updated_group
        assert self.repo.get_by_name("Обновленная группа") == updated_group
        assert self.repo.get_by_gk(5, 6) == updated_group
        assert self.repo.get_by_gk(1, 2) is None
    
    def test_update_group_name_only_success(self):
        """Тест обновления только названия группы"""
        # Arrange
        self.repo.add(self.test_group)
        updated_group = SystemGroup(
            id="group1",
            name="Новое название",
            color="#FF0000",  # тот же цвет
            G=1,              # тот же G
            k=2               # тот же k
        )
        
        # Act
        self.repo.update(updated_group)
        
        # Assert
        assert len(self.repo.get_all()) == 1
        assert self.repo.get_by_id("group1") == updated_group
        assert self.repo.get_by_name("Новое название") == updated_group
        assert self.repo.get_by_gk(1, 2) == updated_group
    
    def test_get_by_gk_not_found(self):
        """Тест поиска группы по G,k, когда она не найдена"""
        # Act
        result = self.repo.get_by_gk(99, 99)
        
        # Assert
        assert result is None
    
    def test_get_by_name_not_found(self):
        """Тест поиска группы по названию, когда она не найдена"""
        # Act
        result = self.repo.get_by_name("Несуществующая группа")
        
        # Assert
        assert result is None
    
    def test_get_by_id_not_found(self):
        """Тест поиска группы по ID, когда она не найдена"""
        # Act
        result = self.repo.get_by_id("nonexistent")
        
        # Assert
        assert result is None