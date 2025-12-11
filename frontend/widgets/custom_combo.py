"""
Кастомный QComboBox с изменяющейся стрелкой
"""

from PySide6.QtWidgets import QComboBox, QStyle, QStyleOptionComboBox
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPolygon


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_open = False
        self._base_style = None
        self.view().installEventFilter(self)

    def setStyleSheet(self, style):
        self._base_style = style
        base_style = style
        if "QComboBox::down-arrow" in base_style:
            parts = base_style.split("QComboBox::down-arrow")
            base_style = parts[0]
            if len(parts) > 1:
                remaining = parts[1]
                if "}" in remaining:
                    remaining = remaining.split("}", 1)[1]
                base_style += remaining
        super().setStyleSheet(base_style)

    def eventFilter(self, obj, event):
        if obj == self.view():
            if event.type() == event.Type.Hide:
                self._is_open = False
                self.update()
        return super().eventFilter(obj, event)

    def showPopup(self):
        self._is_open = True
        super().showPopup()
        self.update()

    def hidePopup(self):
        self._is_open = False
        super().hidePopup()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)

        arrow_rect = self.style().subControlRect(
            QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, self
        )

        if arrow_rect.isValid():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            center_x = arrow_rect.center().x()
            center_y = arrow_rect.center().y()

            if self._is_open:
                points = [
                    QPoint(center_x - 5, center_y + 2),
                    QPoint(center_x, center_y - 3),
                    QPoint(center_x + 5, center_y + 2),
                ]
            else:
                points = [
                    QPoint(center_x - 5, center_y - 2),
                    QPoint(center_x, center_y + 3),
                    QPoint(center_x + 5, center_y - 2),
                ]

            polygon = QPolygon(points)
            painter.setBrush(Qt.black)
            painter.setPen(Qt.NoPen)
            painter.drawPolygon(polygon)
