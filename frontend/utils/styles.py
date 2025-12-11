"""
Стили приложения согласно руководству по стилю
"""

STYLES = {
    "MAIN_BG": "#FFFFFF",  # Основной фон
    "ADDITIONAL_BG": "#7FFF00",  # Дополнительный фон
    "ACCENT": "#00FA9A",  # Акцентирование внимания
    "DISCOUNT_BG": "#2E8B57",  # Фон для скидки > 15%
    # Шрифт
    "FONT_FAMILY": "Times New Roman",
    # Стили для окон
    "WINDOW_STYLE": """
        QMainWindow {
            background-color: #FFFFFF;
            font-family: "Times New Roman";
            color: #000000;
        }
        QWidget {
            background-color: #FFFFFF;
            font-family: "Times New Roman";
            color: #000000;
        }
    """,
    # Стили для заголовков
    "TITLE_STYLE": """
        QLabel {
            font-family: "Times New Roman";
            font-size: 20px;
            font-weight: bold;
            color: #000000;
            padding: 10px;
            background-color: transparent;
        }
    """,
    # Стили для обычных меток
    "LABEL_STYLE": """
        QLabel {
            font-family: "Times New Roman";
            font-size: 11px;
            color: #000000;
            background-color: transparent;
        }
    """,
    # Стили для кнопок
    "BUTTON_STYLE": """
        QPushButton {
            background-color: #00FA9A;
            color: #000000;
            font-family: "Times New Roman";
            font-size: 12px;
            padding: 8px 16px;
            border: 1px solid #00FA9A;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #7FFF00;
        }
        QPushButton:pressed {
            background-color: #2E8B57;
        }
    """,
    # Стили для полей ввода
    "INPUT_STYLE": """
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #FFFFFF;
            border: 2px solid #00FA9A;
            padding: 10px;
            font-family: "Times New Roman";
            font-size: 14px;
            color: #000000;
            min-height: 30px;
        }
        QLineEdit {
            min-height: 35px;
        }
        QTextEdit {
            min-height: 80px;
            font-size: 14px;
        }
        QSpinBox, QDoubleSpinBox {
            min-height: 35px;
            min-width: 100px;
        }
        QComboBox {
            min-height: 35px;
        }
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 2px solid #7FFF00;
            background-color: #FFFFFF;
        }
        QLineEdit::placeholder {
            color: #808080;
        }
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #000000;
            selection-background-color: #00FA9A;
            selection-color: #000000;
            border: 1px solid #00FA9A;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #00FA9A;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 0px;
            height: 0px;
        }
    """,
    # Стили для стрелки ComboBox (вниз)
    "COMBO_ARROW_DOWN_STYLE": """
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #000000;
            border-bottom: none;
            margin-right: 3px;
        }
    """,
    # Стили для стрелки ComboBox (вверх)
    "COMBO_ARROW_UP_STYLE": """
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 6px solid #000000;
            border-top: none;
            margin-right: 3px;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            background-color: #00FA9A;
            border: 1px solid #00FA9A;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            background-color: #00FA9A;
            border: 1px solid #00FA9A;
        }
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            border: 2px solid #000000;
            width: 6px;
            height: 6px;
        }
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            border: 2px solid #000000;
            width: 6px;
            height: 6px;
        }
    """,
    # Стили для таблиц
    "TABLE_STYLE": """
        QTableWidget {
            background-color: #FFFFFF;
            border: 1px solid #00FA9A;
            font-family: "Times New Roman";
            font-size: 11px;
            gridline-color: #00FA9A;
            color: #000000;
        }
        QTableWidget::item {
            padding: 5px;
            color: #000000;
        }
        QTableWidget::item:selected {
            background-color: #00FA9A;
            color: #000000;
        }
        QTableWidget::item:alternate {
            background-color: #F0F0F0;
            color: #000000;
        }
        QHeaderView::section {
            background-color: #7FFF00;
            color: #000000;
            font-family: "Times New Roman";
            font-weight: bold;
            padding: 8px;
            border: 1px solid #00FA9A;
        }
    """,
    # Стиль для строк с большой скидкой
    "DISCOUNT_ROW_STYLE": """
        background-color: #2E8B57;
        color: #FFFFFF;
    """,
    # Стиль для итоговой суммы
    "TOTAL_LABEL_STYLE": """
        QLabel {
            font-family: "Times New Roman";
            font-size: 16px;
            font-weight: bold;
            color: #000000;
            background-color: transparent;
        }
    """,
    # Стили для диалоговых окон (QMessageBox)
    "MESSAGEBOX_STYLE": """
        QMessageBox {
            background-color: #FFFFFF;
            font-family: "Times New Roman";
        }
        QMessageBox QLabel {
            color: #000000;
            background-color: #FFFFFF;
            font-family: "Times New Roman";
            font-size: 11px;
        }
        QMessageBox QPushButton {
            background-color: #00FA9A;
            color: #000000;
            font-family: "Times New Roman";
            font-size: 12px;
            padding: 8px 16px;
            border: 1px solid #00FA9A;
            border-radius: 4px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #7FFF00;
        }
        QMessageBox QPushButton:pressed {
            background-color: #2E8B57;
        }
    """,
    # Стили для групповых боксов (QGroupBox)
    "GROUPBOX_STYLE": """
        QGroupBox {
            font-family: "Times New Roman";
            font-size: 12px;
            font-weight: bold;
            color: #000000;
            border: 2px solid #00FA9A;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #FFFFFF;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            background-color: #FFFFFF;
        }
    """,
    # Стили для вкладок (QTabWidget)
    "TAB_STYLE": """
        QTabWidget::pane {
            border: 1px solid #00FA9A;
            background-color: #FFFFFF;
        }
        QTabBar::tab {
            background-color: #FFFFFF;
            color: #000000;
            font-family: "Times New Roman";
            font-size: 12px;
            padding: 8px 16px;
            border: 1px solid #00FA9A;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #7FFF00;
            color: #000000;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background-color: #00FA9A;
            color: #000000;
        }
        QTabBar::tab:!selected {
            background-color: #FFFFFF;
            color: #000000;
        }
    """,
    # Стили для карточки заказа (OrderCard)
    "ORDER_CARD_STYLE": """
        QFrame {
            background-color: #FFFFFF;
            border: 1px solid #000000;
        }
        QLabel {
            color: #000000;
            font-family: "Times New Roman";
        }
    """,
    # Стиль для выбранной карточки заказа
    "ORDER_CARD_SELECTED_STYLE": """
        QFrame {
            border: 2px solid #7FFF00;
        }
    """,
    # Стили для карточки товара (ProductCard)
    "PRODUCT_CARD_STYLE": """
        QFrame {
            background-color: #FFFFFF;
            border: 1px solid #000000;
        }
        QLabel {
            color: #000000;
            font-family: "Times New Roman";
        }
    """,
    # Стиль для карточки товара со скидкой > 15%
    "PRODUCT_CARD_DISCOUNT_STYLE": """
        QFrame {
            background-color: #2E8B57;
            border: 1px solid #000000;
        }
        QLabel {
            color: #FFFFFF;
            font-family: "Times New Roman";
        }
    """,
    # Стиль для карточки товара без остатка
    "PRODUCT_CARD_OUT_OF_STOCK_STYLE": """
        QFrame {
            background-color: #ADD8E6;
            border: 1px solid #000000;
        }
        QLabel {
            color: #000000;
            font-family: "Times New Roman";
        }
    """,
    # Стиль для выбранной карточки товара
    "PRODUCT_CARD_SELECTED_STYLE": """
        QFrame {
            border: 2px solid #7FFF00;
        }
    """,
    # Стили для цены в карточке товара
    "PRODUCT_CARD_PRICE_DISCOUNTED_STYLE": """
        QLabel {
            color: #FF0000;
        }
    """,
    "PRODUCT_CARD_PRICE_NORMAL_STYLE": """
        QLabel {
            color: #000000;
        }
    """,
    # Стиль для названия товара в карточке
    "PRODUCT_CARD_NAME_STYLE": """
        QLabel {
            font-weight: bold;
            font-size: 12px;
        }
    """,
    # Стиль для значения скидки в карточке
    "PRODUCT_CARD_DISCOUNT_VALUE_STYLE": """
        QLabel {
            font-weight: bold;
            font-size: 14px;
        }
    """,
    # Стиль для области прокрутки
    "SCROLL_AREA_STYLE": """
        QScrollArea {
            border: 1px solid #000000;
            background-color: #FFFFFF;
        }
    """,
    # Стиль для строки с количеством 0
    "PRODUCT_CARD_COUNT_ZERO_STYLE": """
        QLabel {
            background-color: #ADD8E6;
            padding: 2px;
        }
    """,
    # Стиль для метки ошибки валидации
    "ERROR_LABEL_STYLE": """
        QLabel {
            font-family: "Times New Roman";
            font-size: 10px;
            color: #FF0000;
            background-color: transparent;
            padding: 2px;
        }
    """,
    # Стиль для поля ввода с ошибкой
    "INPUT_ERROR_STYLE": """
        QDateEdit {
            background-color: #FFFFFF;
            border: 2px solid #FF0000;
            padding: 10px;
            font-family: "Times New Roman";
            font-size: 14px;
            color: #000000;
            min-height: 35px;
        }
        QLineEdit {
            background-color: #FFFFFF;
            border: 2px solid #FF0000;
            padding: 10px;
            font-family: "Times New Roman";
            font-size: 14px;
            color: #000000;
            min-height: 35px;
        }
    """,
}
