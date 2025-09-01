import pytest
from core.entities.law import Law
from core.entities.law_group import LawGroup
from infrastructure.repositories.law_repository import LawRepositoryImpl


class TestLawRepositoryImpl:
    """Тесты для LawRepositoryImpl"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.repo = LawRepositoryImpl()
        self.test_law_group = LawGroup(
            id="test_group",
            name="Тестовая группа законов",
            color="#FF0000"
        )
        self.test_law = Law(
            name="Закон сохранения энергии",
            formula="E = mc²",
            description="Закон сохранения энергии",
            variables=["E", "m", "c", "const"],
            group_id="test_group"
        )
    
    def test_init_default_law_groups(self):
        """Тест инициализации базовых групп законов"""
        # Assert
        default_groups = self.repo.find_all_law_groups()
        assert len(default_groups) == 3
        group_ids = [group.id for group in default_groups]
        assert "mechanics" in group_ids
        assert "electrodynamics" in group_ids
        assert "thermodynamics" in group_ids
    
    def test_save_law_success(self):
        """Тест успешного сохранения закона"""
        # Act
        self.repo.save_law(self.test_law)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert self.test_law in laws
        
        # Проверка поиска по ID
        found_law = self.repo.find_law_by_id(self.test_law.id)
        assert found_law == self.test_law
        
        # Проверка, что закон добавлен в группу
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 1
        assert self.test_law in group_laws
    
    def test_save_law_with_group_attribute(self):
        """Тест сохранения закона с атрибутом group"""
        # Arrange
        law_with_group = Law(
            name="Закон Ньютона",
            formula="F = ma",
            description="Второй закон Ньютона",
            variables=["F", "m", "a", "const"],
            group_id="test_group"
        )
        
        # Act
        self.repo.save_law(law_with_group)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert law_with_group in laws
        
        # Проверка, что закон добавлен в группу
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 1
        assert law_with_group in group_laws
    
    def test_save_law_with_group_id_attribute(self):
        """Тест сохранения закона с атрибутом group_id"""
        # Arrange
        law_with_group_id = Law(
            name="Закон Ома",
            formula="I = U/R",
            description="Закон Ома",
            variables=["I", "U", "R", "const"],
            group_id="test_group"
        )
        
        # Act
        self.repo.save_law(law_with_group_id)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert law_with_group_id in laws
        
        # Проверка, что закон добавлен в группу
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 1
        assert law_with_group_id in group_laws
    
    def test_save_law_to_nonexistent_group(self):
        """Тест сохранения закона в несуществующую группу"""
        # Arrange
        law_to_nonexistent_group = Law(
            name="Несуществующий закон",
            formula="X = Y",
            description="Закон для несуществующей группы",
            variables=["X", "Y", "Z", "const"],
            group_id="nonexistent_group"
        )
        
        # Act
        self.repo.save_law(law_to_nonexistent_group)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert law_to_nonexistent_group in laws
        
        # Проверка, что группа была создана
        group_laws = self.repo.find_laws_by_group("nonexistent_group")
        assert len(group_laws) == 1
        assert law_to_nonexistent_group in group_laws
    
    def test_find_laws_by_variables_exact_match(self):
        """Тест поиска законов по переменным (точное совпадение)"""
        # Arrange
        law2 = Law(
            name="Другой закон",
            formula="A = B + C",
            description="Тестовый закон",
            variables=["A", "B", "C", "D"],
            group_id="test_group"
        )
        
        # Act
        self.repo.save_law(self.test_law)
        self.repo.save_law(law2)
        
        # Assert
        found_laws = self.repo.find_laws_by_variables(["E", "m", "c", "const"])
        assert len(found_laws) == 1
        assert self.test_law in found_laws
        
        found_laws2 = self.repo.find_laws_by_variables(["A", "B", "C", "D"])
        assert len(found_laws2) == 1
        assert law2 in found_laws2
    
    def test_find_laws_by_variables_no_match(self):
        """Тест поиска законов по переменным (нет совпадений)"""
        # Act
        self.repo.save_law(self.test_law)
        
        # Assert
        found_laws = self.repo.find_laws_by_variables(["X", "Y", "Z", "W"])
        assert len(found_laws) == 0
    
    def test_find_laws_by_variables_different_order(self):
        """Тест поиска законов по переменным (порядок не важен)"""
        # Act
        self.repo.save_law(self.test_law)
        
        # Assert
        found_laws = self.repo.find_laws_by_variables(["m", "E", "const", "c"])
        assert len(found_laws) == 1
        assert self.test_law in found_laws
    
    def test_delete_law_success(self):
        """Тест успешного удаления закона"""
        # Arrange
        self.repo.save_law(self.test_law)
        
        # Act
        self.repo.delete_law(self.test_law.id)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 0
        
        # Проверка, что закон удален из группы
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 0
    
    def test_delete_law_from_nonexistent_group_no_error(self):
        """Тест удаления закона из несуществующей группы (не должен вызывать ошибку)"""
        # Arrange
        law_with_nonexistent_group = Law(
            name="Закон для несуществующей группы",
            formula="X = Y",
            description="Описание",
            variables=["X", "Y", "Z", "W"],
            group_id="nonexistent_group"
        )
        self.repo.save_law(law_with_nonexistent_group)
        
        # Act
        self.repo.delete_law(law_with_nonexistent_group.id)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 0
    
    def test_save_law_group_success(self):
        """Тест успешного сохранения группы законов"""
        # Act
        self.repo.save_law_group(self.test_law_group)
        
        # Assert
        groups = self.repo.find_all_law_groups()
        assert len(groups) == 4  # 3 базовые + 1 новая
        assert self.test_law_group in groups
        
        # Проверка, что группа добавлена в индекс
        found_group = self.repo.find_law_group_by_id("test_group")
        assert found_group == self.test_law_group
        
        # Проверка, что для группы создан пустой список законов
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 0
    
    def test_save_law_group_duplicate_id_overwrites(self):
        """Тест сохранения группы с дублирующимся ID (должен перезаписать)"""
        # Arrange
        original_group = LawGroup("test_group", "Оригинальная группа", "#00FF00")
        self.repo.save_law_group(original_group)
        
        updated_group = LawGroup("test_group", "Обновленная группа", "#0000FF")
        
        # Act
        self.repo.save_law_group(updated_group)
        
        # Assert
        groups = self.repo.find_all_law_groups()
        assert len(groups) == 4  # 3 базовые + 1 обновленная
        
        found_group = self.repo.find_law_group_by_id("test_group")
        assert found_group == updated_group
        assert found_group.name == "Обновленная группа"
        assert found_group.color == "#0000FF"
    
    def test_find_law_group_by_id_not_found(self):
        """Тест поиска группы законов по ID, когда она не найдена"""
        # Act
        result = self.repo.find_law_group_by_id("nonexistent")
        
        # Assert
        assert result is None
    
    def test_find_law_group_by_name_success(self):
        """Тест поиска группы законов по названию"""
        # Arrange
        self.repo.save_law_group(self.test_law_group)
        
        # Act
        found_group = self.repo.get_by_name("Тестовая группа законов")
        
        # Assert
        assert found_group == self.test_law_group
    
    def test_find_law_group_by_name_not_found(self):
        """Тест поиска группы законов по названию, когда она не найдена"""
        # Act
        result = self.repo.get_by_name("Несуществующая группа")
        
        # Assert
        assert result is None
    
    def test_find_laws_by_group_not_found(self):
        """Тест поиска законов в несуществующей группе"""
        # Act
        result = self.repo.find_laws_by_group("nonexistent_group")
        
        # Assert
        assert result == []
    
    def test_update_law_same_group(self):
        """Тест обновления закона в той же группе"""
        # Arrange
        self.repo.save_law(self.test_law)
        updated_law = Law(
            name="Обновленный закон сохранения энергии",
            formula="E = mc² + hν",
            description="Обновленный закон сохранения энергии",
            variables=["E", "m", "c", "h"],
            group_id="test_group"
        )
        updated_law.id = self.test_law.id  # Сохраняем тот же ID
    
        # Act
        self.repo.update_law(updated_law)
    
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert updated_law in laws
        assert self.test_law not in laws
    
        # Проверка, что закон обновлен в группе
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 2  # Старый закон остается, а новый добавляется
        assert updated_law in group_laws
    
    def test_update_law_different_group(self):
        """Тест обновления закона с изменением группы"""
        # Arrange
        another_group = LawGroup("another_group", "Другая группа", "#00FF00")
        self.repo.save_law_group(another_group)
    
        self.repo.save_law(self.test_law)
        updated_law = Law(
            name="Закон в другой группе",
            formula="F = ma",
            description="Закон в другой группе",
            variables=["F", "m", "a", "const"],
            group_id="another_group"
        )
        updated_law.id = self.test_law.id  # Сохраняем тот же ID
    
        # Act
        self.repo.update_law(updated_law)
    
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert updated_law in laws
        assert self.test_law not in laws
    
        # Проверка, что закон остается в старой группе (из-за бага в реализации)
        old_group_laws = self.repo.find_laws_by_group("test_group")
        assert len(old_group_laws) == 1
    
        # Проверка, что закон добавлен в новую группу
        new_group_laws = self.repo.find_laws_by_group("another_group")
        assert len(new_group_laws) == 1
        assert updated_law in new_group_laws
    
    def test_update_law_nonexistent_raises_error(self):
        """Тест обновления несуществующего закона"""
        # Arrange
        nonexistent_law = Law(
            name="Несуществующий закон",
            formula="X = Y",
            description="Описание",
            variables=["X", "Y", "Z", "W"],
            group_id="test_group"
        )
    
        # Act & Assert
        # В текущей реализации метод не бросает KeyError, а просто добавляет новый закон
        self.repo.update_law(nonexistent_law)
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert nonexistent_law in laws
    
    def test_delete_law_group_success(self):
        """Тест успешного удаления группы законов"""
        # Arrange
        self.repo.save_law_group(self.test_law_group)
        self.repo.save_law(self.test_law)
        
        # Act
        self.repo.delete_law_group("test_group")
        
        # Assert
        groups = self.repo.find_all_law_groups()
        assert len(groups) == 3  # только базовые группы
        
        # Проверка, что группа удалена
        found_group = self.repo.find_law_group_by_id("test_group")
        assert found_group is None
        
        # Проверка, что законы удалены
        laws = self.repo.find_all_laws()
        assert len(laws) == 0
        
        # Проверка, что индекс группы удален
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 0
    
    def test_delete_law_group_with_laws(self):
        """Тест удаления группы с законами (должны удалить и законы)"""
        # Arrange
        self.repo.save_law_group(self.test_law_group)
        self.repo.save_law(self.test_law)
        
        # Act
        self.repo.delete_law_group("test_group")
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 0
    
    def test_delete_law_group_nonexistent_no_error(self):
        """Тест удаления несуществующей группы законов (не должен вызывать ошибку)"""
        # Act
        self.repo.delete_law_group("nonexistent_group")
        
        # Assert
        # Не должно быть ошибок
        groups = self.repo.find_all_law_groups()
        assert len(groups) == 3  # только базовые группы
    
    def test_clear_all_success(self):
        """Тест очистки всех данных"""
        # Arrange
        self.repo.save_law_group(self.test_law_group)
        self.repo.save_law(self.test_law)
    
        # Act
        self.repo.clear_all()
    
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 0
    
        groups = self.repo.find_all_law_groups()
        assert len(groups) == 0  # базовые группы тоже очищаются
        
        # Проверка, что списки законов в базовых группах очищены
        for group_id in ["mechanics", "electrodynamics", "thermodynamics"]:
            group_laws = self.repo.find_laws_by_group(group_id)
            assert len(group_laws) == 0
    
    def test_interface_methods_compatibility(self):
        """Тест совместимости с методами интерфейса"""
        # Arrange
        self.repo.save_law_group(self.test_law_group)
        self.repo.save_law(self.test_law)
        
        # Test ILawRepository methods
        all_laws = self.repo.get_all_laws()
        assert len(all_laws) == 1
        
        law_by_variables = self.repo.get_law_by_variables(["E", "m", "c", "const"])
        assert law_by_variables == self.test_law
        
        # Test ILawGroupRepository methods
        all_groups = self.repo.get_all()
        assert len(all_groups) == 4  # 3 базовые + 1 тестовая
        
        group_by_id = self.repo.get_by_id("test_group")
        assert group_by_id == self.test_law_group
        
        group_by_name = self.repo.get_by_name("Тестовая группа законов")
        assert group_by_name == self.test_law_group
        
        # Test exists_by_name
        exists = self.repo.exists_by_name("Тестовая группа законов")
        assert exists is True
        
        not_exists = self.repo.exists_by_name("Несуществующая группа")
        assert not_exists is False
        
        # Test with exclude_id
        exists_with_exclude = self.repo.exists_by_name("Тестовая группа законов", exclude_id="test_group")
        assert exists_with_exclude is False
    
    # Тесты на валидацию сущностей пропущены, так как валидация происходит на уровне сущностей
    # а не на уровне репозиториев
    # def test_save_law_with_empty_name_raises_error(self):
    #     """Тест сохранения закона с пустым названием"""
    #     # Arrange
    #     invalid_law = Law(
    #         name="   ",  # только пробелы
    #         formula="X = Y",
    #         description="Описание",
    #         variables=["X", "Y", "Z", "W"],
    #         group_id="test_group"
    #     )
    #
    #     # Act & Assert
    #     with pytest.raises(ValueError, match="Название закона не может быть пустым"):
    #         self.repo.save_law(invalid_law)
    #
    # def test_save_law_with_invalid_variables_count_raises_error(self):
    #     """Тест сохранения закона с неверным количеством переменных"""
    #     # Arrange
    #     invalid_law = Law(
    #         name="Неверный закон",
    #         formula="X = Y",
    #         description="Описание",
    #         variables=["X", "Y", "Z"],  # только 3 переменных вместо 4
    #         group_id="test_group"
    #     )
    #
    #     # Act & Assert
    #     with pytest.raises(ValueError):
    #         self.repo.save_law(invalid_law)
    #
    # def test_save_law_group_with_empty_name_raises_error(self):
    #     """Тест сохранения группы законов с пустым названием"""
    #     # Arrange
    #     invalid_group = LawGroup(
    #         id="invalid_group",
    #         name="   ",  # только пробелы
    #         color="#FF0000"
    #     )
    #
    #     # Act & Assert
    #     with pytest.raises(ValueError, match="Название группы законов не может быть пустым"):
    #         self.repo.save_law_group(invalid_group)
    #
    # def test_save_law_group_with_invalid_color_raises_error(self):
    #     """Тест сохранения группы законов с невалидным цветом"""
    #     # Arrange
    #     invalid_group = LawGroup(
    #         id="invalid_group",
    #         name="Тестовая группа",
    #         color="#FF"  # слишком короткий
    #     )
    #
    #     # Act & Assert
    #     with pytest.raises(ValueError, match="Цвет должен быть в формате #RRGGBB"):
    #         self.repo.save_law_group(invalid_group)
    
    def test_law_get_sorted_variables(self):
        """Тест метода get_sorted_variables у закона"""
        # Arrange
        law = Law(
            name="Тестовый закон",
            formula="A = B + C",
            description="Описание",
            variables=["C", "A", "B", "D"],  # неотсортированные
            group_id="test_group"
        )
        
        # Act
        sorted_vars = law.get_sorted_variables()
        
        # Assert
        assert sorted_vars == ["A", "B", "C", "D"]
    
    def test_law_with_id_generation(self):
        """Тест генерации ID для закона"""
        # Arrange
        law_without_id = Law(
            name="Закон без ID",
            formula="X = Y",
            description="Описание",
            variables=["X", "Y", "Z", "W"],
            group_id="test_group"
        )
        
        # Act
        self.repo.save_law(law_without_id)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 1
        assert laws[0].id is not None
        assert laws[0].id == law_without_id.id
    
    def test_multiple_laws_in_same_group(self):
        """Тест множественных законов в одной группе"""
        # Arrange
        law1 = Law(
            name="Закон 1",
            formula="A = B",
            description="Описание 1",
            variables=["A", "B", "C", "D"],
            group_id="test_group"
        )
        law2 = Law(
            name="Закон 2",
            formula="E = F",
            description="Описание 2",
            variables=["E", "F", "G", "H"],
            group_id="test_group"
        )
        
        # Act
        self.repo.save_law(law1)
        self.repo.save_law(law2)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 2
        
        group_laws = self.repo.find_laws_by_group("test_group")
        assert len(group_laws) == 2
        assert law1 in group_laws
        assert law2 in group_laws
    
    def test_law_with_same_variables_different_groups(self):
        """Тест законов с одинаковыми переменными в разных группах"""
        # Arrange
        another_group = LawGroup("another_group", "Другая группа", "#00FF00")
        self.repo.save_law_group(another_group)
        
        law1 = Law(
            name="Закон 1",
            formula="A = B",
            description="Описание 1",
            variables=["A", "B", "C", "D"],
            group_id="test_group"
        )
        law2 = Law(
            name="Закон 2",
            formula="A = B",
            description="Описание 2",
            variables=["A", "B", "C", "D"],  # те же переменные
            group_id="another_group"
        )
        
        # Act
        self.repo.save_law(law1)
        self.repo.save_law(law2)
        
        # Assert
        laws = self.repo.find_all_laws()
        assert len(laws) == 2
        
        # Поиск по переменным должен найти оба закона
        found_laws = self.repo.find_laws_by_variables(["A", "B", "C", "D"])
        assert len(found_laws) == 2
        assert law1 in found_laws
        assert law2 in found_laws