"""
Виджет карточки товара согласно макету product_card.png
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame, QWidget
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from backend.internal.entity.good import Good
from frontend.utils.styles import STYLES
from frontend.services.goods_service import GoodsService
import os


class ProductCard(QFrame):
    def __init__(
        self,
        good: Good,
        goods_service: GoodsService = None,
        parent=None,
        on_double_click=None,
    ):
        super().__init__(parent)
        self.good = good
        self.goods_service = goods_service
        self.on_double_click = on_double_click
        self._selected = False
        self.setup_ui()
        self.apply_styles()

    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика"""
        if self.on_double_click:
            try:
                self.on_double_click()
            except TypeError:
                self.on_double_click(self.good)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """Обработка клика для выбора карточки"""
        self._selected = True

        if self.parent():
            for child in self.parent().findChildren(ProductCard):
                if child != self:
                    child._selected = False
                    child.update_selection_style()
        self.update_selection_style()
        super().mousePressEvent(event)

    def update_selection_style(self):
        """Обновить стиль в зависимости от выбора"""
        if self._selected:
            base_style = self._get_base_style()
            selected_style = STYLES.get("PRODUCT_CARD_SELECTED_STYLE", "")
            self.setStyleSheet(base_style + selected_style)
        else:
            self.apply_styles()

    def _get_base_style(self):
        """Получить базовый стиль в зависимости от состояния товара"""
        if self.good.discount and float(self.good.discount) > 15:
            return STYLES.get("PRODUCT_CARD_DISCOUNT_STYLE", "")
        else:
            return STYLES.get("PRODUCT_CARD_STYLE", "")

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        photo_panel = QFrame()
        photo_panel.setFrameStyle(QFrame.Box)
        photo_panel.setLineWidth(2)
        photo_layout = QVBoxLayout()
        photo_panel.setLayout(photo_layout)

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumSize(150, 150)
        self.photo_label.setMaximumSize(150, 150)
        self.load_photo()
        photo_layout.addWidget(self.photo_label)

        main_layout.addWidget(photo_panel)

        info_panel = QFrame()
        info_panel.setFrameStyle(QFrame.Box)
        info_panel.setLineWidth(1)
        info_layout = QVBoxLayout()
        info_panel.setLayout(info_layout)

        name_label = QLabel(f"{self.good.category or ''} | {self.good.name}")
        name_label.setStyleSheet(STYLES.get("PRODUCT_CARD_NAME_STYLE", ""))
        info_layout.addWidget(name_label)

        if self.good.description:
            desc_label = QLabel(f"Описание товара: {self.good.description}")
            info_layout.addWidget(desc_label)

        if self.good.manufacturer:
            manufacturer_label = QLabel(f"Производитель: {self.good.manufacturer}")
            info_layout.addWidget(manufacturer_label)

        if self.good.provider:
            provider_label = QLabel(f"Поставщик: {self.good.provider}")
            info_layout.addWidget(provider_label)

        price_label = QLabel("Цена:")
        info_layout.addWidget(price_label)
        price_value_label = self.format_price()
        info_layout.addWidget(price_value_label)

        unit_label = QLabel(f"Единица измерения: {self.good.unit_of_measurement}")
        info_layout.addWidget(unit_label)

        self.count_label = QLabel(f"Количество на складе: {self.good.count}")
        if self.good.count == 0:
            self.count_label.setStyleSheet(
                STYLES.get("PRODUCT_CARD_COUNT_ZERO_STYLE", "")
            )
        info_layout.addWidget(self.count_label)

        info_layout.addStretch()
        main_layout.addWidget(info_panel, stretch=1)

        discount_panel = QFrame()
        discount_panel.setFrameStyle(QFrame.Box)
        discount_panel.setLineWidth(2)
        discount_layout = QVBoxLayout()
        discount_panel.setLayout(discount_layout)

        discount_label = QLabel("Действующая скидка")
        discount_label.setAlignment(Qt.AlignCenter)
        discount_layout.addWidget(discount_label)

        if self.good.discount and float(self.good.discount) > 0:
            discount_value = QLabel(f"{float(self.good.discount)}%")
            discount_value.setAlignment(Qt.AlignCenter)
            discount_value.setStyleSheet(
                STYLES.get("PRODUCT_CARD_DISCOUNT_VALUE_STYLE", "")
            )
            discount_layout.addWidget(discount_value)
        else:
            no_discount = QLabel("Нет")
            no_discount.setAlignment(Qt.AlignCenter)
            discount_layout.addWidget(no_discount)

        discount_layout.addStretch()
        main_layout.addWidget(discount_panel)
        discount_panel.setMaximumWidth(150)
        discount_panel.setMinimumWidth(150)

    def load_photo(self):
        """Загрузить фото товара или заглушку"""
        if self.good.image:
            image_path = self.good.image

            if "temp" in image_path:
                image_path = image_path.replace("temp/", "").replace("temp\\", "")
            if not os.path.isabs(image_path):
                image_path = os.path.join("frontend/public", image_path)

            if not os.path.exists(image_path):
                filename = os.path.basename(image_path)
                image_path = os.path.join("frontend/public", filename)

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.photo_label.setPixmap(pixmap)
                    return

        placeholder_path = os.path.join("frontend/public", "picture.png")
        if os.path.exists(placeholder_path):
            pixmap = QPixmap(placeholder_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("Фото")

    def format_price(self):
        """Форматировать цену с учетом скидки"""
        price_container = QHBoxLayout()
        price_widget = QWidget()
        price_widget.setLayout(price_container)

        original_price = float(self.good.price)

        if not self.goods_service:
            final_price = original_price
        else:
            final_price = self.goods_service.calculate_price_with_discount(
                original_price, self.good.discount
            )

        if self.good.discount and float(self.good.discount) > 0:
            original_label = QLabel(f"{original_price:.2f}")
            font = QFont()
            font.setStrikeOut(True)
            original_label.setFont(font)
            original_label.setStyleSheet(
                STYLES.get("PRODUCT_CARD_PRICE_DISCOUNTED_STYLE", "")
            )
            price_container.addWidget(original_label)

            final_label = QLabel(f"{final_price:.2f}")
            final_label.setStyleSheet(STYLES.get("PRODUCT_CARD_PRICE_NORMAL_STYLE", ""))
            price_container.addWidget(final_label)
        else:
            price_label = QLabel(str(final_price))
            price_label.setStyleSheet(STYLES.get("PRODUCT_CARD_PRICE_NORMAL_STYLE", ""))
            price_container.addWidget(price_label)

        price_container.addStretch()
        return price_widget

    def apply_styles(self):
        """Применить стили к карточке"""
        self.setStyleSheet(self._get_base_style())
