from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator
from core.additional_classes import NumericTableItem
from ui.styles import get_form_label_style

class IssuesDialog(QDialog):
    """
    Диалог управления заказами (выдачами книг).
    Позволяет просматривать, добавлять, редактировать и удалять заказы.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_issues = controller.get_issues()

        self.setWindowTitle("Заказы (выдачи книг)")
        self.setMinimumSize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("<h2>Заказы</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Таблица заказов
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(5)
        self.issues_table.setHorizontalHeaderLabels(
            ["ID заказа", "ID книги", "ID читателя", "Дата выдачи", "Дата возврата"])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issues_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Заполнение таблицы данными
        self.update_issues_table()

        # Включение сортировки и обработки двойного клика
        self.issues_table.setSortingEnabled(True)
        self.issues_table.cellDoubleClicked.connect(self.edit_issue)

        layout.addWidget(self.issues_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        add_issue_btn = QPushButton("Добавить заказ")
        add_issue_btn.clicked.connect(self.add_issue)
        buttons_layout.addWidget(add_issue_btn)

        delete_issue_btn = QPushButton("Удалить заказ")
        delete_issue_btn.clicked.connect(self.delete_issue)
        buttons_layout.addWidget(delete_issue_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def update_issues_table(self):
        """Обновление содержимого таблицы заказов"""
        self.all_issues = self.controller.get_issues()
        self.issues_table.setRowCount(len(self.all_issues))
        self.issues_table.setSortingEnabled(False)

        for i, issue in enumerate(self.all_issues):
            id_issue_item = NumericTableItem(str(issue['issue_id']), issue['issue_id'])
            book_id_item = NumericTableItem(str(issue['book_id']), issue['book_id'])
            reader_id_item = NumericTableItem(str(issue['reader_id']), issue['reader_id'])
            issue_date_item = QTableWidgetItem(issue['issue_date'].strftime('%Y-%m-%d') if issue['issue_date'] else "")
            return_date_item = QTableWidgetItem(issue['return_date'].strftime('%Y-%m-%d') if issue['return_date'] else "")

            self.issues_table.setItem(i, 0, id_issue_item)
            self.issues_table.setItem(i, 1, book_id_item)
            self.issues_table.setItem(i, 2, reader_id_item)
            self.issues_table.setItem(i, 3, issue_date_item)
            self.issues_table.setItem(i, 4, return_date_item)

        self.issues_table.setSortingEnabled(True)

    def add_issue(self):
        """Открытие диалога добавления нового заказа"""
        dialog = AddIssueDialog(self.controller, self)
        if dialog.exec():
            book_id = int(dialog.book_id_combo.currentData())
            reader_id = int(dialog.reader_id_combo.currentData())
            issue_date = dialog.issue_date_edit.text().strip()
            return_date = dialog.return_date_edit.text().strip() or None
            issue_id = self.controller.add_issue(
                book_id, reader_id, issue_date, return_date
            )

            if issue_id:
                self.update_issues_table()
                QMessageBox.information(self, "Успех", "Заказ успешно добавлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить заказ")

    def edit_issue(self, row, column):
        """Открытие диалога редактирования заказа"""
        issue_id = int(self.issues_table.item(row, 0).text())
        issue = next((a for a in self.all_issues if a['issue_id'] == issue_id), None)

        if not issue:
            return

        dialog = EditIssueDialog(self.controller, issue, self)
        if dialog.exec():
            book_id = int(dialog.book_id_combo.currentData())
            reader_id = int(dialog.reader_id_combo.currentData())
            issue_date = dialog.issue_date_edit.text().strip()
            return_date = dialog.return_date_edit.text().strip() or None

            success, message = self.controller.update_issue(
                issue_id, book_id, reader_id, issue_date, return_date
            )
            if success:
                self.update_issues_table()
                QMessageBox.information(self, "Успех", "Заказ успешно обновлен")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить заказ: {message}")

    def delete_issue(self):
        """Удаление выбранного заказа"""
        selected_rows = self.issues_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для удаления")
            return

        row = selected_rows[0].row()
        issue_id = int(self.issues_table.item(row, 0).text())

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этот заказ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success, message = self.controller.delete_issue(issue_id)
            if success:
                self.update_issues_table()
                QMessageBox.information(self, "Успех", "Заказ успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить заказ: {message}")

class AddIssueDialog(QDialog):
    """
    Диалог добавления нового заказа (выдачи книги).
    Позволяет выбрать существующий ID книги и читателя, дату выдачи и дату возврата.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить заказ")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Получаем список книг и читателей
        self.books = self.controller.get_books()    # список словарей книг
        self.readers = self.controller.get_readers() # список словарей читателей

        # ID книги (выбор из существующих)
        book_id_label = QLabel("ID книги:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            # Можно выводить: "ID - Название"
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        layout.addRow(book_id_label, self.book_id_combo)

        # ID читателя (выбор из существующих)
        reader_id_label = QLabel("ID читателя:")
        reader_id_label.setStyleSheet(label_style)
        self.reader_id_combo = QComboBox()
        for reader in self.readers:
            # Можно выводить: "ID - Фамилия Имя"
            self.reader_id_combo.addItem(f"{reader['reader_id']} — {reader['last_name']} {reader['first_name']}", reader['reader_id'])
        layout.addRow(reader_id_label, self.reader_id_combo)

        # Дата выдачи (по умолчанию сегодня, можно изменить)
        issue_date_label = QLabel("Дата выдачи (ГГГГ-ММ-ДД):")
        issue_date_label.setStyleSheet(label_style)
        self.issue_date_edit = QLineEdit()
        from datetime import date
        self.issue_date_edit.setText(str(date.today()))
        layout.addRow(issue_date_label, self.issue_date_edit)

        # Дата возврата (может быть пустой, если книга не возвращена)
        return_date_label = QLabel("Дата возврата (ГГГГ-ММ-ДД, можно оставить пустым):")
        return_date_label.setStyleSheet(label_style)
        self.return_date_edit = QLineEdit()
        layout.addRow(return_date_label, self.return_date_edit)

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
        # Получаем выбранные ID
        book_id = self.book_id_combo.currentData()
        reader_id = self.reader_id_combo.currentData()

        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if reader_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя")
            return

        # Проверка корректности даты выдачи
        issue_date_str = self.issue_date_edit.text().strip()
        from datetime import datetime
        try:
            parsed_issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите дату выдачи в формате ГГГГ-ММ-ДД (например, 2024-09-29)")
            return

        # Проверка корректности даты возврата (если не пусто)
        return_date_str = self.return_date_edit.text().strip()
        if return_date_str:
            try:
                parsed_return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите дату возврата в формате ГГГГ-ММ-ДД (или оставьте пустым)")
                return

        self.accept()

class EditIssueDialog(QDialog):
    """
    Диалог редактирования данных заказа (выдачи книги).
    Позволяет изменить книгу, читателя, дату выдачи и дату возврата.
    """
    def __init__(self, controller, issue, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.issue = issue

        self.setWindowTitle("Редактировать данные заказа")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Получаем список книг и читателей
        self.books = self.controller.get_books()
        self.readers = self.controller.get_readers()

        # Книга (выбор из существующих)
        book_id_label = QLabel("Книга:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        # Установить текущий выбранный book_id
        index = self.book_id_combo.findData(self.issue['book_id'])
        if index >= 0:
            self.book_id_combo.setCurrentIndex(index)
        layout.addRow(book_id_label, self.book_id_combo)

        # Читатель (выбор из существующих)
        reader_id_label = QLabel("Читатель:")
        reader_id_label.setStyleSheet(label_style)
        self.reader_id_combo = QComboBox()
        for reader in self.readers:
            self.reader_id_combo.addItem(f"{reader['reader_id']} — {reader['last_name']} {reader['first_name']}", reader['reader_id'])
        index = self.reader_id_combo.findData(self.issue['reader_id'])
        if index >= 0:
            self.reader_id_combo.setCurrentIndex(index)
        layout.addRow(reader_id_label, self.reader_id_combo)

        # Дата выдачи
        issue_date_label = QLabel("Дата выдачи:")
        issue_date_label.setStyleSheet(label_style)
        self.issue_date_edit = QDateEdit()
        self.issue_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.issue_date_edit.setCalendarPopup(True)
        issue_date = self.issue['issue_date']
        if hasattr(issue_date, 'strftime'):
            issue_date_str = issue_date.strftime("%Y-%m-%d")
        else:
            issue_date_str = str(issue_date)
        self.issue_date_edit.setDate(QDate.fromString(issue_date_str, "yyyy-MM-dd"))
        layout.addRow(issue_date_label, self.issue_date_edit)

        # Дата возврата (может быть пустой)
        return_date_label = QLabel("Дата возврата:")
        return_date_label.setStyleSheet(label_style)
        self.return_date_edit = QDateEdit()
        self.return_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.return_date_edit.setCalendarPopup(True)
        return_date = self.issue['return_date']
        if return_date:
            if hasattr(return_date, 'strftime'):
                return_date_str = return_date.strftime("%Y-%m-%d")
            else:
                return_date_str = str(return_date)
            self.return_date_edit.setDate(QDate.fromString(return_date_str, "yyyy-MM-dd"))
        layout.addRow(return_date_label, self.return_date_edit)

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
        # Проверка выбранных значений
        book_id = self.book_id_combo.currentData()
        reader_id = self.reader_id_combo.currentData()
        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if reader_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя")
            return

        # Проверка корректности дат
        issue_date = self.issue_date_edit.date().toString("yyyy-MM-dd")
        return_date = self.return_date_edit.date().toString("yyyy-MM-dd")

        # Можно добавить дополнительные проверки на пустую дату возврата, если нужно

        self.accept()
