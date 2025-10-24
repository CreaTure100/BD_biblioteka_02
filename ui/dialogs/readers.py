from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator
from ui.styles import get_form_label_style
from core.additional_classes import NumericTableItem, ValidatedLineEdit

class ReadersDialog(QDialog):
    """
    Диалог управления читателями.
    Позволяет просматривать, добавлять, редактировать и удалять читателей
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_readers = controller.get_readers()

        self.setWindowTitle("Читатели")
        self.setMinimumSize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса диалога."""
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("<h2>Читатели</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)



        # Таблица читателей
        self.readers_table = QTableWidget()
        self.readers_table.setColumnCount(6)
        self.readers_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Отчество", "Номер чит билета", "Дата регистрации"])
        self.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.readers_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Заполнение таблицы данными
        self.update_readers_table()

        # Включение сортировки и обработки двойного клика
        self.readers_table.setSortingEnabled(True)
        self.readers_table.cellDoubleClicked.connect(self.edit_reader)

        layout.addWidget(self.readers_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        add_reader_btn = QPushButton("Добавить читателя")
        add_reader_btn.clicked.connect(self.add_reader)
        buttons_layout.addWidget(add_reader_btn)

        delete_reader_btn = QPushButton("Удалить читателя")
        delete_reader_btn.clicked.connect(self.delete_reader)
        buttons_layout.addWidget(delete_reader_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def update_readers_table(self):
        """Обновление содержимого таблицы читателей"""
        # Получение актуального списка читателей
        self.all_readers = self.controller.get_readers()
        self.readers_table.setRowCount(len(self.all_readers))

        # Временно отключаем сортировку для заполнения таблицы
        self.readers_table.setSortingEnabled(False)



        # Заполнение таблицы данными
        for i, reader in enumerate(self.all_readers):
            id_reader_item = NumericTableItem(str(reader['reader_id']), reader['reader_id'])
            last_name_item = QTableWidgetItem(reader['last_name'])
            first_name_item = QTableWidgetItem(reader['first_name'])
            patronymic_item = QTableWidgetItem(reader['patronymic'])
            ticket_number_item = NumericTableItem(str(reader['ticket_number']), reader['ticket_number'])
            registration_date_item = NumericTableItem(reader['registration_date'].strftime('%Y-%m-%d'), reader['registration_date'])


            self.readers_table.setItem(i, 0, id_reader_item)
            self.readers_table.setItem(i, 1, last_name_item)
            self.readers_table.setItem(i, 2, first_name_item)
            self.readers_table.setItem(i, 3, patronymic_item)
            self.readers_table.setItem(i, 4, ticket_number_item)
            self.readers_table.setItem(i, 5, registration_date_item)

        # Включаем сортировку обратно
        self.readers_table.setSortingEnabled(True)

    def add_reader(self):
        """Открытие диалога добавления нового читателя"""
        dialog = AddReaderDialog(self.controller, self)
        if dialog.exec():
            # Получаем данные из диалога
            last_name = dialog.last_name_edit.text().strip()
            first_name = dialog.first_name_edit.text().strip()
            patronymic = dialog.patronymic_edit.text().strip()
            ticket_number = dialog.ticket_number_edit.text().strip()
            registration_date = dialog.registration_date_edit.text().strip()

            # Добавление читателя в БД
            reader_id = self.controller.add_reader(
                last_name, first_name, patronymic, ticket_number, registration_date
            )

            if reader_id:
                self.update_readers_table()
                QMessageBox.information(self, "Успех", "Читатель успешно добавлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить читателя")

    def edit_reader(self, row, column):
        """Открытие диалога редактирования читателя"""
        # Получение ID читателя из таблицы
        reader_id = int(self.readers_table.item(row, 0).text())
        reader = next((a for a in self.all_readers if a['reader_id'] == reader_id), None)

        if not reader:
            return

        # Открытие диалога редактирования
        dialog = EditReaderDialog(self.controller, reader, self)
        if dialog.exec():
            # Если диалог был принят, получаем данные и обновляем читателя
            last_name = dialog.last_name_edit.text().strip()
            first_name = dialog.first_name_edit.text().strip()
            patronymic = dialog.patronymic_edit.text().strip()
            ticket_number = dialog.ticket_number_edit.text().strip()
            registration_date = dialog.registration_date_edit.text().strip()

            # Обновление читателя в БД
            success, message = self.controller.update_reader(
                reader_id, last_name, first_name, patronymic, ticket_number, registration_date
            )
            if success:
                # Обновление таблицы при успешном обновлении
                self.update_readers_table()
                QMessageBox.information(self, "Успех", "Читатель успешно обновлен")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить итателя: {message}")

    def delete_reader(self):
        """Удаление выбранного читателя"""
        # Проверка наличия выбранных строк
        selected_rows = self.readers_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя для удаления")
            return

        # Получение ID читателя
        row = selected_rows[0].row()
        reader_id = int(self.readers_table.item(row, 0).text())

        # Запрос подтверждения
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этого читателя?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Удаление читателя из БД
            success, message = self.controller.delete_reader(reader_id)

            if success:
                # Обновление таблицы при успешном удалении
                self.update_readers_table()
                QMessageBox.information(self, "Успех", "Читатель успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить читателя: {message}")

class AddReaderDialog(QDialog):
    """
    Диалог добавления нового читателя.
    Позволяет ввести ФИО, номер читательского билета и дату регистрации.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить читателя")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = ValidatedLineEdit(self.controller)
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = ValidatedLineEdit(self.controller)
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = ValidatedLineEdit(self.controller)
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Номер читательского билета
        ticket_number_label = QLabel("Номер чит билета:")
        ticket_number_label.setStyleSheet(label_style)
        self.ticket_number_edit = ValidatedLineEdit(self.controller)
        layout.addRow(ticket_number_label, self.ticket_number_edit)

        # Дата регистрации (по умолчанию сегодня, можно изменить)
        registration_date_label = QLabel("Дата регистрации (ГГГГ-ММ-ДД):")
        registration_date_label.setStyleSheet(label_style)
        self.registration_date_edit = QLineEdit()
        from datetime import date
        self.registration_date_edit.setText(str(date.today()))
        layout.addRow(registration_date_label, self.registration_date_edit)

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
            QMessageBox.warning(self, "Ошибка", "Введите фамилию")
            return
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя")
            return
        if not self.ticket_number_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер читательского билета")
            return

        # Проверка корректности даты
        date_str = self.registration_date_edit.text().strip()
        from datetime import datetime
        try:
            # Попытка распарсить дату
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите дату в формате ГГГГ-ММ-ДД (например, 2024-09-29)")
            return

        self.accept()

class EditReaderDialog(QDialog):
    """
    Диалог редактирования данных читателя.
    Позволяет изменить ФИО, звание, количество наград и опыт.
    """
    def __init__(self, controller, reader, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.reader = reader

        self.setWindowTitle("Редактировать данные читателя")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса диалога."""
        layout = QFormLayout(self)

        # Стиль для меток
        label_style = get_form_label_style()

        # Поля для ввода данных читателя
        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = ValidatedLineEdit(self.controller, self.reader['last_name'])
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = ValidatedLineEdit(self.controller, self.reader['first_name'])
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = ValidatedLineEdit(self.controller, self.reader['patronymic'])
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Номер читательского билета
        ticket_number_label = QLabel("Номер чит билета:")
        ticket_number_label.setStyleSheet(label_style)
        self.ticket_number_edit = ValidatedLineEdit(self.controller, self.reader['ticket_number'])
        layout.addRow(ticket_number_label, self.ticket_number_edit)

        # дата регистрации
        registration_date_label = QLabel("Дата регистрации:")
        registration_date_label.setStyleSheet(label_style)

        self.registration_date_edit = QDateEdit()
        self.registration_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.registration_date_edit.setCalendarPopup(True)

        # Устанавливаем значение из reader (строка или date)
        reg_date = self.reader['registration_date']
        if hasattr(reg_date, 'strftime'):
            reg_date_str = reg_date.strftime("%Y-%m-%d")
        else:
            reg_date_str = str(reg_date)
        self.registration_date_edit.setDate(QDate.fromString(reg_date_str, "yyyy-MM-dd"))

        layout.addRow(registration_date_label, self.registration_date_edit)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)

        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        """Валидация введенных данных и закрытие диалога с принятием."""
        # Проверка заполнения обязательных полей
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию")
            return

        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя")
            return

        # Если все проверки пройдены, принимаем диалог
        self.accept()
