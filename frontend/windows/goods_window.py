"""
Окно для работы с товарами
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QScrollArea,
    QApplication,
)
from frontend.widgets.custom_combo import CustomComboBox
from PySide6.QtCore import QTimer
from frontend.services.goods_service import GoodsService
from frontend.utils.async_helper import run_async_sync
from frontend.utils.styles import STYLES
from frontend.windows.good_form_window import GoodFormWindow
from frontend.widgets.product_card import ProductCard
from backend.internal.entity.user import User
from backend.internal.entity.good import Good
from typing import Optional


class GoodsWindow(QWidget):
    def __init__(self, goods_service: GoodsService, user: Optional[User] = None):
        super().__init__()
        self.goods_service = goods_service
        self.user = user
        self.goods: list[Good] = []
        self.providers: list[str] = []
        self.current_provider: Optional[str] = None
        self.current_sort: Optional[str] = None
        self.current_search: str = ""
        self._edit_window = None
        self.setup_ui()
        try:
            self.load_providers()
            self.load_goods()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при загрузке товаров: {str(e)}"
            )

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Товары")
        title.setStyleSheet(STYLES["TITLE_STYLE"])
        layout.addWidget(title)

        from backend.internal.usecase.authorization_usecase import AuthorizationUseCase

        can_search = AuthorizationUseCase.can_search_filter_sort_goods(self.user)

        if can_search:
            search_layout = QHBoxLayout()
            search_label = QLabel("Поиск:")
            search_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
            search_layout.addWidget(search_label)

            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Введите текст для поиска")
            self.search_input.textChanged.connect(self.on_filter_changed)
            self.search_input.setStyleSheet(STYLES["INPUT_STYLE"])
            search_layout.addWidget(self.search_input)

            provider_label = QLabel("Поставщик:")
            provider_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
            search_layout.addWidget(provider_label)

            self.provider_combo = CustomComboBox()
            self.provider_combo.addItem("Все поставщики", None)
            self.provider_combo.currentIndexChanged.connect(self.on_filter_changed)
            self.provider_combo.setStyleSheet(STYLES["INPUT_STYLE"])
            search_layout.addWidget(self.provider_combo)

            sort_label = QLabel("Сортировка:")
            sort_label.setStyleSheet(STYLES.get("LABEL_STYLE", ""))
            search_layout.addWidget(sort_label)

            self.sort_combo = CustomComboBox()
            self.sort_combo.addItem("Без сортировки", None)
            self.sort_combo.addItem("По возрастанию", "asc")
            self.sort_combo.addItem("По убыванию", "desc")
            self.sort_combo.setStyleSheet(STYLES["INPUT_STYLE"])
            self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
            search_layout.addWidget(self.sort_combo)

            layout.addLayout(search_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(STYLES["SCROLL_AREA_STYLE"])

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(10)
        self.cards_container.setLayout(self.cards_layout)

        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)

        self.product_cards = []

        buttons_layout = QHBoxLayout()

        if self.user and self.user.role == "Администратор":
            add_button = QPushButton("Добавить товар")
            add_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            add_button.clicked.connect(self.add_good)
            buttons_layout.addWidget(add_button)

            edit_button = QPushButton("Редактировать")
            edit_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            edit_button.clicked.connect(self.edit_good)
            buttons_layout.addWidget(edit_button)

            delete_button = QPushButton("Удалить")
            delete_button.setStyleSheet(STYLES["BUTTON_STYLE"])
            delete_button.clicked.connect(self.delete_good)
            buttons_layout.addWidget(delete_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def load_providers(self):
        """Загрузить список поставщиков"""
        try:
            self.providers = run_async_sync(self.goods_service.get_all_providers())
            if hasattr(self, "provider_combo"):
                current_index = self.provider_combo.currentIndex()
                self.provider_combo.clear()
                self.provider_combo.addItem("Все поставщики", None)
                for provider in sorted(self.providers):
                    self.provider_combo.addItem(provider, provider)

                if current_index >= 0 and current_index < self.provider_combo.count():
                    self.provider_combo.setCurrentIndex(current_index)
        except Exception as e:
            print(f"Ошибка при загрузке поставщиков: {e}")

    def load_goods(self):
        """Загрузить товары с учетом фильтров"""
        try:
            has_search = self.current_search and self.current_search.strip()
            has_provider = self.current_provider is not None
            has_sort = self.current_sort is not None

            has_filters = has_search or has_provider or has_sort

            if has_filters:
                self.goods = run_async_sync(
                    self.goods_service.filter_and_sort(
                        provider=self.current_provider,
                        sort_by_count=self.current_sort,
                        search_query=self.current_search if has_search else None,
                        user=self.user,
                    )
                )
            else:
                self.goods = run_async_sync(self.goods_service.get_all_goods(self.user))

            self.update_table()
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError):
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                QMessageBox.critical(
                    self, "Ошибка", f"Ошибка при загрузке товаров: {str(e)}"
                )

    def update_table(self):
        """Обновить карточки товаров"""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                elif item.spacerItem():
                    del item

        self.product_cards = []

        for good in self.goods:
            on_double_click = None
            if self.user and self.user.role == "Администратор":

                def make_handler(g):
                    return lambda: self.on_card_double_clicked(g)

                on_double_click = make_handler(good)

            card = ProductCard(
                good,
                goods_service=self.goods_service,
                parent=self.cards_container,
                on_double_click=on_double_click,
            )
            self.product_cards.append(card)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

        self.cards_container.update()
        self.scroll_area.update()
        QApplication.processEvents()

        if hasattr(self, "scroll_area"):

            def scroll_to_top():
                scroll_bar = self.scroll_area.verticalScrollBar()
                scroll_bar.setValue(0)

                if self.product_cards:
                    self.scroll_area.ensureWidgetVisible(self.product_cards[0], 0, 0)

            QTimer.singleShot(50, scroll_to_top)

    def on_sort_changed(self, index: int):
        """Обработка изменения сортировки в выпадающем списке"""
        if hasattr(self, "sort_combo"):
            sort_value = self.sort_combo.itemData(index)
            if self.current_sort != sort_value:
                self.current_sort = sort_value
                self.load_goods()

    def set_sort(self, sort_value: Optional[str]):
        """Установить сортировку (программно)"""
        if self.current_sort == sort_value:
            return

        self.current_sort = sort_value
        if hasattr(self, "sort_combo"):
            self.sort_combo.blockSignals(True)
            for i in range(self.sort_combo.count()):
                if self.sort_combo.itemData(i) == sort_value:
                    self.sort_combo.setCurrentIndex(i)
                    break
            self.sort_combo.blockSignals(False)
        self.load_goods()

    def on_filter_changed(self):
        """Обработка изменения фильтров (поиск, поставщик, сортировка)"""
        self.current_search = (
            self.search_input.text() if hasattr(self, "search_input") else ""
        )
        self.current_provider = (
            self.provider_combo.currentData()
            if hasattr(self, "provider_combo")
            else None
        )
        self.load_goods()

    def add_good(self):
        """Добавить товар"""
        try:
            form_window = GoodFormWindow(
                self.goods_service, parent=self, user=self.user
            )
            form_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии формы: {str(e)}")

    def on_card_double_clicked(self, good: Good):
        """Обработка двойного клика на карточку товара"""
        self.edit_good_by_id(good.id)

    def edit_good(self):
        """Редактировать товар (по выбранной карточке)"""
        if self._edit_window is not None and self._edit_window.isVisible():
            QMessageBox.warning(
                self,
                "Ошибка",
                "Окно редактирования уже открыто. Закройте его перед открытием нового.",
            )
            return

        selected_good = None
        for card in self.product_cards:
            if hasattr(card, "_selected") and card._selected:
                selected_good = card.good
                break
        if not selected_good:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для редактирования")
            return

        self.edit_good_by_id(selected_good.id)

    def edit_good_by_id(self, good_id: int):
        """Редактировать товар по ID"""
        if self._edit_window is not None and self._edit_window.isVisible():
            QMessageBox.warning(
                self,
                "Ошибка",
                "Окно редактирования уже открыто. Закройте его перед открытием нового.",
            )
            return

        try:
            good = run_async_sync(self.goods_service.get_good_by_id(good_id))
            if not good:
                QMessageBox.warning(self, "Ошибка", "Товар не найден")
                return
            form_window = GoodFormWindow(
                self.goods_service, good=good, parent=self, user=self.user
            )
            self._edit_window = form_window
            form_window.destroyed.connect(lambda: setattr(self, "_edit_window", None))
            form_window.show()
        except Exception as e:
            from backend.internal.usecase.authorization_usecase import PermissionError

            if isinstance(e, PermissionError):
                QMessageBox.warning(self, "Ошибка доступа", str(e))
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Ошибка при открытии формы редактирования: {str(e)}",
                )

    def delete_good(self):
        """Удалить товар"""
        selected_good = None
        for card in self.product_cards:
            if hasattr(card, "_selected") and card._selected:
                selected_good = card.good
                break
        if not selected_good:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для удаления")
            return

        good = selected_good
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить товар '{good.name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                run_async_sync(self.goods_service.delete_good(good.id, self.user))
                QMessageBox.information(self, "Успех", "Товар удален")
                self.load_goods()
            except Exception as e:
                from backend.internal.usecase.authorization_usecase import (
                    PermissionError,
                )

                if isinstance(e, PermissionError):
                    QMessageBox.warning(self, "Ошибка доступа", str(e))
                else:
                    QMessageBox.critical(
                        self, "Ошибка", f"Ошибка при удалении: {str(e)}"
                    )
