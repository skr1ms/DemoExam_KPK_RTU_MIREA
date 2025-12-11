"""
Окно формы для добавления и редактирования заказов (для администратора)
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
    QDateEdit,
)
from frontend.widgets.custom_combo import CustomComboBox
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
import os
from frontend.services.orders_service import OrdersService
from frontend.services.goods_service import GoodsService
from frontend.services.auth_service import AuthService
from frontend.utils.async_helper import run_async_sync
from frontend.utils.styles import STYLES
from backend.internal.entity.order import Order
from backend.internal.entity.user import User
from typing import Optional


class OrderFormWindow(QMainWindow):
    def __init__(
        self,
        orders_service: OrdersService,
        goods_service: GoodsService,
        auth_service: Optional[AuthService] = None,
        order: Optional[Order] = None,
        parent=None,
        user: Optional[User] = None,
    ):
        super().__init__(parent)
        self.orders_service = orders_service
        self.goods_service = goods_service
        self.auth_service = auth_service
        self.order = order
        self.user = user
        self.setup_ui()
        self.apply_styles()
        if self.order:
            self.load_order_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        title = "Редактирование заказа" if self.order else "Добавление заказа"
        self.setWindowTitle(title)
        self.setGeometry(150, 150, 500, 400)

        icon_path = os.path.join("frontend/public", "Icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(STYLES["TITLE_STYLE"])
        layout.addWidget(title_label)

        if self.order:
            article_label = QLabel("Артикул (ID):")
            article_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
            layout.addWidget(article_label)
            self.article_input = QLineEdit()
            self.article_input.setText(str(self.order.id))
            self.article_input.setReadOnly(True)
            self.article_input.setStyleSheet(STYLES["INPUT_STYLE"])
            layout.addWidget(self.article_input)

        status_label = QLabel("Статус заказа:")
        status_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(status_label)
        self.status_combo = CustomComboBox()
        self.status_combo.addItems(
            ["новый", "в обработке", "готов к выдаче", "выдан", "отменен"]
        )
        self.status_combo.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.status_combo)

        user_label = QLabel("Пользователь:")
        user_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(user_label)
        self.user_combo = CustomComboBox()
        self.user_combo.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.user_combo)
        self.load_users()

        pick_up_label = QLabel("Пункт выдачи:")
        pick_up_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(pick_up_label)
        self.pick_up_combo = CustomComboBox()
        self.pick_up_combo.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.pick_up_combo)
        self.load_pick_up_points()

        date_order_label = QLabel("Дата заказа:")
        date_order_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(date_order_label)
        self.date_order_input = QDateEdit()
        self.date_order_input.setCalendarPopup(True)
        self.date_order_input.setDate(QDate.currentDate())
        self.date_order_input.setStyleSheet(STYLES["INPUT_STYLE"])
        self.date_order_input.dateChanged.connect(self.validate_dates)
        layout.addWidget(self.date_order_input)

        date_delivery_label = QLabel("Дата выдачи:")
        date_delivery_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(date_delivery_label)
        self.date_delivery_input = QDateEdit()
        self.date_delivery_input.setCalendarPopup(True)
        self.date_delivery_input.setDate(QDate.currentDate())
        self.date_delivery_input.setStyleSheet(STYLES["INPUT_STYLE"])
        self.date_delivery_input.dateChanged.connect(self.validate_dates)
        layout.addWidget(self.date_delivery_input)

        self.date_error_label = QLabel("")
        self.date_error_label.setStyleSheet(STYLES.get("ERROR_LABEL_STYLE", ""))
        self.date_error_label.setWordWrap(True)
        layout.addWidget(self.date_error_label)

        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        self.save_button.clicked.connect(self.handle_save)
        buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        layout.addStretch()

    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(STYLES["WINDOW_STYLE"])

    def load_users(self):
        """Загрузить список пользователей"""
        if not self.auth_service:
            return
        try:
            users = run_async_sync(self.auth_service.get_all_users())
            self.user_combo.clear()
            self.user_combo.addItem("Выберите пользователя", None)
            for user in users:
                self.user_combo.addItem(f"{user.full_name} ({user.role})", user.id)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при загрузке пользователей: {str(e)}"
            )

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

    def load_order_data(self):
        """Загрузить данные заказа для редактирования"""
        if not self.order:
            return

        if self.order.status:
            index = self.status_combo.findText(self.order.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

        if self.order.user_id:
            index = self.user_combo.findData(self.order.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)

        if self.order.pick_up_point_id:
            index = self.pick_up_combo.findData(self.order.pick_up_point_id)
            if index >= 0:
                self.pick_up_combo.setCurrentIndex(index)

        if self.order.created_at:
            self.date_order_input.setDate(
                QDate.fromString(
                    self.order.created_at.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                )
            )

        if self.order.delivered_at:
            self.date_delivery_input.setDate(
                QDate.fromString(
                    self.order.delivered_at.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                )
            )

    def validate_dates(self):
        """Валидация дат - дата создания не должна быть позже даты выдачи"""
        date_order = self.date_order_input.date().toPython()
        date_delivery = self.date_delivery_input.date().toPython()

        if date_order and date_delivery and date_order > date_delivery:
            self.date_error_label.setText(
                "Дата заказа не может быть позже даты выдачи!"
            )
            self.date_error_label.setVisible(True)
            self.date_delivery_input.setStyleSheet(STYLES.get("INPUT_ERROR_STYLE", ""))
            self.date_order_input.setStyleSheet(STYLES.get("INPUT_ERROR_STYLE", ""))
            return False
        else:
            self.date_error_label.setText("")
            self.date_error_label.setVisible(False)
            self.date_delivery_input.setStyleSheet(STYLES["INPUT_STYLE"])
            self.date_order_input.setStyleSheet(STYLES["INPUT_STYLE"])
            return True

    def handle_save(self):
        """Обработка сохранения"""
        try:
            if not self.validate_dates():
                QMessageBox.warning(
                    self,
                    "Ошибка валидации",
                    "Дата заказа не может быть позже даты выдачи!",
                )
                return

            status = self.status_combo.currentText()
            user_id = self.user_combo.currentData()
            pick_up_point_id = self.pick_up_combo.currentData()
            date_order = self.date_order_input.date().toPython()
            date_delivery = self.date_delivery_input.date().toPython()

            from datetime import datetime

            created_at = (
                datetime.combine(date_order, datetime.min.time())
                if date_order
                else None
            )
            delivered_at = (
                datetime.combine(date_delivery, datetime.min.time())
                if date_delivery
                else None
            )

            if created_at and delivered_at and created_at > delivered_at:
                QMessageBox.warning(
                    self,
                    "Ошибка валидации",
                    "Дата заказа не может быть позже даты выдачи!",
                )
                return

            if self.order:
                updated_order = run_async_sync(
                    self.orders_service.update_order_data(
                        self.order.id,
                        status=status,
                        user_id=user_id,
                        pick_up_point_id=pick_up_point_id,
                        created_at=created_at,
                        delivered_at=delivered_at,
                        items=None,
                        user=self.user,
                    )
                )
                if updated_order:
                    QMessageBox.information(self, "Успех", "Заказ успешно обновлен")
                    self.close()

                    if self.parent():
                        if hasattr(self.parent(), "load_orders"):
                            self.parent().load_orders()
            else:
                created_order = run_async_sync(
                    self.orders_service.create_order_for_admin(
                        status=status,
                        user_id=user_id,
                        pick_up_point_id=pick_up_point_id,
                        created_at=created_at,
                        delivered_at=delivered_at,
                        items=None,
                        user=self.user,
                    )
                )

                if created_order:
                    QMessageBox.information(self, "Успех", "Заказ успешно создан")
                    self.close()

                    if self.parent():
                        if hasattr(self.parent(), "load_orders"):
                            self.parent().load_orders()
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError):
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                QMessageBox.critical(
                    self, "Ошибка", f"Ошибка при сохранении заказа: {str(e)}"
                )
