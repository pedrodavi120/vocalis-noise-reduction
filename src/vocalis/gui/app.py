import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QPixmap, QColor

from vocalis.gui.styles import (
    STYLESHEET, resource_path, COLOR_PRIMARY
)
from vocalis.gui.components import NotificationPopup
from vocalis.gui.tabs.recorder_tab import RecorderTab
from vocalis.gui.tabs.file_tab import FileTab
from vocalis.gui.tabs.realtime_tab import RealtimeTab


class VocalisMainWindow(QMainWindow):
    """
    Janela Principal do Vocalis Studio.
    """

    def __init__(self):
        super().__init__()
        self.oldPos = None

        self.setWindowTitle("Vocalis Studio")
        self.setFixedSize(540, 710)
        self.setObjectName("JanelaPrincipal")

        # Janela moderna sem bordas do SO
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()
        self.setStyleSheet(STYLESHEET)

    def _build_ui(self):
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.setCentralWidget(self.central_widget)

        # Card Principal com Sombra
        self.main_container = QFrame()
        self.main_container.setObjectName("MainContainer")
        self.container_layout = QVBoxLayout(self.main_container)
        self.container_layout.setContentsMargins(24, 16, 24, 24)
        self.container_layout.setSpacing(14)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 5)
        self.main_container.setGraphicsEffect(shadow)
        self.main_layout.addWidget(self.main_container)

        # Barra de Título (macOS style)
        self._build_title_bar()

        # Logo Header
        self._build_logo()

        # Barra de Navegação por Abas
        self._build_tab_nav()

        # Stack de Conteúdo
        self.tabs_stack = QStackedWidget()
        self.recorder_tab = RecorderTab(self)
        self.file_tab = FileTab(self)
        self.realtime_tab = RealtimeTab(self)

        self.tabs_stack.addWidget(self.recorder_tab)
        self.tabs_stack.addWidget(self.file_tab)
        self.tabs_stack.addWidget(self.realtime_tab)
        self.container_layout.addWidget(self.tabs_stack)

        # Pop-up de Notificação
        self.notification_popup = NotificationPopup(self.main_container)

        # Conexões de notificação
        self.recorder_tab.signals.show_notification.connect(self.show_notification)
        self.file_tab.signals.show_notification.connect(self.show_notification)
        self.realtime_tab.signals.notification_requested.connect(self.show_notification)

    def _build_title_bar(self):
        title_bar = QFrame()
        title_bar.setObjectName("TitleBar")
        t_layout = QHBoxLayout(title_bar)
        t_layout.setContentsMargins(4, 2, 4, 4)
        t_layout.setSpacing(8)

        # Controles clássicos do macOS (Traffic Lights) à esquerda
        btn_close = QPushButton("×")
        btn_close.setObjectName("MacCloseButton")
        btn_close.setFixedSize(12, 12)
        btn_close.setToolTip("Fechar")
        btn_close.clicked.connect(self.close)

        btn_min = QPushButton("–")
        btn_min.setObjectName("MacMinimizeButton")
        btn_min.setFixedSize(12, 12)
        btn_min.setToolTip("Minimizar")
        btn_min.clicked.connect(self.showMinimized)

        btn_zoom = QPushButton("+")
        btn_zoom.setObjectName("MacZoomButton")
        btn_zoom.setFixedSize(12, 12)
        btn_zoom.setToolTip("Ajustar")

        t_layout.addWidget(btn_close)
        t_layout.addWidget(btn_min)
        t_layout.addWidget(btn_zoom)
        t_layout.addStretch()

        self.container_layout.addWidget(title_bar)

    def _build_logo(self):
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = resource_path("logo.png")
        pixmap = QPixmap(logo_path)

        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(
                230, 58,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            logo_label.setText("Vocalis")
            logo_label.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {COLOR_PRIMARY};")

        self.container_layout.addWidget(logo_label)

    def _build_tab_nav(self):
        nav_frame = QFrame()
        nav_frame.setObjectName("TabNav")
        n_layout = QHBoxLayout(nav_frame)
        n_layout.setContentsMargins(4, 4, 4, 4)
        n_layout.setSpacing(6)

        self.btn_tab_rec = QPushButton("Gravação Rápida")
        self.btn_tab_rec.setProperty("class", "NavTabButton")
        self.btn_tab_rec.setProperty("active", True)
        self.btn_tab_rec.clicked.connect(lambda: self.switch_tab(0))

        self.btn_tab_file = QPushButton("Limpar Arquivo")
        self.btn_tab_file.setProperty("class", "NavTabButton")
        self.btn_tab_file.setProperty("active", False)
        self.btn_tab_file.clicked.connect(lambda: self.switch_tab(1))

        self.btn_tab_realtime = QPushButton("Tempo Real")
        self.btn_tab_realtime.setProperty("class", "NavTabButton")
        self.btn_tab_realtime.setProperty("active", False)
        self.btn_tab_realtime.clicked.connect(lambda: self.switch_tab(2))

        n_layout.addWidget(self.btn_tab_rec)
        n_layout.addWidget(self.btn_tab_file)
        n_layout.addWidget(self.btn_tab_realtime)

        self.tab_buttons = [self.btn_tab_rec, self.btn_tab_file, self.btn_tab_realtime]
        self.container_layout.addWidget(nav_frame)

    def switch_tab(self, index: int):
        self.tabs_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            btn.setProperty("active", i == index)
            btn.style().polish(btn)

    def show_notification(self, msg: str):
        self.notification_popup.show_notification(msg)

    def closeEvent(self, event):
        # Limpa recursos de áudio e nós de loopback
        if hasattr(self, 'realtime_tab'):
            self.realtime_tab.cleanup()
        super().closeEvent(event)

    # Arrastar janela sem borda
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            interactive = (QPushButton, QFrame)
            is_interactive = False
            curr = child
            while curr:
                if isinstance(curr, QPushButton):
                    is_interactive = True
                    break
                curr = curr.parent()
            if not is_interactive:
                self.oldPos = event.globalPosition().toPoint()
            else:
                self.oldPos = None

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.oldPos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
