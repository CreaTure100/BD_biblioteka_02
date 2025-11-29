"""
Модуль централизованного управления стилями для приложения "Библиотека".
Содержит все стили CSS для компонентов интерфейса в светлой и темной темах.
"""

# Основные цвета для светлой темы
LIGHT_THEME_COLORS = {
    "background": "#f5f5f5",          # Основной фон
    "text": "#333333",                # Основной цвет текста
    "primary": "green",               # Основной цвет акцента (для кнопок)
    "primary_hover": "#2E6F40",       # Цвет при наведении
    "secondary": "#e0e0e0",           # Вторичный цвет (для заголовков таблиц)
    "border": "#c0c0c0",              # Цвет границ
    "selection": "#d0e8ff",           # Цвет выделения
    "input_bg": "white",              # Фон полей ввода
    "table_gridline": "#e0e0e0",      # Цвет линий таблицы
    "log_bg": "black",                # Фон для логов
    "log_text": "green",              # Текст для логов
}

# Основные цвета для темной темы
DARK_THEME_COLORS = {
    "background": "#2b2b2b",          # Основной фон
    "text": "#ffffff",                # Основной цвет текста
    "primary": "#495057",             # Основной цвет акцента (для кнопок)
    "primary_hover": "#6c757d",       # Цвет при наведении
    "secondary": "#3c3f41",           # Вторичный цвет (для заголовков таблиц)
    "border": "#555555",              # Цвет границ
    "selection": "#2e6f40",           # Цвет выделения
    "input_bg": "#495057",            # Фон полей ввода
    "table_gridline": "#555555",      # Цвет линий таблицы
    "log_bg": "#1e1e1e",              # Фон для логов
    "log_text": "#00ff00",            # Текст для логов
    "success": "#28a745",             # Цвет успеха
}

# ОБЩИЕ КОМПОНЕНТЫ СТИЛЕЙ

def get_button_style(theme="light"):
    """
    Возвращает стиль для кнопок в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для кнопок
    """
    if theme == "dark":
        return f"""
            QPushButton {{
                background-color: {DARK_THEME_COLORS["primary"]};
                color: {DARK_THEME_COLORS["text"]};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {DARK_THEME_COLORS["primary_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {DARK_THEME_COLORS["selection"]};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {LIGHT_THEME_COLORS["primary"]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_THEME_COLORS["primary_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {LIGHT_THEME_COLORS["primary_hover"]};
            }}
        """

def get_table_style(theme="light"):
    """
    Возвращает стиль для таблиц в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для таблиц
    """
    if theme == "dark":
        return f"""
            QTableWidget {{
                background-color: {DARK_THEME_COLORS["secondary"]};
                color: {DARK_THEME_COLORS["text"]};
                border: 1px solid {DARK_THEME_COLORS["border"]};
                gridline-color: {DARK_THEME_COLORS["table_gridline"]};
            }}
            QTableWidget::item:selected {{
                background-color: {DARK_THEME_COLORS["selection"]};
                color: {DARK_THEME_COLORS["text"]};
            }}
            QHeaderView::section {{
                background-color: {DARK_THEME_COLORS["primary"]};
                color: {DARK_THEME_COLORS["text"]};
                padding: 4px;
                border: 1px solid {DARK_THEME_COLORS["border"]};
                font-weight: bold;
            }}
        """
    else:
        return f"""
            QTableWidget {{
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                gridline-color: {LIGHT_THEME_COLORS["table_gridline"]};
            }}
            QTableWidget::item:selected {{
                background-color: {LIGHT_THEME_COLORS["selection"]};
            }}
            QHeaderView::section {{
                background-color: {LIGHT_THEME_COLORS["secondary"]};
                color: {LIGHT_THEME_COLORS["text"]};
                padding: 4px;
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                font-weight: bold;
            }}
        """

