from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, \
    QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt

from .searchable_dialog import SearchableDialogMixin
from .string_operations import StringOperationsDialog
from core.custom_types import CustomTypesManager


class SearchableTableViewerDialog(QDialog, SearchableDialogMixin):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.types_manager = CustomTypesManager(controller.connection) if hasattr(controller, 'connection') else None
        self.setWindowTitle("Обозреватель таблиц (динамич.)")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_tables()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Верхняя панель с выбором таблицы
        top = QHBoxLayout()
        top.addWidget(QLabel("Таблица:"))
        self.table_combo = QComboBox()
        top.addWidget(self.table_combo)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.refresh_table)
        top.addWidget(refresh_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        top.addWidget(close_btn)

        layout.addLayout(top)

        self.table_widget = QTableWidget()
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Enable cell editing
        self.table_widget.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.table_widget.cellChanged.connect(self.on_cell_changed)

        layout.addWidget(self.table_widget)

        # Инициализируем компоненты поиска из миксина
        self.init_search_components()
        self.setup_search()

        # Подключаем сигнал смены таблицы
        self.table_combo.currentTextChanged.connect(self.refresh_table)

    def load_tables(self):
        tables = self.controller.get_tables() or []
        self.table_combo.clear()
        self.table_combo.addItems(tables)
        if tables:
            self.refresh_table()

    def refresh_table(self):
        table = self.table_combo.currentText()
        if not table:
            return

        try:
            query = f"SELECT * FROM {table} ORDER BY 1"
            rows = self.controller.execute_custom_request(query)

            self.table_widget.clear()

            if not rows:
                columns = self.controller.get_table_columns(table) or []
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(len(columns))
                self.table_widget.setHorizontalHeaderLabels(columns)
                # ВАЖНО: обновляем столбцы поиска при смене таблицы
                self.update_search_columns(self.table_widget)
                return

            columns = list(rows[0].keys())
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            self.table_widget.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, col in enumerate(columns):
                    val = row.get(col)
                    self.table_widget.setItem(i, j, QTableWidgetItem("" if val is None else str(val)))

            # ВАЖНО: обновляем столбцы поиска при смене таблицы
            self.update_search_columns(self.table_widget)

        except Exception as e:
            # Доп. страховка: на случай, если вызвали не через execute_custom_request
            try:
                if hasattr(self.controller, "connection") and self.controller.connection:
                    self.controller.connection.rollback()
            except Exception:
                pass
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить таблицу:\n{e}")

    def get_table_widget(self):
        """Возвращает таблицу для методов миксина"""
        return self.table_widget

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

    def on_cell_changed(self, row, column):
        """Обработчик изменения ячейки с валидацией"""
        self.table_widget.cellChanged.disconnect(self.on_cell_changed)

        item = self.table_widget.item(row, column)
        if not item:
            self.table_widget.cellChanged.connect(self.on_cell_changed)
            return

        new_value = item.text()
        table_name = self.table_combo.currentText()
        column_name = self.table_widget.horizontalHeaderItem(column).text()

        pk_item = self.table_widget.item(row, 0)
        if not pk_item:
            self.table_widget.cellChanged.connect(self.on_cell_changed)
            return

        pk_value = pk_item.text()

        if self.validate_and_update_cell(table_name, column_name, pk_value, new_value, row, column):
            pass
        else:
            try:
                old_value_query = f"SELECT {column_name} FROM {table_name} WHERE {self.get_primary_key_column(table_name)} = %s"
                self.controller.cursor.execute(old_value_query, (pk_value,))
                old_value = self.controller.cursor.fetchone()[0]
                item.setText(str(old_value) if old_value is not None else "")
            except Exception as e:
                item.setText("")

        self.table_widget.cellChanged.connect(self.on_cell_changed)

    def get_primary_key_column(self, table_name):
        """Get the primary key column name for a table"""
        try:
            self.controller.cursor.execute("""
                SELECT column_name 
                FROM information_schema.key_column_usage 
                WHERE table_name = %s AND constraint_name LIKE '%pkey%'
            """, (table_name,))
            result = self.controller.cursor.fetchone()
            return result[0] if result else self.table_widget.horizontalHeaderItem(0).text()
        except Exception:
            return self.table_widget.horizontalHeaderItem(0).text()

    def validate_and_update_cell(self, table_name, column_name, pk_value, new_value, row, column):
        """Validate the new cell value and update it in the database"""
        try:
            self.controller.cursor.execute("""
                SELECT data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, (table_name, column_name))

            col_info = self.controller.cursor.fetchone()
            if not col_info:
                return False

            data_type, udt_name = col_info

            if udt_name and self.types_manager:
                custom_types = self.types_manager.get_custom_types()
                enum_type = next((t for t in custom_types if t['name'] == udt_name and t['kind'] == 'enum'), None)

                if enum_type:
                    if new_value not in enum_type['values']:
                        QMessageBox.warning(
                            self,
                            "Ошибка валидации",
                            f"Недопустимое значение для типа {udt_name}. "
                            f"Допустимые значения: {', '.join(enum_type['values'])}"
                        )
                        return False

            pk_column = self.get_primary_key_column(table_name)
            update_query = f"UPDATE {table_name} SET {column_name} = %s WHERE {pk_column} = %s"

            if new_value == "" and data_type not in ['text', 'character varying', 'varchar']:
                param_value = None
            else:
                param_value = new_value

            self.controller.cursor.execute(update_query, (param_value, pk_value))
            self.controller.connection.commit()

            return True

        except Exception as e:
            self.controller.connection.rollback()
            QMessageBox.warning(
                self,
                "Ошибка обновления",
                f"Не удалось обновить значение: {str(e)}"
            )
            return False
