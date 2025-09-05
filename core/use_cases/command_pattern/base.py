from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Command(ABC):
    """Абстрактная база для всех команд"""
    
    def __init__(self):
        self._executed = False
        self._undone = False
    
    @abstractmethod
    def execute(self) -> bool:
        """Выполнить команду"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Отменить выполнение команды"""
        pass
    
    @abstractmethod
    def redo(self) -> bool:
        """Повторить выполнение команды"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Получить описание команды для истории"""
        pass
    
    @property
    def executed(self) -> bool:
        return self._executed
    
    @property
    def undone(self) -> bool:
        return self._undone