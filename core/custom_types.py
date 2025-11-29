import psycopg2
from typing import List, Dict, Tuple, Optional
from PySide6.QtWidgets import QMessageBox


class CustomTypesManager:
    """
    Менеджер для работы с пользовательскими типами данных (ENUM и составные типы).
    Полностью совместим с существующей архитектурой приложения.
    """

    def __init__(self, db_connection):
        self.conn = db_connection

    def execute_safe(self, sql: str, params: tuple = None) -> Tuple[bool, str]:
        """Безопасное выполнение SQL-запроса с обработкой ошибок."""
        try:
            with self.conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                self.conn.commit()
                return True, "Операция выполнена успешно"
        except psycopg2.Error as e:
            self.conn.rollback()
            error_msg = f"Ошибка базы данных: {e}"
            return False, error_msg
        except Exception as e:
            self.conn.rollback()
            error_msg = f"Неожиданная ошибка: {e}"
            return False, error_msg

    def get_custom_types(self) -> List[Dict]:
        """Получить список всех пользовательских типов."""
        try:
            with self.conn.cursor() as cursor:
                # Получаем ENUM типы
                cursor.execute("""
                    SELECT t.typname as type_name, 
                           'enum' as type_kind,
                           array_agg(e.enumlabel ORDER BY e.enumsortorder) as values
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid  
                    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                    WHERE n.nspname = 'public'
                    GROUP BY t.typname
                """)
                enum_types = cursor.fetchall()

                # Получаем составные типы
                cursor.execute("""
                    SELECT t.typname as type_name,
                           'composite' as type_kind,
                           json_agg(
                               json_build_object(
                                   'attribute_name', a.attname,
                                   'attribute_type', format_type(a.atttypid, a.atttypmod)
                               ) ORDER BY a.attnum
                           ) as attributes
                    FROM pg_type t
                    JOIN pg_class c ON c.oid = t.typrelid
                    JOIN pg_attribute a ON a.attrelid = c.oid
                    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                    WHERE n.nspname = 'public'
                      AND t.typtype = 'c'
                      AND a.attnum > 0
                      AND NOT a.attisdropped
                    GROUP BY t.typname
                """)
                composite_types = cursor.fetchall()

                # Форматируем результаты
                result = []
                for type_name, type_kind, values in enum_types:
                    result.append({
                        'name': type_name,
                        'kind': type_kind,
                        'values': values if values else []
                    })

                for type_name, type_kind, attributes in composite_types:
                    result.append({
                        'name': type_name,
                        'kind': type_kind,
                        'attributes': attributes if attributes else []
                    })

                return result
        except Exception as e:
            print(f"Ошибка при получении пользовательских типов: {e}")
            return []

    def create_enum_type(self, type_name: str, values: List[str]) -> Tuple[bool, str]:
        """Создать новый ENUM тип."""
        if not values:
            return False, "ENUM должен содержать хотя бы одно значение"

        # Экранируем значения - исправленная строка
        escaped_values = [f"""'{value.replace("'", "''")}'""" for value in values]
        values_sql = ", ".join(escaped_values)

        sql = f"CREATE TYPE {type_name} AS ENUM ({values_sql})"
        return self.execute_safe(sql)

    def create_composite_type(self, type_name: str, attributes: List[Dict]) -> Tuple[bool, str]:
        """Создать новый составной тип."""
        if not attributes:
            return False, "Составной тип должен содержать хотя бы один атрибут"

        attributes_sql = ", ".join([
            f"{attr['name']} {attr['type']}" for attr in attributes
        ])

        sql = f"CREATE TYPE {type_name} AS ({attributes_sql})"
        return self.execute_safe(sql)

    def add_enum_value(self, type_name: str, value: str, after: str = None) -> Tuple[bool, str]:
        """Добавить значение в ENUM тип."""
        # В PostgreSQL нельзя напрямую добавлять значения в ENUM, нужно создать новый тип
        # Это упрощенная реализация - в продакшене нужно быть осторожнее
        sql = f"ALTER TYPE {type_name} ADD VALUE '{value}'"
        if after:
            sql += f" AFTER '{after}'"

        return self.execute_safe(sql)

    def drop_enum_value(self, type_name: str, value: str) -> Tuple[bool, str]:
        """Удалить значение из ENUM типа."""
        # В PostgreSQL нельзя напрямую удалять значения из ENUM
        # Это сложная операция, требующая создания нового типа
        return False, "Удаление значений из ENUM не поддерживается напрямую в PostgreSQL"

    def add_composite_attribute(self, type_name: str, attribute_name: str,
                                attribute_type: str) -> Tuple[bool, str]:
        """Добавить атрибут в составной тип."""
        # В PostgreSQL нельзя напрямую изменять составные типы
        return False, "Изменение составных типов не поддерживается напрямую в PostgreSQL"

    def drop_composite_attribute(self, type_name: str, attribute_name: str) -> Tuple[bool, str]:
        """Удалить атрибут из составного типа."""
        # В PostgreSQL нельзя напрямую изменять составные типы
        return False, "Изменение составных типов не поддерживается напрямую в PostgreSQL"

    def drop_type(self, type_name: str) -> Tuple[bool, str]:
        """Удалить пользовательский тип."""
        sql = f"DROP TYPE {type_name} CASCADE"
        return self.execute_safe(sql)

    def is_type_used(self, type_name: str) -> bool:
        """Проверить, используется ли тип в каких-либо таблицах."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE udt_name = %s
                """, (type_name,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"Ошибка при проверке использования типа: {e}")
            return False

    def get_type_usage(self, type_name: str) -> List[Tuple]:
        """Получить информацию о том, где используется тип."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name, column_name
                    FROM information_schema.columns 
                    WHERE udt_name = %s
                    ORDER BY table_name, column_name
                """, (type_name,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении информации об использовании типа: {e}")
            return []