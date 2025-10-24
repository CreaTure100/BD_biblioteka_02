import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator

from core.additional_classes import NumericTableItem
from ui.styles import get_form_label_style
from core.enums import Genre

class BooksDialog(QDialog):
    """
    Диалог для просмотра книг.
    Отображает список всех книг с возможностью добавления, редактирования и удаления.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent_window = parent
        self.setWindowTitle("Книги")
        self.setMinimumSize(900, 500)
        self.setup_ui()

    def edit_book(self, row, column):
        book_id = int(self.books_table.item(row, 0).text())
        book = next((b for b in self.books if b['book_id'] == book_id), None)
        if not book:
            return
        dialog = EditBookDialog(self.controller, book, self)
        if dialog.exec():
            new_title = dialog.title_edit.text().strip()
            new_year = int(dialog.year_edit.text().strip())
            new_genre = dialog.genre_combo.currentText()
            new_isbn = dialog.isbn_edit.text().strip()
            new_copies = int(dialog.copies_spin.value())

            success, msg = self.controller.update_book(
                book_id,
                new_title,
                new_year,
                new_genre,
                new_isbn,
                new_copies
            )
            if success:
                self.update_books_table()
                QMessageBox.information(self, "Успех", "Книга успешно обновлена.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить книгу: {msg}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title_label = QLabel("<h2>Книги</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        self.books = self.controller.get_books()
        if not self.books:
            empty_label = QLabel("Книг нет.")
            empty_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_label)
        else:
            self.books_table = QTableWidget()
            self.books_table.setColumnCount(6)
            self.books_table.setHorizontalHeaderLabels(
                ["ID", "Название", "Год издания", "Жанр", "ISBN", "Экземпляров"])
            self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.books_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.update_books_table()
            self.books_table.setSortingEnabled(True)
            self.books_table.cellDoubleClicked.connect(self.edit_book)
            layout.addWidget(self.books_table)
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить книгу")
        add_btn.clicked.connect(self.add_book)
        buttons_layout.addWidget(add_btn)
        del_btn = QPushButton("Удалить книгу")
        del_btn.clicked.connect(self.delete_book)
        buttons_layout.addWidget(del_btn)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)

    def update_books_table(self):
        self.books = self.controller.get_books()
        self.books_table.setRowCount(len(self.books))
        for i, book in enumerate(self.books):
            id_item = NumericTableItem(str(book['book_id']), book['book_id'])
            title_item = QTableWidgetItem(book['title'])
            year_item = QTableWidgetItem(str(book['publication_year']) if book['publication_year'] is not None else "")
            genre_item = QTableWidgetItem(book['genre'] if book['genre'] else "")
            isbn_item = QTableWidgetItem(book['isbn'] if book['isbn'] else "")
            copies_item = QTableWidgetItem(str(book['available_copies']) if book['available_copies'] is not None else "0")
            self.books_table.setItem(i, 0, id_item)
            self.books_table.setItem(i, 1, title_item)
            self.books_table.setItem(i, 2, year_item)
            self.books_table.setItem(i, 3, genre_item)
            self.books_table.setItem(i, 4, isbn_item)
            self.books_table.setItem(i, 5, copies_item)

    def add_book(self):
        dialog = AddBookDialog(self.controller, self)
        if dialog.exec():
            title = dialog.title_edit.text().strip()
            year = int(dialog.year_spin.value())
            genre = dialog.genre_combo.currentText()
            isbn = dialog.isbn_edit.text().strip()
            copies = int(dialog.copies_spin.value())
            success = self.controller.add_book(
                title,
                year,
                genre,
                isbn,
                copies
            )
            if success:
                self.update_books_table()
                QMessageBox.information(self, "Успех", "Книга успешно добавлена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить книгу")

    def delete_book(self):
        selected_rows = self.books_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления.")
            return
        row = selected_rows[0].row()
        book_id = int(self.books_table.item(row, 0).text())
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту книгу?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success, msg = self.controller.delete_book_by_id(book_id)
            if success:
                self.update_books_table()
                QMessageBox.information(self, "Успех", "Книга успешно удалена")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить книгу: {msg}")

class EditBookDialog(QDialog):
    """
    Диалог редактирования данных книги.
    """
    def __init__(self, controller, book, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.book = book

        self.setWindowTitle("Редактировать книгу")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Название
        title_label = QLabel("Название:")
        title_label.setStyleSheet(label_style)
        self.title_edit = QLineEdit(self.book['title'])
        layout.addRow(title_label, self.title_edit)

        # Год издания
        year_label = QLabel("Год издания:")
        year_label.setStyleSheet(label_style)
        self.year_edit = QLineEdit(str(self.book['publication_year']))
        layout.addRow(year_label, self.year_edit)

        # Жанр (QComboBox)
        genre_label = QLabel("Жанр:")
        genre_label.setStyleSheet(label_style)
        self.genre_combo = QComboBox()
        genres = [genre.value for genre in Genre]
        self.genre_combo.addItems([genre.value for genre in Genre])
        if self.book['genre'] in genres:
            self.genre_combo.setCurrentText(self.book['genre'])
        else:
            self.genre_combo.addItem(self.book['genre'])
            self.genre_combo.setCurrentText(self.book['genre'])
        layout.addRow(genre_label, self.genre_combo)

        # ISBN
        isbn_label = QLabel("ISBN:")
        isbn_label.setStyleSheet(label_style)
        self.isbn_edit = QLineEdit(self.book['isbn'])
        layout.addRow(isbn_label, self.isbn_edit)

        # Количество экземпляров
        copies_label = QLabel("Экземпляров:")
        copies_label.setStyleSheet(label_style)
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(0, 9999)
        self.copies_spin.setValue(self.book['available_copies'] if self.book['available_copies'] is not None else 1)
        layout.addRow(copies_label, self.copies_spin)

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
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название книги")
            return

        year_text = self.year_edit.text().strip()
        if not year_text.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный год издания")
            return

        year = int(year_text)
        from datetime import datetime
        current_year = datetime.now().year

        if year < 1450 or year > current_year:
            QMessageBox.warning(
                self, "Ошибка",
                f"Год издания должен быть от 1450 до {current_year}"
            )
            return

        if not self.genre_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите жанр книги")
            return
        if not self.isbn_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ISBN книги")
            return
        if int(self.copies_spin.value()) < 0:
            QMessageBox.warning(self, "Ошибка", "Количество экземпляров должно быть положительным")
            return

        self.accept()

class AddBookDialog(QDialog):
    """
    Диалог добавления новой книги.
    Позволяет ввести название, год издания (QSpinBox), выбрать жанр из списка,
    ввести ISBN и количество экземпляров (QSpinBox).
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить книгу")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Название
        title_label = QLabel("Название:")
        title_label.setStyleSheet(label_style)
        self.title_edit = QLineEdit()
        layout.addRow(title_label, self.title_edit)

        # Год издания
        year_label = QLabel("Год издания:")
        year_label.setStyleSheet(label_style)
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1450, 2025)
        self.year_spin.setValue(2000)
        layout.addRow(year_label, self.year_spin)

        # Жанр через QComboBox (выбор из списка)
        genre_label = QLabel("Жанр:")
        genre_label.setStyleSheet(label_style)
        self.genre_combo = QComboBox()
        self.genre_combo.addItems([genre.value for genre in Genre])
        layout.addRow(genre_label, self.genre_combo)

        # ISBN
        isbn_label = QLabel("ISBN:")
        isbn_label.setStyleSheet(label_style)
        self.isbn_edit = QLineEdit()
        layout.addRow(isbn_label, self.isbn_edit)

        # Количество экземпляров через QSpinBox
        copies_label = QLabel("Экземпляров:")
        copies_label.setStyleSheet(label_style)
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 9999)
        self.copies_spin.setValue(1)
        layout.addRow(copies_label, self.copies_spin)

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
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название книги")
            return
        # year_spin всегда возвращает int, дополнительная проверка не нужна
        if not self.genre_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите жанр книги")
            return
        if not self.isbn_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ISBN книги")
            return
        if int(self.copies_spin.value()) < 1:
            QMessageBox.warning(self, "Ошибка", "Количество экземпляров должно быть положительным")
            return
        self.accept()
