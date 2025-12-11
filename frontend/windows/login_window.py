"""
Окно авторизации
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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from frontend.services.auth_service import AuthService
from frontend.utils.async_helper import run_async_sync
from frontend.utils.styles import STYLES
from backend.internal.entity.user import User
import os


class LoginWindow(QMainWindow):
    def __init__(self, auth_service: AuthService, on_success=None):
        super().__init__()
        self.auth_service = auth_service
        self.on_success = on_success
        self.current_user: User = None
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 300)

        icon_path = os.path.join("frontend/public", "Icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(STYLES["TITLE_STYLE"])
        layout.addWidget(title)

        login_label = QLabel("Логин:")
        login_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(login_label)
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.login_input)

        password_label = QLabel("Пароль:")
        password_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.password_input)

        buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        self.register_button.clicked.connect(self.handle_register)
        buttons_layout.addWidget(self.register_button)

        layout.addLayout(buttons_layout)

        guest_button = QPushButton("Войти как гость")
        guest_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        guest_button.clicked.connect(self.handle_guest)
        layout.addWidget(guest_button)

        layout.addStretch()

        self.setStyleSheet(STYLES["WINDOW_STYLE"])

    def handle_login(self):
        """Обработка входа"""
        login = self.login_input.text().strip()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            user = run_async_sync(self.auth_service.login(login, password))
            if user:
                self.current_user = user
                QMessageBox.information(
                    self, "Успех", f"Добро пожаловать, {user.full_name}!"
                )
                if self.on_success:
                    main_window = self.on_success(user)
                    if main_window:
                        self.hide()
                    else:
                        pass
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при входе: {str(e)}")

    def handle_register(self):
        """Обработка регистрации"""
        from frontend.windows.register_window import RegisterWindow

        register_window = RegisterWindow(self.auth_service, self)
        register_window.show()

    def handle_guest(self):
        """Обработка входа как гость"""
        if self.on_success:
            from backend.internal.entity.user import User

            guest_user = User(
                role="Гость", full_name="Гость", login="guest", password=""
            )
            guest_user.id = 0
            main_window = self.on_success(guest_user)
            if main_window:
                self.hide()
