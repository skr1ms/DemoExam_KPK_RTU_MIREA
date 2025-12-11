"""
Окно регистрации нового пользователя
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
from backend.pkg.validator.email_validator import EmailValidator
from backend.pkg.validator.full_name_validator import FullNameValidator
from backend.pkg.validator.password_validator import PasswordValidator
import os


class RegisterWindow(QMainWindow):
    def __init__(self, auth_service: AuthService, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Регистрация")
        self.setGeometry(150, 150, 400, 400)

        icon_path = os.path.join("frontend/public", "Icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(STYLES["TITLE_STYLE"])
        layout.addWidget(title)

        name_label = QLabel("ФИО:")
        name_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ФИО")
        self.name_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.name_input)

        login_label = QLabel("Логин (email):")
        login_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(login_label)
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText(
            "Введите email (например: user@example.com)"
        )
        self.login_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.login_input)

        password_label = QLabel("Пароль (минимум 6 символов):")
        password_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль (минимум 6 символов)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.password_input)

        confirm_label = QLabel("Подтвердите пароль:")
        confirm_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(confirm_label)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Подтвердите пароль")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.confirm_input)

        buttons_layout = QHBoxLayout()

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        self.register_button.clicked.connect(self.handle_register)
        buttons_layout.addWidget(self.register_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.setStyleSheet(STYLES["WINDOW_STYLE"])

    def handle_register(self):
        """Обработка регистрации"""
        full_name = self.name_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        role = "Авторизированный клиент"

        is_valid, error_msg = FullNameValidator.validate(full_name)
        if not is_valid:
            QMessageBox.warning(self, "Ошибка валидации ФИО", error_msg)
            self.name_input.setFocus()
            return

        is_valid, error_msg = EmailValidator.validate(login)
        if not is_valid:
            QMessageBox.warning(self, "Ошибка валидации логина", error_msg)
            self.login_input.setFocus()
            return

        is_valid, error_msg = PasswordValidator.validate(password)
        if not is_valid:
            QMessageBox.warning(self, "Ошибка валидации пароля", error_msg)
            self.password_input.setFocus()
            return

        is_valid, error_msg = PasswordValidator.validate_confirmation(password, confirm)
        if not is_valid:
            QMessageBox.warning(self, "Ошибка подтверждения пароля", error_msg)
            self.confirm_input.setFocus()
            return

        try:
            run_async_sync(self.auth_service.register(login, password, full_name, role))
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка регистрации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при регистрации: {str(e)}")
