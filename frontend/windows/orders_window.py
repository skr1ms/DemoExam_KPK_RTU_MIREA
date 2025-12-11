"""
Окно для работы с заказами
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
    QScrollArea,
    QApplication,
)
from PySide6.QtCore import QTimer
from frontend.services.orders_service import OrdersService
from frontend.services.goods_service import GoodsService
from frontend.utils.async_helper import run_async_sync
from frontend.utils.styles import STYLES
from frontend.windows.create_order_window import CreateOrderWindow
from frontend.windows.order_form_window import OrderFormWindow
from frontend.widgets.order_card import OrderCard
from backend.internal.entity.user import User
from backend.internal.entity.order import Order


class OrdersWindow(QWidget):
    def __init__(
        self,
        orders_service: OrdersService,
        goods_service: GoodsService,
        user: User,
        auth_service=None,
    ):
        super().__init__()
        self.orders_service = orders_service
        self.goods_service = goods_service
        self.auth_service = auth_service
        self.user = user
        self.orders: list[Order] = []
        self.setup_ui()
        try:
            self.load_orders()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при загрузке заказов: {str(e)}"
            )

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Заказы")
        title.setStyleSheet(STYLES["TITLE_STYLE"])
        layout.addWidget(title)

        buttons_layout = QHBoxLayout()

        if self.user.role == "Администратор":
            add_button = QPushButton("Добавить заказ")
            add_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            add_button.clicked.connect(self.add_order)
            buttons_layout.addWidget(add_button)

            edit_button = QPushButton("Редактировать")
            edit_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            edit_button.clicked.connect(self.edit_order)
            buttons_layout.addWidget(edit_button)

            delete_button = QPushButton("Удалить")
            delete_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            delete_button.clicked.connect(self.delete_order)
            buttons_layout.addWidget(delete_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(STYLES["SCROLL_AREA_STYLE"])

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(10)
        self.cards_container.setLayout(self.cards_layout)

        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)

        self.order_cards = []

    def load_orders(self):
        """Загрузить заказы"""
        try:
            self.orders = run_async_sync(
                self.orders_service.get_orders_for_user(self.user)
            )
            self.update_table()
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError):
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                QMessageBox.critical(
                    self, "Ошибка", f"Ошибка при загрузке заказов: {str(e)}"
                )

    def update_table(self):
        """Обновить карточки заказов"""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                elif item.spacerItem():
                    del item

        self.order_cards = []

        pick_up_points = run_async_sync(self.orders_service.get_all_pick_up_points())
        pick_up_points_dict = {point.id: point for point in pick_up_points}

        for order in self.orders:
            on_double_click = None
            if self.user.role == "Администратор":

                def make_handler(o):
                    return lambda: self.on_card_double_clicked(o)

                on_double_click = make_handler(order)
            card = OrderCard(
                order,
                parent=self.cards_container,
                pick_up_points_dict=pick_up_points_dict,
            )
            if on_double_click:
                card.on_double_click = on_double_click
            self.order_cards.append(card)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

        QApplication.processEvents()

        if hasattr(self, "scroll_area"):

            def scroll_to_top():
                scroll_bar = self.scroll_area.verticalScrollBar()
                scroll_bar.setValue(0)

                if self.order_cards:
                    self.scroll_area.ensureWidgetVisible(self.order_cards[0], 0, 0)

            QTimer.singleShot(50, scroll_to_top)

    def create_order(self):
        """Создать заказ (для клиента)"""
        create_window = CreateOrderWindow(
            self.orders_service, self.goods_service, self.user, parent=self
        )
        create_window.show()

    def add_order(self):
        """Добавить заказ (для администратора)"""
        form_window = OrderFormWindow(
            self.orders_service,
            self.goods_service,
            auth_service=self.auth_service,
            order=None,
            parent=self,
            user=self.user,
        )
        form_window.show()

    def on_card_double_clicked(self, order: Order):
        """Обработка двойного клика на карточку заказа"""
        if self.user.role == "Администратор":
            self.edit_order_by_id(order.id)

    def edit_order(self):
        """Редактировать заказ (по выбранной карточке)"""

        selected_order = None
        for card in self.order_cards:
            if hasattr(card, "_selected") and card._selected:
                selected_order = card.order
                break

        if not selected_order:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для редактирования")
            return

        self.edit_order_by_id(selected_order.id)

    def edit_order_by_id(self, order_id: int):
        """Редактировать заказ по ID"""

        try:
            order = run_async_sync(self.orders_service.get_order_by_id(order_id))
            if not order:
                QMessageBox.warning(self, "Ошибка", "Заказ не найден")
                return

            form_window = OrderFormWindow(
                self.orders_service,
                self.goods_service,
                auth_service=self.auth_service,
                order=order,
                parent=self,
                user=self.user,
            )
            form_window.show()
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError):
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                QMessageBox.critical(
                    self, "Ошибка", f"Ошибка при загрузке заказа: {str(e)}"
                )

    def delete_order(self):
        """Удалить заказ (для администратора)"""
        selected_order = None
        for card in self.order_cards:
            if hasattr(card, "_selected") and card._selected:
                selected_order = card.order
                break

        if not selected_order:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для удаления")
            return

        order = selected_order
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить заказ #{order.id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                run_async_sync(self.orders_service.delete_order(order.id, self.user))
                QMessageBox.information(self, "Успех", "Заказ удален")
                self.load_orders()
            except Exception as e:
                from backend.internal.usecase.authorization_usecase import (
                    PermissionError,
                )

                if isinstance(e, PermissionError):
                    QMessageBox.warning(self, "Ошибка доступа", str(e))
                else:
                    QMessageBox.critical(
                        self, "Ошибка", f"Ошибка при удалении заказа: {str(e)}"
                    )

    def on_item_double_clicked(self, item):
        """Обработка двойного клика на элемент таблицы"""
        if self.user.role == "Администратор":
            self.edit_order()
