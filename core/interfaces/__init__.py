# Core interfaces exports
from .physical_quantity_repository import IPhysicalQuantityRepository
from .system_group_repository import ISystemGroupRepository
from .law_repository import ILawRepository, ILawGroupRepository

__all__ = [
    'IPhysicalQuantityRepository',
    'ISystemGroupRepository',
    'ILawRepository',
    'ILawGroupRepository'
]
