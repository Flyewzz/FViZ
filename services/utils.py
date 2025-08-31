# services/utils.py

def is_quantity_name_used(cell_service, name, exclude=None):
    """Проверить, используется ли имя физической величины"""
    name = name.strip().lower()
    
    # Если это презентер, используем его методы
    if hasattr(cell_service, 'app_model'):
        # Получаем все величины через модель приложения
        all_quantities_dict = cell_service.app_model.get_all_quantities()
        for (L, T), quantities in all_quantities_dict.items():
            for quantity in quantities:
                if quantity.name.strip().lower() == name:
                    if exclude is None or quantity.id != getattr(exclude, 'id', None):
                        return True
        return False
    
    # Старая логика для совместимости
    if hasattr(cell_service, 'get_all_groups'):
        for group in cell_service.get_all_groups():
            for quantity in group.cells.values():
                if quantity.name.strip().lower() == name and quantity is not exclude:
                    return True
    
    return False

def is_group_name_used(groups, name, exclude=None):
    return any(g.name == name and g is not exclude for g in groups)

def is_law_name_used(law_groups, name, exclude=None):
    for group in law_groups:
        for law in group.laws:
            if law.name == name and law is not exclude:
                return True
    return False
