from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator
from core.additional_classes import NumericTableItem
from ui.styles import get_form_label_style

class BookAuthorsDialog(QDialog):
    """
    Диалог управления связями автор–книга.
    Позволяет просматривать, добавлять, редактировать и удалять связи.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_links = controller.get_book_authors()  # список связей

        self.setWindowTitle("Связи автор–книга")
        self.setMinimumSize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("<h2>Автор–Книга</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Таблица связей
        self.links_table = QTableWidget()
        self.links_table.setColumnCount(3)
        self.links_table.setHorizontalHeaderLabels(
            ["ID связи", "ID книги", "ID автора"])
        self.links_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.links_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Заполнение таблицы данными
        self.update_links_table()

        # Включение сортировки и обработки двойного клика
        self.links_table.setSortingEnabled(True)
        self.links_table.cellDoubleClicked.connect(self.edit_link)

        layout.addWidget(self.links_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        add_link_btn = QPushButton("Добавить связь")
        add_link_btn.clicked.connect(self.add_link)
        buttons_layout.addWidget(add_link_btn)

        delete_link_btn = QPushButton("Удалить связь")
        delete_link_btn.clicked.connect(self.delete_link)
        buttons_layout.addWidget(delete_link_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def update_links_table(self):
        """Обновление содержимого таблицы связей"""
        self.all_links = self.controller.get_book_authors()
        self.links_table.setRowCount(len(self.all_links))
        self.links_table.setSortingEnabled(False)

        for i, link in enumerate(self.all_links):

            book_id_item = NumericTableItem(str(link['book_id']), link['book_id'])
            author_id_item = NumericTableItem(str(link['author_id']), link['author_id'])
            id_item = QTableWidgetItem(f"{link['book_id']}-{link['author_id']}")
            self.links_table.setItem(i, 0, id_item)
            self.links_table.setItem(i, 1, book_id_item)
            self.links_table.setItem(i, 2, author_id_item)

        self.links_table.setSortingEnabled(True)

    def add_link(self):
        """Открытие диалога добавления новой связи"""
        dialog = AddBookAuthorDialog(self.controller, self)
        if dialog.exec():
            book_id = int(dialog.book_id_combo.currentData())
            author_id = int(dialog.author_id_combo.currentData())
            link_id = self.controller.add_book_author(book_id, author_id)

            if link_id:
                self.update_links_table()
                QMessageBox.information(self, "Успех", "Связь успешно добавлена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить связь")

    def edit_link(self, row, column):
        """Открытие диалога редактирования связи"""
        # Получаем строку вида "2-2"
        book_id_str, author_id_str = self.links_table.item(row, 0).text().split('-')
        book_id = int(book_id_str)
        author_id = int(author_id_str)

        # Ищем нужную связь
        link = next(
            (a for a in self.all_links if a['book_id'] == book_id and a['author_id'] == author_id),
            None
        )

        if not link:
            return

        dialog = EditBookAuthorDialog(self.controller, link, self)
        if dialog.exec():
            new_book_id = int(dialog.book_id_combo.currentData())
            new_author_id = int(dialog.author_id_combo.currentData())

            success, message = self.controller.update_book_author(book_id, author_id, new_book_id, new_author_id)
            if success:
                self.update_links_table()
                QMessageBox.information(self, "Успех", "Связь успешно обновлена")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить связь: {message}")

    def delete_link(self):
        """Удаление выбранной связи"""
        selected_rows = self.links_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите связь для удаления")
            return

        row = selected_rows[0].row()
        key_text = self.links_table.item(row, 0).text()
        book_id_str, author_id_str = key_text.split('-')
        book_id = int(book_id_str)
        author_id = int(author_id_str)

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту связь?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success, message = self.controller.delete_book_author(book_id, author_id)
            if success:
                self.update_links_table()
                QMessageBox.information(self, "Успех", "Связь успешно удалена")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить связь: {message}")

class AddBookAuthorDialog(QDialog):
    """
    Диалог добавления новой связи книга–автор.
    Позволяет выбрать существующую книгу и автора.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить связь книга–автор")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Получаем список книг и авторов
        self.books = self.controller.get_books()    # список словарей книг
        self.authors = self.controller.get_authors() # список словарей авторов

        # Книга (выбор из существующих)
        book_id_label = QLabel("Книга:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        layout.addRow(book_id_label, self.book_id_combo)

        # Автор (выбор из существующих)
        author_id_label = QLabel("Автор:")
        author_id_label.setStyleSheet(label_style)
        self.author_id_combo = QComboBox()
        for author in self.authors:
            self.author_id_combo.addItem(f"{author['author_id']} — {author['last_name']} {author['first_name']}", author['author_id'])
        layout.addRow(author_id_label, self.author_id_combo)

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
        author_id = self.author_id_combo.currentData()

        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if author_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите автора")
            return

        self.accept()

class EditBookAuthorDialog(QDialog):
    """
    Диалог редактирования связи книга–автор.
    Позволяет изменить книгу и автора для существующей связи.
    """
    def __init__(self, controller, link, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.link = link  # link должен содержать 'book_id' и 'author_id'

        self.setWindowTitle("Редактировать связь книга–автор")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = get_form_label_style()

        # Получаем список книг и авторов
        self.books = self.controller.get_books()
        self.authors = self.controller.get_authors()

        # Книга (выбор из существующих)
        book_id_label = QLabel("Книга:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        # Установить текущий выбранный book_id
        index = self.book_id_combo.findData(self.link['book_id'])
        if index >= 0:
            self.book_id_combo.setCurrentIndex(index)
        layout.addRow(book_id_label, self.book_id_combo)

        # Автор (выбор из существующих)
        author_id_label = QLabel("Автор:")
        author_id_label.setStyleSheet(label_style)
        self.author_id_combo = QComboBox()
        for author in self.authors:
            self.author_id_combo.addItem(f"{author['author_id']} — {author['last_name']} {author['first_name']}", author['author_id'])
        index = self.author_id_combo.findData(self.link['author_id'])
        if index >= 0:
            self.author_id_combo.setCurrentIndex(index)
        layout.addRow(author_id_label, self.author_id_combo)

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
        author_id = self.author_id_combo.currentData()
        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if author_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите автора")
            return

        self.accept()

