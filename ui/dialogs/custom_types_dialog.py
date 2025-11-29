from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QListWidget, QListWidgetItem, QLineEdit, QComboBox,
    QFormLayout, QGroupBox, QInputDialog, QTabWidget
)
from PySide6.QtCore import Qt

from core.custom_types import CustomTypesManager


class CustomTypesDialog(QDialog):


    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.types_manager = CustomTypesManager(db_connection)

        self.setWindowTitle("Управление пользовательскими типами")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_types()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        layout = QVBoxLayout(self)

        # Кнопки создания новых типов
        create_buttons_layout = QHBoxLayout()

        self.new_enum_btn = QPushButton("Новый ENUM")
        self.new_enum_btn.clicked.connect(self.create_new_enum)
        create_buttons_layout.addWidget(self.new_enum_btn)

        self.new_composite_btn = QPushButton("Новый составной тип")
        self.new_composite_btn.clicked.connect(self.create_new_composite)
        create_buttons_layout.addWidget(self.new_composite_btn)

        self.edit_type_btn = QPushButton("Редактировать пользовательский тип")
        self.edit_type_btn.clicked.connect(self.edit_type)
        create_buttons_layout.addWidget(self.edit_type_btn)

        layout.addLayout(create_buttons_layout)

        # Таблица существующих типов
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(3)
        self.types_table.setHorizontalHeaderLabels(["Имя типа", "Тип", "Детали"])
        self.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.types_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.types_table)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_types)
        buttons_layout.addWidget(self.refresh_btn)

        self.delete_btn = QPushButton("Удалить выбранный тип")
        self.delete_btn.clicked.connect(self.delete_type)
        buttons_layout.addWidget(self.delete_btn)

        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)

        layout.addLayout(buttons_layout)

    def load_types(self):
        """Загрузка списка пользовательских типов."""
        types = self.types_manager.get_custom_types()
        self.types_table.setRowCount(len(types))

        for i, type_info in enumerate(types):
            self.types_table.setItem(i, 0, QTableWidgetItem(type_info['name']))
            self.types_table.setItem(i, 1, QTableWidgetItem(type_info['kind']))

            details = ""
            if type_info['kind'] == 'enum' and 'values' in type_info:
                details = f"Значения: {', '.join(type_info['values'])}"
            elif type_info['kind'] == 'composite' and 'attributes' in type_info:
                attrs = [f"{attr['attribute_name']} {attr['attribute_type']}"
                         for attr in type_info['attributes']]
                details = f"Атрибуты: {', '.join(attrs)}"

            self.types_table.setItem(i, 2, QTableWidgetItem(details))

    def create_new_enum(self):
        """Создание нового ENUM типа."""
        dialog = CreateEnumDialog(self)
        if dialog.exec():
            type_name, values = dialog.get_data()
            success, message = self.types_manager.create_enum_type(type_name, values)

            if success:
                QMessageBox.information(self, "Успех", f"ENUM тип '{type_name}' успешно создан")
                self.load_types()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать ENUM тип: {message}")

    def create_new_composite(self):
        """Создание нового составного типа."""
        dialog = CreateCompositeDialog(self)
        if dialog.exec():
            type_name, attributes = dialog.get_data()
            success, message = self.types_manager.create_composite_type(type_name, attributes)

            if success:
                QMessageBox.information(self, "Успех", f"Составной тип '{type_name}' успешно создан")
                self.load_types()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать составной тип: {message}")

    def edit_type(self):
        """Редактирование выбранного типа."""
        selected_items = self.types_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите тип для редактирования")
            return

        row = selected_items[0].row()
        type_name = self.types_table.item(row, 0).text()
        type_kind = self.types_table.item(row, 1).text()

        types = self.types_manager.get_custom_types()
        type_info = next((t for t in types if t['name'] == type_name), None)

        if not type_info:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти информацию о типе")
            return

        if type_kind == 'enum':
            dialog = EditEnumDialog(type_info, self.db_connection, self)
        else:  # composite
            dialog = EditCompositeDialog(type_info, self.db_connection, self)

        if dialog.exec():
            # Обновляем таблицу после успешного редактирования
            self.load_types()

    def delete_type(self):
        """Удаление выбранного типа."""
        selected_items = self.types_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите тип для удаления")
            return

        row = selected_items[0].row()
        type_name = self.types_table.item(row, 0).text()

        # Проверяем, используется ли тип
        if self.types_manager.is_type_used(type_name):
            usage = self.types_manager.get_type_usage(type_name)
            usage_info = "\n".join([f"- {table}.{column}" for table, column in usage])

            reply = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Тип '{type_name}' используется в следующих столбцах:\n{usage_info}\n\n"
                f"Удаление может привести к ошибкам. Продолжить?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить тип '{type_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.types_manager.drop_type(type_name)

            if success:
                QMessageBox.information(self, "Успех", f"Тип '{type_name}' успешно удален")
                self.load_types()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить тип: {message}")