def get_tab_style(theme="light"):
    """
    Возвращает стиль для вкладок в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для вкладок
    """
    if theme == "dark":
        return f"""
            QTabWidget::pane {{
                border: 1px solid {DARK_THEME_COLORS["border"]};
                background-color: {DARK_THEME_COLORS["secondary"]};
            }}
            QTabBar::tab {{
                background-color: {DARK_THEME_COLORS["primary"]};
                color: {DARK_THEME_COLORS["text"]};
                padding: 8px 12px;
                border: 1px solid {DARK_THEME_COLORS["border"]};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {DARK_THEME_COLORS["secondary"]};
                font-weight: bold;
            }}
        """
    else:
        return f"""
            QTabWidget::pane {{
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: {LIGHT_THEME_COLORS["secondary"]};
                color: {LIGHT_THEME_COLORS["text"]};
                padding: 8px 12px;
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                font-weight: bold;
            }}
        """

def get_combobox_style(theme="light"):
    """
    Возвращает стиль для выпадающих списков в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для выпадающих списков
    """
    if theme == "dark":
        return f"""
            QComboBox {{
                background-color: {DARK_THEME_COLORS["input_bg"]};
                color: {DARK_THEME_COLORS["text"]};
                border: 1px solid {DARK_THEME_COLORS["border"]};
                border-radius: 4px;
                padding: 6px;
                min-height: 25px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {DARK_THEME_COLORS["border"]};
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 10px;
                height: 10px;
                background: {DARK_THEME_COLORS["success"]};
                border-radius: 5px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {DARK_THEME_COLORS["border"]};
                border-radius: 4px;
                background-color: {DARK_THEME_COLORS["input_bg"]};
                color: {DARK_THEME_COLORS["text"]};
                selection-background-color: {DARK_THEME_COLORS["selection"]};
                selection-color: {DARK_THEME_COLORS["text"]};
                padding: 4px;
            }}
        """
    else:
        return f"""
            QComboBox {{
                background-color: {LIGHT_THEME_COLORS["input_bg"]};
                color: {LIGHT_THEME_COLORS["text"]};
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                border-radius: 4px;
                padding: 6px;
                min-height: 25px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {LIGHT_THEME_COLORS["border"]};
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 10px;
                height: 10px;
                background: #00FF00;
                border-radius: 5px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                border-radius: 4px;
                background-color: {LIGHT_THEME_COLORS["input_bg"]};
                color: {LIGHT_THEME_COLORS["text"]};
                selection-background-color: {LIGHT_THEME_COLORS["selection"]};
                selection-color: {LIGHT_THEME_COLORS["text"]};
                padding: 4px;
            }}
        """

def get_input_fields_style(theme="light"):
    """
    Возвращает стиль для полей ввода (QLineEdit, QTextEdit, QSpinBox) в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для полей ввода
    """
    if theme == "dark":
        return f"""
            QLineEdit {{
                background-color: {DARK_THEME_COLORS["input_bg"]};
                color: {DARK_THEME_COLORS["text"]};
                border: 1px solid {DARK_THEME_COLORS["border"]};
                padding: 4px;
                min-width: 120px;
            }}
            QTextEdit {{
                background-color: {DARK_THEME_COLORS["input_bg"]};
                color: {DARK_THEME_COLORS["text"]};
                border: 1px solid {DARK_THEME_COLORS["border"]};
                padding: 2px;
            }}
            QSpinBox {{
                background-color: {DARK_THEME_COLORS["input_bg"]};
                color: {DARK_THEME_COLORS["text"]};
                border: 1px solid {DARK_THEME_COLORS["border"]};
                border-radius: 4px;
                padding: 1px 1px 1px 4px;
                min-width: 80px;
                max-height: 22px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {DARK_THEME_COLORS["primary_hover"]};
                width: 16px;
                border: none;
                border-left: 1px solid {DARK_THEME_COLORS["border"]};
            }}
            QSpinBox::up-button {{
                border-top-right-radius: 3px;
                border-bottom: 1px solid {DARK_THEME_COLORS["border"]};
            }}
            QSpinBox::down-button {{
                border-bottom-right-radius: 3px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {DARK_THEME_COLORS["selection"]};
            }}
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
                background-color: {DARK_THEME_COLORS["success"]};
            }}
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                width: 6px;
                height: 6px;
                background: {DARK_THEME_COLORS["success"]};
            }}
            QSpinBox:focus {{
                border: 1px solid {DARK_THEME_COLORS["success"]};
            }}
        """
    else:
        return f"""
            QLineEdit {{
                background-color: {LIGHT_THEME_COLORS["input_bg"]};
                color: {LIGHT_THEME_COLORS["text"]};
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                padding: 4px;
                min-width: 120px;
            }}
            QTextEdit {{
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                padding: 2px;
            }}
            QSpinBox {{
                background-color: {LIGHT_THEME_COLORS["input_bg"]};
                color: {LIGHT_THEME_COLORS["text"]};
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                border-radius: 4px;
                padding: 1px 1px 1px 4px;
                min-width: 80px;
                max-height: 22px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: #e8e8e8;
                width: 16px;
                border: none;
                border-left: 1px solid {LIGHT_THEME_COLORS["border"]};
            }}
            QSpinBox::up-button {{
                border-top-right-radius: 3px;
                border-bottom: 1px solid {LIGHT_THEME_COLORS["border"]};
            }}
            QSpinBox::down-button {{
                border-bottom-right-radius: 3px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {LIGHT_THEME_COLORS["selection"]};
            }}
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
                background-color: #c0c0c0;
            }}
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                width: 6px;
                height: 6px;
                background: #00FF00;
            }}
            QSpinBox:focus {{
                border: 1px solid #4a86e8;
            }}
        """

