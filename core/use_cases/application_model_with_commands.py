from typing import List, Dict, Tuple, Optional
from core.entities import PhysicalQuantity, SystemGroup, Law
from core.use_cases.physical_quantity_manager import PhysicalQuantityManager
from core.use_cases.system_group_manager import SystemGroupManager
from core.use_cases.law_manager import LawManager, LawGroupManager, ParallelogramLogic
from core.use_cases.command_pattern.delete_quantity_command import DeletePhysicalQuantityCommand
from core.use_cases.command_pattern.command_history import CommandHistory
from core.use_cases.application_model import ApplicationModel


class ApplicationModelWithCommands(ApplicationModel):
    """Главная модель приложения с поддержкой команд для отмены/повтора"""
    
    def __init__(self, quantity_manager: PhysicalQuantityManager, system_group_manager: SystemGroupManager,
                 law_manager: LawManager, law_group_manager: LawGroupManager, parallelogram_logic: ParallelogramLogic):
        super().__init__(quantity_manager, system_group_manager, law_manager, law_group_manager, parallelogram_logic)

        # История команд
        self.command_history = CommandHistory()
    
    # === Операции с физическими величинами ===
    
    def create_physical_quantity(
        self,
        name: str,
        symbol: str,
        unit: str,
        dimension: str,
        L: int,
        T: int,
        group_id: str
    ) -> PhysicalQuantity:
        """Создать физическую величину"""
        return self.quantity_manager.create_quantity(name, symbol, unit, dimension, L, T, group_id)
    
    def update_physical_quantity(
        self,
        old_quantity: PhysicalQuantity,
        name: str,
        symbol: str,
        unit: str,
        dimension: str,
        new_group_id: str
    ) -> PhysicalQuantity:
        """Обновить физическую величину"""
        return self.quantity_manager.update_quantity(old_quantity, name, symbol, unit, dimension, new_group_id)
    
    def delete_physical_quantity_with_command(self, L: int, T: int, group_id: str) -> bool:
        """Удалить физическую величину с поддержкой отмены/повтора"""
        command = DeletePhysicalQuantityCommand(self, L, T, group_id)
        
        # Выполняем команду
        if command.execute():
            # Добавляем в историю
            self.command_history.add_command(command)
            return True
        return False
    
    def delete_physical_quantity(self, L: int, T: int, group_id: str) -> None:
        """Удалить физическую величину (без поддержки отмены/повтора)"""
        self.quantity_manager.delete_quantity(L, T, group_id)
    
    def get_alternative_quantities(self, L: int, T: int, exclude_group_id: str) -> List[PhysicalQuantity]:
        """Получить альтернативные величины для замены"""
        return self.quantity_manager.get_alternatives_for_cell(L, T, exclude_group_id)
    
    def set_visible_quantity(self, L: int, T: int, quantity: PhysicalQuantity) -> None:
        """Установить видимую величину"""
        self.quantity_manager.set_visible_quantity(L, T, quantity)
    
    def get_visible_quantities(self) -> Dict[Tuple[int, int], PhysicalQuantity]:
        """Получить видимые величины"""
        return self.quantity_manager.get_visible_quantities()
    
    # === Операции с системными группами ===
    
    def create_system_group(self, id: str, name: str, color: str, G: int, k: int) -> SystemGroup:
        """Создать системную группу"""
        return self.system_group_manager.create_group(id, name, color, G, k)
    
    def update_system_group(self, group_id: str, name: str, color: str, G: int, k: int) -> SystemGroup:
        """Обновить системную группу"""
        return self.system_group_manager.update_group(group_id, name, color, G, k)
    
    def get_all_system_groups(self) -> List[SystemGroup]:
        """Получить все системные группы"""
        return self.system_group_manager.get_all_groups()
    
    def get_system_group_by_id(self, group_id: str) -> SystemGroup:
        """Получить системную группу по ID"""
        return self.system_group_manager.get_group_by_id(group_id)
    
    def update_group_properties(self, group_id: str, properties: Dict) -> SystemGroup:
        """Обновить свойства группы"""
        group = self.get_system_group_by_id(group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")
        
        # Обновляем свойства
        if 'name' in properties:
            group.name = properties['name']
        if 'color' in properties:
            group.color = properties['color']
        if 'G' in properties:
            group.G = properties['G']
        if 'k' in properties:
            group.k = properties['k']
        
        # Сохраняем изменения
        return self.system_group_manager.update_group(group_id, group.name, group.color, group.G, group.k)
    
    # === Операции с выделением и параллелограммами ===
    
    def toggle_quantity_selection(self, quantity: PhysicalQuantity) -> None:
        """Переключить выделение величины"""
        if quantity in self._selected_quantities:
            self._selected_quantities.remove(quantity)
        else:
            self._selected_quantities.append(quantity)
    
    def get_selected_quantities(self) -> List[PhysicalQuantity]:
        """Получить выделенные величины"""
        return self._selected_quantities.copy()
    
    def clear_selection(self) -> None:
        """Очистить выделение"""
        self._selected_quantities.clear()
    
    def check_parallelogram(self) -> List[PhysicalQuantity]:
        """Проверить параллелограмм из выделенных величин"""
        if len(self._selected_quantities) not in (3, 4):
            return None
        
        return self.parallelogram_logic.check_parallelogram(self._selected_quantities)
    
    # === Операции с законами ===
    
    def find_law_for_selection(self) -> 'Law':
        """Найти закон для текущего выделения"""
        parallelogram = self.check_parallelogram()
        if not parallelogram:
            return None
        
        return self.law_manager.find_law_by_quantities(parallelogram)
    
    def create_law_from_selection(self, name: str, formula: str, description: str, group_id: str) -> 'Law':
        """Создать закон из выделенных величин"""
        parallelogram = self.check_parallelogram()
        if not parallelogram:
            raise ValueError("Выделенные величины не образуют параллелограмм")
        
        variables = [q.name for q in parallelogram]
        return self.law_manager.create_law(name, formula, description, variables, group_id)
    
    def get_all_law_groups(self) -> List['LawGroup']:
        """Получить все группы законов"""
        return self.law_group_manager.get_all_groups()
    
    def get_law_group_by_id(self, group_id: str) -> 'LawGroup':
        """Получить группу законов по ID"""
        return self.law_group_manager.get_group_by_id(group_id)
    
    def create_law_group(self, id: str, name: str, color: str) -> 'LawGroup':
        """Создать группу законов"""
        return self.law_group_manager.create_group(id, name, color)
    
    def update_law_group(self, group_id: str, name: str, color: str) -> 'LawGroup':
        """Обновить группу законов"""
        return self.law_group_manager.update_group(group_id, name, color)
    
    def delete_law_group(self, group_id: str) -> None:
        """Удалить группу законов"""
        self.law_group_manager.delete_group(group_id)
    
    # === Валидация ===
    
    def validate_quantity_name(self, name: str, exclude_quantity: PhysicalQuantity = None) -> bool:
        """Проверить уникальность названия величины"""
        return self.quantity_manager.validate_name_uniqueness(name, exclude_quantity)
    
    def validate_group_name(self, name: str, exclude_id: str = None) -> bool:
        """Проверить уникальность названия группы"""
        return self.system_group_manager.validate_name_uniqueness(name, exclude_id)
    
    def validate_group_gk(self, G: int, k: int, exclude_id: str = None) -> bool:
        """Проверить уникальность комбинации G и k"""
        return self.system_group_manager.validate_gk_uniqueness(G, k, exclude_id)
    
    # === Дополнительные методы ===
    
    def get_quantity_at_position(self, L: int, T: int, group_id: str) -> PhysicalQuantity:
        """Получить физическую величину в позиции для определенной группы"""
        return self.quantity_manager.get_quantity_at_position(L, T, group_id)
    
    def get_used_groups_at_position(self, L: int, T: int) -> List[SystemGroup]:
        """Получить группы, занятые в данной позиции"""
        return self.quantity_manager.get_used_groups_at_position(L, T)
    
    def get_all_quantities(self) -> Dict[Tuple[int, int], List[PhysicalQuantity]]:
        """Получить все физические величины, сгруппированные по координатам"""
        return self.quantity_manager.get_all_quantities_by_position()
    
    def clear_all_data(self) -> None:
        """Очистить все данные приложения"""
        self.quantity_manager.clear_all()
        self.system_group_manager.system_group_repo.clear_all()
        self.law_manager.law_repo.clear_all()
        self.law_group_manager.law_group_repo.clear_all()
        self._selected_quantities.clear()
        self.command_history.clear()
    
    # === Методы проверки зависимостей ===
    
    def check_quantity_dependencies(self, quantity_name: str) -> List[Law]:
        """Проверить, какие законы используют физическую величину по имени"""
        return self.law_manager.law_repo.get_laws_by_variable(quantity_name)
    
    def check_quantity_dependencies_by_entity(self, quantity: PhysicalQuantity) -> List[Law]:
        """Проверить, какие законы используют физическую величину по сущности"""
        return self.check_quantity_dependencies(quantity.name)
    
    def check_group_dependencies(self, group_id: str) -> Dict[str, List]:
        """Проверить зависимости системной группы"""
        dependencies = {
            'quantities': [],
            'laws': [],
            'orphan_laws': []
        }
        
        # Получаем все физические величины в группе
        quantities_in_group = self.quantity_manager.quantity_repo.get_by_group(group_id)
        dependencies['quantities'] = quantities_in_group
        
        # Проверяем законы, использующие эти величины
        all_laws = []
        for quantity in quantities_in_group:
            laws = self.check_quantity_dependencies(quantity.name)
            all_laws.extend(laws)
        
        # Убираем дубликаты по ID закона
        unique_laws = []
        seen_ids = set()
        for law in all_laws:
            if law.id not in seen_ids:
                unique_laws.append(law)
                seen_ids.add(law.id)
        
        dependencies['laws'] = unique_laws
        
        return dependencies
    
    def check_cell_dependencies(self, L: int, T: int, group_id: str) -> Dict:
        """Проверить зависимости конкретной соты"""
        dependencies = {
            'quantity': None,
            'laws': [],
            'is_empty': True
        }
        
        # Получаем физическую величину в соте
        quantity = self.quantity_manager.get_quantity_at_position(L, T, group_id)
        
        if quantity:
            dependencies['quantity'] = quantity
            dependencies['is_empty'] = False
            
            # Проверяем законы, использующие эту величину
            laws = self.check_quantity_dependencies(quantity.name)
            dependencies['laws'] = laws
        
        return dependencies
    
    def check_law_dependencies(self, law: Law) -> Dict[str, List]:
        """Проверить зависимости закона"""
        dependencies = {
            'quantities': [],
            'related_laws': []
        }
        
        # Получаем физические величины, используемые в законе
        for var_name in law.variables:
            quantity = self.quantity_manager.quantity_repo.get_by_name(var_name)
            if quantity:
                dependencies['quantities'].append(quantity)
        
        # Проверяем, есть ли другие законы, использующие те же величины
        for quantity in dependencies['quantities']:
            related_laws = self.check_quantity_dependencies(quantity.name)
            for related_law in related_laws:
                if related_law != law:
                    dependencies['related_laws'].append(related_law)
        
        # Убираем дубликаты
        dependencies['related_laws'] = list(set(dependencies['related_laws']))
        
        return dependencies
    
    def detect_orphan_laws(self) -> List[Law]:
        """Обнаружить "осиротевшие" законы - законы, ссылающиеся на несуществующие величины"""
        orphan_laws = []
        all_laws = self.law_manager.law_repo.get_all_laws()
        
        for law in all_laws:
            is_orphan = False
            for var_name in law.variables:
                quantity = self.quantity_manager.quantity_repo.get_by_name(var_name)
                if not quantity:
                    is_orphan = True
                    break
            
            if is_orphan:
                orphan_laws.append(law)
        
        return orphan_laws
    
    # === Каскадные методы удаления ===
    
    def delete_cell_cascade(self, L: int, T: int, group_id: str) -> Dict:
        """Удалить соту с каскадным удалением связанных законов
        
        Args:
            L: Координата L
            T: Координата T
            group_id: ID системной группы
            
        Returns:
            Dict: Результат операции с информацией об удаленных объектах
        """
        result = {
            'action': 'delete_cell',
            'coordinates': (L, T),
            'group_id': group_id,
            'deleted_quantity': None,
            'deleted_laws': [],
            'success': True,
            'error': None
        }
        
        try:
            # Проверяем существование группы
            group = self.system_group_manager.get_group_by_id(group_id)
            if not group:
                raise ValueError(f'Системная группа с ID "{group_id}" не существует')
            
            # Проверяем зависимости
            dependencies = self.check_cell_dependencies(L, T, group_id)
            
            if dependencies['is_empty']:
                # Пустая сота - проверяем, есть ли запись для удаления
                try:
                    self.quantity_manager.delete_quantity(L, T, group_id)
                    result['message'] = 'Пустая сота успешно удалена'
                except ValueError:
                    # Записи не было - просто считаем, что сота удалена
                    result['message'] = 'Пустая сота успешно удалена (не было записи)'
            else:
                # Сота содержит физическую величину
                quantity = dependencies['quantity']
                
                # Удаляем связанные законы
                if dependencies['laws']:
                    for law in dependencies['laws']:
                        self.law_manager.law_repo.remove_law(law)
                        result['deleted_laws'].append({
                            'id': law.id,
                            'name': law.name,
                            'variables': law.variables
                        })
                
                # Удаляем физическую величину
                self.quantity_manager.delete_quantity(L, T, group_id)
                result['deleted_quantity'] = {
                    'name': quantity.name,
                    'coordinates': (quantity.L, quantity.T),
                    'group_id': quantity.group_id
                }
                
                if dependencies['laws']:
                    result['message'] = f'Удалена величина "{quantity.name}" и {len(dependencies["laws"])} законов'
                else:
                    result['message'] = f'Удалена величина "{quantity.name}"'
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['message'] = f'Ошибка при удалении соты: {e}'
        
        return result
    
    def delete_quantity_cascade(self, quantity_name: str) -> Dict:
        """Удалить физическую величину по имени с каскадным удалением законов
        
        Args:
            quantity_name: Имя физической величины
            
        Returns:
            Dict: Результат операции с информацией об удаленных объектах
        """
        result = {
            'action': 'delete_quantity',
            'quantity_name': quantity_name,
            'deleted_quantities': [],
            'deleted_laws': [],
            'success': True,
            'error': None
        }
        
        try:
            # Находим все физические величины с таким именем (в разных группах)
            all_quantities = self.quantity_manager.quantity_repo.get_all()
            quantities_to_delete = [q for q in all_quantities if q.name == quantity_name]
            
            if not quantities_to_delete:
                raise ValueError(f'Физическая величина с именем "{quantity_name}" не найдена')
            
            # Проверяем зависимости
            laws_to_delete = self.check_quantity_dependencies(quantity_name)
            
            # Удаляем законы, использующие эту величину
            for law in laws_to_delete:
                self.law_manager.law_repo.remove_law(law)
                result['deleted_laws'].append({
                    'id': law.id,
                    'name': law.name,
                    'variables': law.variables
                })
            
            # Удаляем все физические величины с таким именем
            for quantity in quantities_to_delete:
                self.quantity_manager.delete_quantity(quantity.L, quantity.T, quantity.group_id)
                result['deleted_quantities'].append({
                    'name': quantity.name,
                    'coordinates': (quantity.L, quantity.T),
                    'group_id': quantity.group_id
                })
            
            result['message'] = f'Удалено {len(quantities_to_delete)} величин(ы) и {len(laws_to_delete)} законов'
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['message'] = f'Ошибка при удалении величины: {e}'
        
        return result
    
    def delete_system_group_cascade(self, group_id: str) -> Dict:
        """Удалить системную группу с каскадным удалением связанных ФВ и законов
        
        Args:
            group_id: ID системной группы
            
        Returns:
            Dict: Результат операции с информацией об удаленных объектах
        """
        result = {
            'action': 'delete_system_group',
            'group_id': group_id,
            'deleted_quantities': [],
            'deleted_laws': [],
            'deleted_group': None,
            'success': True,
            'error': None
        }
        
        try:
            # Проверяем существование группы
            group = self.system_group_manager.get_group_by_id(group_id)
            if not group:
                raise ValueError(f'Системная группа с ID "{group_id}" не существует')
            
            # Проверяем зависимости
            dependencies = self.check_group_dependencies(group_id)
            
            # Удаляем законы, использующие величины из этой группы
            for law in dependencies['laws']:
                self.law_manager.law_repo.remove_law(law)
                result['deleted_laws'].append({
                    'id': law.id,
                    'name': law.name,
                    'variables': law.variables
                })
            
            # Удаляем физические величины из этой группы
            for quantity in dependencies['quantities']:
                self.quantity_manager.delete_quantity(quantity.L, quantity.T, quantity.group_id)
                result['deleted_quantities'].append({
                    'name': quantity.name,
                    'coordinates': (quantity.L, quantity.T),
                    'group_id': quantity.group_id
                })
            
            # Удаляем саму группу
            self.system_group_manager.system_group_repo.remove_group(group_id)
            result['deleted_group'] = {
                'id': group.id,
                'name': group.name,
                'color': group.color,
                'G': group.G,
                'k': group.k
            }
            
            result['message'] = f'Удалена группа "{group.name}" с {len(dependencies["quantities"])} величинами и {len(dependencies["laws"])} законами'
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['message'] = f'Ошибка при удалении группы: {e}'
        
        return result
    
    # === Методы управления историей команд ===
    
    def undo_last_action(self) -> bool:
        """Отменить последнее действие"""
        return self.command_history.undo()
    
    def redo_last_action(self) -> bool:
        """Повторить последнее отмененное действие"""
        return self.command_history.redo()
    
    def can_undo(self) -> bool:
        """Проверить, можно ли отменить действие"""
        return self.command_history.can_undo()
    
    def can_redo(self) -> bool:
        """Проверить, можно ли повторить действие"""
        return self.command_history.can_redo()
    
    def get_undo_description(self) -> Optional[str]:
        """Получить описание действия для отмены"""
        return self.command_history.get_undo_description()
    
    def get_redo_description(self) -> Optional[str]:
        """Получить описание действия для повтора"""
        return self.command_history.get_redo_description()
    
    def clear_command_history(self) -> None:
        """Очистить историю команд"""
        self.command_history.clear()