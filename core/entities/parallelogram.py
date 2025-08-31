from dataclasses import dataclass
from typing import List, Optional, Set
from .physical_quantity import PhysicalQuantity


@dataclass
class Parallelogram:
    """
    Параллелограмм из физических величин для создания законов.
    Содержит логику проверки корректности параллелограмма.
    """
    quantities: List[PhysicalQuantity]
    law_group_id: Optional[str] = None
    
    def __post_init__(self):
        if len(self.quantities) not in (3, 4):
            raise ValueError("Параллелограмм должен содержать 3 или 4 физические величины")
    
    @property
    def is_valid(self) -> bool:
        """Проверяет, образуют ли величины корректный параллелограмм"""
        if len(self.quantities) == 3:
            return self._check_line_parallelogram()
        else:
            return self._check_full_parallelogram()
    
    def _check_line_parallelogram(self) -> bool:
        """Проверка параллелограмма из 3 точек (линейное расположение)"""
        if len(self.quantities) != 3:
            return False
            
        # Сортируем по L, затем по T
        sorted_q = sorted(self.quantities, key=lambda q: (q.L, q.T))
        q1, q2, q3 = sorted_q
        
        # Проверяем, что точки на одной линии и равноудалены
        if q1.L == q2.L == q3.L:  # Вертикальная линия
            return abs(q2.T - q1.T) == abs(q3.T - q2.T)
        elif q1.T == q2.T == q3.T:  # Горизонтальная линия  
            return abs(q2.L - q1.L) == abs(q3.L - q2.L)
        else:
            # Диагональная линия
            return (q2.L - q1.L, q2.T - q1.T) == (q3.L - q2.L, q3.T - q2.T)
    
    def _check_full_parallelogram(self) -> bool:
        """Проверка параллелограмма из 4 точек"""
        if len(self.quantities) != 4:
            return False
            
        # Сортировка как в оригинальном коде
        items = self.quantities.copy()
        items.sort(key=lambda q: (-q.L, -q.T))
        e1 = items[0]
        
        rest = items[1:]
        rest.sort(key=lambda q: (q.L, q.T))
        e2, e3, e4 = rest
        
        # Проверяем условия параллелограмма
        def check_property(prop_func):
            return prop_func(e1) + prop_func(e2) == prop_func(e3) + prop_func(e4)
        
        return all([
            check_property(lambda q: q.system_group_id),  # Проверяем по ID группы
            check_property(lambda q: q.L),
            check_property(lambda q: q.T),
        ])
    
    @property
    def ordered_quantities(self) -> List[PhysicalQuantity]:
        """Возвращает упорядоченные величины для создания закона"""
        if len(self.quantities) == 3:
            # Для линейного параллелограмма возвращаем [q1, q2, q2, q3]
            sorted_q = sorted(self.quantities, key=lambda q: (q.L, q.T))
            return [sorted_q[0], sorted_q[1], sorted_q[1], sorted_q[2]]
        else:
            # Для полного параллелограмма используем оригинальную сортировку
            items = self.quantities.copy()
            items.sort(key=lambda q: (-q.L, -q.T))
            e1 = items[0]
            
            rest = items[1:]
            rest.sort(key=lambda q: (q.L, q.T))
            e2, e3, e4 = rest
            
            return [e1, e3, e2, e4]
    
    def get_variable_names(self) -> List[str]:
        """Возвращает имена переменных для закона"""
        ordered = self.ordered_quantities
        return [q.name for q in ordered]
