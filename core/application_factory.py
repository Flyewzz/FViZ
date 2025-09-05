from typing import List

from core.use_cases.application_model import ApplicationModel
from core.use_cases.application_model_with_commands import ApplicationModelWithCommands
from core.use_cases.physical_quantity_manager import PhysicalQuantityManager
from core.use_cases.system_group_manager import SystemGroupManager
from core.use_cases.law_manager import LawManager, LawGroupManager, ParallelogramLogic

from infrastructure.repositories.physical_quantity_repository import PhysicalQuantityRepositoryImpl
from infrastructure.repositories.system_group_repository import SystemGroupRepositoryImpl
from infrastructure.repositories.law_repository import LawRepositoryImpl

from ui.controllers.main_controller import MainController
from ui.presenters.main_presenter import MainPresenter


class ApplicationFactory:
    """Фабрика для создания всех компонентов приложения"""
    
    @staticmethod
    def create_application_model() -> ApplicationModel:
        """Создать основную модель приложения со всеми зависимостями"""
        
        # Создаем репозитории
        pq_repository = PhysicalQuantityRepositoryImpl()
        sg_repository = SystemGroupRepositoryImpl()
        law_repository = LawRepositoryImpl()
        
        # Создаем use cases
        quantity_manager = PhysicalQuantityManager(pq_repository, sg_repository)
        system_group_manager = SystemGroupManager(sg_repository)
        law_manager = LawManager(law_repository, law_repository, pq_repository)
        law_group_manager = LawGroupManager(law_repository)
        parallelogram_logic = ParallelogramLogic(pq_repository)
        
        # Устанавливаем репозиторий системных групп для ParallelogramLogic
        parallelogram_logic.system_group_repo = sg_repository
        
        # Создаем главную модель приложения
        app_model = ApplicationModel(
            quantity_manager=quantity_manager,
            system_group_manager=system_group_manager,
            law_manager=law_manager,
            law_group_manager=law_group_manager,
            parallelogram_logic=parallelogram_logic
        )
        
        return app_model

    @staticmethod
    def create_application_model_with_commands() -> ApplicationModelWithCommands:
        """Создать основную модель приложения со всеми зависимостями и поддержкой команд"""

        # Создаем репозитории
        pq_repository = PhysicalQuantityRepositoryImpl()
        sg_repository = SystemGroupRepositoryImpl()
        law_repository = LawRepositoryImpl()

        # Создаем use cases
        quantity_manager = PhysicalQuantityManager(pq_repository, sg_repository)
        system_group_manager = SystemGroupManager(sg_repository)
        law_manager = LawManager(law_repository, law_repository, pq_repository)
        law_group_manager = LawGroupManager(law_repository)
        parallelogram_logic = ParallelogramLogic(pq_repository)

        # Устанавливаем репозиторий системных групп для ParallelogramLogic
        parallelogram_logic.system_group_repo = sg_repository

        # Создаем главную модель приложения с поддержкой команд
        app_model = ApplicationModelWithCommands(
            quantity_manager=quantity_manager,
            system_group_manager=system_group_manager,
            law_manager=law_manager,
            law_group_manager=law_group_manager,
            parallelogram_logic=parallelogram_logic
        )

        return app_model
    
    @staticmethod
    def create_main_controller(app_model: ApplicationModel, web_view) -> MainController:
        """Создать главный контроллер"""
        return MainController(app_model, web_view)
    
    @staticmethod
    def create_main_presenter(app_model: ApplicationModel) -> MainPresenter:
        """Создать главный презентер"""
        return MainPresenter(app_model)
    
    @staticmethod
    def setup_default_data(app_model: ApplicationModel):
        """Настроить начальные данные приложения"""
        # Создаем системные группы по умолчанию
        try:
            app_model.create_system_group("group1", "Группа 1", "#73ecfa", G=1, k=1)
            app_model.create_system_group("group2", "Группа 2", "#fa73ec", G=2, k=2)
            app_model.create_system_group("group3", "Группа 3", "#ecfa73", G=3, k=3)
        except Exception as e:
            print(f"Ошибка создания групп по умолчанию: {e}")
        
        # Можем добавить создание тестовых величин
        try:
            # Добавляем несколько тестовых величин с разными L, T для тестирования параллелограмма
            test_quantities = [
                ("Частота", "f", "Гц", "T^{-1}", 0, -1, "group1"),  # L=0, T=-1, G=1, k=1
                ("Скорость", "v", "м/с", "L T^{-1}", 1, -1, "group2"),  # L=1, T=-1, G=2, k=2
                ("Масса", "m", "кг", "M", 0, 0, "group3"),  # L=0, T=0, G=3, k=3
                ("Энергия", "E", "Дж", "M L^2 T^{-2}", 2, -2, "group1"),  # L=2, T=-2, G=1, k=1
            ]
            
            for name, symbol, unit, dimension, L, T, group_id in test_quantities:
                quantity = app_model.create_physical_quantity(
                    name, symbol, unit, dimension, L, T, group_id
                )
                app_model.set_visible_quantity(L, T, quantity)
                
        except Exception as e:
            print(f"Ошибка создания тестовых величин: {e}")
