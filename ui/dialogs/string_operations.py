from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QComboBox, QTextEdit,
                              QFormLayout, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt

class StringOperationsDialog(QDialog):
    """Диалог для выполнения строковых операций"""
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Строковые операции")
        self.setMinimumSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Ввод исходного текста
        form_layout = QFormLayout()
        self.input_text = QLineEdit()
        form_layout.addRow("Исходный текст:", self.input_text)

        # Выбор операции
        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "UPPER - Верхний регистр",
            "LOWER - Нижний регистр",
            "SUBSTRING - Извлечение подстроки",
            "TRIM - Удаление пробелов",
            "LPAD - Дополнение слева",
            "RPAD - Дополнение справа",
            "CONCAT - Объединение строк"
        ])
        form_layout.addRow("Операция:", self.operation_combo)

        # Дополнительные параметры
        self.params_layout = QFormLayout()
        self.setup_params_ui()
        
        layout.addLayout(form_layout)
        layout.addLayout(self.params_layout)

        # Кнопка выполнения
        execute_btn = QPushButton("Выполнить")
        execute_btn.clicked.connect(self.execute_operation)
        layout.addWidget(execute_btn)

        # Результат
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.result_text)

        # Обработчик изменения операции
        self.operation_combo.currentIndexChanged.connect(self.on_operation_changed)

    def setup_params_ui(self):
        """Настройка параметров для текущей операции"""
        self.clear_params()
        operation = self.operation_combo.currentText().split(' - ')[0]

        if operation in ["SUBSTRING"]:
            self.start_pos = QSpinBox()
            self.start_pos.setMinimum(1)
            self.length = QSpinBox()
            self.length.setMinimum(1)
            self.params_layout.addRow("Начальная позиция:", self.start_pos)
            self.params_layout.addRow("Длина:", self.length)

        elif operation in ["LPAD", "RPAD"]:
            self.length = QSpinBox()
            self.length.setMinimum(1)
            self.length.setValue(10)
            self.fill_char = QLineEdit()
            self.fill_char.setMaxLength(1)
            self.fill_char.setText(" ")
            self.params_layout.addRow("Итоговая длина:", self.length)
            self.params_layout.addRow("Символ заполнения:", self.fill_char)

        elif operation == "CONCAT":
            self.second_text = QLineEdit()
            self.params_layout.addRow("Вторая строка:", self.second_text)

    def clear_params(self):
        """Очистка дополнительных параметров"""
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def on_operation_changed(self):
        """Обработчик изменения выбранной операции"""
        self.setup_params_ui()

    def execute_operation(self):
        """Выполнение выбранной строковой операции"""
        operation = self.operation_combo.currentText().split(' - ')[0]
        input_text = self.input_text.text()
        
        try:
            if operation == "UPPER":
                result = self.controller.execute_string_operation("UPPER", input_text)
            elif operation == "LOWER":
                result = self.controller.execute_string_operation("LOWER", input_text)
            elif operation == "SUBSTRING":
                result = self.controller.execute_string_operation("SUBSTRING", 
                    input_text, self.start_pos.value(), self.length.value())
            elif operation == "TRIM":
                result = self.controller.execute_string_operation("TRIM", input_text)
            elif operation == "LPAD":
                result = self.controller.execute_string_operation("LPAD", 
                    input_text, self.length.value(), self.fill_char.text())
            elif operation == "RPAD":
                result = self.controller.execute_string_operation("RPAD", 
                    input_text, self.length.value(), self.fill_char.text())
            elif operation == "CONCAT":
                result = self.controller.execute_string_operation("CONCAT", 
                    input_text, self.second_text.text())
            
            self.result_text.setText(f"Результат: {result}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))