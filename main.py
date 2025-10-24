"""
Главный модуль приложения "Библиотека".
Точка входа в программу.зн 
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.windows.MainWindow import MainWindow
from ui.dialogs.login import LoginDialog
from core.logger import Logger

if __name__ == "__main__":
    # Инициализация логгера
    logger = Logger()
    logger.info("Запуск приложения")

    # Создание и настройка приложения Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Библиотека")

    # Показ диалога авторизации
    login_dialog = LoginDialog()
    if login_dialog.exec():
        # Если авторизация успешна, открываем главное окно
        window = MainWindow(login_dialog.controller)
        window.show()
        sys.exit(app.exec())
    else:
        # Если авторизация отменена, выходим из приложения
        sys.exit(0)