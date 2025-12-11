"""
Виджет карточки заказа согласно макету order_card.png
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from backend.internal.entity.order import Order
from frontend.utils.styles import STYLES


class OrderCard(QFrame):
    def __init__(
        self, order: Order, parent=None, on_double_click=None, pick_up_points_dict=None
    ):
        super().__init__(parent)
        self.order = order
        self.on_double_click = on_double_click
        self.pick_up_points_dict = pick_up_points_dict or {}
        self._selected = False
        self.setup_ui()
        self.apply_styles()

    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика"""
        if self.on_double_click:
            self.on_double_click(self.order)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """Обработка клика для выбора карточки"""
        self._selected = True

        if self.parent():
            for child in self.parent().findChildren(OrderCard):
                if child != self:
                    child._selected = False
                    child.update_selection_style()
        self.update_selection_style()
        super().mousePressEvent(event)

    def update_selection_style(self):
        """Обновить стиль в зависимости от выбора"""
        if self._selected:
            self.setStyleSheet(
                STYLES.get("ORDER_CARD_STYLE", "")
                + STYLES.get("ORDER_CARD_SELECTED_STYLE", "")
            )
        else:
            self.apply_styles()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        info_panel = QFrame()
        info_panel.setFrameStyle(QFrame.Box)
        info_panel.setLineWidth(1)
        info_layout = QVBoxLayout()
        info_panel.setLayout(info_layout)

        article_label = QLabel(f"Артикул заказа: {self.order.id}")
        info_layout.addWidget(article_label)

        status_label = QLabel(f"Статус заказа: {self.order.status or 'Не указан'}")
        info_layout.addWidget(status_label)

        if (
            self.order.pick_up_point_id
            and self.order.pick_up_point_id in self.pick_up_points_dict
        ):
            address = self.pick_up_points_dict[self.order.pick_up_point_id].full_address
            pick_up_text = f"Адрес пункта выдачи: {address}"
        else:
            pick_up_text = "Пункт выдачи не указан"
        pick_up_label = QLabel(pick_up_text)
        info_layout.addWidget(pick_up_label)

        date_text = ""
        if self.order.created_at:
            date_text = self.order.created_at.strftime("%Y-%m-%d %H:%M")
        else:
            date_text = "Не указана"
        date_label = QLabel(f"Дата заказа: {date_text}")
        info_layout.addWidget(date_label)

        info_layout.addStretch()
        main_layout.addWidget(info_panel, stretch=2)

        delivery_panel = QFrame()
        delivery_panel.setFrameStyle(QFrame.Box)
        delivery_panel.setLineWidth(1)
        delivery_layout = QVBoxLayout()
        delivery_panel.setLayout(delivery_layout)

        delivery_label = QLabel("Дата доставки")
        delivery_label.setAlignment(Qt.AlignCenter)
        delivery_layout.addWidget(delivery_label)

        if self.order.delivered_at:
            delivery_date = QLabel(self.order.delivered_at.strftime("%Y-%m-%d %H:%M"))
        else:
            delivery_date = QLabel("Не указана")
        delivery_date.setAlignment(Qt.AlignCenter)
        delivery_layout.addWidget(delivery_date)

        delivery_layout.addStretch()
        main_layout.addWidget(delivery_panel, stretch=1)
        delivery_panel.setMaximumWidth(200)
        delivery_panel.setMinimumWidth(200)

    def apply_styles(self):
        """Применить стили к карточке"""
        self.setStyleSheet(STYLES.get("ORDER_CARD_STYLE", ""))
