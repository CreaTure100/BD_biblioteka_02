from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator

from core.enums import Country
from core.additional_classes import NumericTableItem
from ui.styles import get_form_label_style

from ui.widgets.search_widget import SearchWidget

class AuthorsDialog(QDialog):
    """
    Диалог для просмотра авторов.
    Отображает список всех свторов с возможностью добавления и удаления.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent_window = parent
        self.setWindowTitle("Авторы")
        self.setMinimumSize(800, 500)
        self.setup_ui()

    def edit_author(self, row, column):
        author_id = int(self.author_table.item(row, 0).text())
        author = next((p for p in self.authors if p['author_id'] == author_id), None)
        if not author:
            return
        dialog = EditAuthorDialog(self.controller, author, self)
        if dialog.exec():
            new_last_name = dialog.last_name_edit.text().strip()
            new_first_name = dialog.first_name_edit.text().strip()
            new_patronymic = dialog.patronymic_edit.text().strip()
            new_birth_year = int(dialog.birth_year_edit.text().strip())
            new_country = dialog.country_combo.currentText().strip()

            success, msg = self.controller.update_author(
                author_id,
                new_last_name,
                new_first_name,
                new_patronymic,
                new_birth_year,
                new_country
            )
            if success:
                self.update_authors_table()
                QMessageBox.information(self, "Успех", "Автор успешно обновлен.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить автора: {msg}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title_label = QLabel("<h2>Авторы</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        self.authors = self.controller.get_authors()
        if not self.authors:
            empty_label = QLabel("Авторов нет.")
            empty_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_label)
        else:
            self.author_table = QTableWidget()
            self.author_table.setColumnCount(6)
            self.author_table.setHorizontalHeaderLabels(
                ["ID", "Фамилия", "Имя", "Отчество", "Год рождения", "Страна"])
            self.author_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.author_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.update_authors_table()
            self.author_table.setSortingEnabled(True)
            self.author_table.cellDoubleClicked.connect(self.edit_author)
            layout.addWidget(self.author_table)
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить автора")
        add_btn.clicked.connect(self.add_author)
        buttons_layout.addWidget(add_btn)
        del_btn = QPushButton("Удалить автора")
        del_btn.clicked.connect(self.delete_author)
        buttons_layout.addWidget(del_btn)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)

        self.search_widget = SearchWidget()
        self.search_widget.searchRequested.connect(self.perform_search)
        layout.addWidget(self.search_widget)

    def update_authors_table(self, authors=None):
        if authors is None:
            self.authors = self.controller.get_authors()
        else:
            self.authors = authors

        self.author_table.setRowCount(len(self.authors))
        for i, auth in enumerate(self.authors):
            id_item = NumericTableItem(str(auth['author_id']), auth['author_id'])
            last_name_item = QTableWidgetItem(auth['last_name'])
            first_name_item = QTableWidgetItem(auth['first_name'])
            patronymic_item = QTableWidgetItem(auth['patronymic'])
            year_item = NumericTableItem(str(auth['birth_year']), auth['birth_year'])
            country_item = QTableWidgetItem(auth['country'])
            self.author_table.setItem(i, 0, id_item)
            self.author_table.setItem(i, 1, last_name_item)
            self.author_table.setItem(i, 2, first_name_item)
            self.author_table.setItem(i, 3, patronymic_item)
            self.author_table.setItem(i, 4, year_item)
            self.author_table.setItem(i, 5, country_item)

    def add_author(self):
        dialog = AddAuthorDialog(self.controller, self)
        if dialog.exec():
            last_name = dialog.last_name_edit.text().strip()
            first_name = dialog.first_name_edit.text().strip()
            patronymic = dialog.patronymic_edit.text().strip()
            birth_year = dialog.birth_year_spin.value()
            country = dialog.country_combo.currentText().strip()
            success = self.controller.add_author(
                last_name,
                first_name,
                patronymic,
                birth_year,
                country
            )
            if success:
                self.update_authors_table()
                QMessageBox.information(self, "Успех", "Автор успешно добавлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить автора")

    def delete_author(self):
        selected_rows = self.author_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите автора для удаления.")
            return
        row = selected_rows[0].row()
        author_id = int(self.author_table.item(row, 0).text())
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этого автора?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success, msg = self.controller.delete_author(author_id)
            if success:
                self.update_authors_table()
                QMessageBox.information(self, "Успех", "Автор успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить автора: {msg}")

    def perform_search(self, search_type, search_text):
        """Выполнение поиска по авторам"""
        if not search_text:
            self.update_authors_table()  # Показать все записи
            return

        try:
            # ИСПРАВЛЕННЫЙ ПОИСК - теперь ищет по всем полям
            authors = self.controller.search_authors_comprehensive(
                search_type, 
                search_text, 
                search_in_all_fields=True  # ← ВКЛЮЧАЕМ ПОИСК ПО ВСЕМ ПОЛЯМ
            )
        
            # Обновляем таблицу с результатами
            self.update_authors_table(authors)
            
            # Показываем сообщение о количестве найденных результатов
            if authors:
                QMessageBox.information(self, "Поиск завершен", 
                                      f"Найдено авторов: {len(authors)}")
            else:
                QMessageBox.information(self, "Поиск завершен", 
                                      "Авторы не найдены")
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при поиске: {str(e)}")

class AddAuthorDialog(QDialog):
    """
    Диалог добавления нового автора.
    Позволяет ввести ФИО, год рождения (удобно через QSpinBox) и выбрать страну из списка.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить автора")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = QLineEdit()
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = QLineEdit()
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = QLineEdit()
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Год рождения через QSpinBox (аналогично year_spin)
        birth_year_label = QLabel("Год рождения:")
        birth_year_label.setStyleSheet(label_style)
        self.birth_year_spin = QSpinBox()
        self.birth_year_spin.setRange(1700, 2025)
        self.birth_year_spin.setValue(1980)
        layout.addRow(birth_year_label, self.birth_year_spin)

        # Страна через QComboBox (выбор из списка)
        country_label = QLabel("Страна:")
        country_label.setStyleSheet(label_style)
        self.country_combo = QComboBox()
        # Список стран (можно расширить по необходимости)
        countries = [
            "Россия", "Великобритания", "США", "Франция", "Германия", "Италия",
            "Китай", "Япония", "Испания", "Польша", "Чехия", "Украина", "Беларусь",
            "Казахстан", "Канада", "Австралия", "Швеция", "Нидерланды", "Другая"
        ]
        self.country_combo.addItems([country.value for country in Country])
        layout.addRow(country_label, self.country_combo)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию автора")
            return
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя автора")
            return
        if not self.country_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите страну автора")
            return
        self.accept()

