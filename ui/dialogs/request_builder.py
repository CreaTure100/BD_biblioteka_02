from PySide6.QtWidgets import (QDialog, QMainWindow, QMessageBox, QScrollArea, QVBoxLayout, QHBoxLayout, 
                              QGroupBox, QCheckBox, QLineEdit, QComboBox, QPushButton, 
                              QTableWidget, QTableWidgetItem, QLabel, QFormLayout, QFrame,
                              QTextEdit, QSplitter, QSizePolicy, QWidget, QHeaderView, QTabWidget,
                              QListWidget, QListWidgetItem, QApplication)
from PySide6.QtCore import Qt
from core.additional_classes import RequestBuilder

class RequestBuilderDialog(QDialog):
    """
    Построение сложных запросов к базе данных с визуальным интерфейсом
    """
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.request_builder = RequestBuilder()
        self.subqueries = []
        self.where_conditions = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Конструктор SELECT запросов")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        self.tabs = QTabWidget()
        
        # Основная вкладка - построение запроса
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "Основной запрос")
        
        # Вкладка для вложенных запросов
        self.subquery_tab = QWidget()
        self.setup_subquery_tab()
        self.tabs.addTab(self.subquery_tab, "Вложенные запросы")
        
        # Вкладка для агрегации и группировки
        self.aggregation_tab = QWidget()
        self.setup_aggregation_tab()
        self.tabs.addTab(self.aggregation_tab, "Агрегация и группировка")
        
        layout.addWidget(self.tabs)
        
        # Кнопки выполнения
        buttons_layout = QHBoxLayout()
        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_request)
        self.clear_btn = QPushButton("Очистить форму")
        self.clear_btn.clicked.connect(self.clear_form)
        self.show_sql_btn = QPushButton("Показать SQL")
        self.show_sql_btn.clicked.connect(self.show_sql)
        buttons_layout.addWidget(self.execute_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.show_sql_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        results_group = QGroupBox("Результаты запроса")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setMinimumHeight(300)
        self.results_table.setMaximumHeight(600)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.results_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        results_layout.addWidget(self.results_table)
        layout.addWidget(results_group)
        
        main_scroll.setWidget(main_widget)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(main_scroll)
        
        self.on_table_changed(self.table_combo.currentText())
    
    def setup_main_tab(self):
        """Настройка основной вкладки построения запроса"""
        layout = QVBoxLayout(self.main_tab)
        
        # Выбор таблицы
        table_group = QGroupBox("Выбор таблицы")
        table_layout = QHBoxLayout(table_group)
        self.table_combo = QComboBox()
        self.table_combo.addItems(["authors", "books", "readers", "issues", "book_authors"])
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        table_layout.addWidget(QLabel("Основная таблица:"))
        table_layout.addWidget(self.table_combo)
        table_layout.addStretch()
        layout.addWidget(table_group)
        
        # Выбор столбцов
        columns_group = QGroupBox("Выбор столбцов для отображения")
        columns_layout = QVBoxLayout(columns_group)
        
        columns_scroll = QScrollArea()
        columns_scroll.setWidgetResizable(True)
        columns_scroll.setMinimumHeight(100)
        columns_scroll.setMaximumHeight(120)
        columns_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.columns_widget = QWidget()
        self.columns_layout = QVBoxLayout(self.columns_widget)
        columns_scroll.setWidget(self.columns_widget)
        columns_layout.addWidget(columns_scroll)
        
        layout.addWidget(columns_group)
        
        # Условия WHERE
        where_group = QGroupBox("Условия фильтрации (WHERE)")
        where_layout = QVBoxLayout(where_group)
        
        # Простые условия WHERE
        simple_where_layout = QHBoxLayout()
        self.where_column = QComboBox()
        self.where_column.setMinimumWidth(120)
        self.where_operator = QComboBox()
        self.where_operator.addItems(["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "NOT IN", "BETWEEN", "IS NULL", "IS NOT NULL"])
        self.where_operator.setMinimumWidth(80)
        self.where_value = QLineEdit()
        self.where_value.setPlaceholderText("Значение для фильтрации")
        self.where_value.setMinimumWidth(150)
        self.add_where_btn = QPushButton("Добавить условие")
        self.add_where_btn.clicked.connect(self.add_where_condition)
        
        simple_where_layout.addWidget(QLabel("Столбец:"))
        simple_where_layout.addWidget(self.where_column)
        simple_where_layout.addWidget(QLabel("Оператор:"))
        simple_where_layout.addWidget(self.where_operator)
        simple_where_layout.addWidget(QLabel("Значение:"))
        simple_where_layout.addWidget(self.where_value)
        simple_where_layout.addWidget(self.add_where_btn)
        
        where_layout.addLayout(simple_where_layout)
        
        # Список добавленных условий
        where_list_layout = QHBoxLayout()
        where_list_left = QVBoxLayout()
        where_list_left.addWidget(QLabel("Добавленные условия:"))
        self.where_conditions_list = QListWidget()
        self.where_conditions_list.setMinimumHeight(80)
        self.where_conditions_list.setMaximumHeight(120)
        self.where_conditions_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        where_list_left.addWidget(self.where_conditions_list)

        where_buttons_layout = QVBoxLayout()
        where_buttons_layout.addStretch()
        self.remove_where_btn = QPushButton("Удалить")
        self.remove_where_btn.clicked.connect(self.remove_where_condition)
        self.remove_where_btn.setMinimumWidth(80)
        where_buttons_layout.addWidget(self.remove_where_btn)
        where_buttons_layout.addStretch()

        where_list_layout.addLayout(where_list_left, 3)
        where_list_layout.addLayout(where_buttons_layout, 1)
        
        where_layout.addLayout(where_list_layout)
        layout.addWidget(where_group)
        
        # Сортировка ORDER BY
        order_group = QGroupBox("Сортировка (ORDER BY)")
        order_layout = QVBoxLayout(order_group)
        
        # Простой выбор сортировки
        order_input_layout = QHBoxLayout()
        self.order_column = QComboBox()
        self.order_column.setMinimumWidth(150)
        self.order_column.addItem("")
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])
        
        order_input_layout.addWidget(QLabel("Столбец для сортировки:"))
        order_input_layout.addWidget(self.order_column)
        order_input_layout.addWidget(QLabel("Направление:"))
        order_input_layout.addWidget(self.order_direction)
        order_input_layout.addStretch()
        
        order_layout.addLayout(order_input_layout)
        layout.addWidget(order_group)
    
    def setup_subquery_tab(self):
        """Настройка вкладки для вложенных запросов"""
        layout = QVBoxLayout(self.subquery_tab)
        
        # Создание вложенного запроса
        subquery_create_group = QGroupBox("Создание вложенного запроса")
        subquery_create_layout = QVBoxLayout(subquery_create_group)
        
        # Первая строка - таблица и столбец
        first_row_layout = QHBoxLayout()
        self.subquery_table = QComboBox()
        self.subquery_table.addItems(["authors", "books", "readers", "issues", "book_authors"])
        self.subquery_table.setMinimumWidth(120)
        
        self.subquery_column = QComboBox()
        self.subquery_column.setMinimumWidth(120)
        self.subquery_table.currentTextChanged.connect(self.update_subquery_columns)
        
        first_row_layout.addWidget(QLabel("Таблица:"))
        first_row_layout.addWidget(self.subquery_table)
        first_row_layout.addWidget(QLabel("Столбец:"))
        first_row_layout.addWidget(self.subquery_column)
        first_row_layout.addStretch()
        
        # Вторая строка - оператор и тип
        second_row_layout = QHBoxLayout()
        self.subquery_operator = QComboBox()
        self.subquery_operator.addItems(["IN", "NOT IN", "EXISTS", "NOT EXISTS", "ANY", "ALL", "=", ">", "<", ">=", "<=", "!="])
        self.subquery_operator.setMinimumWidth(100)
        
        self.subquery_type = QComboBox()
        self.subquery_type.addItems(["Некоррелированный", "Коррелированный"])
        self.subquery_type.setMinimumWidth(130)
        
        second_row_layout.addWidget(QLabel("Оператор:"))
        second_row_layout.addWidget(self.subquery_operator)
        second_row_layout.addWidget(QLabel("Тип:"))
        second_row_layout.addWidget(self.subquery_type)
        second_row_layout.addStretch()
        
        # Третья строка - условие
        third_row_layout = QHBoxLayout()
        self.subquery_condition = QLineEdit()
        self.subquery_condition.setPlaceholderText("Дополнительное условие (WHERE ...)")
        
        third_row_layout.addWidget(QLabel("Условие:"))
        third_row_layout.addWidget(self.subquery_condition)
        
        # Четвертая строка - алиас и кнопка
        fourth_row_layout = QHBoxLayout()
        self.subquery_alias = QLineEdit()
        self.subquery_alias.setPlaceholderText("Алиас (необязательно)")
        self.subquery_alias.setMaximumWidth(150)
        
        self.add_subquery_btn = QPushButton("Добавить вложенный запрос")
        self.add_subquery_btn.clicked.connect(self.add_subquery)
        
        fourth_row_layout.addWidget(QLabel("Алиас:"))
        fourth_row_layout.addWidget(self.subquery_alias)
        fourth_row_layout.addWidget(self.add_subquery_btn)
        fourth_row_layout.addStretch()
        
        # Добавляем все в форму
        subquery_create_layout.addLayout(first_row_layout)
        subquery_create_layout.addLayout(second_row_layout)
        subquery_create_layout.addLayout(third_row_layout)
        subquery_create_layout.addLayout(fourth_row_layout)
        
        layout.addWidget(subquery_create_group)
        
        # Список вложенных запросов
        subqueries_group = QGroupBox("Добавленные вложенные запросы")
        subqueries_layout = QVBoxLayout(subqueries_group)
        
        self.subqueries_list = QListWidget()
        self.subqueries_list.setMinimumHeight(150)
        self.subqueries_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        subquery_buttons_layout = QHBoxLayout()
        self.remove_subquery_btn = QPushButton("Удалить выбранный")
        self.remove_subquery_btn.clicked.connect(self.remove_subquery)
        subquery_buttons_layout.addWidget(self.remove_subquery_btn)
        subquery_buttons_layout.addStretch()
        
        subqueries_layout.addWidget(self.subqueries_list)
        subqueries_layout.addLayout(subquery_buttons_layout)
        
        layout.addWidget(subqueries_group)
        self.update_subquery_columns(self.subquery_table.currentText())
    
    def setup_aggregation_tab(self):
        """Настройка вкладки для агрегации и группировки"""
        layout = QVBoxLayout(self.aggregation_tab)
        
        # Агрегатные функции с алиасами
        aggregation_group = QGroupBox("Агрегатные функции")
        aggregation_layout = QVBoxLayout(aggregation_group)
        
        agg_row_layout = QHBoxLayout()
        self.agg_function = QComboBox()
        self.agg_function.addItems(["", "COUNT", "SUM", "AVG", "MIN", "MAX"])
        self.agg_function.setMinimumWidth(80)
        
        self.agg_column = QComboBox()
        self.agg_column.addItem("")
        self.agg_column.addItem("*")
        self.agg_column.setMinimumWidth(120)
        
        self.agg_alias = QLineEdit()
        self.agg_alias.setPlaceholderText("Алиас для результата")
        self.agg_alias.setMaximumWidth(120)
        
        self.add_aggregation_btn = QPushButton("Добавить")
        self.add_aggregation_btn.clicked.connect(self.add_aggregation)
        
        agg_row_layout.addWidget(QLabel("Функция:"))
        agg_row_layout.addWidget(self.agg_function)
        agg_row_layout.addWidget(QLabel("Столбец:"))
        agg_row_layout.addWidget(self.agg_column)
        agg_row_layout.addWidget(QLabel("Алиас:"))
        agg_row_layout.addWidget(self.agg_alias)
        agg_row_layout.addWidget(self.add_aggregation_btn)
        agg_row_layout.addStretch()
        
        aggregation_layout.addLayout(agg_row_layout)
        layout.addWidget(aggregation_group)
        
        # Группировка
        grouping_group = QGroupBox("Группировка (GROUP BY)")
        grouping_layout = QVBoxLayout(grouping_group)
        
        group_columns_layout = QHBoxLayout()
        self.group_column = QComboBox()
        self.group_column.setMinimumWidth(150)
        self.group_column.addItem("")
        self.add_group_btn = QPushButton("Добавить группировку")
        self.add_group_btn.clicked.connect(self.add_grouping)
        self.remove_group_btn = QPushButton("Удалить выбранную")
        self.remove_group_btn.clicked.connect(self.remove_grouping)
        
        group_columns_layout.addWidget(QLabel("Столбец для группировки:"))
        group_columns_layout.addWidget(self.group_column)
        group_columns_layout.addWidget(self.add_group_btn)
        group_columns_layout.addWidget(self.remove_group_btn)
        group_columns_layout.addStretch()
        
        grouping_layout.addLayout(group_columns_layout)
        
        # Список группировок
        self.grouping_list = QListWidget()
        self.grouping_list.setMinimumHeight(60)
        self.grouping_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        grouping_layout.addWidget(self.grouping_list)
        
        layout.addWidget(grouping_group)
        
        # Условия HAVING
        having_group = QGroupBox("Условия для групп (HAVING)")
        having_layout = QVBoxLayout(having_group)
        
        having_input_layout = QHBoxLayout()
        self.having_condition = QLineEdit()
        self.having_condition.setPlaceholderText("Например: COUNT(*) > 5 OR AVG(rating) > 4.0")
        self.add_having_btn = QPushButton("Добавить условие HAVING")
        self.add_having_btn.clicked.connect(self.add_having_condition)
        self.remove_having_btn = QPushButton("Очистить")
        self.remove_having_btn.clicked.connect(self.clear_having)
        
        having_input_layout.addWidget(QLabel("Условие:"))
        having_input_layout.addWidget(self.having_condition)
        having_input_layout.addWidget(self.add_having_btn)
        having_input_layout.addWidget(self.remove_having_btn)
        
        self.having_display = QTextEdit()
        self.having_display.setMinimumHeight(50)
        self.having_display.setMaximumHeight(80)
        self.having_display.setPlaceholderText("Текущее условие HAVING...")
        self.having_display.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        having_layout.addLayout(having_input_layout)
        having_layout.addWidget(self.having_display)
        
        layout.addWidget(having_group)

    def get_order_by_condition(self):
        """Получение условия ORDER BY (только один последний выбор)"""
        column = self.order_column.currentText()
        direction = self.order_direction.currentText()
        
        if not column:
            return None
        
        return f"{column} {direction}"
    
    def add_where_condition(self):
        """Добавление условия WHERE с приоритетом"""
        column = self.where_column.currentText()
        operator = self.where_operator.currentText()
        value = self.where_value.text()
        
        if not column:
            QMessageBox.warning(self, "Ошибка", "Выберите столбец для условия")
            return
        
        if operator not in ["IS NULL", "IS NOT NULL"] and not value:
            QMessageBox.warning(self, "Ошибка", "Введите значение для условия")
            return
        
        if operator not in ["IS NULL", "IS NOT NULL"]:
            if operator in ["IN", "NOT IN"]:
                values = [v.strip() for v in value.split(",")]
                escaped_value = "(" + ", ".join([f"'{v}'" for v in values]) + ")"
            elif operator == "BETWEEN":
                values = [v.strip() for v in value.split(" AND ")]
                if len(values) == 2:
                    escaped_value = f"'{values[0]}' AND '{values[1]}'"
                else:
                    QMessageBox.warning(self, "Ошибка", "Для BETWEEN используйте формат: значение1 AND значение2")
                    return
            else:
                escaped_value = f"'{value}'"
            
            condition = f"{column} {operator} {escaped_value}"
        else:
            condition = f"{column} {operator}"
        
        self.where_conditions.append(condition)
        self.update_where_display()
        self.where_value.clear()
    
    def remove_where_condition(self):
        current_row = self.where_conditions_list.currentRow()
        if current_row >= 0:
            self.where_conditions.pop(current_row)
            self.update_where_display()
    
    def update_where_display(self):
        self.where_conditions_list.clear()
        for i, condition in enumerate(self.where_conditions, 1):
            item = QListWidgetItem(f"{i}. {condition}")
            self.where_conditions_list.addItem(item)
    
    def add_aggregation(self):
        function = self.agg_function.currentText()
        column = self.agg_column.currentText()
        alias = self.agg_alias.text().strip()
        
        if not function:
            QMessageBox.warning(self, "Ошибка", "Выберите агрегатную функцию")
            return
        
        if function != "COUNT" and not column:
            QMessageBox.warning(self, "Ошибка", f"Для функции {function} необходимо выбрать столбец")
            return
        
        if function == "COUNT" and column == "*":
            agg_expression = "COUNT(*)"
        elif function == "COUNT" and not column:
            agg_expression = "COUNT(*)"
        else:
            agg_expression = f"{function}({column})"
        
        if alias:
            agg_expression += f" AS {alias}"
        for i in range(self.columns_layout.count()):
            checkbox = self.columns_layout.itemAt(i).widget()
            if checkbox and checkbox.text() == agg_expression:
                QMessageBox.information(self, "Информация", "Такое агрегатное выражение уже добавлено")
                return
        
        checkbox = QCheckBox(agg_expression)
        checkbox.setChecked(True)
        checkbox.setMinimumHeight(20)
        self.columns_layout.addWidget(checkbox)
        self.agg_function.setCurrentIndex(0)
        self.agg_column.setCurrentIndex(0)
        self.agg_alias.clear()
    
    def add_grouping(self):
        column = self.group_column.currentText()
        
        if not column:
            QMessageBox.warning(self, "Ошибка", "Выберите столбец для группировки")
            return
        
        for i in range(self.grouping_list.count()):
            if self.grouping_list.item(i).text() == column:
                QMessageBox.information(self, "Информация", "Этот столбец уже добавлен в группировку")
                return
        
        self.grouping_list.addItem(column)
    
    def remove_grouping(self):
        current_row = self.grouping_list.currentRow()
        if current_row >= 0:
            self.grouping_list.takeItem(current_row)
    
    def add_having_condition(self):
        condition = self.having_condition.text().strip()
        
        if not condition:
            QMessageBox.warning(self, "Ошибка", "Введите условие HAVING")
            return
        
        if not self.validate_having_condition(condition):
            QMessageBox.warning(self, "Ошибка", 
                              "Условие HAVING содержит ошибки. Используйте агрегатные функции и логические операторы.")
            return
        
        self.having_display.setText(condition)
        self.having_condition.clear()
    
    def clear_having(self):
        self.having_display.clear()
    
    def validate_having_condition(self, condition):
        aggregate_functions = ["COUNT(", "SUM(", "AVG(", "MIN(", "MAX("]
        has_aggregate = any(func in condition.upper() for func in aggregate_functions)
        
        if not has_aggregate:
            return False
        
        dangerous_patterns = ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER"]
        if any(pattern in condition.upper() for pattern in dangerous_patterns):
            return False
        
        return True
    
    def add_subquery(self):
        table = self.subquery_table.currentText()
        column = self.subquery_column.currentText()
        operator = self.subquery_operator.currentText()
        subquery_type = self.subquery_type.currentText()
        condition = self.subquery_condition.text().strip()
        alias = self.subquery_alias.text().strip()
        
        if not column:
            QMessageBox.warning(self, "Ошибка", "Выберите столбец для подзапроса")
            return
        
        if operator in ["EXISTS", "NOT EXISTS"]:
            subquery_text = f"{operator} (SELECT 1 FROM {table}"
        else:
            subquery_text = f"{operator} (SELECT {column} FROM {table}"
        
        if condition:
            subquery_text += f" WHERE {condition}"
        
        subquery_text += ")"
        
        if subquery_type == "Коррелированный":
            subquery_text += " -- КОРРЕЛИРОВАННЫЙ"
        
        if alias:
            subquery_text += f" AS {alias}"
        
        item = QListWidgetItem(subquery_text)
        self.subqueries_list.addItem(item)
        
        self.subqueries.append({
            'table': table,
            'column': column,
            'operator': operator,
            'type': subquery_type,
            'condition': condition,
            'alias': alias,
            'text': subquery_text
        })
        
        self.subquery_condition.clear()
        self.subquery_alias.clear()
    
    def remove_subquery(self):
        current_row = self.subqueries_list.currentRow()
        if current_row >= 0:
            self.subqueries_list.takeItem(current_row)
            if current_row < len(self.subqueries):
                self.subqueries.pop(current_row)
    
    def on_table_changed(self, table_name):
        for i in reversed(range(self.columns_layout.count())):
            widget = self.columns_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        columns = self.controller.get_table_columns(table_name)
        for column in columns:
            checkbox = QCheckBox(column)
            checkbox.setChecked(True)
            checkbox.setMinimumHeight(20)
            self.columns_layout.addWidget(checkbox)
        
        self.update_combo_boxes(columns)
    
    def update_combo_boxes(self, columns):
        """Обновление всех комбобоксов с столбцами"""
        current_order = self.order_column.currentText()
        current_group = self.group_column.currentText()
        current_where = self.where_column.currentText()
        current_agg = self.agg_column.currentText()

        for combo in [self.order_column, self.group_column, self.where_column]:
            combo.clear()
            combo.addItem("")
            combo.addItems(columns)
        
        self.agg_column.blockSignals(True)
        current_agg_text = self.agg_column.currentText()
        self.agg_column.clear()
        self.agg_column.addItem("")
        self.agg_column.addItem("*")
        self.agg_column.addItems(columns)
        
        if current_agg_text in columns or current_agg_text == "*":
            self.agg_column.setCurrentText(current_agg_text)
        self.agg_column.blockSignals(False)
        
        if current_order in columns:
            self.order_column.setCurrentText(current_order)
        if current_group in columns:
            self.group_column.setCurrentText(current_group)
        if current_where in columns:
            self.where_column.setCurrentText(current_where)
    
    def update_subquery_columns(self, table_name):
        columns = self.controller.get_table_columns(table_name)
        current = self.subquery_column.currentText()
        
        self.subquery_column.clear()
        self.subquery_column.addItems(columns)
        
        if current in columns:
            self.subquery_column.setCurrentText(current)
    
    def execute_request(self):
        try:
            selected_columns = []
            for i in range(self.columns_layout.count()):
                checkbox = self.columns_layout.itemAt(i).widget()
                if checkbox and checkbox.isChecked():
                    selected_columns.append(checkbox.text())
            
            if not selected_columns:
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один столбец для отображения")
                return
            
            has_aggregate = any(any(func in col.upper() for func in ['COUNT(', 'SUM(', 'AVG(', 'MIN(', 'MAX(']) 
                            for col in selected_columns)
            group_columns = []
            for i in range(self.grouping_list.count()):
                group_columns.append(self.grouping_list.item(i).text())
            
            if has_aggregate and not group_columns:
                # Автоматически добавляем все неагрегированные столбцы в GROUP BY
                non_aggregated_columns = []
                for col in selected_columns:
                    if not any(func in col.upper() for func in ['COUNT(', 'SUM(', 'AVG(', 'MIN(', 'MAX(']):
                        non_aggregated_columns.append(col.split(' AS ')[0].strip())
                
                if non_aggregated_columns:
                    reply = QMessageBox.question(self, "GROUP BY", 
                                            f"Для агрегатных функций требуется GROUP BY.\n"
                                            f"Добавить автоматически столбцы: {', '.join(non_aggregated_columns)}?",
                                            QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        group_columns = non_aggregated_columns
                        self.grouping_list.clear()
                        for col in group_columns:
                            self.grouping_list.addItem(col)
            
            self.request_builder.reset()
            self.request_builder.select(selected_columns)
            self.request_builder.from_table(self.table_combo.currentText())
            
            for condition in self.where_conditions:
                self.request_builder.where(condition)
            
            for subquery in self.subqueries:
                self.request_builder.where(subquery['text'])
            
            if group_columns:
                self.request_builder.group_by(*group_columns)
            
            having_condition = self.having_display.toPlainText().strip()
            if having_condition:
                self.request_builder.having(having_condition)
            
            order_condition = self.get_order_by_condition()
            if order_condition:
                parts = order_condition.split()
                if len(parts) == 2:
                    self.request_builder.order_by(parts[0], parts[1])
            
            sql = self.request_builder.build()
            self.controller.logger.info(f"Выполняется запрос: {sql}")
            results = self.controller.execute_custom_request(sql)
            
            self.display_results(results)
            
            QMessageBox.information(self, "Успех", f"Запрос выполнен успешно!\nНайдено записей: {len(results)}")
        
        except Exception as e:
            self.controller.logger.error(f"Ошибка выполнения запроса: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось выполнить запрос:\n{str(e)}")
    
    def show_sql(self):
        try:
            sql = self.build_sql_preview()
            QMessageBox.information(self, "SQL запрос", f"Сгенерированный SQL:\n\n{sql}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сгенерировать SQL:\n{str(e)}")
    
    def build_sql_preview(self):
        temp_builder = RequestBuilder()
        
        selected_columns = []
        for i in range(self.columns_layout.count()):
            checkbox = self.columns_layout.itemAt(i).widget()
            if checkbox and checkbox.isChecked():
                selected_columns.append(checkbox.text())
        
        if not selected_columns:
            return "SELECT * FROM " + self.table_combo.currentText()
        
        temp_builder.select(selected_columns)
        temp_builder.from_table(self.table_combo.currentText())
        
        for condition in self.where_conditions:
            temp_builder.where(condition)
        
        for subquery in self.subqueries:
            temp_builder.where(subquery['text'])
        
        group_columns = []
        for i in range(self.grouping_list.count()):
            group_columns.append(self.grouping_list.item(i).text())
        
        if group_columns:
            temp_builder.group_by(*group_columns)
        
        having_condition = self.having_display.toPlainText().strip()
        if having_condition:
            temp_builder.having(having_condition)
        
        order_condition = self.get_order_by_condition()
        if order_condition:
            parts = order_condition.split()
            if len(parts) == 2:
                temp_builder.order_by(parts[0], parts[1])
        
        return temp_builder.build()
    
    def display_results(self, results):
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
            
        self.results_table.setRowCount(len(results))
        
        if results:
            columns = list(results[0].keys())
            self.results_table.setColumnCount(len(columns))
            self.results_table.setHorizontalHeaderLabels(columns)
            
            header = self.results_table.horizontalHeader()
            for i in range(len(columns)):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        for row_idx, row_data in enumerate(results):
            for col_idx, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.results_table.setItem(row_idx, col_idx, item)
    
    def clear_form(self):
        self.where_conditions.clear()
        self.subqueries.clear()
        
        self.where_conditions_list.clear()
        self.subqueries_list.clear()
        self.grouping_list.clear()
        self.having_display.clear()
        
        self.where_value.clear()
        self.subquery_condition.clear()
        self.subquery_alias.clear()
        self.agg_alias.clear()
        self.having_condition.clear()
        
        self.where_operator.setCurrentIndex(0)
        self.order_direction.setCurrentIndex(0)
        self.subquery_operator.setCurrentIndex(0)
        self.subquery_type.setCurrentIndex(0)
        self.agg_function.setCurrentIndex(0)
        self.agg_column.setCurrentIndex(0)
        
        self.order_column.setCurrentIndex(0)
        
        for i in range(self.columns_layout.count()):
            checkbox = self.columns_layout.itemAt(i).widget()
            if checkbox:
                checkbox.setChecked(True)
        
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
