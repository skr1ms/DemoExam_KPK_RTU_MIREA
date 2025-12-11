"""
Окно формы для добавления и редактирования товаров
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
    QTextEdit,
    QDoubleSpinBox,
    QSpinBox,
    QFileDialog,
)
from frontend.widgets.custom_combo import CustomComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from frontend.services.goods_service import GoodsService
from frontend.utils.async_helper import run_async_sync
from frontend.utils.styles import STYLES
from backend.internal.entity.good import Good
from backend.internal.entity.user import User
from typing import Optional
import os
import shutil


class GoodFormWindow(QMainWindow):
    def __init__(
        self,
        goods_service: GoodsService,
        good: Good = None,
        parent=None,
        user: Optional[User] = None,
    ):
        super().__init__(parent)
        self.goods_service = goods_service
        self.good = good
        self.user = user
        self.is_edit_mode = good is not None
        self.image_path = None
        self.categories: list[str] = []
        self.manufacturers: list[str] = []
        self.setup_ui()
        self.apply_styles()
        self.load_categories_and_manufacturers()

        if self.is_edit_mode:
            self.load_good_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        title = "Редактирование товара" if self.is_edit_mode else "Добавление товара"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 700, 900)

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

        if self.is_edit_mode:
            id_label = QLabel("ID товара:")
            id_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
            layout.addWidget(id_label)
            self.id_input = QLineEdit()
            self.id_input.setText(str(self.good.id))
            self.id_input.setReadOnly(True)
            self.id_input.setStyleSheet(STYLES["INPUT_STYLE"])
            layout.addWidget(self.id_input)

        article_label = QLabel("Артикул *:")
        article_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(article_label)
        self.article_input = QLineEdit()
        self.article_input.setPlaceholderText("Введите артикул")
        self.article_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.article_input)

        name_label = QLabel("Название *:")
        name_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название товара")
        self.name_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.name_input)

        unit_label = QLabel("Единица измерения *:")
        unit_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(unit_label)
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("шт, кг, л и т.д.")
        self.unit_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.unit_input)

        price_label = QLabel("Цена *:")
        price_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(price_label)
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.price_input)

        count_label = QLabel("Количество:")
        count_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(count_label)
        self.count_input = QSpinBox()
        self.count_input.setMinimum(0)
        self.count_input.setMaximum(999999)
        self.count_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.count_input)

        provider_label = QLabel("Поставщик:")
        provider_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(provider_label)
        self.provider_input = QLineEdit()
        self.provider_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.provider_input)

        manufacturer_label = QLabel("Производитель:")
        manufacturer_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(manufacturer_label)
        self.manufacturer_combo = CustomComboBox()
        self.manufacturer_combo.setEditable(True)
        self.manufacturer_combo.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.manufacturer_combo)

        category_label = QLabel("Категория:")
        category_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(category_label)
        self.category_combo = CustomComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.category_combo)

        discount_label = QLabel("Скидка (%):")
        discount_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(discount_label)
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(100)
        self.discount_input.setDecimals(2)
        self.discount_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.discount_input)

        description_label = QLabel("Описание:")
        description_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        layout.addWidget(description_label)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet(STYLES["INPUT_STYLE"])
        layout.addWidget(self.description_input)

        image_layout = QHBoxLayout()
        image_label = QLabel("Изображение:")
        image_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        image_layout.addWidget(image_label)

        self.image_path_label = QLabel("Не выбрано")
        self.image_path_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
        image_layout.addWidget(self.image_path_label)

        browse_button = QPushButton("Выбрать файл")
        browse_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        browse_button.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_button)

        layout.addLayout(image_layout)

        buttons_layout = QHBoxLayout()

        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        save_button.clicked.connect(self.save_good)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet(STYLES["BUTTON_STYLE"])
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        layout.addStretch()

    def load_categories_and_manufacturers(self):
        """Загрузить списки категорий и производителей"""
        from frontend.utils.async_helper import run_async_sync

        try:
            self.categories = run_async_sync(self.goods_service.get_all_categories())
            self.manufacturers = run_async_sync(
                self.goods_service.get_all_manufacturers()
            )

            self.category_combo.clear()
            for category in sorted(self.categories):
                self.category_combo.addItem(category)

            self.manufacturer_combo.clear()
            for manufacturer in sorted(self.manufacturers):
                self.manufacturer_combo.addItem(manufacturer)
        except Exception as e:
            print(f"Ошибка при загрузке категорий и производителей: {e}")

    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(STYLES["WINDOW_STYLE"])
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(STYLES["BUTTON_STYLE"])

        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(STYLES["INPUT_STYLE"])
        for widget in self.findChildren(QTextEdit):
            widget.setStyleSheet(STYLES["INPUT_STYLE"])
        for widget in self.findChildren(QDoubleSpinBox):
            widget.setStyleSheet(STYLES["INPUT_STYLE"])
        for widget in self.findChildren(QSpinBox):
            widget.setStyleSheet(STYLES["INPUT_STYLE"])
        for widget in self.findChildren(CustomComboBox):
            widget.setStyleSheet(STYLES["INPUT_STYLE"])

    def load_good_data(self):
        """Загрузить данные товара для редактирования"""
        if not self.good:
            return

        self.article_input.setText(self.good.article)
        self.name_input.setText(self.good.name)
        self.unit_input.setText(self.good.unit_of_measurement)
        self.price_input.setValue(float(self.good.price))
        self.count_input.setValue(self.good.count)
        self.provider_input.setText(self.good.provider or "")

        if self.good.manufacturer:
            index = self.manufacturer_combo.findText(self.good.manufacturer)
            if index >= 0:
                self.manufacturer_combo.setCurrentIndex(index)
            else:
                self.manufacturer_combo.setCurrentText(self.good.manufacturer)

        if self.good.category:
            index = self.category_combo.findText(self.good.category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentText(self.good.category)
        self.discount_input.setValue(
            float(self.good.discount) if self.good.discount else 0
        )
        self.description_input.setPlainText(self.good.description or "")

        if self.good.image:
            self.image_path = self.good.image
            self.image_path_label.setText(os.path.basename(self.good.image))

    def browse_image(self):
        """Выбрать файл изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "frontend/public",
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
        )

        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                width = pixmap.width()
                height = pixmap.height()
                if width != 300 or height != 200:
                    reply = QMessageBox.question(
                        self,
                        "Размер изображения",
                        f"Изображение имеет размер {width}x{height} пикселей.\n"
                        f"Требуется размер 300x200 пикселей.\n"
                        f"Изменить размер автоматически?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        pixmap = pixmap.scaled(
                            300,
                            200,
                            Qt.KeepAspectRatioByExpanding,
                            Qt.SmoothTransformation,
                        )
                        app_image_dir = "frontend/public"
                        os.makedirs(app_image_dir, exist_ok=True)
                        original_name = os.path.basename(file_path)
                        final_path = os.path.join(app_image_dir, original_name)
                        pixmap.save(final_path)
                        file_path = final_path
                    else:
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            "Изображение должно иметь размер 300x200 пикселей",
                        )
                        return

            self.image_path = file_path
            self.image_path_label.setText(os.path.basename(file_path))

    def save_good(self):
        """Сохранить товар"""
        if not self.article_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите артикул")
            return

        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название")
            return

        if not self.unit_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите единицу измерения")
            return

        try:
            article = self.article_input.text().strip()
            name = self.name_input.text().strip()
            unit = self.unit_input.text().strip()
            price = self.price_input.value()
            count = self.count_input.value()
            provider = self.provider_input.text().strip() or None
            manufacturer = self.manufacturer_combo.currentText().strip() or None
            category = self.category_combo.currentText().strip() or None
            discount = (
                self.discount_input.value() if self.discount_input.value() > 0 else None
            )
            description = self.description_input.toPlainText().strip() or None
            old_image_path = None
            if self.is_edit_mode and self.good.image:
                old_image_path = self.good.image
            final_image_path = None
            if self.image_path:
                if os.path.exists(self.image_path):
                    app_image_dir = "frontend/public"
                    os.makedirs(app_image_dir, exist_ok=True)
                    normalized_path = os.path.normpath(self.image_path)
                    normalized_public = os.path.normpath(app_image_dir)
                    image_filename = os.path.basename(self.image_path)
                    if (
                        normalized_path.startswith(normalized_public)
                        and "temp" not in normalized_path
                    ):
                        final_image_path = image_filename
                    else:
                        final_image_path_full = os.path.join(
                            app_image_dir, image_filename
                        )
                        shutil.copy2(self.image_path, final_image_path_full)
                        final_image_path = image_filename
                        if "temp" in normalized_path:
                            try:
                                os.remove(self.image_path)
                            except Exception as e:
                                print(f"Ошибка при удалении временного файла: {e}")
            if self.is_edit_mode:
                if (
                    final_image_path
                    and old_image_path
                    and old_image_path != final_image_path
                ):
                    old_full_path = os.path.join("frontend/public", old_image_path)
                    if os.path.exists(old_full_path):
                        try:
                            os.remove(old_full_path)
                        except Exception as e:
                            print(f"Ошибка при удалении старого изображения: {e}")
                run_async_sync(
                    self.goods_service.update_good_data(
                        self.good.id,
                        article,
                        name,
                        unit,
                        price,
                        provider,
                        manufacturer,
                        category,
                        discount,
                        count,
                        description,
                        final_image_path,
                        self.user,
                    )
                )
                QMessageBox.information(self, "Успех", "Товар обновлен")
            else:
                run_async_sync(
                    self.goods_service.create_good(
                        article,
                        name,
                        unit,
                        price,
                        provider,
                        manufacturer,
                        category,
                        discount,
                        count,
                        description,
                        final_image_path,
                        self.user,
                    )
                )
                QMessageBox.information(self, "Успех", "Товар добавлен")

            self.close()
            if self.parent():
                self.parent().load_goods()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError) or type(e).__name__ == "PermissionError":
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                error_msg = (
                    f"Ошибка при сохранении: {str(e)}\nТип ошибки: {type(e).__name__}"
                )
                QMessageBox.critical(self, "Ошибка", error_msg)
