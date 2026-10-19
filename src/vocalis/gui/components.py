import math
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFrame, QHBoxLayout,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
)
from PySide6.QtGui import (
    QPainter, QColor, QLinearGradient
)
from vocalis.gui.styles import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_RECORDING,
    COLOR_CARD, COLOR_SUCCESS
)


class AnimatedButton(QPushButton):
    def __init__(self, text: str, shadow_color: QColor = QColor(159, 85, 255), parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(46)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow_color = shadow_color
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(159, 85, 255, 90))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)

        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius", self)
        self.shadow_anim.setDuration(160)
        self.shadow_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        self.shadow_anim.setStartValue(self.shadow.blurRadius())
        self.shadow_anim.setEndValue(18)
        self.shadow_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shadow_anim.setStartValue(self.shadow.blurRadius())
        self.shadow_anim.setEndValue(10)
        self.shadow_anim.start()
        super().leaveEvent(event)


class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.anim_step = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pulse)
        self.setMinimumHeight(90)

        self.idle_color_top = QColor(COLOR_PRIMARY_LIGHT)
        self.idle_color_bottom = QColor(COLOR_PRIMARY)
        self.record_color_top = QColor(255, 100, 0, 255)
        self.record_color_bottom = QColor(200, 50, 0, 255)

        self.freqs = [0.08, 0.1, 0.07, 0.09, 0.06]
        self.offsets = [0, 1.2, 0.7, 1.0, 0.4]
        self.min_height = 8.0
        self.max_height = 60.0

        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setOffset(0, 2)
        self.shadow_effect.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self.shadow_effect)

    def start(self):
        self.anim_step = 0
        self.timer.start(16)

    def stop(self):
        self.timer.stop()
        self.update()

    def update_pulse(self):
        self.anim_step += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.PenStyle.NoPen)

        is_active = self.timer.isActive()
        num_bars = 5
        total_width = self.width() * 0.6
        bar_width = total_width / (num_bars * 2 - 1)
        spacing = bar_width

        start_x = (self.width() - total_width) / 2
        bottom_y = self.height() - 10

        for i in range(num_bars):
            if is_active:
                cycle = self.anim_step * self.freqs[i] + self.offsets[i]
                height_ratio = (math.sin(cycle) + 1) / 2
                bar_height = self.min_height + height_ratio * (self.max_height - self.min_height)
                top_c = self.record_color_top
                bot_c = self.record_color_bottom
            else:
                bar_height = self.min_height
                top_c = self.idle_color_top
                bot_c = self.idle_color_bottom

            bar_x = start_x + i * (bar_width + spacing)
            gradient = QLinearGradient(bar_x, bottom_y - bar_height, bar_x, bottom_y)
            gradient.setColorAt(0.0, top_c)
            gradient.setColorAt(1.0, bot_c)
            painter.setBrush(gradient)

            rect_radius = bar_width / 2
            painter.drawRoundedRect(
                int(bar_x),
                int(bottom_y - bar_height),
                int(bar_width),
                int(bar_height),
                int(rect_radius),
                int(rect_radius)
            )


class NotificationPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationPopup")
        self.setFixedSize(300, 44)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(self.label)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)

        self.hide()
        self.setWindowOpacity(0.0)

        self.show_anim = QPropertyAnimation(self, b"geometry", self)
        self.show_anim.setDuration(250)
        self.show_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.opacity_anim.setDuration(250)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def show_notification(self, message: str):
        self.label.setText(message)
        parent_width = self.parent().width() if self.parent() else 500
        start_x = (parent_width - self.width()) // 2
        start_y = 5
        end_y = 45

        self.show_anim.setStartValue(QRect(start_x, start_y, self.width(), self.height()))
        self.show_anim.setEndValue(QRect(start_x, end_y, self.width(), self.height()))

        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)

        self.show()
        self.show_anim.start()
        self.opacity_anim.start()
        self.hide_timer.start(2500)

    def hide_notification(self):
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.start()
        self.opacity_anim.finished.connect(self.hide)
