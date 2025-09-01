import pytest
from core.entities.law import Law
from core.entities.law_group import LawGroup


class TestEntityValidation:
    """Тесты для валидации сущностей"""
    
    def test_law_group_valid_name_success(self):
        """Тест создания LawGroup с валидным названием"""
        # Act & Assert - не должно вызывать ошибку
        group = LawGroup(
            id="test_group",
            name="Тестовая группа",
            color="#FF0000"
        )
        assert group.name == "Тестовая группа"
    
    def test_law_group_empty_name_raises_error(self):
        """Тест создания LawGroup с пустым названием"""
        # Act & Assert
        with pytest.raises(ValueError, match="Название группы законов не может быть пустым"):
            LawGroup(
                id="test_group",
                name="   ",  # только пробелы
                color="#FF0000"
            )
    
    def test_law_group_whitespace_name_raises_error(self):
        """Тест создания LawGroup с названием из пробелов"""
        # Act & Assert
        with pytest.raises(ValueError, match="Название группы законов не может быть пустым"):
            LawGroup(
                id="test_group",
                name="   ",
                color="#FF0000"
            )
    
    def test_law_group_valid_color_success(self):
        """Тест создания LawGroup с валидным цветом"""
        # Act & Assert - не должно вызывать ошибку
        group = LawGroup(
            id="test_group",
            name="Тестовая группа",
            color="#FF0000"
        )
        assert group.color == "#FF0000"
    
    def test_law_group_invalid_color_format_raises_error(self):
        """Тест создания LawGroup с невалидным форматом цвета"""
        # Act & Assert
        with pytest.raises(ValueError, match="Цвет должен быть в формате #RRGGBB"):
            LawGroup(
                id="test_group",
                name="Тестовая группа",
                color="#FF"  # слишком короткий
            )
    
    def test_law_group_invalid_color_no_hash_raises_error(self):
        """Тест создания LawGroup без # в цвете"""
        # Act & Assert
        with pytest.raises(ValueError, match="Цвет должен быть в формате #RRGGBB"):
            LawGroup(
                id="test_group",
                name="Тестовая группа",
                color="FF0000"  # нет #
            )
    
    def test_law_group_invalid_color_too_long_raises_error(self):
        """Тест создания LawGroup с слишком длинным цветом"""
        # Act & Assert
        with pytest.raises(ValueError, match="Цвет должен быть в формате #RRGGBB"):
            LawGroup(
                id="test_group",
                name="Тестовая группа",
                color="#FF00000"  # слишком длинный
            )
    
    def test_law_valid_name_success(self):
        """Тест создания Law с валидным названием"""
        # Act & Assert - не должно вызывать ошибку
        law = Law(
            name="Закон сохранения энергии",
            formula="E = mc²",
            description="Описание",
            variables=["E", "m", "c", "const"],
            group_id="test_group"
        )
        assert law.name == "Закон сохранения энергии"
    
    def test_law_empty_name_raises_error(self):
        """Тест создания Law с пустым названием"""
        # Act & Assert
        with pytest.raises(ValueError, match="Название закона не может быть пустым"):
            Law(
                name="   ",  # только пробелы
                formula="X = Y",
                description="Описание",
                variables=["X", "Y", "Z", "W"],
                group_id="test_group"
            )
    
    def test_law_whitespace_name_raises_error(self):
        """Тест создания Law с названием из пробелов"""
        # Act & Assert
        with pytest.raises(ValueError, match="Название закона не может быть пустым"):
            Law(
                name="   ",
                formula="X = Y",
                description="Описание",
                variables=["X", "Y", "Z", "W"],
                group_id="test_group"
            )
    
    def test_law_valid_variables_count_success(self):
        """Тест создания Law с правильным количеством переменных"""
        # Act & Assert - не должно вызывать ошибку
        law = Law(
            name="Закон",
            formula="A = B",
            description="Описание",
            variables=["A", "B", "C", "D"],  # ровно 4 переменных
            group_id="test_group"
        )
        assert len(law.variables) == 4
    
    def test_law_too_few_variables_raises_error(self):
        """Тест создания Law с недостаточным количеством переменных"""
        # Act & Assert
        with pytest.raises(ValueError, match="Закон должен содержать ровно 4 переменные"):
            Law(
                name="Закон",
                formula="A = B",
                description="Описание",
                variables=["A", "B", "C"],  # только 3 переменных
                group_id="test_group"
            )
    
    def test_law_too_many_variables_raises_error(self):
        """Тест создания Law с избыточным количеством переменных"""
        # Act & Assert
        with pytest.raises(ValueError, match="Закон должен содержать ровно 4 переменные"):
            Law(
                name="Закон",
                formula="A = B",
                description="Описание",
                variables=["A", "B", "C", "D", "E"],  # 5 переменных
                group_id="test_group"
            )
    
    def test_law_id_generation_success(self):
        """Тест автоматической генерации ID для Law"""
        # Arrange
        law_without_id = Law(
            name="Закон без ID",
            formula="X = Y",
            description="Описание",
            variables=["X", "Y", "Z", "W"],
            group_id="test_group"
        )
        
        # Act & Assert
        assert law_without_id.id is not None
        assert isinstance(law_without_id.id, str)
        assert len(law_without_id.id) > 0  # UUID должен быть не пустым
    
    def test_law_with_predefined_id_success(self):
        """Тест создания Law с предопределенным ID"""
        # Arrange
        predefined_id = "custom-law-id"
        
        # Act
        law = Law(
            name="Закон с ID",
            formula="X = Y",
            description="Описание",
            variables=["X", "Y", "Z", "W"],
            group_id="test_group",
            id=predefined_id
        )
        
        # Assert
        assert law.id == predefined_id
    
    def test_law_get_sorted_variables_success(self):
        """Тест метода get_sorted_variables"""
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
    
    def test_law_group_to_dict_success(self):
        """Тест метода to_dict у LawGroup"""
        # Arrange
        group = LawGroup(
            id="test_group",
            name="Тестовая группа",
            color="#FF0000"
        )
        
        # Act
        result = group.to_dict()
        
        # Assert
        expected = {
            "id": "test_group",
            "name": "Тестовая группа",
            "color": "#FF0000"
        }
        assert result == expected
    
    def test_law_to_dict_success(self):
        """Тест метода to_dict у Law"""
        # Arrange
        law = Law(
            name="Тестовый закон",
            formula="A = B",
            description="Описание",
            variables=["A", "B", "C", "D"],
            group_id="test_group"
        )
        
        # Act
        result = law.to_dict()
        
        # Assert
        expected = {
            "id": law.id,
            "name": "Тестовый закон",
            "formula": "A = B",
            "description": "Описание",
            "variables": ["A", "B", "C", "D"],
            "group_id": "test_group"
        }
        assert result == expected
    
    def test_law_group_from_dict_success(self):
        """Тест метода from_dict у LawGroup"""
        # Arrange
        data = {
            "id": "test_group",
            "name": "Тестовая группа",
            "color": "#FF0000"
        }
        
        # Act
        group = LawGroup.from_dict(data)
        
        # Assert
        assert group.id == "test_group"
        assert group.name == "Тестовая группа"
        assert group.color == "#FF0000"
    
    def test_law_group_from_dict_backward_compatibility(self):
        """Тест обратной совместимости в from_dict у LawGroup"""
        # Arrange - нет ID, только name
        data = {
            "name": "Тестовая группа",
            "color": "#FF0000"
        }
        
        # Act
        group = LawGroup.from_dict(data)
        
        # Assert - ID должен быть взят из name
        assert group.id == "Тестовая группа"
        assert group.name == "Тестовая группа"
        assert group.color == "#FF0000"
    
    def test_law_from_dict_success(self):
        """Тест метода from_dict у Law"""
        # Arrange
        data = {
            "id": "law_id",
            "name": "Тестовый закон",
            "formula": "A = B",
            "description": "Описание",
            "variables": ["A", "B", "C", "D"],
            "group_id": "test_group"
        }
        
        # Act
        law = Law.from_dict(data)
        
        # Assert
        assert law.id == "law_id"
        assert law.name == "Тестовый закон"
        assert law.formula == "A = B"
        assert law.description == "Описание"
        assert law.variables == ["A", "B", "C", "D"]
        assert law.group_id == "test_group"
    
    def test_law_from_dict_with_group_id_override(self):
        """Тест переопределения group_id в from_dict у Law"""
        # Arrange
        data = {
            "name": "Тестовый закон",
            "formula": "A = B",
            "description": "Описание",
            "variables": ["A", "B", "C", "D"],
            "group_id": "original_group"
        }
        
        # Act
        law = Law.from_dict(data, group_id="new_group")
        
        # Assert
        assert law.group_id == "new_group"  # должно использовать переданный group_id