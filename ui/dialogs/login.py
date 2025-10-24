from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator

from core.data import DatabaseManager
from core.additional_classes import TextValidator
from core.logger import Logger
from ui.styles import get_message_box_style, get_form_label_style, get_combobox_style, get_button_style


class ValidatedLoginLineEdit(QLineEdit):
    """
    Поле ввода с валидацией для окна логина.
    Разрешает только определенные символы.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = DatabaseManager()

    def keyPressEvent(self, event):
        """Обработка нажатия клавиш с валидацией."""
        # Сохраняем текущий текст и позицию курсора
        old_text = self.text()
        cursor_pos = self.cursorPosition()

        # Вызываем стандартную обработку нажатия клавиш
        super().keyPressEvent(event)

        # Проверяем валидность нового текста
        new_text = self.text()

        # Если текст пустой, разрешаем его
        if not new_text:
            return

        # Используем функцию валидации
        if TextValidator.is_valid_text_input(new_text):
            return

        # Если текст не валиден, восстанавливаем старый текст
        self.setText(old_text)
        self.setCursorPosition(cursor_pos)

class LoginDialog(QDialog):
    """
    Диалог авторизации и подключения к базе данных.
    Позволяет ввести параметры подключения, создать БД или подключиться к существующей.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = DatabaseManager()
        self.logger = Logger()

        # Единый стиль для всех диалоговых окон сообщений
        self.message_box_style = get_message_box_style()
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса диалога."""
        self.setWindowTitle("Подключение к базе данных")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f5f5;")

        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("Библиотека")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: green; ")
        layout.addWidget(title_label)

        # Форма для ввода параметров
        form_layout = QFormLayout()
        form_label_style = get_form_label_style()

        # Выбор базы данных
        self.db_combo = QComboBox()
        self.db_combo.addItem("test1")
        self.db_combo.addItem("test2")
        self.db_combo.setStyleSheet(get_combobox_style())
        db_label = QLabel("База данных:")
        db_label.setStyleSheet(form_label_style)
        form_layout.addRow(db_label, self.db_combo)

        # Поле для ввода хоста
        self.host_edit = ValidatedLoginLineEdit("localhost")
        self.host_edit.setStyleSheet("color: black;")
        host_label = QLabel("Хост:")
        host_label.setStyleSheet(form_label_style)
        form_layout.addRow(host_label, self.host_edit)

        # Поле для ввода порта
        self.port_edit = ValidatedLoginLineEdit("5432")
        self.port_edit.setStyleSheet("color: black;")
        self.port_edit.setValidator(QIntValidator(1, 65535))
        port_label = QLabel("Порт:")
        port_label.setStyleSheet(form_label_style)
        form_layout.addRow(port_label, self.port_edit)

        # Поле для ввода имени пользователя
        self.user_edit = ValidatedLoginLineEdit("postgres")
        self.user_edit.setStyleSheet("color: black;")
        user_label = QLabel("Пользователь:")
        user_label.setStyleSheet(form_label_style)
        form_layout.addRow(user_label, self.user_edit)

        # Поле для ввода пароля
        self.password_edit = QLineEdit("1234qwer")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("color: black;")
        password_label = QLabel("Пароль:")
        password_label.setStyleSheet(form_label_style)
        form_layout.addRow(password_label, self.password_edit)

        layout.addLayout(form_layout)

        # Кнопки действий
        buttons_layout = QHBoxLayout()



        # Кнопка подключения
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.try_connect)
        self.connect_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.connect_btn)

        # Кнопка создания БД
        self.create_db_btn = QPushButton("Создать БД")
        self.create_db_btn.clicked.connect(self.create_database)
        self.create_db_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.create_db_btn)

        # Кнопка выхода
        self.exit_btn = QPushButton("Выход")
        self.exit_btn.clicked.connect(self.reject)
        self.exit_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.exit_btn)

        layout.addLayout(buttons_layout)

    def try_connect(self):
        """Попытка подключения к базе данных с введенными параметрами."""
        # Получение параметров из полей ввода
        dbname = self.db_combo.currentText()
        host = self.host_edit.text()
        port = self.port_edit.text()
        user = self.user_edit.text()
        password = self.password_edit.text()

        # Проверка заполнения всех обязательных полей
        if not dbname or not host or not port or not user:
            warn_box = QMessageBox(self)
            warn_box.setWindowTitle("Ошибка")
            warn_box.setText("Все поля, кроме пароля, должны быть заполнены")
            warn_box.setIcon(QMessageBox.Warning)
            warn_box.setStyleSheet(self.message_box_style)
            warn_box.exec()
            return

        # Установка параметров подключения
        self.controller.set_connection_params(dbname, user, password, host, port)

        # Попытка подключения
        if self.controller.connect():
            try:
                # Проверка существования структуры базы данных
                self.controller.cursor.execute(
                    "SELECT 1 FROM information_schema.tables WHERE table_name = 'books'")
                table_exists = self.controller.cursor.fetchone() is not None

                # Если структура не существует, предлагаем создать
                if not table_exists:
                    reply_box = QMessageBox(self)
                    reply_box.setWindowTitle("Схема не найдена")
                    reply_box.setText("Структура базы данных не найдена. Схемы и таблицы будут созданы")
                    reply_box.setIcon(QMessageBox.Information)
                    reply_box.setStyleSheet(self.message_box_style)
                    reply = reply_box.exec()

                    # Создание схемы и таблиц
                    if self.controller.initialize_database():
                        ok_box = QMessageBox(self)
                        ok_box.setWindowTitle("Успех")
                        ok_box.setText("Схема и таблицы успешно созданы")
                        ok_box.setIcon(QMessageBox.Information)
                        ok_box.setStyleSheet(self.message_box_style)
                        ok_box.exec()
                    else:
                        err_box = QMessageBox(self)
                        err_box.setWindowTitle("Ошибка")
                        err_box.setText("Не удалось создать схему базы данных")
                        err_box.setIcon(QMessageBox.Critical)
                        err_box.setStyleSheet(self.message_box_style)
                        err_box.exec()
                        return

                # Подключение успешно
                success_box = QMessageBox(self)
                success_box.setWindowTitle("Успех")
                success_box.setText("Подключение успешно установлено")
                success_box.setIcon(QMessageBox.Information)
                success_box.setStyleSheet(self.message_box_style)
                success_box.exec()
                self.accept()

            except Exception as e:
                # Ошибка при проверке структуры БД
                err_box = QMessageBox(self)
                err_box.setWindowTitle("Ошибка")
                err_box.setText(f"Ошибка при проверке структуры базы данных: {str(e)}")
                err_box.setIcon(QMessageBox.Critical)
                err_box.setStyleSheet(self.message_box_style)
                err_box.exec()
        else:
            # Ошибка подключения к БД
            err_box = QMessageBox(self)
            err_box.setWindowTitle("Ошибка")
            err_box.setText("Не удалось подключиться к базе данных. Проверьте параметры подключения.")
            err_box.setIcon(QMessageBox.Critical)
            err_box.setStyleSheet(self.message_box_style)
            err_box.exec()

    def create_database(self):
        """Создание новой базы данных с введенными параметрами."""
        # Получение параметров из полей ввода
        dbname = self.db_combo.currentText()
        host = self.host_edit.text()
        port = self.port_edit.text()
        user = self.user_edit.text()
        password = self.password_edit.text()

        # Проверка заполнения всех обязательных полей
        if not dbname or not host or not port or not user:
            warn_box = QMessageBox(self)
            warn_box.setWindowTitle("Ошибка")
            warn_box.setText("Все поля, кроме пароля, должны быть заполнены")
            warn_box.setIcon(QMessageBox.Warning)
            warn_box.setStyleSheet(self.message_box_style)
            warn_box.exec()
            return

        # Установка параметров подключения
        self.controller.set_connection_params(dbname, user, password, host, port)
        try:
            # Попытка создания базы данных
            if self.controller.create_database():
                # Запрос на создание схемы и таблиц
                reply_box = QMessageBox(self)
                reply_box.setWindowTitle("База данных создана")
                reply_box.setText("База данных успешно создана. Хотите создать схемы и таблицы?")
                reply_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                reply_box.setIcon(QMessageBox.Question)
                reply_box.setStyleSheet(self.message_box_style)
                reply = reply_box.exec()

                if reply == QMessageBox.Yes:
                    # Подключение и инициализация базы данных
                    if self.controller.connect() and self.controller.initialize_database():
                        success_box = QMessageBox(self)
                        success_box.setWindowTitle("Успех")
                        success_box.setText("База данных, схема и таблицы успешно созданы")
                        success_box.setIcon(QMessageBox.Information)
                        success_box.setStyleSheet(self.message_box_style)
                        success_box.exec()
                        self.accept()
                    else:
                        err_box = QMessageBox(self)
                        err_box.setWindowTitle("Ошибка")
                        err_box.setText("Не удалось создать схему базы данных")
                        err_box.setIcon(QMessageBox.Critical)
                        err_box.setStyleSheet(self.message_box_style)
                        err_box.exec()
                else:
                    # Пользователь отказался создавать схемы и таблицы
                    return
            else:
                # Ошибка создания базы данных
                err_box = QMessageBox(self)
                err_box.setWindowTitle("Ошибка")
                err_box.setText("Не удалось создать базу данных")
                err_box.setIcon(QMessageBox.Critical)
                err_box.setStyleSheet(self.message_box_style)
                err_box.exec()

        except Exception as e:
            err_box = QMessageBox(self)
            err_box.setWindowTitle("Ошибка")
            err_box.setText(f"Ошибка при создании базы данных:\n{str(e)}")
            err_box.setIcon(QMessageBox.Critical)
            err_box.setStyleSheet(self.message_box_style)
            err_box.exec()