class CreateEnumDialog(QDialog):
    """Диалог для создания нового ENUM типа."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать новый ENUM тип")
        self.setMinimumWidth(400)
        self.values = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow("Имя типа:", self.name_edit)

        layout.addLayout(form_layout)

        # Управление значениями
        values_group = QGroupBox("Значения ENUM")
        values_layout = QVBoxLayout(values_group)

        self.values_list = QListWidget()
        values_layout.addWidget(self.values_list)

        values_buttons_layout = QHBoxLayout()

        self.add_value_btn = QPushButton("Добавить значение")
        self.add_value_btn.clicked.connect(self.add_value)
        values_buttons_layout.addWidget(self.add_value_btn)

        self.remove_value_btn = QPushButton("Удалить значение")
        self.remove_value_btn.clicked.connect(self.remove_value)
        values_buttons_layout.addWidget(self.remove_value_btn)

        values_layout.addLayout(values_buttons_layout)
        layout.addWidget(values_group)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.create_btn = QPushButton("Создать")
        self.create_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(self.create_btn)

        layout.addLayout(buttons_layout)

    def add_value(self):
        value, ok = QInputDialog.getText(self, "Добавить значение", "Введите значение ENUM:")
        if ok and value.strip():
            self.values.append(value.strip())
            self.values_list.addItem(value.strip())

    def remove_value(self):
        current_row = self.values_list.currentRow()
        if current_row >= 0:
            self.values_list.takeItem(current_row)
            self.values.pop(current_row)

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя типа")
            return

        if not self.values:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одно значение ENUM")
            return

        self.accept()

    def get_data(self):
        return self.name_edit.text().strip(), self.values


class CreateCompositeDialog(QDialog):
    """Диалог для создания нового составного типа."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать новый составной тип")
        self.setMinimumWidth(500)
        self.attributes = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow("Имя типа:", self.name_edit)

        layout.addLayout(form_layout)

        # Управление атрибутами
        attrs_group = QGroupBox("Атрибуты составного типа")
        attrs_layout = QVBoxLayout(attrs_group)

        self.attrs_table = QTableWidget()
        self.attrs_table.setColumnCount(2)
        self.attrs_table.setHorizontalHeaderLabels(["Имя атрибута", "Тип данных"])
        self.attrs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        attrs_layout.addWidget(self.attrs_table)

        attrs_buttons_layout = QHBoxLayout()

        self.add_attr_btn = QPushButton("Добавить атрибут")
        self.add_attr_btn.clicked.connect(self.add_attribute)
        attrs_buttons_layout.addWidget(self.add_attr_btn)

        self.remove_attr_btn = QPushButton("Удалить атрибут")
        self.remove_attr_btn.clicked.connect(self.remove_attribute)
        attrs_buttons_layout.addWidget(self.remove_attr_btn)

        attrs_layout.addLayout(attrs_buttons_layout)
        layout.addWidget(attrs_group)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.create_btn = QPushButton("Создать")
        self.create_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(self.create_btn)

        layout.addLayout(buttons_layout)

    def add_attribute(self):
        dialog = AddAttributeDialog(self)
        if dialog.exec():
            attr_name, attr_type = dialog.get_data()
            self.attributes.append({'name': attr_name, 'type': attr_type})
            self.update_attributes_table()

    def remove_attribute(self):
        current_row = self.attrs_table.currentRow()
        if current_row >= 0:
            self.attributes.pop(current_row)
            self.update_attributes_table()

    def update_attributes_table(self):
        self.attrs_table.setRowCount(len(self.attributes))
        for i, attr in enumerate(self.attributes):
            self.attrs_table.setItem(i, 0, QTableWidgetItem(attr['name']))
            self.attrs_table.setItem(i, 1, QTableWidgetItem(attr['type']))

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя типа")
            return

        if not self.attributes:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один атрибут")
            return

        self.accept()

    def get_data(self):
        return self.name_edit.text().strip(), self.attributes


