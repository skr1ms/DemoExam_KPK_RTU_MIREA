"""
Главное окно приложения
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from backend.internal.entity.user import User
from frontend.services.goods_service import GoodsService
from frontend.services.orders_service import OrdersService
from frontend.services.auth_service import AuthService
from frontend.windows.goods_window import GoodsWindow
from frontend.windows.orders_window import OrdersWindow
from frontend.utils.styles import STYLES
import os


class MainWindow(QMainWindow):
    def __init__(
        self,
        user: User,
        goods_service: GoodsService,
        orders_service: OrdersService,
        auth_service: AuthService = None,
        on_logout=None,
    ):
        super().__init__()
        self.user = user
        self.goods_service = goods_service
        self.orders_service = orders_service
        self.auth_service = auth_service
        self.on_logout = on_logout
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Магазин одежды ООО «Обувь»")
        self.setGeometry(100, 100, 1200, 800)

        icon_path = os.path.join("frontend/public", "Icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        header_container = QVBoxLayout()

        top_header = QHBoxLayout()

        logo_label = QLabel()
        logo_path = os.path.join("frontend/public", "Icon.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                max_size = 80
                if pixmap.width() > max_size or pixmap.height() > max_size:
                    pixmap = pixmap.scaled(
                        max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                logo_label.setPixmap(pixmap)
        top_header.addWidget(logo_label)

        shop_name = QLabel("ООО «Обувь»")
        shop_name.setStyleSheet(STYLES["TITLE_STYLE"])
        top_header.addWidget(shop_name)

        top_header.addStretch()

        user_info = QLabel(f"{self.user.full_name} ({self.user.role})")
        user_info.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        top_header.addWidget(user_info)

        logout_button = QPushButton("Выйти")
        logout_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        logout_button.clicked.connect(self.handle_logout)
        top_header.addWidget(logout_button)

        header_container.addLayout(top_header)

        welcome_label = QLabel(f"Добро пожаловать, {self.user.full_name}!")
        welcome_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        header_container.addWidget(welcome_label)

        layout.addLayout(header_container)

        self.setStyleSheet(STYLES["WINDOW_STYLE"])

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(STYLES.get("TAB_STYLE", ""))

        self.goods_window = GoodsWindow(self.goods_service, self.user)
        self.tabs.addTab(self.goods_window, "Товары")

        if self.user.role in ["Менеджер", "Администратор"]:
            self.orders_window = OrdersWindow(
                self.orders_service, self.goods_service, self.user, self.auth_service
            )
            self.tabs.addTab(self.orders_window, "Заказы")

        layout.addWidget(self.tabs)

    def handle_logout(self):
        """Обработка выхода из системы"""
        reply = QMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.close()
            if self.on_logout:
                self.on_logout()
