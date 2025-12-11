"""
Окно создания заказа
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QHeaderView,
    QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from frontend.widgets.custom_combo import CustomComboBox
from frontend.services.orders_service import OrdersService
from frontend.services.goods_service import GoodsService
from frontend.utils.async_helper import run_async_sync
from frontend.utils.styles import STYLES
from backend.internal.entity.user import User
from backend.internal.entity.good import Good
from typing import Dict, List


class CreateOrderWindow(QMainWindow):
    def __init__(
        self,
        orders_service: OrdersService,
        goods_service: GoodsService,
        user: User,
        parent=None,
    ):
        super().__init__(parent)
        self.orders_service = orders_service
        self.goods_service = goods_service
        self.user = user
        self.cart: List[Dict] = []
        self.goods: List[Good] = []
        self.setup_ui()
        self.apply_styles()
        self.load_goods()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Создание заказа")
        self.setGeometry(150, 150, 900, 700)

        icon_path = os.path.join("frontend/public", "Icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("Создание заказа")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(STYLES["TITLE_STYLE"])
        layout.addWidget(title)

        goods_group = QGroupBox("Выбор товаров")
        goods_group.setStyleSheet(STYLES.get("GROUPBOX_STYLE", ""))
        goods_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        search_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название или артикул")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet(STYLES["INPUT_STYLE"])
        search_layout.addWidget(self.search_input)

        goods_layout.addLayout(search_layout)

        self.goods_table = QTableWidget()
        self.goods_table.setColumnCount(6)
        self.goods_table.setHorizontalHeaderLabels(
            ["Артикул", "Название", "Цена", "Скидка", "Количество", "Добавить"]
        )
        self.goods_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.goods_table.setSelectionBehavior(QTableWidget.SelectRows)
        goods_layout.addWidget(self.goods_table)

        goods_group.setLayout(goods_layout)
        layout.addWidget(goods_group)

        cart_group = QGroupBox("Корзина")
        cart_group.setStyleSheet(STYLES.get("GROUPBOX_STYLE", ""))
        cart_layout = QVBoxLayout()

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(
            ["Артикул", "Название", "Цена", "Количество", "Сумма", "Действие"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        cart_layout.addWidget(self.cart_table)

        self.total_label = QLabel("Итого: 0.00 ₽")
        self.total_label.setStyleSheet(STYLES["TOTAL_LABEL_STYLE"])
        cart_layout.addWidget(self.total_label)

        cart_group.setLayout(cart_layout)
        layout.addWidget(cart_group)

        delivery_group = QGroupBox("Данные доставки")
        delivery_group.setStyleSheet(STYLES.get("GROUPBOX_STYLE", ""))
        delivery_layout = QVBoxLayout()

        pick_up_label = QLabel("Пункт выдачи:")
        pick_up_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        delivery_layout.addWidget(pick_up_label)
        self.pick_up_combo = CustomComboBox()
        self.pick_up_combo.setStyleSheet(STYLES["INPUT_STYLE"])
        delivery_layout.addWidget(self.pick_up_combo)
        self.load_pick_up_points()

        code_label = QLabel("Код получателя:")
        code_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        delivery_layout.addWidget(code_label)
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Введите код получателя (опционально)")
        self.code_input.setStyleSheet(STYLES["INPUT_STYLE"])
        delivery_layout.addWidget(self.code_input)

        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)

        buttons_layout = QHBoxLayout()

        create_button = QPushButton("Создать заказ")
        create_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        create_button.clicked.connect(self.create_order)
        buttons_layout.addWidget(create_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        layout.addStretch()

    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(STYLES["WINDOW_STYLE"])
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(STYLES["BUTTON_STYLE"])
        for input_widget in self.findChildren(QLineEdit):
            input_widget.setStyleSheet(STYLES["INPUT_STYLE"])
        self.goods_table.setStyleSheet(STYLES["TABLE_STYLE"])
        self.cart_table.setStyleSheet(STYLES["TABLE_STYLE"])

    def load_goods(self):
        """Загрузить товары"""
        try:
            self.goods = run_async_sync(self.goods_service.get_all_goods())
            self.update_goods_table()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при загрузке товаров: {str(e)}"
            )

    def update_goods_table(self):
        """Обновить таблицу товаров"""
        self.goods_table.setRowCount(len(self.goods))

        for row, good in enumerate(self.goods):
            self.goods_table.setItem(row, 0, QTableWidgetItem(good.article))
            self.goods_table.setItem(row, 1, QTableWidgetItem(good.name))
            self.goods_table.setItem(row, 2, QTableWidgetItem(str(float(good.price))))

            discount_text = f"{float(good.discount)}%" if good.discount else "0%"
            self.goods_table.setItem(row, 3, QTableWidgetItem(discount_text))

            quantity_spin = QSpinBox()
            quantity_spin.setMinimum(1)
            quantity_spin.setMaximum(good.count if good.count > 0 else 999)
            quantity_spin.setValue(1)
            self.goods_table.setCellWidget(row, 4, quantity_spin)

            add_button = QPushButton("+")
            add_button.clicked.connect(
                lambda checked, g=good, s=quantity_spin: self.add_to_cart(g, s.value())
            )
            self.goods_table.setCellWidget(row, 5, add_button)

    def on_search_changed(self, text):
        """Обработка изменения поискового запроса"""
        if not text.strip():
            self.load_goods()
            return

        try:
            self.goods = run_async_sync(
                self.goods_service.search_goods(text, self.user)
            )
            self.update_goods_table()
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError):
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске: {str(e)}")

    def add_to_cart(self, good: Good, quantity: int):
        """Добавить товар в корзину"""
        if quantity <= 0:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть больше 0")
            return

        if good.count < quantity:
            QMessageBox.warning(
                self, "Ошибка", f"Недостаточно товара. В наличии: {good.count}"
            )
            return

        for item in self.cart:
            if item["good"].id == good.id:
                item["quantity"] += quantity
                self.update_cart_table()
                return

        self.cart.append({"good": good, "quantity": quantity})
        self.update_cart_table()

    def update_cart_table(self):
        """Обновить таблицу корзины"""
        self.cart_table.setRowCount(len(self.cart))
        items = [
            {"goods_id": item["good"].id, "quantity": item["quantity"]}
            for item in self.cart
        ]

        try:
            total = run_async_sync(
                self.orders_service.calculate_order_total(order_id=None, items=items)
            )
        except Exception as e:
            total = 0.0
            QMessageBox.warning(
                self, "Ошибка расчета", f"Ошибка при расчете суммы: {str(e)}"
            )

        for row, item in enumerate(self.cart):
            good = item["good"]
            quantity = item["quantity"]

            self.cart_table.setItem(row, 0, QTableWidgetItem(good.article))
            self.cart_table.setItem(row, 1, QTableWidgetItem(good.name))

            price = self.goods_service.calculate_price_with_discount(
                float(good.price), good.discount
            )

            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(quantity)))

            item_total = price * quantity
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{item_total:.2f}"))

            remove_button = QPushButton("Удалить")
            remove_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            remove_button.clicked.connect(
                lambda checked, r=row: self.remove_from_cart(r)
            )
            self.cart_table.setCellWidget(row, 5, remove_button)

        self.total_label.setText(f"Итого: {total:.2f} ₽")

    def remove_from_cart(self, row: int):
        """Удалить товар из корзины"""
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.update_cart_table()

    def load_pick_up_points(self):
        """Загрузить пункты выдачи"""
        try:
            pick_up_points = run_async_sync(
                self.orders_service.get_all_pick_up_points()
            )
            self.pick_up_combo.clear()
            self.pick_up_combo.addItem("Выберите пункт выдачи", None)
            for point in pick_up_points:
                self.pick_up_combo.addItem(point.full_address, point.id)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при загрузке пунктов выдачи: {str(e)}"
            )

    def create_order(self):
        """Создать заказ"""
        if not self.cart:
            QMessageBox.warning(self, "Ошибка", "Добавьте товары в корзину")
            return

        pick_up_point_id = self.pick_up_combo.currentData()
        if not pick_up_point_id:
            QMessageBox.warning(self, "Ошибка", "Выберите пункт выдачи")
            return

        try:
            items = [
                {"goods_id": item["good"].id, "quantity": item["quantity"]}
                for item in self.cart
            ]

            order = run_async_sync(
                self.orders_service.create_order(
                    user=self.user,
                    pick_up_point_id=pick_up_point_id,
                    recipient_code=self.code_input.text().strip() or None,
                    items=items,
                )
            )

            QMessageBox.information(self, "Успех", f"Заказ #{order.id} создан успешно!")
            self.close()
            if self.parent():
                self.parent().load_orders()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при создании заказа: {str(e)}"
            )