class AddAttributeDialog(QDialog):
    """Диалог для добавления атрибута в составной тип."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить атрибут")
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        layout.addRow("Имя атрибута:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "VARCHAR(255)", "TEXT", "INTEGER", "BIGINT", "SMALLINT",
            "DECIMAL(10,2)", "NUMERIC", "BOOLEAN", "DATE", "TIMESTAMP"
        ])
        layout.addRow("Тип данных:", self.type_combo)

        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(add_btn)

        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя атрибута")
            return

        self.accept()

    def get_data(self):
        return self.name_edit.text().strip(), self.type_combo.currentText()


class EditEnumDialog(QDialog):
    """Диалог для редактирования ENUM типа."""

    def __init__(self, type_info, db_connection, parent=None):
        super().__init__(parent)
        self.type_info = type_info
        self.db_connection = db_connection
        self.types_manager = CustomTypesManager(db_connection)
        self.setWindowTitle(f"Редактировать ENUM: {type_info['name']}")
        self.setMinimumWidth(500)
        self.values = type_info.get('values', [])[:]  # Копируем значения
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Поле для имени типа
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Новое имя типа:"))
        self.name_edit = QLineEdit(self.type_info['name'])
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Управление значениями
        values_group = QGroupBox("Значения ENUM")
        values_layout = QVBoxLayout(values_group)

        self.values_list = QListWidget()
        for value in self.values:
            self.values_list.addItem(value)
        values_layout.addWidget(self.values_list)

        values_buttons_layout = QHBoxLayout()

        self.add_value_btn = QPushButton("Добавить значение")
        self.add_value_btn.clicked.connect(self.add_value)
        values_buttons_layout.addWidget(self.add_value_btn)

        self.remove_value_btn = QPushButton("Удалить значение")
        self.remove_value_btn.clicked.connect(self.remove_value)
        values_buttons_layout.addWidget(self.remove_value_btn)

        self.edit_value_btn = QPushButton("Редактировать значение")
        self.edit_value_btn.clicked.connect(self.edit_value)
        values_buttons_layout.addWidget(self.edit_value_btn)

        values_layout.addLayout(values_buttons_layout)
        layout.addWidget(values_group)

        # Информация о миграции
        if self.types_manager.is_type_used(self.type_info['name']):
            info_label = QLabel(
                "⚠️ ВНИМАНИЕ: Этот тип используется в таблицах. \n"
                "Изменение приведет к созданию нового типа и миграции данных."
            )
            info_label.setStyleSheet("color: orange; font-weight: bold;")
            layout.addWidget(info_label)

        # Кнопки
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("Сохранить изменения")
        self.save_btn.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_btn)

        layout.addLayout(buttons_layout)

    def add_value(self):
        value, ok = QInputDialog.getText(self, "Добавить значение", "Введите значение ENUM:")
        if ok and value.strip():
            self.values.append(value.strip())
            self.values_list.addItem(value.strip())

    def remove_value(self):
        current_row = self.values_list.currentRow()
        if current_row >= 0:
            self.values_list.takeItem(current_row)
            self.values.pop(current_row)

    def edit_value(self):
        current_row = self.values_list.currentRow()
        if current_row >= 0:
            old_value = self.values[current_row]
            new_value, ok = QInputDialog.getText(
                self, "Редактировать значение",
                "Введите новое значение:",
                text=old_value
            )
            if ok and new_value.strip():
                self.values[current_row] = new_value.strip()
                self.values_list.currentItem().setText(new_value.strip())

    def save_changes(self):
        new_name = self.name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Ошибка", "Введите имя типа")
            return

        if not self.values:
            QMessageBox.warning(self, "Ошибка", "ENUM должен содержать хотя бы одно значение")
            return

        old_name = self.type_info['name']
        old_values = self.type_info.get('values', [])

        # Всегда используем подход с созданием нового типа для любых изменений
        if new_name == old_name and self.values == old_values:
            QMessageBox.information(self, "Информация", "Изменений не обнаружено")
            return

        # Для любых изменений (даже при том же имени) создаем новый тип
        if new_name == old_name:
            # Генерируем временное имя для нового типа
            temp_name = f"{old_name}_new_{id(self)}"
            success, message = self.types_manager.update_enum_type(old_name, temp_name, self.values)
            if success:
                # Переименовываем обратно
                success, message = self.types_manager.update_enum_type(temp_name, old_name, self.values)
        else:
            # Создаем новый тип с новым именем
            success, message = self.types_manager.update_enum_type(old_name, new_name, self.values)

        if success:
            QMessageBox.information(self, "Успех", "ENUM тип успешно обновлен")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить тип: {message}")


class EditCompositeDialog(QDialog):
    """Диалог для редактирования составного типа."""

    def __init__(self, type_info, db_connection, parent=None):
        super().__init__(parent)
        self.type_info = type_info
        self.db_connection = db_connection
        self.types_manager = CustomTypesManager(db_connection)
        self.setWindowTitle(f"Редактировать составной тип: {type_info['name']}")
        self.setMinimumWidth(600)
        self.attributes = [
            {'name': attr['attribute_name'], 'type': attr['attribute_type']}
            for attr in type_info.get('attributes', [])
        ]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Поле для имени типа
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Новое имя типа:"))
        self.name_edit = QLineEdit(self.type_info['name'])
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Управление атрибутами
        attrs_group = QGroupBox("Атрибуты составного типа")
        attrs_layout = QVBoxLayout(attrs_group)

        self.attrs_table = QTableWidget()
        self.attrs_table.setColumnCount(2)
        self.attrs_table.setHorizontalHeaderLabels(["Имя атрибута", "Тип данных"])
        self.attrs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.attrs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.update_attributes_table()
        attrs_layout.addWidget(self.attrs_table)

        attrs_buttons_layout = QHBoxLayout()

        self.add_attr_btn = QPushButton("Добавить атрибут")
        self.add_attr_btn.clicked.connect(self.add_attribute)
        attrs_buttons_layout.addWidget(self.add_attr_btn)

        self.remove_attr_btn = QPushButton("Удалить атрибут")
        self.remove_attr_btn.clicked.connect(self.remove_attribute)
        attrs_buttons_layout.addWidget(self.remove_attr_btn)

        self.edit_attr_btn = QPushButton("Редактировать атрибут")
        self.edit_attr_btn.clicked.connect(self.edit_attribute)
        attrs_buttons_layout.addWidget(self.edit_attr_btn)

        attrs_layout.addLayout(attrs_buttons_layout)
        layout.addWidget(attrs_group)

        # Информация о миграции
        if self.types_manager.is_type_used(self.type_info['name']):
            info_label = QLabel(
                "⚠️ ВНИМАНИЕ: Этот тип используется в таблицах. \n"
                "Изменение приведет к созданию нового типа и миграции данных."
            )
            info_label.setStyleSheet("color: orange; font-weight: bold;")
            layout.addWidget(info_label)

        # Кнопки
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("Сохранить изменения")
        self.save_btn.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_btn)

        layout.addLayout(buttons_layout)

    def update_attributes_table(self):
        self.attrs_table.setRowCount(len(self.attributes))
        for i, attr in enumerate(self.attributes):
            self.attrs_table.setItem(i, 0, QTableWidgetItem(attr['name']))
            self.attrs_table.setItem(i, 1, QTableWidgetItem(attr['type']))

    def add_attribute(self):
        dialog = AddAttributeDialog(self)
        if dialog.exec():
            attr_name, attr_type = dialog.get_data()
            self.attributes.append({'name': attr_name, 'type': attr_type})
            self.update_attributes_table()

    def remove_attribute(self):
        current_row = self.attrs_table.currentRow()
        if current_row >= 0:
            self.attributes.pop(current_row)
            self.update_attributes_table()

    def edit_attribute(self):
        current_row = self.attrs_table.currentRow()
        if current_row >= 0:
            old_attr = self.attributes[current_row]
            dialog = AddAttributeDialog(self)
            dialog.name_edit.setText(old_attr['name'])
            dialog.type_combo.setCurrentText(old_attr['type'])

            if dialog.exec():
                new_name, new_type = dialog.get_data()
                self.attributes[current_row] = {'name': new_name, 'type': new_type}
                self.update_attributes_table()

    def save_changes(self):
        new_name = self.name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Ошибка", "Введите имя типа")
            return

        if not self.attributes:
            QMessageBox.warning(self, "Ошибка", "Составной тип должен содержать хотя бы один атрибут")
            return

        # Проверяем, изменилось ли что-то
        old_name = self.type_info['name']
        old_attributes = [
            {'name': attr['attribute_name'], 'type': attr['attribute_type']}
            for attr in self.type_info.get('attributes', [])
        ]

        if new_name == old_name and self.attributes == old_attributes:
            QMessageBox.information(self, "Информация", "Изменений не обнаружено")
            return

        # Подтверждение для используемых типов
        if self.types_manager.is_type_used(old_name):
            reply = QMessageBox.question(
                self, "Подтверждение миграции",
                f"Тип '{old_name}' используется в таблицах. \n"
                f"Будет создан новый тип '{new_name}' и выполнена миграция данных. \n"
                f"Продолжить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Сохраняем изменения через создание нового типа
        success, message = self.types_manager.update_composite_type(
            old_name, new_name, self.attributes
        )

        if success:
            QMessageBox.information(self, "Успех", "Составной тип успешно обновлен")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить тип: {message}")