def get_message_box_style(theme="light"):
    """
    Возвращает стиль для диалоговых окон сообщений в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для диалоговых окон сообщений
    """
    if theme == "dark":
        return f"""
            QMessageBox {{
                background-color: {DARK_THEME_COLORS["secondary"]};
                color: {DARK_THEME_COLORS["text"]};
            }}
            QMessageBox QLabel {{
                color: {DARK_THEME_COLORS["text"]};
            }}
            QMessageBox QPushButton {{
                background-color: {DARK_THEME_COLORS["primary"]};
                color: {DARK_THEME_COLORS["text"]};
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                min-width: 40px;
                min-height: 20px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {DARK_THEME_COLORS["primary_hover"]};
            }}
        """
    else:
        return f"""
            QMessageBox {{
                background-color: {LIGHT_THEME_COLORS["background"]};
            }}
            QMessageBox QLabel {{
                color: {LIGHT_THEME_COLORS["text"]};
            }}
            QMessageBox QPushButton {{
                background-color: {LIGHT_THEME_COLORS["primary"]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                min-width: 40px;
                min-height: 20px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {LIGHT_THEME_COLORS["primary_hover"]};
            }}
        """

def get_log_display_style(theme="light"):
    """
    Возвращает стиль для отображения логов в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для отображения логов
    """
    if theme == "dark":
        return f"""
            background-color: {DARK_THEME_COLORS["log_bg"]}; 
            color: {DARK_THEME_COLORS["log_text"]};
        """
    else:
        return f"""
            background-color: {LIGHT_THEME_COLORS["log_bg"]}; 
            color: {LIGHT_THEME_COLORS["log_text"]};
        """
def get_groupbox_style(theme="light"):
    """
    Возвращает стиль для GroupBox в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для GroupBox
    """
    if theme == "dark":
        return f"""
            QGroupBox {{
                color: {DARK_THEME_COLORS["text"]};
                border: 1px solid {DARK_THEME_COLORS["border"]};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {DARK_THEME_COLORS["text"]};
            }}
        """
    else:
        return f"""
            QGroupBox {{
                color: {LIGHT_THEME_COLORS["text"]};
                border: 1px solid {LIGHT_THEME_COLORS["border"]};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {LIGHT_THEME_COLORS["text"]};
            }}
        """

