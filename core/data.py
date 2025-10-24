import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from core.logger import Logger


class DatabaseManager:
    """
    Менеджер базы данных
    Отвечает за взаимодействие с PostgreSQL, выполнение запросов
    и преобразование данных.
    """

    def __init__(self):
        """Инициализация менеджера БД"""
        self.logger = Logger()
        self.connection_params = None
        self.connection = None
        self.cursor = None

    def set_connection_params(self, dbname, user, password, host, port):
        """Установка параметров подключения к базе данных."""
        self.connection_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.logger.info(f"Установлены параметры подключения: {dbname}@{host}:{port}")

    def connect(self):
        """
        Подключение к базе данных с использованием установленных параметров.

        Returns:
            bool: Успешность подключения
        """
        if self.connection_params is None:
            self.logger.error("Параметры подключения не установлены")
            return False

        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            self.logger.info(f"Подключение к БД {self.connection_params['dbname']} успешно")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка подключения к БД: {str(e)}")
            return False

    def connect_to_postgres(self):
        if self.connection_params is None:
            self.logger.error("Параметры подключения не установлены")
            return False

        try:
            # Копируем параметры и меняем имя БД на 'postgres'
            postgres_params = self.connection_params.copy()
            postgres_params["dbname"] = "postgres"

            conn = psycopg2.connect(**postgres_params)
            conn.autocommit = True
            cursor = conn.cursor()
            self.logger.info(f"Подключение к системной БД postgres успешно")
            return conn, cursor
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка подключения к системной БД postgres: {str(e)}")
            return None, None

    def create_database(self):
        """
        Создание новой базы данных если она не существует
        Returns:
            bool: Успешность создания БД
        """
        try:
            conn, cursor = self.connect_to_postgres()
            if not conn:
                return False

            dbname = self.connection_params["dbname"]

            # Проверяем существование БД
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            exists = cursor.fetchone()

            if not exists:
                # Создаем БД если она не существует
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
                self.logger.info(f"База данных {dbname} успешно создана")
            else:
                self.logger.info(f"База данных {dbname} уже существует")

            cursor.close()
            conn.close()
            return True
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка создания БД: {str(e)}")
            return False

    def disconnect(self):
        """Закрытие соединения с базой данных."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.logger.info("Соединение с БД закрыто")

    def create_schema(self):
        """
        Создание схемы базы данных с таблицами и типами данных.
        """
        try:

            # Создание таблицы читателей
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS readers (
                    reader_id SERIAL PRIMARY KEY,
                    last_name VARCHAR(100) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    patronymic VARCHAR(100),
                    ticket_number VARCHAR(20) UNIQUE NOT NULL,
                    registration_date DATE DEFAULT CURRENT_DATE
                );
            """)

            # Создание таблицы авторов
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS authors (
                    author_id SERIAL PRIMARY KEY,
                    last_name VARCHAR(100) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    patronymic VARCHAR(100),
                    birth_year INTEGER,
                    country VARCHAR(100),
                    UNIQUE (last_name, first_name, patronymic)
                );
            """)

            # Создание таблицы книг
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    publication_year INTEGER,
                    genre VARCHAR(100),
                    isbn VARCHAR(30) UNIQUE,
                    available_copies INTEGER NOT NULL DEFAULT 1
                );
            """)

            # Создание таблицы связей между книгами и авторами
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS book_authors (
                    book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
                    author_id INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE CASCADE,
                    PRIMARY KEY (book_id, author_id)
                );
            """)

            # Создание таблицы выдачи книг
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    issue_id SERIAL PRIMARY KEY,
                    reader_id INTEGER NOT NULL REFERENCES readers(reader_id) ON DELETE CASCADE,
                    book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
                    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    return_date DATE
                );
            """)

            self.connection.commit()
            self.logger.info("Схема БД успешно создана")
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка создания схемы БД: {str(e)}")
            return False

    def initialize_database(self):
        """
        Инициализация схемы БД и заполнение тестовыми данными.

        Returns:
            bool: Успешность инициализации
        """
        result1 = self.create_schema()
        result2 = self.init_sample_data()
        return result1 and result2

    def init_sample_data(self):
        """
        Инициализация БД тестовыми данными.

        Returns:
            bool: Успешность инициализации
        """

        try:

            # Добавление тестовых авторов
            authors = [
                ('Пушкин', 'Александр', 'Сергеевич', 1799, 'Россия'),
                ('Толстой', 'Лев', 'Николаевич', 1828, 'Россия'),
                ('Достоевский', 'Фёдор', 'Михайлович', 1821, 'Россия'),
                ('Оруэлл', 'Джордж', '', 1903, 'Великобритания'),
                ('Роулинг', 'Джоан', '', 1965, 'Великобритания')
            ]

            for author in authors:
                self.cursor.execute("""
                    INSERT INTO authors (last_name, first_name, patronymic, birth_year, country)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (last_name, first_name, patronymic) DO NOTHING
                """, author)

            # Добавление тестовых книг
            books = [
                ('Евгений Онегин', 1833, 'Роман в стихах', '978-5-17-088433-8', 3),
                ('Война и мир', 1869, 'Роман', '978-5-389-07453-2', 2),
                ('Преступление и наказание', 1866, 'Роман', '978-5-699-12014-9', 4),
                ('1984', 1949, 'Антиутопия', '978-0-452-28423-4', 5),
                ('Гарри Поттер и философский камень', 1997, 'Фэнтези', '978-5-353-02452-7', 7)
            ]
            for book in books:
                self.cursor.execute("""
                    INSERT INTO books (title, publication_year, genre, isbn, available_copies)
                    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (isbn) DO NOTHING
                """, book)

            # Добавление тестовых читателей
            readers = [
                ('Иванов', 'Иван', 'Иванович', '1001', '2022-09-01'),
                ('Петрова', 'Мария', 'Сергеевна', '1002', '2023-01-15'),
                ('Сидоров', 'Павел', 'Алексеевич', '1003', '2024-02-10')
            ]
            for reader in readers:
                self.cursor.execute("""
                    INSERT INTO readers (last_name, first_name, patronymic, ticket_number, registration_date)
                    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (ticket_number) DO NOTHING
                """, reader)

            # Добавление связей книг с авторами
            book_authors = [
                (1, 1),
                (2, 2),
                (3, 3),
                (4, 4),
                (5, 5)
            ]
            for ba in book_authors:
                self.cursor.execute("""
                    INSERT INTO book_authors (book_id, author_id)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING
                """, ba)

            #выдача книг
            issues = [
                (1, 1, '2024-06-01', '2024-06-15'),
                (2, 2, '2024-06-03', None),
                (3, 3, '2024-06-04', '2024-06-20'),
                (4, 1, '2024-06-10', None),
            ]
            for i in issues:
                self.cursor.execute("""
                    INSERT INTO issues (book_id, reader_id, issue_date, return_date)
                    VALUES (%s, %s, %s, %s)
                """, i)

            self.connection.commit()
            self.logger.info("Тестовые данные успешно добавлены")
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка добавления тестовых данных: {str(e)}")
            return False

    def reset_database(self):
        """
        Сброс всей базы данных к начальному состоянию.

        Returns:
            bool: Успешность сброса
        """
        try:
            # Очистка всех таблиц
            self.cursor.execute("TRUNCATE TABLE issues CASCADE")
            self.cursor.execute("TRUNCATE TABLE book_authors CASCADE")
            self.cursor.execute("TRUNCATE TABLE books CASCADE")
            self.cursor.execute("TRUNCATE TABLE authors CASCADE")
            self.cursor.execute("TRUNCATE TABLE readers CASCADE")

            # Сброс последовательностей идентификаторов
            self.cursor.execute("ALTER SEQUENCE books_book_id_seq RESTART WITH 1")
            self.cursor.execute("ALTER SEQUENCE authors_author_id_seq RESTART WITH 1")
            self.cursor.execute("ALTER SEQUENCE readers_reader_id_seq RESTART WITH 1")
            self.cursor.execute("ALTER SEQUENCE issues_issue_id_seq RESTART WITH 1")

            # Инициализация тестовыми данными

            self.init_sample_data()

            self.connection.commit()
            self.logger.info("База данных успешно сброшена")
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка сброса БД: {str(e)}")
            return False

    def reset_schema(self):
        """
        Сброс схемы базы данных (удаление всех таблиц и типов).

        Returns:
            bool: Успешность сброса
        """
        try:
            # Удаление всех таблиц и типов
            self.cursor.execute("""
                DROP TABLE IF EXISTS book_authors CASCADE;
                DROP TABLE IF EXISTS authors CASCADE;
                DROP TABLE IF EXISTS books CASCADE;
                DROP TABLE IF EXISTS readers CASCADE;
                DROP TABLE IF EXISTS issues CASCADE;
            """)
            self.connection.commit()
            self.logger.info("Схема БД успешно удалена")

            # Создание новой схемы
            success = self.create_schema()

            return success
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка сброса схемы БД: {str(e)}")
            return False

    def get_readers(self):
        """
        Получение списка всех читателей
        """
        try:
            self.cursor.execute("SELECT * FROM readers ORDER BY reader_id")
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка получения списка читателей: {str(e)}")
            return []

    def get_books(self):
        """
        Получение списка всех книг
        """
        try:
            self.cursor.execute("SELECT * FROM books ORDER BY book_id")
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка получения списка книг: {str(e)}")
            return []

    def get_issues(self):
        """
        Получение списка всех заказов
        """
        try:
            self.cursor.execute("SELECT * FROM issues ORDER BY issue_id")
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка получения списка закаазов: {str(e)}")
            return []

    def get_book_authors(self):
        """
        Получение списка всех связей книга–автор.
        """
        try:
            self.cursor.execute("SELECT * FROM book_authors ORDER BY book_id, author_id")
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка получения списка связей книга–автор: {str(e)}")
            return []

    def get_authors(self, year=None):

        try:
            self.cursor.execute("SELECT * FROM authors ORDER BY author_id")
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка получения авторов: {str(e)}")
            return []

    def add_book_author(self, book_id, author_id):
        """
        Добавление новой связи книга–автор.
        """
        try:
            self.cursor.execute("""
                                INSERT INTO book_authors (book_id, author_id)
                                VALUES (%s, %s) ON CONFLICT DO NOTHING
                                """, (book_id, author_id))
            self.connection.commit()
            self.logger.info(f"Добавлена связь: книга {book_id} — автор {author_id}")
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка добавления связи книга–автор: {str(e)}")
            return False

    def add_author(self, last_name, first_name, patronymic, birth_year, country):
        """
        Добавление нового автора в базу данных.
        """
        try:
            self.cursor.execute("""
                INSERT INTO authors (last_name, first_name, patronymic, birth_year, country)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING author_id
            """, (last_name, first_name, patronymic, birth_year, country))
            author_id = self.cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Добавлен автор с ID {author_id}")
            return author_id
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка добавления автора: {str(e)}")
            return None

    def add_reader(self, last_name, first_name, patronymic, ticket_number, registration_date):
        """
        Добавление нового читателя в базу данных.

        Args:
            last_name: Фамилия
            first_name: Имя
            patronymic: Отчество
            ticket_number: Номер читательского билета
            registration_date: Дата регистрации (строкой в формате YYYY-MM-DD)

        Returns:
            int or None: ID добавленного читателя или None при ошибке
        """
        try:
            self.cursor.execute("""
                                INSERT INTO readers (last_name, first_name, patronymic, ticket_number, registration_date)
                                VALUES (%s, %s, %s, %s, %s) RETURNING reader_id
                                """, (last_name, first_name, patronymic, ticket_number, registration_date))
            reader_id = self.cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Добавлен читатель с ID {reader_id}")
            return reader_id
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка добавления читателя: {str(e)}")
            return None

    def add_book(self, title, publication_year, genre, isbn, available_copies):
        """
        Добавление новой книги в базу данных.

        Args:
            title: Название книги
            publication_year: Год издания
            genre: Жанр
            isbn: ISBN книги
            available_copies: Количество экземпляров

        Returns:
            int or None: ID добавленной книги или None при ошибке
        """
        try:
            self.cursor.execute("""
                                INSERT INTO books (title, publication_year, genre, isbn, available_copies)
                                VALUES (%s, %s, %s, %s, %s) RETURNING book_id
                                """, (title, publication_year, genre, isbn, available_copies))
            book_id = self.cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Добавлена книга с ID {book_id}")
            return book_id
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка добавления книги: {str(e)}")
            return None

    def add_issue(self, book_id, reader_id, issue_date, return_date):
        """
        Добавление нового заказа (выдачи книги) в базу данных.

        Args:
            book_id: ID книги
            reader_id: ID читателя
            issue_date: Дата выдачи (строкой в формате YYYY-MM-DD)
            return_date: Дата возврата (строкой в формате YYYY-MM-DD или None)

        Returns:
            int or None: ID добавленного заказа или None при ошибке
        """
        try:
            self.cursor.execute("""
                                INSERT INTO issues (book_id, reader_id, issue_date, return_date)
                                VALUES (%s, %s, %s, %s) RETURNING issue_id
                                """, (book_id, reader_id, issue_date, return_date))
            issue_id = self.cursor.fetchone()[0]
            self.connection.commit()
            self.logger.info(f"Добавлен заказ (выдача) с ID {issue_id}")
            return issue_id
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка добавления заказа: {str(e)}")
            return None

    def update_book_author(self, old_book_id, old_author_id, new_book_id, new_author_id):
        """
        Обновление связи книга–автор.
        Меняет пару (old_book_id, old_author_id) на (new_book_id, new_author_id).
        """
        try:
            self.cursor.execute("""
                                UPDATE book_authors
                                SET book_id   = %s,
                                    author_id = %s
                                WHERE book_id = %s
                                  AND author_id = %s
                                """, (new_book_id, new_author_id, old_book_id, old_author_id))
            self.connection.commit()
            self.logger.info(f"Обновлена связь: {old_book_id}-{old_author_id} -> {new_book_id}-{new_author_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка обновления связи книга–автор: {str(e)}")
            return False, str(e)

    def update_issue(self, issue_id, book_id, reader_id, issue_date, return_date):
        """
        Обновление данных заказа (выдачи книги).

        Args:
            issue_id: ID заказа
            book_id: ID книги
            reader_id: ID читателя
            issue_date: Дата выдачи (строкой в формате YYYY-MM-DD)
            return_date: Дата возврата (строкой в формате YYYY-MM-DD или None)

        Returns:
            tuple: (успех операции (bool), сообщение об ошибке (str))
        """
        try:
            self.cursor.execute("""
                                UPDATE issues
                                SET book_id     = %s,
                                    reader_id   = %s,
                                    issue_date  = %s,
                                    return_date = %s
                                WHERE issue_id = %s RETURNING issue_id
                                """, (book_id, reader_id, issue_date, return_date, issue_id))

            updated_id = self.cursor.fetchone()
            if not updated_id:
                self.logger.error(f"Заказ с ID {issue_id} не найден")
                return False, "Заказ не найден"

            self.connection.commit()
            self.logger.info(f"Обновлен заказ с ID {issue_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка обновления заказа: {str(e)}")
            return False, str(e)

    def update_reader(self, reader_id, last_name, first_name, patronymic, ticket_number, registration_date):
        """
        Обновление данных читателя.

        Args:
            reader_id: ID читателя
            last_name: Фамилия
            first_name: Имя
            patronymic: Отчество
            ticket_number: Номер читательского билета
            registration_date: Дата регистрации (строкой в формате YYYY-MM-DD)

        Returns:
            tuple: (успех операции (bool), сообщение об ошибке (str))
        """
        try:
            self.cursor.execute("""
                                UPDATE readers
                                SET last_name         = %s,
                                    first_name        = %s,
                                    patronymic        = %s,
                                    ticket_number     = %s,
                                    registration_date = %s
                                WHERE reader_id = %s RETURNING reader_id
                                """, (last_name, first_name, patronymic, ticket_number, registration_date, reader_id))

            updated_id = self.cursor.fetchone()
            if not updated_id:
                self.logger.error(f"Читатель с ID {reader_id} не найден")
                return False, "Читатель не найден"

            self.connection.commit()
            self.logger.info(f"Обновлен читатель с ID {reader_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка обновления читателя: {str(e)}")
            return False, str(e)

    def update_book(self, book_id, title, publication_year, genre, isbn, available_copies):
        """
        Обновление данных книги.

        Args:
            book_id: ID книги
            title: Название книги
            publication_year: Год издания
            genre: Жанр
            isbn: ISBN книги
            available_copies: Количество экземпляров

        Returns:
            tuple: (успех операции (bool), сообщение об ошибке (str))
        """
        try:
            self.cursor.execute("""
                                UPDATE books
                                SET title            = %s,
                                    publication_year = %s,
                                    genre            = %s,
                                    isbn             = %s,
                                    available_copies = %s
                                WHERE book_id = %s RETURNING book_id
                                """, (title, publication_year, genre, isbn, available_copies, book_id))

            updated_id = self.cursor.fetchone()
            if not updated_id:
                self.logger.error(f"Книга с ID {book_id} не найдена")
                return False, "Книга не найдена"

            self.connection.commit()
            self.logger.info(f"Обновлена книга с ID {book_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка обновления книги: {str(e)}")
            return False, str(e)

    def delete_reader(self, reader_id):
        """
        Удаление читателя из базы данных.
        Args:
            reader_id: ID читателя

        Returns:
            tuple: (успех операции (bool), сообщение об ошибке (str))
        """
        try:
            self.cursor.execute("DELETE FROM readers WHERE reader_id = %s", (reader_id,))
            self.connection.commit()
            self.logger.info(f"Удален читатель с ID {reader_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка удаления читателя: {str(e)}")
            return False, str(e)

    def delete_book_author(self, book_id, author_id):
        """
        Удаление связи книга–автор по составному ключу.
        """
        try:
            self.cursor.execute(
                "DELETE FROM book_authors WHERE book_id = %s AND author_id = %s",
                (book_id, author_id)
            )
            self.connection.commit()
            self.logger.info(f"Удалена связь книга {book_id} — автор {author_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка удаления связи книга–автор: {str(e)}")
            return False, str(e)

    def delete_issue(self, issue_id):
        """
        Удаление заказа (выдачи книги) из базы данных.

        Args:
            issue_id: ID заказа

        Returns:
            tuple: (успех операции (bool), сообщение об ошибке (str))
        """
        try:
            self.cursor.execute("DELETE FROM issues WHERE issue_id = %s", (issue_id,))
            self.connection.commit()
            self.logger.info(f"Удален заказ с ID {issue_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка удаления заказа: {str(e)}")
            return False, str(e)

    def delete_book(self, book_id):
        """
        Удаление книги из базы данных.
        Args:
            book_id: ID книги

        Returns:
            tuple: (успех операции (bool), сообщение об ошибке (str))
        """
        try:
            self.cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            self.connection.commit()
            self.logger.info(f"Удалена книга с ID {book_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка удаления книги: {str(e)}")
            return False, str(e)

    def update_author(self, author_id, last_name, first_name, patronymic, birth_year, country):
        try:
            self.cursor.execute("""
                                UPDATE authors
                                SET last_name  = %s,
                                    first_name = %s,
                                    patronymic = %s,
                                    birth_year = %s,
                                    country    = %s
                                WHERE author_id = %s
                                """, (last_name, first_name, patronymic, birth_year, country, author_id))
            self.connection.commit()
            self.logger.info(f"Обновлен автор с ID {author_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка обновления автора: {str(e)}")
            return False, str(e)

    def delete_author(self, author_id):
        try:
            self.cursor.execute("DELETE FROM authors WHERE author_id = %s", (author_id,))
            self.connection.commit()
            self.logger.info(f"Удален аавтор с ID {author_id}")
            return True, ""
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Ошибка удаления автора: {str(e)}")
            return False, str(e)

    def execute_string_operation(self, operation, text, *args):
        """
        Выполнение строковой операции
        :param operation: Тип операции (UPPER, LOWER, etc.)
        :param text: Исходный текст
        :param args: Дополнительные аргументы
        :return: Результат операции
        """
        try:
            if operation == "UPPER":
                sql = f"SELECT UPPER(%s)"
                params = (text,)
            elif operation == "LOWER":
                sql = f"SELECT LOWER(%s)"
                params = (text,)
            elif operation == "SUBSTRING":
                start, length = args
                sql = f"SELECT SUBSTRING(%s FROM %s FOR %s)"
                params = (text, start, length)
            elif operation == "TRIM":
                sql = f"SELECT TRIM(%s)"
                params = (text,)
            elif operation == "LPAD":
                length, fill_char = args
                sql = f"SELECT LPAD(%s, %s, %s)"
                params = (text, length, fill_char)
            elif operation == "RPAD":
                length, fill_char = args
                sql = f"SELECT RPAD(%s, %s, %s)"
                params = (text, length, fill_char)
            elif operation == "CONCAT":
                second_text = args[0]
                sql = f"SELECT %s || %s"
                params = (text, second_text)

            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Ошибка выполнения строковой операции: {str(e)}")
            raise

    def search_books(self, column, search_type, search_text):
        """
        Поиск книг с использованием различных операторов
        :param column: Имя столбца для поиска
        :param search_type: Тип поиска (LIKE, ~, ~*, !~, !~*)
        :param search_text: Текст для поиска
        :return: Список найденных книг
        """
        try:
            if search_type == "LIKE":
                condition = f"{column} LIKE %s"
                params = (search_text,)
            elif search_type == "LIKE %":
                condition = f"{column} LIKE %s"
                params = (f"%{search_text}%",)
            elif search_type == "~":
                condition = f"{column} ~ %s"
                params = (search_text,)
            elif search_type == "~*":
                condition = f"{column} ~* %s"
                params = (search_text,)
            elif search_type == "!~":
                condition = f"{column} !~ %s"
                params = (search_text,)
            elif search_type == "!~*":
                condition = f"{column} !~* %s"
                params = (search_text,)
            else:
                raise ValueError(f"Неподдерживаемый тип поиска: {search_type}")

            sql = f"SELECT * FROM books WHERE {condition}"
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Ошибка поиска книг: {str(e)}")
            return []

    def search_authors(self, column, search_type, search_text):
        """
        Поиск авторов с использованием различных операторов
        :param column: Имя столбца для поиска
        :param search_type: Тип поиска (LIKE, ~, ~*, !~, !~*)
        :param search_text: Текст для поиска
        :return: Список найденных авторов
        """
        try:
            if search_type == "LIKE":
                condition = f"{column} LIKE %s"
                params = (search_text,)
            elif search_type == "LIKE %":
                condition = f"{column} LIKE %s"
                params = (f"%{search_text}%",)
            elif search_type == "~":
                condition = f"{column} ~ %s"
                params = (search_text,)
            elif search_type == "~*":
                condition = f"{column} ~* %s"
                params = (search_text,)
            elif search_type == "!~":
                condition = f"{column} !~ %s"
                params = (search_text,)
            elif search_type == "!~*":
                condition = f"{column} !~* %s"
                params = (search_text,)
            else:
                raise ValueError(f"Неподдерживаемый тип поиска: {search_type}")

            sql = f"SELECT * FROM authors WHERE {condition}"
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Ошибка поиска авторов: {str(e)}")
            return []