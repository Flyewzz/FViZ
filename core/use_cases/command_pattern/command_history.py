from typing import List, Optional
from core.use_cases.command_pattern.base import Command


class CommandHistory:
    """История команд для операций отмены/повтора"""
    
    def __init__(self, max_size: int = 50):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_size = max_size
    
    def add_command(self, command: Command) -> None:
        """Добавить команду в историю"""
        # Всегда добавляем в undo стек
        self.undo_stack.append(command)
        
        # Ограничиваем размер undo стека
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)
        
        # Очищаем redo стек при добавлении новой команды
        self.redo_stack.clear()
    
    def undo(self) -> bool:
        """Отменить последнюю команду"""
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        if command.undo():
            self.redo_stack.append(command)
            return True
        else:
            # Если отмена не удалась, возвращаем команду обратно
            self.undo_stack.append(command)
            return False
    
    def redo(self) -> bool:
        """Повторить последнюю отмененную команду"""
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        if command.redo():
            self.undo_stack.append(command)
            return True
        else:
            # Если повтор не удался, возвращаем команду обратно
            self.redo_stack.append(command)
            return False
    
    def can_undo(self) -> bool:
        """Проверить, можно ли отменить команду"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Проверить, можно ли повторить команду"""
        return len(self.redo_stack) > 0
    
    def get_undo_description(self) -> Optional[str]:
        """Получить описание команды для отмены"""
        if self.can_undo():
            return self.undo_stack[-1].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Получить описание команды для повтора"""
        if self.can_redo():
            return self.redo_stack[-1].get_description()
        return None
    
    def clear(self) -> None:
        """Очистить всю историю"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_count(self) -> int:
        """Получить количество команд для отмены"""
        return len(self.undo_stack)
    
    def get_redo_count(self) -> int:
        """Получить количество команд для повтора"""
        return len(self.redo_stack)