import pytest
from core.entities.physical_quantity import PhysicalQuantity
from core.entities.system_group import SystemGroup
from infrastructure.repositories.physical_quantity_repository import PhysicalQuantityRepositoryImpl


class TestPhysicalQuantityRepositoryImpl:
    """Тесты для PhysicalQuantityRepositoryImpl"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.repo = PhysicalQuantityRepositoryImpl()
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
    
    def test_save_quantity_success(self):
        """Тест успешного сохранения величины"""
        # Act
        self.repo.save(self.test_quantity)
        
        # Assert
        quantities = self.repo.find_all()
        assert len(quantities) == 1
        assert self.test_quantity in quantities
        
        # Проверка поиска по позиции
        found_quantity = self.repo.find_by_position(1, 0, "group1")
        assert found_quantity == self.test_quantity
        
        # Проверка поиска по группе
        group_quantities = self.repo.find_all_by_group("group1")
        assert len(group_quantities) == 1
        assert self.test_quantity in group_quantities
    
    def test_save_multiple_quantities_same_group(self):
        """Тест сохранения нескольких величин в одной группе"""
        # Arrange
        quantity2 = PhysicalQuantity(
            name="Время",
            symbol="t",
            unit="с",
            dimension="T",
            L=0,
            T=1,
            group_id="group1"
        )
        
        # Act
        self.repo.save(self.test_quantity)
        self.repo.save(quantity2)
        
        # Assert
        quantities = self.repo.find_all()
        assert len(quantities) == 2
        assert self.test_quantity in quantities
        assert quantity2 in quantities
        
        group_quantities = self.repo.find_all_by_group("group1")
        assert len(group_quantities) == 2
    
    def test_save_quantities_different_groups(self):
        """Тест сохранения величин в разных группах"""
        # Arrange
        another_group = SystemGroup(
            id="group2",
            name="Другая группа",
            color="#00FF00",
            G=3,
            k=4
        )
        quantity2 = PhysicalQuantity(
            name="Масса",
            symbol="m",
            unit="кг",
            dimension="M",
            L=0,
            T=0,
            group_id="group2"
        )
        
        # Act
        self.repo.save(self.test_quantity)
        self.repo.save(quantity2)
        
        # Assert
        quantities = self.repo.find_all()
        assert len(quantities) == 2
        
        # Проверка поиска по группам
        group1_quantities = self.repo.find_all_by_group("group1")
        group2_quantities = self.repo.find_all_by_group("group2")
        assert len(group1_quantities) == 1
        assert len(group2_quantities) == 1
        assert self.test_quantity in group1_quantities
        assert quantity2 in group2_quantities
    
    def test_find_by_position_not_found(self):
        """Тест поиска величины по позиции, когда она не найдена"""
        # Act
        result = self.repo.find_by_position(99, 99, "group1")
        
        # Assert
        assert result is None
    
    def test_find_all_by_position(self):
        """Тест поиска всех величин в данной позиции"""
        # Arrange
        quantity2 = PhysicalQuantity(
            name="Скорость",
            symbol="v",
            unit="м/с",
            dimension="LT⁻¹",
            L=1,  # та же позиция L
            T=0,  # та же позиция T
            group_id="group2"  # другая группа
        )
        
        # Act
        self.repo.save(self.test_quantity)
        self.repo.save(quantity2)
        
        # Assert
        result = self.repo.find_all_by_position(1, 0)
        assert len(result) == 2
        assert self.test_quantity in result
        assert quantity2 in result
    
    def test_find_by_name_success(self):
        """Тест поиска величины по имени"""
        # Act
        self.repo.save(self.test_quantity)
        
        # Assert
        found_quantity = self.repo.find_by_name("Длина")
        assert found_quantity == self.test_quantity
    
    def test_find_by_name_not_found(self):
        """Тест поиска величины по имени, когда она не найдена"""
        # Act
        result = self.repo.find_by_name("Несуществующая величина")
        
        # Assert
        assert result is None
    
    def test_remove_quantity_success(self):
        """Тест успешного удаления величины"""
        # Arrange
        self.repo.save(self.test_quantity)
        
        # Act
        self.repo.remove(1, 0, "group1")
        
        # Assert
        quantities = self.repo.find_all()
        assert len(quantities) == 0
        
        found_quantity = self.repo.find_by_position(1, 0, "group1")
        assert found_quantity is None
    
    def test_remove_nonexistent_quantity_no_error(self):
        """Тест удаления несуществующей величины (не должен вызывать ошибку)"""
        # Act
        self.repo.remove(99, 99, "group1")
        
        # Assert
        quantities = self.repo.find_all()
        assert len(quantities) == 0
    
    def test_update_quantity_success(self):
        """Тест успешного обновления величины"""
        # Arrange
        self.repo.save(self.test_quantity)
        updated_quantity = PhysicalQuantity(
            name="Обновленная длина",
            symbol="L'",
            unit="м",
            dimension="L",
            L=1,
            T=0,
            group_id="group1"
        )
        
        # Act
        self.repo.update(self.test_quantity, updated_quantity)
        
        # Assert
        quantities = self.repo.find_all()
        assert len(quantities) == 1
        assert updated_quantity in quantities
        assert self.test_quantity not in quantities
        
        found_quantity = self.repo.find_by_name("Обновленная длина")
        assert found_quantity == updated_quantity
    
    def test_get_all_quantities_by_position(self):
        """Тест получения всех величин, сгруппированных по позициям"""
        # Arrange
        quantity2 = PhysicalQuantity(
            name="Время",
            symbol="t",
            unit="с",
            dimension="T",
            L=0,
            T=1,
            group_id="group1"
        )
        
        # Act
        self.repo.save(self.test_quantity)
        self.repo.save(quantity2)
        
        # Assert
        result = self.repo.get_all_quantities_by_position()
        assert len(result) == 2
        assert (1, 0) in result
        assert (0, 1) in result
        assert len(result[(1, 0)]) == 1
        assert len(result[(0, 1)]) == 1
    
    def test_visible_quantities_functionality(self):
        """Тест работы с видимыми величинами"""
        # Arrange
        another_quantity = PhysicalQuantity(
            name="Масса",
            symbol="m",
            unit="кг",
            dimension="M",
            L=2,
            T=2,
            group_id="group1"
        )
        
        # Act
        self.repo.set_visible_quantity(1, 0, self.test_quantity)
        self.repo.set_visible_quantity(2, 2, another_quantity)
        
        # Assert
        visible_quantity = self.repo.get_visible_quantity(1, 0)
        assert visible_quantity == self.test_quantity
        
        visible_quantity_2 = self.repo.get_visible_quantity(2, 2)
        assert visible_quantity_2 == another_quantity
        
        all_visible = self.repo.get_all_visible_quantities()
        assert len(all_visible) == 2
        assert (1, 0) in all_visible
        assert (2, 2) in all_visible
        
        # Test removing visible quantity
        self.repo.remove_visible_quantity(1, 0)
        assert self.repo.get_visible_quantity(1, 0) is None
        assert len(self.repo.get_all_visible_quantities()) == 1
    
    def test_clear_all(self):
        """Тест очистки всех данных"""
        # Arrange
        quantity2 = PhysicalQuantity(
            name="Время",
            symbol="t",
            unit="с",
            dimension="T",
            L=0,
            T=1,
            group_id="group1"
        )
        self.repo.save(self.test_quantity)
        self.repo.save(quantity2)
        self.repo.set_visible_quantity(1, 0, self.test_quantity)
        
        # Act
        self.repo.clear_all()
        
        # Assert
        assert len(self.repo.find_all()) == 0
        assert len(self.repo._quantities_by_group) == 0
        assert len(self.repo._visible_quantities) == 0
    
    def test_interface_methods_compatibility(self):
        """Тест совместимости с методами интерфейса"""
        # Arrange
        self.repo.save(self.test_quantity)
        
        # Test interface methods
        all_quantities = self.repo.get_all()
        assert len(all_quantities) == 1
        
        by_id = self.repo.get_by_id("Длина")
        assert by_id == self.test_quantity
        
        by_name = self.repo.get_by_name("Длина")
        assert by_name == self.test_quantity
        
        by_coordinates = self.repo.get_by_coordinates(1, 0, "group1")
        assert by_coordinates == self.test_quantity
        
        by_group = self.repo.get_by_group("group1")
        assert len(by_group) == 1
        assert self.test_quantity in by_group
        
        # Test exists_by_name
        exists = self.repo.exists_by_name("Длина")
        assert exists is True
        
        not_exists = self.repo.exists_by_name("Несуществующая")
        assert not_exists is False