def get_radiobutton_style(theme="light"):
    """
    Возвращает стиль для RadioButton в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для RadioButton
    """
    if theme == "dark":
        return f"""
            QRadioButton {{
                color: {DARK_THEME_COLORS["text"]};
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 13px;
                height: 13px;
                border-radius: 7px;
                border: 2px solid {DARK_THEME_COLORS["border"]};
                background-color: {DARK_THEME_COLORS["secondary"]};
            }}
            QRadioButton::indicator:checked {{
                background-color: {DARK_THEME_COLORS["success"]};
                border: 2px solid {DARK_THEME_COLORS["success"]};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {DARK_THEME_COLORS["primary_hover"]};
            }}
        """
    else:
        return f"""
            QRadioButton {{
                color: {LIGHT_THEME_COLORS["text"]};
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 13px;
                height: 13px;
                border-radius: 7px;
                border: 2px solid {LIGHT_THEME_COLORS["border"]};
                background-color: white;
            }}
            QRadioButton::indicator:checked {{
                background-color: {LIGHT_THEME_COLORS["primary"]};
                border: 2px solid {LIGHT_THEME_COLORS["primary"]};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {LIGHT_THEME_COLORS["primary_hover"]};
            }}
        """

def get_checkbox_style(theme="light"):
    """
    Возвращает стиль для CheckBox в зависимости от выбранной темы.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для CheckBox
    """
    if theme == "dark":
        return f"""
            QCheckBox {{
                color: {DARK_THEME_COLORS["text"]};
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 13px;
                height: 13px;
                border: 2px solid {DARK_THEME_COLORS["border"]};
                background-color: {DARK_THEME_COLORS["secondary"]};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {DARK_THEME_COLORS["success"]};
                border: 2px solid {DARK_THEME_COLORS["success"]};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {DARK_THEME_COLORS["primary_hover"]};
            }}
        """
    else:
        return f"""
            QCheckBox {{
                color: {LIGHT_THEME_COLORS["text"]};
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 13px;
                height: 13px;
                border: 2px solid {LIGHT_THEME_COLORS["border"]};
                background-color: white;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {LIGHT_THEME_COLORS["primary"]};
                border: 2px solid {LIGHT_THEME_COLORS["primary"]};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {LIGHT_THEME_COLORS["primary_hover"]};
            }}
        """

# ПОЛНЫЕ НАБОРЫ СТИЛЕЙ ДЛЯ ПРИЛОЖЕНИЯ

def get_light_theme_style():
    """
    Возвращает полный набор стилей для светлой темы приложения.

    Returns:
        str: Полный CSS стиль для светлой темы
    """
    return f"""
        QMainWindow, QDialog {{
            background-color: {LIGHT_THEME_COLORS["background"]};
        }}
        QLabel {{
            color: {LIGHT_THEME_COLORS["text"]};
        }}
        {get_button_style("light")}
        {get_table_style("light")}
        {get_tab_style("light")}
        {get_combobox_style("light")}
        {get_input_fields_style("light")}
        {get_groupbox_style("light")}
        {get_radiobutton_style("light")}
        {get_checkbox_style("light")}
    """

def get_dark_theme_style():
    """
    Возвращает полный набор стилей для темной темы приложения.

    Returns:
        str: Полный CSS стиль для темной темы
    """
    return f"""
        QMainWindow, QDialog {{
            background-color: {DARK_THEME_COLORS["background"]};
            color: {DARK_THEME_COLORS["text"]};
        }}
        QLabel {{
            color: {DARK_THEME_COLORS["text"]};
        }}
        {get_button_style("dark")}
        {get_table_style("dark")}
        {get_tab_style("dark")}
        {get_combobox_style("dark")}
        {get_input_fields_style("dark")}
        {get_groupbox_style("dark")}
        {get_radiobutton_style("dark")}
        {get_checkbox_style("dark")}
    """

def get_title_style(theme="light"):
    """
    Возвращает стиль для заголовка приложения.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для заголовка
    """
    if theme == "dark":
        return f"color: {DARK_THEME_COLORS['success']}; margin: 10px;"
    else:
        return f"color: {LIGHT_THEME_COLORS['primary']}; margin: 10px;"

def get_form_label_style(theme="light"):
    """
    Возвращает стиль для меток в формах.

    Args:
        theme (str): "light" или "dark" - выбранная тема

    Returns:
        str: CSS стиль для меток в формах
    """
    if theme == "dark":
        return f"color: {DARK_THEME_COLORS['text']}; font-weight: bold;"
    else:
        return f"color: {LIGHT_THEME_COLORS['text']}; font-weight: bold;"