class EditAuthorDialog(QDialog):
    """
    Диалог редактирования данных автора.
    """
    def __init__(self, controller, author, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.author = author

        self.setWindowTitle("Редактировать автора")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = QLineEdit(self.author['last_name'])
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = QLineEdit(self.author['first_name'])
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = QLineEdit(self.author['patronymic'])
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Год рождения
        birth_year_label = QLabel("Год рождения:")
        birth_year_label.setStyleSheet(label_style)
        self.birth_year_edit = QLineEdit(str(self.author['birth_year']))
        layout.addRow(birth_year_label, self.birth_year_edit)

        # Страна (QComboBox)
        country_label = QLabel("Страна:")
        country_label.setStyleSheet(label_style)
        self.country_combo = QComboBox()
        # Пример списка стран (можешь заменить на свой)
        countries = [country.value for country in Country]
        self.country_combo.addItems(country.value for country in Country)
        # Установить текущую страну автора, если она есть в списке
        if self.author['country'] in countries:
            self.country_combo.setCurrentText(self.author['country'])
        else:
            self.country_combo.addItem(self.author['country'])
            self.country_combo.setCurrentText(self.author['country'])
        layout.addRow(country_label, self.country_combo)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию автора")
            return
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя автора")
            return

        birth_year_text = self.birth_year_edit.text().strip()
        if not birth_year_text.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный год рождения")
            return

        birth_year = int(birth_year_text)
        from datetime import datetime
        current_year = datetime.now().year

        # Ограничения: не раньше 1890 и не позже текущего года
        if birth_year < 1200 or birth_year > current_year:
            QMessageBox.warning(
                self, "Ошибка",
                f"Год рождения должен быть от 1200 до {current_year}"
            )
            return

        if not self.country_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите страну автора")
            return
        self.accept()
