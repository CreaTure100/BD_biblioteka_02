from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QLabel,
    QLineEdit, QComboBox, QPushButton, QTextEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QCheckBox, QHeaderView, QGridLayout, QWidget
)
from PySide6.QtCore import QDateTime

from core.alter_operations import AlterTableManager
from core.custom_types import CustomTypesManager  # Добавляем импорт


class AlterTableDialog(QDialog):
    """
    Диалоговое окно для управления структурой базы данных через ALTER TABLE.
    Полностью совместимо с существующей архитектурой приложения.
    """

    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.alter_manager = AlterTableManager(db_connection)
        self.setup_ui()
        # ВАЖНО: сначала подключаем сигналы, затем загружаем данные
        self.connect_signals()
        self.load_tables()

    def setup_ui(self):
        self.setWindowTitle("Управление структурой базы данных")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Вкладки для разных операций
        self.tabs = QTabWidget()

        # Создаем вкладки
        self.setup_info_tab()
        self.setup_columns_tab()
        self.setup_rename_tab()
        self.setup_constraints_tab()
        self.setup_custom_types_tab()  # Добавляем новую вкладку

        layout.addWidget(self.tabs)

        # Поле для вывода результатов
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("Результат выполнения:"))
        layout.addWidget(self.result_text)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить информацию")
        self.refresh_btn.clicked.connect(self.load_tables)
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.close)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def setup_custom_types_tab(self):
        """Вкладка для работы с пользовательскими типами данных."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Кнопка для открытия диалога пользовательских типов
        self.custom_types_btn = QPushButton("Управление пользовательскими типами")
        self.custom_types_btn.clicked.connect(self.open_custom_types_dialog)
        layout.addWidget(self.custom_types_btn)

        # Информация о доступных пользовательских типах
        layout.addWidget(QLabel("Существующие пользовательские типы:"))
        self.custom_types_table = QTableWidget()
        self.custom_types_table.setColumnCount(3)
        self.custom_types_table.setHorizontalHeaderLabels(["Имя типа", "Тип", "Детали"])
        self.custom_types_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.custom_types_table)

        self.tabs.addTab(widget, "Пользовательские типы")

        # Загружаем информацию о типах
        self.load_custom_types()

    def open_custom_types_dialog(self):
        """Открыть диалог управления пользовательскими типами."""
        from ui.dialogs.custom_types_dialog import CustomTypesDialog
        dialog = CustomTypesDialog(self.db_connection, self)
        dialog.exec()
        # Обновляем информацию после закрытия диалога
        self.load_custom_types()
        self.load_tables()  # Обновляем информацию о таблицах, т.к. могли измениться типы

    def load_custom_types(self):
        """Загрузка информации о пользовательских типах."""
        types_manager = CustomTypesManager(self.db_connection)
        types = types_manager.get_custom_types()

        self.custom_types_table.setRowCount(len(types))

        for i, type_info in enumerate(types):
            self.custom_types_table.setItem(i, 0, QTableWidgetItem(type_info['name']))
            self.custom_types_table.setItem(i, 1, QTableWidgetItem(type_info['kind']))

            details = ""
            if type_info['kind'] == 'enum' and 'values' in type_info:
                details = f"Значения: {', '.join(type_info['values'])}"
            elif type_info['kind'] == 'composite' and 'attributes' in type_info:
                attrs = [f"{attr['attribute_name']} {attr['attribute_type']}"
                         for attr in type_info['attributes']]
                details = f"Атрибуты: {', '.join(attrs)}"

            self.custom_types_table.setItem(i, 2, QTableWidgetItem(details))
    def connect_signals(self):
        """Подключение сигналов для обновления комбобоксов."""
        self.drop_table_combo.currentTextChanged.connect(
            lambda: self.update_columns_combo(self.drop_table_combo, self.drop_column_combo)
        )
        self.rename_column_table_combo.currentTextChanged.connect(
            lambda: self.update_columns_combo(self.rename_column_table_combo, self.rename_old_column_combo)
        )
        self.drop_constraint_table_combo.currentTextChanged.connect(
            lambda: self.update_constraints_combo(self.drop_constraint_table_combo, self.drop_constraint_combo)
        )

    def setup_info_tab(self):
        """Вкладка с информацией о таблицах."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Таблица с информацией о таблицах БД
        self.tables_table = QTableWidget()
        self.tables_table.setColumnCount(4)
        self.tables_table.setHorizontalHeaderLabels(["Таблица", "Кол-во столбцов", "Типы данных", "Ограничения"])
        self.tables_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel("Информация о таблицах базы данных:"))
        layout.addWidget(self.tables_table)

        self.tabs.addTab(widget, "Обзор БД")

    def setup_columns_tab(self):
        """Вкладка для работы со столбцами."""
        widget = QWidget()
        layout = QGridLayout(widget)

        # Добавление столбца
        add_group = QGroupBox("Добавить столбец")
        add_layout = QGridLayout(add_group)

        add_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.add_table_combo = QComboBox()
        add_layout.addWidget(self.add_table_combo, 0, 1)

        add_layout.addWidget(QLabel("Имя столбца:"), 1, 0)
        self.column_name_edit = QLineEdit()
        add_layout.addWidget(self.column_name_edit, 1, 1)

        add_layout.addWidget(QLabel("Тип данных:"), 2, 0)
        self.data_type_combo = QComboBox()
        # Базовые типы данных
        base_types = [
            "VARCHAR(255)", "TEXT", "INTEGER", "BIGINT", "SMALLINT",
            "DECIMAL(10,2)", "NUMERIC", "BOOLEAN", "DATE", "TIMESTAMP",
            "SERIAL", "BIGSERIAL"
        ]
        self.data_type_combo.addItems(base_types)

        # Загружаем пользовательские типы
        self.load_custom_types_to_combo()

        add_layout.addWidget(self.data_type_combo, 2, 1)

        self.nullable_check = QCheckBox("Разрешить NULL")
        self.nullable_check.setChecked(True)
        add_layout.addWidget(self.nullable_check, 3, 0, 1, 2)

        add_layout.addWidget(QLabel("Значение по умолчанию:"), 4, 0)
        self.default_edit = QLineEdit()
        add_layout.addWidget(self.default_edit, 4, 1)

        self.add_column_btn = QPushButton("Добавить столбец")
        self.add_column_btn.clicked.connect(self.add_column)
        add_layout.addWidget(self.add_column_btn, 5, 0, 1, 2)

        layout.addWidget(add_group, 0, 0)

        # Удаление столбца
        drop_group = QGroupBox("Удалить столбец")
        drop_layout = QGridLayout(drop_group)

        drop_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.drop_table_combo = QComboBox()
        drop_layout.addWidget(self.drop_table_combo, 0, 1)

        drop_layout.addWidget(QLabel("Столбец:"), 1, 0)
        self.drop_column_combo = QComboBox()
        drop_layout.addWidget(self.drop_column_combo, 1, 1)

        self.drop_column_btn = QPushButton("Удалить столбец")
        self.drop_column_btn.clicked.connect(self.drop_column)
        drop_layout.addWidget(self.drop_column_btn, 2, 0, 1, 2)

        layout.addWidget(drop_group, 1, 0)

        self.tabs.addTab(widget, "Столбцы")

    def load_custom_types_to_combo(self):
        """Загрузка пользовательских типов в комбобокс типов данных."""
        types_manager = CustomTypesManager(self.db_connection)
        custom_types = types_manager.get_custom_types()

        # Добавляем разделитель
        if custom_types:
            self.data_type_combo.insertSeparator(self.data_type_combo.count())

            # Добавляем пользовательские типы
            for type_info in custom_types:
                self.data_type_combo.addItem(type_info['name'])

    def setup_rename_tab(self):
        """Вкладка для переименования."""
        widget = QWidget()
        layout = QGridLayout(widget)

        # Переименование таблицы
        table_rename_group = QGroupBox("Переименовать таблицу")
        table_layout = QGridLayout(table_rename_group)

        table_layout.addWidget(QLabel("Текущее имя:"), 0, 0)
        self.rename_old_table_combo = QComboBox()
        table_layout.addWidget(self.rename_old_table_combo, 0, 1)

        table_layout.addWidget(QLabel("Новое имя:"), 1, 0)
        self.rename_new_table_edit = QLineEdit()
        table_layout.addWidget(self.rename_new_table_edit, 1, 1)

        self.rename_table_btn = QPushButton("Переименовать таблицу")
        self.rename_table_btn.clicked.connect(self.rename_table)
        table_layout.addWidget(self.rename_table_btn, 2, 0, 1, 2)

        layout.addWidget(table_rename_group, 0, 0)

        # Переименование столбца
        column_rename_group = QGroupBox("Переименовать столбец")
        column_layout = QGridLayout(column_rename_group)

        column_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.rename_column_table_combo = QComboBox()
        column_layout.addWidget(self.rename_column_table_combo, 0, 1)

        column_layout.addWidget(QLabel("Текущее имя:"), 1, 0)
        self.rename_old_column_combo = QComboBox()
        column_layout.addWidget(self.rename_old_column_combo, 1, 1)

        column_layout.addWidget(QLabel("Новое имя:"), 2, 0)
        self.rename_new_column_edit = QLineEdit()
        column_layout.addWidget(self.rename_new_column_edit, 2, 1)

        self.rename_column_btn = QPushButton("Переименовать столбец")
        self.rename_column_btn.clicked.connect(self.rename_column)
        column_layout.addWidget(self.rename_column_btn, 3, 0, 1, 2)

        layout.addWidget(column_rename_group, 1, 0)

        self.tabs.addTab(widget, "Переименование")

    def setup_constraints_tab(self):
        """Вкладка для работы с ограничениями."""
        widget = QWidget()
        layout = QGridLayout(widget)

        # Добавление ограничений
        add_constraint_group = QGroupBox("Добавить ограничение")
        add_layout = QGridLayout(add_constraint_group)

        add_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.constraint_table_combo = QComboBox()
        add_layout.addWidget(self.constraint_table_combo, 0, 1)

        add_layout.addWidget(QLabel("Тип ограничения:"), 1, 0)
        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems(["UNIQUE", "CHECK", "PRIMARY KEY", "FOREIGN KEY"])
        add_layout.addWidget(self.constraint_type_combo, 1, 1)

        add_layout.addWidget(QLabel("Имя ограничения:"), 2, 0)
        self.constraint_name_edit = QLineEdit()
        add_layout.addWidget(self.constraint_name_edit, 2, 1)

        add_layout.addWidget(QLabel("Определение:"), 3, 0)
        self.constraint_definition_edit = QLineEdit()
        self.constraint_definition_edit.setPlaceholderText("имя_столбца или условие CHECK")
        add_layout.addWidget(self.constraint_definition_edit, 3, 1)

        self.add_constraint_btn = QPushButton("Добавить ограничение")
        self.add_constraint_btn.clicked.connect(self.add_constraint)
        add_layout.addWidget(self.add_constraint_btn, 4, 0, 1, 2)

        layout.addWidget(add_constraint_group, 0, 0)

        # Удаление ограничений
        drop_constraint_group = QGroupBox("Удалить ограничение")
        drop_layout = QGridLayout(drop_constraint_group)

        drop_layout.addWidget(QLabel("Таблица:"), 0, 0)
        self.drop_constraint_table_combo = QComboBox()
        drop_layout.addWidget(self.drop_constraint_table_combo, 0, 1)

        drop_layout.addWidget(QLabel("Ограничение:"), 1, 0)
        self.drop_constraint_combo = QComboBox()
        drop_layout.addWidget(self.drop_constraint_combo, 1, 1)

        self.drop_constraint_btn = QPushButton("Удалить ограничение")
        self.drop_constraint_btn.clicked.connect(self.drop_constraint)
        drop_layout.addWidget(self.drop_constraint_btn, 2, 0, 1, 2)

        layout.addWidget(drop_constraint_group, 1, 0)

        self.tabs.addTab(widget, "Ограничения")

    def load_tables(self):
        """Загрузка списка таблиц и их информации."""
        tables = self.alter_manager.get_tables()

        # Обновляем все комбобоксы с таблицами
        for combo in [self.add_table_combo, self.drop_table_combo,
                      self.rename_old_table_combo, self.constraint_table_combo,
                      self.drop_constraint_table_combo, self.rename_column_table_combo]:
            combo.blockSignals(True)
            combo.clear()
            if tables:
                combo.addItems(tables)
                combo.setCurrentIndex(0)
            combo.blockSignals(False)

        # Первичная инициализация зависимых комбобоксов
        if tables:
            self.update_columns_combo(self.drop_table_combo, self.drop_column_combo)
            self.update_columns_combo(self.rename_column_table_combo, self.rename_old_column_combo)
            self.update_constraints_combo(self.drop_constraint_table_combo, self.drop_constraint_combo)

        # Обновляем таблицу “Обзор БД”
        self.tables_table.setRowCount(len(tables))
        for i, table in enumerate(tables):
            columns = self.alter_manager.get_table_columns(table)
            constraints = self.alter_manager.get_table_constraints(table)

            self.tables_table.setItem(i, 0, QTableWidgetItem(table))
            self.tables_table.setItem(i, 1, QTableWidgetItem(str(len(columns))))
            self.tables_table.setItem(i, 2, QTableWidgetItem(", ".join([col[1] for col in columns])))
            self.tables_table.setItem(i, 3, QTableWidgetItem(", ".join([con[0] for con in constraints])))

    def rename_table(self):
        old_name = (self.rename_old_table_combo.currentText() or "").strip()
        new_name = (self.rename_new_table_edit.text() or "").strip()

        # Базовые проверки
        if not old_name or not new_name:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        if old_name == new_name:
            QMessageBox.information(self, "Информация", "Новое имя совпадает со старым")
            return

        # Усиленное предупреждение для системных таблиц приложения
        app_core_tables = {"authors", "books", "readers", "issues", "book_authors"}
        is_core = old_name in app_core_tables

        # Всегда спрашиваем подтверждение, чтобы диалог точно показывался
        title = "Внимание" if is_core else "Подтверждение"
        msg = (
            "Вы собираетесь переименовать системную таблицу приложения.\n"
            "Нестатические окна перестанут работать (до возврата имени).\n\n"
            f"Переименовать '{old_name}' в '{new_name}'?"
            if is_core else
            f"Переименовать таблицу '{old_name}' в '{new_name}'?"
        )

        reply = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            # Отмена пользователем
            return

        # Выполняем переименование
        success, message = self.alter_manager.rename_table(old_name, new_name)
        self.log_result(success, message)

        if success:
            # Обновляем все списки и очищаем поле ввода
            self.load_tables()
            self.rename_new_table_edit.clear()
    def update_columns_combo(self, table_combo, column_combo):
        """Обновить комбобокс столбцов при изменении таблицы."""
        table = table_combo.currentText()
        column_combo.clear()
        if table:
            columns = self.alter_manager.get_table_columns(table)
            column_combo.addItems([col[0] for col in columns])

    def update_constraints_combo(self, table_combo, constraint_combo):
        """Обновить комбобокс ограничений при изменении таблицы."""
        table = table_combo.currentText()
        constraint_combo.clear()
        if table:
            constraints = self.alter_manager.get_table_constraints(table)
            constraint_combo.addItems([con[0] for con in constraints])

    def log_result(self, success: bool, message: str):
        """Логирование результатов операций."""
        color = "green" if success else "red"
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.result_text.append(f'<font color="{color}">[{timestamp}] {message}</font>')

        if not success:
            QMessageBox.warning(self, "Ошибка", message)
        else:
            QMessageBox.information(self, "Успех", message)

    # Методы для обработки действий
    def add_column(self):
        table = self.add_table_combo.currentText()
        column = self.column_name_edit.text()
        data_type = self.data_type_combo.currentText()
        nullable = self.nullable_check.isChecked()
        default = self.default_edit.text() or None

        if not table or not column:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        success, message = self.alter_manager.add_column(table, column, data_type, nullable, default)
        self.log_result(success, message)
        if success:
            self.load_tables()
            self.column_name_edit.clear()
            self.default_edit.clear()

    def drop_column(self):
        table = self.drop_table_combo.currentText()
        column = self.drop_column_combo.currentText()

        if not table or not column:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу и столбец")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить столбец '{column}' из таблицы '{table}'?")
        if reply == QMessageBox.Yes:
            success, message = self.alter_manager.drop_column(table, column)
            self.log_result(success, message)
            if success:
                self.load_tables()

    def rename_column(self):
        table = self.rename_column_table_combo.currentText()
        old_name = self.rename_old_column_combo.currentText()
        new_name = self.rename_new_column_edit.text()

        if not table or not old_name or not new_name:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        success, message = self.alter_manager.rename_column(table, old_name, new_name)
        self.log_result(success, message)
        if success:
            self.load_tables()

            self.rename_new_column_edit.clear()

    def add_constraint(self):
        table = self.constraint_table_combo.currentText()
        constraint_type = self.constraint_type_combo.currentText()
        constraint_name = self.constraint_name_edit.text()
        definition = self.constraint_definition_edit.text()

        if not table or not constraint_name or not definition:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        success, message = self.alter_manager.add_constraint(table, constraint_type, constraint_name, definition)
        self.log_result(success, message)
        if success:
            self.load_tables()
            self.constraint_name_edit.clear()
            self.constraint_definition_edit.clear()

    def drop_constraint(self):
        table = self.drop_constraint_table_combo.currentText()
        constraint_name = self.drop_constraint_combo.currentText()

        if not table or not constraint_name:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу и ограничение")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить ограничение '{constraint_name}'?")
        if reply == QMessageBox.Yes:
            success, message = self.alter_manager.drop_constraint(table, constraint_name)
            self.log_result(success, message)
            if success:
                self.load_tables()