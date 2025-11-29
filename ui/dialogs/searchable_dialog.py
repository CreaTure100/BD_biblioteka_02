from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QTableWidget, QTableWidgetItem, QComboBox, QLineEdit)

from .string_operations import StringOperationsDialog

class SearchableDialogMixin:
    """Миксин для добавления функционала поиска в диалоги с таблицами"""
    
    def init_search_components(self):
        """Инициализация компонентов поиска"""
        # Создаем компоненты поиска
        self.search_type_combo = QComboBox()
        self.column_combo = QComboBox()
        self.search_input = QLineEdit()
        
        # Настраиваем комбобокс для выбора типа поиска
        self.search_type_combo.addItems([
            "LIKE",
            "SIMILAR TO",
            "NOT SIMILAR TO",  
            "POSIX regex (~)",
            "POSIX regex case-insensitive (~*)",
            "POSIX regex NOT (!~)",
            "POSIX regex NOT case-insensitive (!~*)"
        ])
        
        # Настраиваем поле для ввода поискового запроса
        self.search_input.setPlaceholderText("Введите текст для поиска...")
    
    def setup_search(self):
        """Настройка интерфейса поиска"""
        # Создаем layout для поисковых элементов и кнопки строковых операций
        search_layout = QHBoxLayout()
        
        # Добавляем компоненты в layout
        search_layout.addWidget(self.search_type_combo)
        search_layout.addWidget(self.column_combo)
        search_layout.addWidget(self.search_input)
        
        # Кнопка поиска
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(search_button)
        
        # Добавляем кнопку строковых операций
        string_ops_button = QPushButton("Строковые операции")
        string_ops_button.clicked.connect(self.show_string_operations)
        search_layout.addWidget(string_ops_button)
        
        # Добавляем поисковый layout перед закрытием окна
        self.layout().insertLayout(self.layout().count() - 1, search_layout)

    def update_search_columns(self, table_widget):
        """Обновление списка колонок в поисковом комбобоксе"""
        if self.column_combo is not None:
            self.column_combo.clear()
            headers = []
            for col in range(table_widget.columnCount()):
                headers.append(table_widget.horizontalHeaderItem(col).text())
            self.column_combo.addItems(headers)

    def perform_search(self):
        """Выполнение поиска по таблице"""
        search_type = self.search_type_combo.currentText()
        column_index = self.column_combo.currentIndex()
        search_text = self.search_input.text()
        
        # Получаем ссылку на таблицу из конкретного класса
        table = self.get_table_widget()
        
        if not search_text:
            # Если поисковый запрос пустой, показываем все строки
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
            return
            
        # Преобразуем тип поиска в оператор
        operator_map = {
            "LIKE": lambda text, search: search.lower() in text.lower(),
            "SIMILAR TO": lambda text, search: self.similar_to_match(text, search),
            "NOT SIMILAR TO": lambda text, search: not self.similar_to_match(text, search),
            "POSIX regex (~)": lambda text, search: self.regex_match(text, search, False, False),
            "POSIX regex case-insensitive (~*)": lambda text, search: self.regex_match(text, search, True, False),
            "POSIX regex NOT (!~)": lambda text, search: not self.regex_match(text, search, False, False),
            "POSIX regex NOT case-insensitive (!~*)": lambda text, search: not self.regex_match(text, search, True, False)
        }
        
        operator = operator_map[search_type]
        
        # Проходим по всем строкам таблицы
        for row in range(table.rowCount()):
            cell_text = table.item(row, column_index).text()
            # Скрываем или показываем строку в зависимости от результата поиска
            table.setRowHidden(row, not operator(cell_text, search_text))
    
    def regex_match(self, text, pattern, case_insensitive, is_not):
        """Проверка соответствия текста регулярному выражению"""
        import re
        try:
            flags = re.IGNORECASE if case_insensitive else 0
            return bool(re.search(pattern, text, flags))
        except re.error:
            return False
            
    def get_table_widget(self):
        """Метод должен быть переопределен в конкретных классах"""
        raise NotImplementedError
    def similar_to_match(self, text, pattern):
        """Проверка соответствия текста шаблону SIMILAR TO"""
        import re
        regex_pattern = pattern.replace('%', '.*').replace('_', '.')
        try:
            return bool(re. search(f'^{regex_pattern}$', text))
        except re.error:
            return False

    def show_string_operations(self):
        """Открывает диалог строковых операций"""
        table = self.get_table_widget()
        
        # Собираем данные из таблицы
        table_data = {
            'headers': [],
            'rows': []
        }
        
        # Получаем заголовки
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col).text()
            table_data['headers'].append(header)
        
        # Получаем данные
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            table_data['rows'].append(row_data)
        
        # Создаем и показываем диалог
        dialog = StringOperationsDialog(table_data, self)
        dialog.exec()
