# services/utils.py

def is_quantity_name_used(cell_service, name, exclude=None):
    name = name.strip().lower()
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