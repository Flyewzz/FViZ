# main.py
from PyQt5.QtWidgets import QApplication
from ui.views.main_window import MainWindow
from core.application_factory import ApplicationFactory
import sys
import res_rc

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Создаем главную модель приложения через фабрику
    application_model = ApplicationFactory.create_application_model_with_commands()
    
    # Настраиваем начальные данные
    ApplicationFactory.setup_default_data(application_model)
    
    # Создаем главное окно с новой архитектурой
    window = MainWindow(application_model)
    window.show()
    
    sys.exit(app.exec_())
