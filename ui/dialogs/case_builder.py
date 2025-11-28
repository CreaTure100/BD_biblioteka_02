from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTextEdit, QCheckBox, QSpinBox, QFrame, QScrollArea,
    QTabWidget, QWidget, QSizePolicy, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from ui.styles import get_button_style, get_combobox_style, get_table_style, get_input_fields_style


class CaseBuilderDialog(QDialog):
    """
    Диалог для построения CASE выражений и работы с NULL-значениями.
    Позволяет создавать сложные условия WHEN...THEN...ELSE через графический интерфейс.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.case_conditions = []
        self.null_expressions = []
        self.setWindowTitle("Конструктор CASE выражений и работа с NULL")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        self.tabs = QTabWidget()
        
        # Вкладка CASE выражений
        self.case_tab = QWidget()
        self.setup_case_tab()
        self.tabs.addTab(self.case_tab, "CASE выражения")
        
        # Вкладка NULL функций
        self.null_tab = QWidget()
        self.setup_null_tab()
        self.tabs.addTab(self.null_tab, "Функции NULL")
        
        layout.addWidget(self.tabs)
        
        # Предпросмотр SQL
        sql_group = QGroupBox("Предпросмотр SQL запроса")
        sql_layout = QVBoxLayout(sql_group)
        
        self.sql_preview = QTextEdit()
        self.sql_preview.setReadOnly(True)
        self.sql_preview.setMaximumHeight(120)
        self.sql_preview.setPlaceholderText("Здесь будет отображаться сгенерированный SQL запрос...")
        self.sql_preview.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sql_layout.addWidget(self.sql_preview)
        
        layout.addWidget(sql_group)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_query)
        self.execute_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.execute_btn)
        
        self.update_preview_btn = QPushButton("Обновить предпросмотр")
        self.update_preview_btn.clicked.connect(self.update_sql_preview)
        self.update_preview_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.update_preview_btn)
        
        self.clear_btn = QPushButton("Очистить форму")
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.clear_btn)
        
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.close_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Результаты запроса
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
        self.results_table.setStyleSheet(get_table_style())
        
        results_layout.addWidget(self.results_table)
        layout.addWidget(results_group)
        
        main_scroll.setWidget(main_widget)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(main_scroll)
        
        # Загрузка начальных данных
        self.load_tables()

    def setup_case_tab(self):
        """Настройка вкладки для построения CASE выражений."""
        layout = QVBoxLayout(self.case_tab)
        
        # Выбор таблицы и столбцов
        selection_group = QGroupBox("Выбор данных")
        selection_layout = QHBoxLayout(selection_group)
        
        selection_layout.addWidget(QLabel("Таблица:"))
        self.table_combo = QComboBox()
        self.table_combo.setStyleSheet(get_combobox_style())
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        selection_layout.addWidget(self.table_combo)
        
        selection_layout.addWidget(QLabel("Столбец для CASE:"))
        self.column_combo = QComboBox()
        self.column_combo.setStyleSheet(get_combobox_style())
        selection_layout.addWidget(self.column_combo)
        
        selection_layout.addStretch()
        layout.addWidget(selection_group)
        
        # Управление условиями CASE
        conditions_group = QGroupBox("Управление условиями CASE")
        conditions_layout = QVBoxLayout(conditions_group)
        
        # Кнопки управления условиями
        conditions_buttons_layout = QHBoxLayout()
        
        self.add_condition_btn = QPushButton("Добавить условие WHEN")
        self.add_condition_btn.clicked.connect(self.add_case_condition)
        self.add_condition_btn.setStyleSheet(get_button_style())
        conditions_buttons_layout.addWidget(self.add_condition_btn)
        
        self.remove_condition_btn = QPushButton("Удалить выбранное условие")
        self.remove_condition_btn.clicked.connect(self.remove_case_condition)
        self.remove_condition_btn.setStyleSheet(get_button_style())
        conditions_buttons_layout.addWidget(self.remove_condition_btn)
        
        conditions_buttons_layout.addStretch()
        conditions_layout.addLayout(conditions_buttons_layout)
        
        # Таблица условий
        self.conditions_table = QTableWidget()
        self.conditions_table.setColumnCount(4)
        self.conditions_table.setHorizontalHeaderLabels(["Тип", "Условие/Значение", "Результат THEN", "Действие"])
        self.conditions_table.setStyleSheet(get_table_style())
        self.conditions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.conditions_table.setMinimumHeight(200)
        self.conditions_table.setMaximumHeight(400)
        conditions_layout.addWidget(self.conditions_table)
        
        layout.addWidget(conditions_group)
        
        # Настройки CASE выражения
        settings_group = QGroupBox("Настройки CASE выражения")
        settings_layout = QVBoxLayout(settings_group)
        
        # ELSE условие
        else_layout = QHBoxLayout()
        else_layout.addWidget(QLabel("ELSE результат:"))
        self.else_value = QLineEdit()
        self.else_value.setStyleSheet(get_input_fields_style())
        self.else_value.setPlaceholderText("Значение по умолчанию, если ни одно условие не выполнено")
        else_layout.addWidget(self.else_value)
        else_layout.addStretch()
        settings_layout.addLayout(else_layout)
        
        # Алиас для результата
        alias_layout = QHBoxLayout()
        alias_layout.addWidget(QLabel("Алиас для столбца:"))
        self.case_alias = QLineEdit()
        self.case_alias.setStyleSheet(get_input_fields_style())
        self.case_alias.setPlaceholderText("Имя нового вычисляемого столбца")
        alias_layout.addWidget(self.case_alias)
        alias_layout.addStretch()
        settings_layout.addLayout(alias_layout)
        
        layout.addWidget(settings_group)

    def setup_null_tab(self):
        """Настройка вкладки для работы с NULL-значениями."""
        layout = QVBoxLayout(self.null_tab)
        
        # Выбор таблицы для NULL функций
        table_group = QGroupBox("Выбор таблицы")
        table_layout = QHBoxLayout(table_group)
        
        table_layout.addWidget(QLabel("Таблица:"))
        self.null_table_combo = QComboBox()
        self.null_table_combo.setStyleSheet(get_combobox_style())
        self.null_table_combo.currentTextChanged.connect(self.on_null_table_changed)
        table_layout.addWidget(self.null_table_combo)
        
        table_layout.addStretch()
        layout.addWidget(table_group)
        
        # COALESCE
        coalesce_group = QGroupBox("COALESCE - подстановка значений вместо NULL")
        coalesce_layout = QVBoxLayout(coalesce_group)
        
        coalesce_input_layout = QHBoxLayout()
        coalesce_input_layout.addWidget(QLabel("Столбец:"))
        self.coalesce_column = QComboBox()
        self.coalesce_column.setStyleSheet(get_combobox_style())
        coalesce_input_layout.addWidget(self.coalesce_column)
        
        coalesce_input_layout.addWidget(QLabel("Значения для подстановки (через запятую):"))
        self.coalesce_values = QLineEdit()
        self.coalesce_values.setStyleSheet(get_input_fields_style())
        self.coalesce_values.setPlaceholderText("значение1, значение2, ...")
        coalesce_input_layout.addWidget(self.coalesce_values)
        
        coalesce_input_layout.addStretch()
        coalesce_layout.addLayout(coalesce_input_layout)
        
        coalesce_buttons_layout = QHBoxLayout()
        coalesce_buttons_layout.addStretch()
        self.add_coalesce_btn = QPushButton("Добавить COALESCE")
        self.add_coalesce_btn.clicked.connect(self.add_coalesce_expression)
        self.add_coalesce_btn.setStyleSheet(get_button_style())
        coalesce_buttons_layout.addWidget(self.add_coalesce_btn)
        coalesce_layout.addLayout(coalesce_buttons_layout)
        
        layout.addWidget(coalesce_group)
        
        # NULLIF
        nullif_group = QGroupBox("NULLIF - замена совпадающих значений на NULL")
        nullif_layout = QVBoxLayout(nullif_group)
        
        nullif_input_layout = QHBoxLayout()
        nullif_input_layout.addWidget(QLabel("Столбец:"))
        self.nullif_column = QComboBox()
        self.nullif_column.setStyleSheet(get_combobox_style())
        nullif_input_layout.addWidget(self.nullif_column)
        
        nullif_input_layout.addWidget(QLabel("Значение для замены на NULL:"))
        self.nullif_value = QLineEdit()
        self.nullif_value.setStyleSheet(get_input_fields_style())
        nullif_input_layout.addWidget(self.nullif_value)
        
        nullif_input_layout.addStretch()
        nullif_layout.addLayout(nullif_input_layout)
        
        nullif_buttons_layout = QHBoxLayout()
        nullif_buttons_layout.addStretch()
        self.add_nullif_btn = QPushButton("Добавить NULLIF")
        self.add_nullif_btn.clicked.connect(self.add_nullif_expression)
        self.add_nullif_btn.setStyleSheet(get_button_style())
        nullif_buttons_layout.addWidget(self.add_nullif_btn)
        nullif_layout.addLayout(nullif_buttons_layout)
        
        layout.addWidget(nullif_group)
        
        # Список добавленных NULL выражений
        expressions_group = QGroupBox("Добавленные выражения для работы с NULL")
        expressions_layout = QVBoxLayout(expressions_group)
        
        self.null_expressions_list = QListWidget()
        self.null_expressions_list.setMinimumHeight(150)
        self.null_expressions_list.setMaximumHeight(300)
        self.null_expressions_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        expressions_layout.addWidget(self.null_expressions_list)
        
        # Управление выражениями
        expr_buttons_layout = QHBoxLayout()
        self.remove_null_expr_btn = QPushButton("Удалить выбранное")
        self.remove_null_expr_btn.clicked.connect(self.remove_null_expression)
        self.remove_null_expr_btn.setStyleSheet(get_button_style())
        expr_buttons_layout.addWidget(self.remove_null_expr_btn)
        
        expr_buttons_layout.addStretch()
        expressions_layout.addLayout(expr_buttons_layout)
        
        layout.addWidget(expressions_group)

    def load_tables(self):
        """Загрузка списка таблиц."""
        tables = self.controller.get_tables()
        
        self.table_combo.clear()
        self.null_table_combo.clear()
        
        self.table_combo.addItems(tables)
        self.null_table_combo.addItems(tables)
        
        if tables:
            self.on_table_changed(tables[0])
            self.on_null_table_changed(tables[0])

    def on_table_changed(self, table_name):
        """Обновление списка столбцов при изменении таблицы."""
        if table_name:
            columns = self.controller.get_table_columns(table_name)
            self.column_combo.clear()
            self.column_combo.addItems(columns)

    def on_null_table_changed(self, table_name):
        """Обновление списка столбцов для NULL функций."""
        if table_name:
            columns = self.controller.get_table_columns(table_name)
            self.coalesce_column.clear()
            self.nullif_column.clear()
            self.coalesce_column.addItems(columns)
            self.nullif_column.addItems(columns)

    def add_case_condition(self):
        """Добавление нового условия WHEN в CASE выражение."""
        row = self.conditions_table.rowCount()
        self.conditions_table.insertRow(row)

        # Тип условия
        condition_type = QComboBox()
        condition_type.addItems(["WHEN условие", "WHEN значение"])
        condition_type.setStyleSheet(get_combobox_style())
        self.conditions_table.setCellWidget(row, 0, condition_type)

        # Условие/значение
        condition_value = QLineEdit()
        condition_value.setStyleSheet(get_input_fields_style())
        condition_value.setPlaceholderText("Условие или значение для сравнения")
        self.conditions_table.setCellWidget(row, 1, condition_value)

        # Результат THEN
        then_value = QLineEdit()
        then_value.setStyleSheet(get_input_fields_style())
        then_value.setPlaceholderText("Результат если условие истинно")
        self.conditions_table.setCellWidget(row, 2, then_value)

        # Кнопка удаления
        remove_btn = QPushButton("Удалить")
        remove_btn.setStyleSheet(get_button_style())
        remove_btn.clicked.connect(lambda: self.remove_case_condition_row(row))
        self.conditions_table.setCellWidget(row, 3, remove_btn)

    def remove_case_condition(self):
        """Удаление выбранного условия CASE."""
        current_row = self.conditions_table.currentRow()
        if current_row >= 0:
            self.conditions_table.removeRow(current_row)

    def remove_case_condition_row(self, row):
        """Удаление конкретной строки условия CASE."""
        self.conditions_table.removeRow(row)
        # Обновляем индексы для оставшихся кнопок удаления
        for i in range(self.conditions_table.rowCount()):
            btn = self.conditions_table.cellWidget(i, 3)
            if btn:
                try:
                    btn.clicked.disconnect()
                except:
                    pass
                btn.clicked.connect(lambda checked, idx=i: self.remove_case_condition_row(idx))

    def add_coalesce_expression(self):
        """Добавление COALESCE выражения."""
        column = self.coalesce_column.currentText()
        values_text = self.coalesce_values.text().strip()
        
        if not column or not values_text:
            QMessageBox.warning(self, "Ошибка", "Заполните столбец и значения для COALESCE")
            return

        values = [v.strip() for v in values_text.split(',') if v.strip()]
        if not values:
            QMessageBox.warning(self, "Ошибка", "Введите хотя бы одно значение для подстановки")
            return

        # Формируем выражение COALESCE
        value_list = ", ".join([f"'{v}'" for v in values])
        expression = f"COALESCE({column}, {value_list})"
        
        self.add_null_expression_to_list("COALESCE", expression, f"{column}_coalesce")
        self.coalesce_values.clear()

    def add_nullif_expression(self):
        """Добавление NULLIF выражения."""
        column = self.nullif_column.currentText()
        value = self.nullif_value.text().strip()
        
        if not column or not value:
            QMessageBox.warning(self, "Ошибка", "Заполните столбец и значение для NULLIF")
            return

        # Формируем выражение NULLIF
        expression = f"NULLIF({column}, '{value}')"
        self.add_null_expression_to_list("NULLIF", expression, f"{column}_nullif")
        self.nullif_value.clear()

    def add_null_expression_to_list(self, func_type, expression, default_alias):
        """Добавление выражения NULL в список."""
        item_text = f"{func_type}: {expression} AS {default_alias}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, {
            'type': func_type,
            'expression': expression,
            'alias': default_alias
        })
        self.null_expressions_list.addItem(item)
        
        self.null_expressions.append({
            'type': func_type,
            'expression': expression,
            'alias': default_alias
        })

    def remove_null_expression(self):
        """Удаление выбранного NULL выражения."""
        current_row = self.null_expressions_list.currentRow()
        if current_row >= 0:
            self.null_expressions_list.takeItem(current_row)
            if current_row < len(self.null_expressions):
                self.null_expressions.pop(current_row)

    def build_case_expression(self):
        """Построение полного CASE выражения."""
        if self.conditions_table.rowCount() == 0:
            return None

        case_parts = ["CASE"]
        
        for row in range(self.conditions_table.rowCount()):
            condition_type_widget = self.conditions_table.cellWidget(row, 0)
            condition_value_widget = self.conditions_table.cellWidget(row, 1)
            then_value_widget = self.conditions_table.cellWidget(row, 2)
            
            if not condition_type_widget or not condition_value_widget or not then_value_widget:
                continue
                
            condition_type = condition_type_widget.currentText()
            condition_value = condition_value_widget.text().strip()
            then_value = then_value_widget.text().strip()

            if not condition_value or not then_value:
                continue

            if condition_type == "WHEN условие":
                case_parts.append(f"WHEN {condition_value} THEN '{then_value}'")
            else:
                column = self.column_combo.currentText()
                case_parts.append(f"WHEN {column} = '{condition_value}' THEN '{then_value}'")

        #ELSE часть
        else_value = self.else_value.text().strip()
        if else_value:
            case_parts.append(f"ELSE '{else_value}'")

        case_parts.append("END")

        #Алиас
        alias = self.case_alias.text().strip()
        if alias:
            case_parts.append(f"AS {alias}")

        return " ".join(case_parts)

    def build_null_expressions(self):
        """Построение списка выражений для NULL функций."""
        expressions = []
        
        for i in range(self.null_expressions_list.count()):
            item = self.null_expressions_list.item(i)
            if item and item.data(Qt.UserRole):
                data = item.data(Qt.UserRole)
                expression = data['expression']
                alias = data['alias']
                
                if alias:
                    expressions.append(f"{expression} AS {alias}")
                else:
                    expressions.append(expression)
                
        return expressions

    def build_complete_query(self):
        """Построение полного SQL запроса."""
        table = self.table_combo.currentText()
        if not table:
            return None

        select_parts = ["*"]

        # Добавляем CASE выражение
        case_expr = self.build_case_expression()
        if case_expr:
            select_parts.append(case_expr)

        # Добавляем NULL выражения
        null_exprs = self.build_null_expressions()
        select_parts.extend(null_exprs)

        # Строим финальный запрос
        query = f"SELECT {', '.join(select_parts)} FROM {table}"
        return query

    def update_sql_preview(self):
        """Обновление предпросмотра SQL."""
        query = self.build_complete_query()
        if query:
            self.sql_preview.setText(query)
        else:
            self.sql_preview.setText("-- Сформируйте выражение для просмотра SQL")

    def execute_query(self):
        """Выполнение построенного запроса."""
        query = self.build_complete_query()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Не удалось построить запрос")
            return

        try:
            self.sql_preview.setText(query)
            results = self.controller.execute_custom_request(query)
            self.display_results(results)
            
            QMessageBox.information(self, "Успех", f"Запрос выполнен успешно! Найдено записей: {len(results)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")

    def display_results(self, results):
        """Отображение результатов запроса."""
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return

        # Получаем названия столбцов из первого результата
        columns = list(results[0].keys())
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)

        # Настраиваем поведение заголовков
        header = self.results_table.horizontalHeader()
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        # Заполняем данными
        self.results_table.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, column_name in enumerate(columns):
                value = row_data.get(column_name, "")
                item = QTableWidgetItem(str(value) if value is not None else "NULL")
                self.results_table.setItem(row_idx, col_idx, item)

    def clear_form(self):
        """Очистка формы."""
        # Очищаем CASE условия
        self.conditions_table.setRowCount(0)
        self.else_value.clear()
        self.case_alias.clear()
        
        # Очищаем NULL выражения
        self.null_expressions_list.clear()
        self.null_expressions.clear()
        self.coalesce_values.clear()
        self.nullif_value.clear()
        
        # Очищаем предпросмотр и результаты
        self.sql_preview.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
