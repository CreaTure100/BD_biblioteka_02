class StringOperations:
    """Класс для выполнения строковых операций"""
    
    def __init__(self, connection):
        self.connection = connection

    def execute_operation(self, operation, text, *args):
        """
        Выполнение строковой операции
        :param operation: Тип операции (UPPER, LOWER, etc.)
        :param text: Исходный текст
        :param args: Дополнительные аргументы
        :return: Результат операции
        """
        with self.connection.cursor() as cursor:
            sql = self._build_sql_query(operation, text, *args)
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0] if result else None

    def _build_sql_query(self, operation, text, *args):
        """Построение SQL запроса для строковой операции"""
        if operation == "UPPER":
            return f"SELECT UPPER('{text}')"
        elif operation == "LOWER":
            return f"SELECT LOWER('{text}')"
        elif operation == "SUBSTRING":
            start, length = args
            return f"SELECT SUBSTRING('{text}' FROM {start} FOR {length})"
        elif operation == "TRIM":
            return f"SELECT TRIM('{text}')"
        elif operation == "LPAD":
            length, fill_char = args
            return f"SELECT LPAD('{text}', {length}, '{fill_char}')"
        elif operation == "RPAD":
            length, fill_char = args
            return f"SELECT RPAD('{text}', {length}, '{fill_char}')"
        elif operation == "CONCAT":
            second_text = args[0]
            return f"SELECT '{text}' || '{second_text}'"
        else:
            raise ValueError(f"Неподдерживаемая операция: {operation}")