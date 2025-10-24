from PySide6.QtWidgets import (QWidget, QHBoxLayout, QComboBox, 
                              QLineEdit, QPushButton)
from PySide6.QtCore import Signal

class SearchWidget(QWidget):
    """Виджет поиска с поддержкой LIKE и POSIX-регулярных выражений"""
    
    # Сигнал, который будет отправляться при выполнении поиска
    searchRequested = Signal(str, str)  # (тип_поиска, текст_поиска)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Выпадающий список для выбора типа поиска
        self.search_type = QComboBox()
        self.search_type.addItems([
            "LIKE - Простой поиск",
            "LIKE % - Шаблонный поиск",
            "~ - POSIX регулярное выражение",
            "~* - POSIX регулярное выражение (без учёта регистра)",
            "!~ - НЕ POSIX регулярное выражение",
            "!~* - НЕ POSIX регулярное выражение (без учёта регистра)"
        ])
        layout.addWidget(self.search_type)

        # Поле ввода текста поиска
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Введите текст для поиска...")
        layout.addWidget(self.search_text)

        # Кнопка поиска
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.perform_search)
        layout.addWidget(self.search_button)

    def perform_search(self):
        """Выполнение поиска"""
        search_type = self.search_type.currentText().split(' - ')[0].strip()
        search_text = self.search_text.text()
        self.searchRequested.emit(search_type, search_text)

    def get_search_sql(self, column_name):
        """
        Получение SQL-условия для поиска
        :param column_name: Имя столбца для поиска
        :return: SQL-условие
        """
        search_type = self.search_type.currentText().split(' - ')[0].strip()
        search_text = self.search_text.text()

        if not search_text:
            return ""

        if search_type == "LIKE":
            return f"{column_name} LIKE '{search_text}'"
        elif search_type == "LIKE %":
            return f"{column_name} LIKE '%{search_text}%'"
        elif search_type == "~":
            return f"{column_name} ~ '{search_text}'"
        elif search_type == "~*":
            return f"{column_name} ~* '{search_text}'"
        elif search_type == "!~":
            return f"{column_name} !~ '{search_text}'"
        elif search_type == "!~*":
            return f"{column_name} !~* '{search_text}'"
        
        return ""