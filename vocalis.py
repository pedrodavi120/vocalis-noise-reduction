import sys
import os
import threading
import math
import numpy as np
import sounddevice as sd
import soundfile as sf
import noisereduce as nr

# Importa o PySide6
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QProgressBar, QStackedWidget,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QObject, Slot, QPoint,
    QPropertyAnimation, QEasingCurve, QRect
)
from PySide6.QtGui import (
    QIcon, QPainter, QPixmap, QColor, QFont,
    QLinearGradient
)

# --- Constantes ---
FILENAME_ORIGINAL = "gravacao_original.wav"
FILENAME_CLEAN = "gravacao_limpa.wav"
SAMPLE_RATE = 44100  # Taxa de amostragem padrão

# --- [PALETA] Tema "Clean White" ---
COLOR_BG = "transparent"     # Fundo da janela principal (transparente)
COLOR_CARD = "#FFFFFF"       # Cor do cartão principal (branco)
COLOR_PRIMARY = "#9F55FF"   # Roxo/Magenta vibrante (cor de destaque)
COLOR_PRIMARY_LIGHT = "#B57FFF" # Roxo mais claro (para gradiente)
COLOR_ACCENT = "#D0A0FF"    # Roxo ainda mais claro (hover para playback)
COLOR_TEXT = "#111111"       # Texto principal (preto)
COLOR_TEXT_SECONDARY = "#666666" # Texto do status (cinza escuro)
COLOR_BORDER = "#EEEEEE"    # Borda sutil (para progresso)
COLOR_RECORDING = "#FF4500"    # Laranja/Vermelho (Estado de gravação)
COLOR_STOP = "#FF6347"         # Vermelho Tomate (Hover da gravação)
COLOR_DISABLED = "#F5F5F5"    # Fundo de botões desabilitados
COLOR_DISABLED_TEXT = "#BBBBBB" # Texto de botões desabilitados
COLOR_SUCCESS = "#27C93F" # Verde (para notificação de sucesso)

# --- [NOVO] Cores dos botões estilo macOS ---
COLOR_MAC_CLOSE = "#FF5F56"      # Vermelho
COLOR_MAC_MINIMIZE = "#FFBD2E"   # Amarelo
COLOR_MAC_MAXIMIZE = "#27C93F"   # Verde (não usado)
COLOR_MAC_CLOSE_ICON = "#990000"     # Ícone 'X' no hover (vermelho escuro)
COLOR_MAC_MINIMIZE_ICON = "#995700"  # Ícone '–' no hover (amarelo escuro)


def resource_path(relative_path):
    """ Pega o caminho absoluto para o recurso, funciona em dev e no PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- [FOLHA DE ESTILO ATUALIZADA] ---
STYLESHEET = f"""
    #JanelaPrincipal {{
        background-color: {COLOR_BG};
        /* Fonte principal mudada para Roboto */
        font-family: 'Roboto', 'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif;
        font-weight: 400;
    }}

    #MainContainer {{
        background-color: {COLOR_CARD};
        border-radius: 20px;
        border: 1px solid {COLOR_BORDER};
    }}

    QLabel {{
        color: {COLOR_TEXT};
        background-color: transparent;
        font-weight: 400;
    }}

    #LogoLabel {{
        min-height: 80px;
    }}

    #StatusLabel {{
        font-size: 16px;
        color: {COLOR_TEXT_SECONDARY};
        min-height: 40px;
    }}

    QPushButton {{
        font-size: 16px;
        font-weight: 500;
        color: {COLOR_CARD};
        background-color: {COLOR_PRIMARY};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_PRIMARY_LIGHT});
        border: none;
        border-radius: 8px;
        height: 50px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY_LIGHT}, stop:1 {COLOR_PRIMARY});
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_PRIMARY});
    }}
    QPushButton:disabled {{
        background: {COLOR_DISABLED};
        color: {COLOR_DISABLED_TEXT};
        border: none;
    }}

    #RecordButton[recording="true"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_RECORDING}, stop:1 {COLOR_STOP});
    }}
    #RecordButton[recording="true"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_STOP}, stop:1 {COLOR_RECORDING});
    }}
    #RecordButton[recording="true"]:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_RECORDING}, stop:1 {COLOR_RECORDING});
    }}

    #CleanButton {{
        height: 45px;
    }}

    #GhostButton {{
        background-color: transparent;
        border: 1px solid {COLOR_PRIMARY};
        color: {COLOR_PRIMARY};
        height: 40px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
    }}
    #GhostButton:hover {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_CARD};
    }}
    #GhostButton:disabled {{
        border-color: {COLOR_DISABLED_TEXT};
        color: {COLOR_DISABLED_TEXT};
        background-color: transparent;
    }}

    QProgressBar {{
        height: 10px;
        text-align: center;
        border: 1px solid {COLOR_BORDER};
        background-color: {COLOR_DISABLED};
        border-radius: 5px;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {COLOR_PRIMARY};
        border-radius: 5px;
    }}

    #TitleBar {{
        background-color: transparent;
        height: 40px;
    }}
    #TitleLabel {{
        color: {COLOR_TEXT};
        font-size: 14px;
        font-weight: 500;
        padding-left: 5px; /* Pequena margem para o título */
    }}

    /* --- Botões de Controle da Janela (Estilo macOS) --- */
    #MacCloseButton, #MacMinimizeButton {{
        /* [NOVO] Reseta o estilo do QPushButton geral */
        background: none; /* Remove o gradiente do QPushButton */
        
        /* Define o tamanho fixo */
        border: none;
        min-width: 12px;
        max-width: 12px;
        min-height: 12px;
        max-height: 12px;
        height: 12px; /* [NOVO] Força a altura para 12px */

        /* Define a forma redonda */
        border-radius: 6px; /* Metade da largura/altura */
        
        /* Estilo do ícone (escondido) */
        padding: 0px;
        margin: 0px;
        color: transparent; /* Esconde o ícone por padrão */
        font-size: 9px;
        font-weight: 700;
    }}

    #MacCloseButton {{
        background-color: {COLOR_MAC_CLOSE};
    }}
    #MacCloseButton:hover {{
        color: {COLOR_MAC_CLOSE_ICON}; /* Mostra o '×' */
    }}

    #MacMinimizeButton {{
        background-color: {COLOR_MAC_MINIMIZE};
    }}
    #MacMinimizeButton:hover {{
        color: {COLOR_MAC_MINIMIZE_ICON}; /* Mostra o '–' */
    }}

    /* --- [NOVO] Estilo para Pop-up de Notificação --- */
    #NotificationPopup {{
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_SUCCESS};
        border-radius: 8px;
    }}
    #NotificationPopup QLabel {{
        color: {COLOR_SUCCESS};
        font-size: 14px;
        font-weight: 500;
        padding: 10px;
        background-color: transparent;
    }}
"""

# --- Comunicação entre Threads ---
class WorkerSignals(QObject):
    update_status = Signal(str, str) # (texto, cor)
    update_state = Signal(str)       # (novo_estado)
    # --- [NOVO] Sinal para Pop-up ---
    show_notification = Signal(str)  # (mensagem)
    recording_finished = Signal()
    # --- [OTIMIZAÇÃO] Novo sinal para quando o salvamento terminar ---
    saving_finished = Signal(bool, str) # (sucesso, msg_erro)
    cleaning_finished = Signal()
    playback_finished = Signal()

# --- Classe Botão Animado ---
class AnimatedButton(QPushButton):
    def __init__(self, text, shadow_color=QColor(159, 85, 255), parent=None):
        super().__init__(text, parent)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow_color = shadow_color
        self.shadow.setBlurRadius(10) # Blur inicial
        self.shadow.setColor(shadow_color.lighter(150).lighter(150)) # Cor inicial (quase invisível)
        self.shadow.setOffset(0, 4) # Offset inicial
        self.setGraphicsEffect(self.shadow)

        self.initial_geometry = self.geometry()

        # Animação de Posição (Elevação)
        self.pos_anim = QPropertyAnimation(self, b"geometry", self)
        self.pos_anim.setDuration(200)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Animação da Sombra
        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius", self)
        self.shadow_anim.setDuration(200)
        self.shadow_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.shadow_color_anim = QPropertyAnimation(self.shadow, b"color", self)
        self.shadow_color_anim.setDuration(200)
        self.shadow_color_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def update_initial_geometry(self):
        # Salva a geometria inicial depois que o layout é estabelecido
        self.initial_geometry = self.geometry()

    def enterEvent(self, event):
        # Salva a geometria inicial na primeira vez
        if self.initial_geometry.isEmpty():
            self.update_initial_geometry()

        # Animação de Elevação
        self.pos_anim.setStartValue(self.geometry())
        self.pos_anim.setEndValue(self.initial_geometry.translated(0, -3)) # Move 3px para cima
        self.pos_anim.start()

        # Animação de Sombra (Torna-se visível)
        self.shadow_anim.setStartValue(self.shadow.blurRadius())
        self.shadow_anim.setEndValue(20) # Blur maior
        self.shadow_anim.start()

        self.shadow_color_anim.setStartValue(self.shadow.color())
        shadow_end_color = self.shadow_color
        shadow_end_color.setAlpha(120) # Define a opacidade
        self.shadow_color_anim.setEndValue(shadow_end_color)
        self.shadow_color_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        # Animação de Volta (Geometria)
        self.pos_anim.setStartValue(self.geometry())
        self.pos_anim.setEndValue(self.initial_geometry) # Volta ao normal
        self.pos_anim.start()

        # Animação de Sombra (Desaparece)
        self.shadow_anim.setStartValue(self.shadow.blurRadius())
        self.shadow_anim.setEndValue(10) # Blur inicial
        self.shadow_anim.start()

        self.shadow_color_anim.setStartValue(self.shadow.color())
        self.shadow_color_anim.setEndValue(self.shadow_color.lighter(150).lighter(150)) # Cor inicial
        self.shadow_color_anim.start()

        super().leaveEvent(event)


# --- Widget de Animação "Visualizer" ---
class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.anim_step = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pulse)
        self.setMinimumHeight(120)

        # Cores para o gradiente e sombra
        self.idle_color_top = QColor(COLOR_PRIMARY_LIGHT)
        self.idle_color_bottom = QColor(COLOR_PRIMARY)
        self.record_color_top = QColor(255, 100, 0, 255) # Laranja vibrante
        self.record_color_bottom = QColor(200, 50, 0, 255) # Laranja mais escuro

        # Frequências e offsets para 5 barras
        self.freqs = [0.08, 0.1, 0.07, 0.09, 0.06]
        self.offsets = [0, 1.2, 0.7, 1.0, 0.4]
        self.min_height = 10.0
        self.max_height = 80.0

        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setOffset(0, 3)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60)) # Sombra padrão
        self.setGraphicsEffect(self.shadow_effect)

    def start(self):
        self.anim_step = 0
        self.timer.start(16) # ~60 FPS

    def stop(self):
        self.timer.stop()
        self.update() # Repinta para o estado ocioso

    def update_pulse(self):
        self.anim_step += 1
        self.update() # Força o paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.PenStyle.NoPen)

        is_active = self.timer.isActive()

        # Define a cor da sombra baseada no estado
        if is_active:
            self.shadow_effect.setColor(QColor(255, 69, 0, 120)) # Sombra vermelha mais intensa
            self.shadow_effect.setBlurRadius(15)
        else:
            self.shadow_effect.setColor(QColor(159, 85, 255, 80)) # Sombra roxa suave
            self.shadow_effect.setBlurRadius(10)

        num_bars = 5
        total_width = self.width() * 0.7 # Usa 70% da largura
        bar_width = total_width / (num_bars * 2 - 1) # 5 barras, 4 espaços
        spacing = bar_width

        start_x = (self.width() - total_width) / 2
        bottom_y = self.height() - 10 # Posição Y da base das barras

        for i in range(num_bars):
            bar_height = self.min_height

            # Define cores e altura baseadas no estado
            if is_active:
                cycle = self.anim_step * self.freqs[i] + self.offsets[i]
                height_ratio = (math.sin(cycle) + 1) / 2 # 0.0 a 1.0
                bar_height = self.min_height + height_ratio * (self.max_height - self.min_height)
                current_top_color = self.record_color_top
                current_bottom_color = self.record_color_bottom
            else:
                bar_height = self.min_height
                current_top_color = self.idle_color_top
                current_bottom_color = self.idle_color_bottom

            bar_x = start_x + i * (bar_width + spacing)

            # Aplicar Gradiente Linear
            gradient = QLinearGradient(bar_x, bottom_y - bar_height, bar_x, bottom_y)
            gradient.setColorAt(0.0, current_top_color)
            gradient.setColorAt(1.0, current_bottom_color)
            painter.setBrush(gradient)

            # Desenhar a cápsula
            rect_radius = bar_width / 2 # Metade da largura para um topo/base redondo

            painter.drawRoundedRect(
                int(bar_x),
                int(bottom_y - bar_height),
                int(bar_width),
                int(bar_height),
                int(rect_radius), # Raio X
                int(rect_radius)  # Raio Y
            )

# --- [NOVO] Classe de Pop-up de Notificação ---
class NotificationPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationPopup")
        self.setFixedSize(300, 50) # Tamanho fixo para o pop-up
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(self.label)

        # Sombra
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

        # Esconde por padrão
        self.hide()
        self.setWindowOpacity(0.0)

        # Animações
        self.show_anim = QPropertyAnimation(self, b"geometry", self)
        self.show_anim.setDuration(300)
        self.show_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.opacity_anim.setDuration(300)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def show_notification(self, message):
        self.label.setText(message)

        # Posição inicial (em cima, fora da tela)
        parent_width = self.parent().width()
        start_x = (parent_width - self.width()) // 2
        start_y = 10 # Posição inicial (escondido)
        end_y = 50   # Posição final (visível, abaixo da barra de título)

        start_rect = QRect(start_x, start_y, self.width(), self.height())
        end_rect = QRect(start_x, end_y, self.width(), self.height())

        # Configura animação de "aparecer"
        self.show_anim.setStartValue(start_rect)
        self.show_anim.setEndValue(end_rect)
        
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        
        self.show()
        self.show_anim.start()
        self.opacity_anim.start()

        # Esconde após 2.5 segundos
        self.hide_timer.start(2500)

    def hide_notification(self):
        # Configura animação de "desaparecer"
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.start()
        
        # Esconde o widget após a animação de opacidade
        self.opacity_anim.finished.connect(self.hide)


# --- Janela Principal ---
class VoiceCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Variáveis de estado e sinais ---
        self.current_state = 'IDLE'
        self.previous_state_before_play = 'IDLE'
        self.signals = WorkerSignals()

        # --- [OTIMIZAÇÃO] Variáveis de áudio movidas para a instância ---
        self.is_recording = False
        self.audio_data = []
        self.stream = None

        # --- Configuração da Janela ---
        self.setWindowTitle("Vocalis")
        self.setFixedSize(500, 620)
        self.setObjectName("JanelaPrincipal")

        # --- JANELA SEM MOLDURA E TRANSPARENTE ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Posição para arrastar a janela
        self.oldPos = self.pos()

        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        # --- Widget Central e Layout ---
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.central_widget)

        # --- Container Central (para largura máxima) ---
        self.main_container = QFrame()
        self.main_container.setObjectName("MainContainer")
        self.container_layout = QVBoxLayout(self.main_container)

        # Margens internas da janela
        self.container_layout.setContentsMargins(25, 10, 25, 30)
        self.container_layout.setSpacing(10)

        # --- SOMBRA (para efeito de janela flutuante) ---
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 80)) # Sombra preta sutil
        self.shadow.setOffset(0, 5)
        self.main_container.setGraphicsEffect(self.shadow)

        # Aumenta a margem do layout principal para a sombra aparecer
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addWidget(self.main_container)

        # --- [NOVO] BARRA DE TÍTULO CUSTOMIZADA (Estilo macOS) ---
        self.title_bar = QFrame()
        self.title_bar.setObjectName("TitleBar")
        self.title_layout = QHBoxLayout(self.title_bar)
        # Margens da barra de título (10px nas laterais)
        self.title_layout.setContentsMargins(10, 5, 10, 5)

        # --- Container para os botões (à esquerda) ---
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(8) # Espaçamento entre os botões

        # Texto '×' para 'fechar' e '–' para 'minimizar'
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("MacCloseButton") # Novo ObjectName
        self.close_button.clicked.connect(self.close)

        self.minimize_button = QPushButton("–")
        self.minimize_button.setObjectName("MacMinimizeButton") # Novo ObjectName
        self.minimize_button.clicked.connect(self.showMinimized) # Conecta para minimizar

        # Adiciona os botões ao container (ordem macOS: Vermelho, Amarelo)
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addWidget(self.minimize_button)

        self.title_label = QLabel("Vocalis")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Título centralizado

        # --- [MUDANÇA] Layout da Barra de Título com botões à DIREITA ---
        
        # 1. Widget "Fantasma" para balancear o espaço dos botões e centralizar o título
        ghost_widget = QWidget()
        # Largura dos botões (12 + 12) + espaçamento (8) = 32px
        ghost_widget.setFixedWidth(32)

        # 1. Widget "Fantasma" à esquerda (para balancear)
        self.title_layout.addWidget(ghost_widget)
        # 2. Stretch
        self.title_layout.addStretch()
        # 3. Título
        self.title_layout.addWidget(self.title_label)
        # 4. Stretch
        self.title_layout.addStretch()
        # 5. Botões à direita
        self.title_layout.addWidget(self.button_container)

        self.container_layout.addWidget(self.title_bar)

        # --- Logo ---
        self.logo_label = QLabel()
        self.logo_label.setObjectName("LogoLabel")
        logo_path = resource_path("logo.png")
        logo_pixmap = QPixmap(logo_path)

        if logo_pixmap.isNull():
            print("AVISO: Não foi possível carregar 'logo.png'. Mostrando texto de fallback.")
            self.logo_label.setText("Vocalis")
            self.logo_label.setStyleSheet(f"font-size: 36px; font-weight: 500; color: {COLOR_PRIMARY};")
        else:
            self.logo_label.setPixmap(logo_pixmap.scaled(
                300, 75,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(self.logo_label)

        # --- Rótulo de Status ---
        self.status_label = QLabel("Pressione 'Gravar' para começar")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.container_layout.addWidget(self.status_label)
        self.container_layout.addSpacing(10)

        # --- Stack para Animação / Progresso ---
        self.middle_stack = QStackedWidget()
        self.middle_stack.setMinimumHeight(120)

        self.visualizer_widget = VisualizerWidget() # Novo widget
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)

        progress_wrapper = QWidget()
        progress_layout = QVBoxLayout(progress_wrapper)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.addWidget(self.progress_bar)
        self.progress_bar.setFixedWidth(400) # Ocupa a largura do container

        self.middle_stack.addWidget(self.visualizer_widget)
        self.middle_stack.addWidget(progress_wrapper)

        self.container_layout.addWidget(self.middle_stack)

        # --- Botões de Ação com Animação ---
        shadow_color_record = QColor(COLOR_RECORDING)
        shadow_color_record.setAlpha(120)

        # [MUDANÇA] Texto do botão sem emoji
        self.record_toggle_button = AnimatedButton("Gravar", shadow_color_record)
        self.record_toggle_button.setObjectName("RecordButton")
        self.record_toggle_button.setProperty("recording", False)
        self.record_toggle_button.clicked.connect(self.toggle_recording)
        self.container_layout.addWidget(self.record_toggle_button)

        shadow_color_clean = QColor(COLOR_PRIMARY)
        shadow_color_clean.setAlpha(120)

        # [MUDANÇA] Texto do botão sem emoji
        self.clean_button = AnimatedButton("Limpar Ruído (IA)", shadow_color_clean)
        self.clean_button.setObjectName("CleanButton")
        self.clean_button.clicked.connect(self.clean_noise_thread)
        self.container_layout.addWidget(self.clean_button)

        self.container_layout.addStretch()

        # --- Frame para botões de Playback (Não animados, usam QSS) ---
        self.playback_frame = QFrame()
        self.playback_layout = QHBoxLayout(self.playback_frame)
        self.playback_layout.setContentsMargins(0, 0, 0, 0)
        self.playback_layout.setSpacing(20)

        # [MUDANÇA] Texto do botão sem emoji
        self.play_original_button = QPushButton("Ouvir Original")
        self.play_original_button.setObjectName("GhostButton")
        self.play_original_button.clicked.connect(lambda: self.play_audio_thread(FILENAME_ORIGINAL))

        # [MUDANÇA] Texto do botão sem emoji
        self.play_clean_button = QPushButton("Ouvir Limpo")
        self.play_clean_button.setObjectName("GhostButton")
        self.play_clean_button.clicked.connect(lambda: self.play_audio_thread(FILENAME_CLEAN))

        self.playback_layout.addWidget(self.play_original_button)
        self.playback_layout.addWidget(self.play_clean_button)
        self.container_layout.addWidget(self.playback_frame)
        
        # --- [NOVO] Instância do Pop-up (fica sobre o main_container) ---
        self.notification_popup = NotificationPopup(self.main_container)

        # --- Conectar Sinais ---
        # --- [NOVO] Conectar sinal de notificação
        self.signals.show_notification.connect(self.show_notification)
        
        self.signals.recording_finished.connect(self.on_recording_finished)
        # --- [OTIMIZAÇÃO] Conectar novo sinal de salvamento ---
        self.signals.saving_finished.connect(self.on_saving_finished)
        self.signals.cleaning_finished.connect(self.on_cleaning_finished)
        self.signals.playback_finished.connect(self.on_playback_finished)

        # --- Aplicar Estilos e Estado Inicial ---
        self.setStyleSheet(STYLESHEET)
        self.update_ui_state('IDLE')

    # --- MÉTODOS PARA ARRASTAR JANELA ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Salva a posição inicial apenas se o clique for fora de um botão filho
            child = self.childAt(event.position().toPoint())
            # Verifica se o clique foi em um botão interativo
            interactive_widgets = (QPushButton, QProgressBar, NotificationPopup)
            
            is_interactive = False
            if child:
                # Verifica se o widget ou seu parente é interativo
                while child:
                    if isinstance(child, interactive_widgets):
                        is_interactive = True
                        break
                    child = child.parent()

            if not is_interactive:
                 self.oldPos = event.globalPosition().toPoint()
            else:
                 self.oldPos = None # Não arrastar se clicar em um botão

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.oldPos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    # --- Slots para Sinais ---
    @Slot(str, str)
    def set_status_label(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; background-color: transparent; font-size: 16px; font-weight: 400;")

    # [NOVO] Slot para mostrar notificação
    @Slot(str)
    def show_notification(self, message):
        self.notification_popup.show_notification(message)

    @Slot()
    def on_recording_finished(self):
        self.signals.update_status.emit("Salvando gravação...", COLOR_TEXT_SECONDARY)

        if not self.audio_data:
            self.set_status_label("Gravação muito curta. Tente novamente.", COLOR_TEXT_SECONDARY)
            self.update_ui_state('IDLE')
            return

        # --- [OTIMIZAÇÃO] Mover processamento e I/O para uma nova thread ---
        # 1. Copia os dados de áudio
        data_to_save = self.audio_data[:]
        # 2. Limpa os dados da memória imediatamente
        self.audio_data = [] 
        # 3. Inicia a thread de salvamento
        threading.Thread(target=self.save_recording_task, args=(data_to_save,), daemon=True).start()
            
    # --- [OTIMIZAÇÃO] Novo slot para lidar com o fim do salvamento ---
    @Slot(bool, str)
    def on_saving_finished(self, success, error_message):
        if success:
            self.update_ui_state('IDLE_SAVED')
            # [MUDANÇA] Emite sinal de notificação
            self.signals.show_notification.emit("Gravação salva com sucesso!")
        else:
            # [MUDANÇA] Texto de erro sem emoji
            self.set_status_label(f"Erro ao salvar: {error_message}", COLOR_RECORDING)
            print(f"Erro ao salvar arquivo: {error_message}")
            self.update_ui_state('IDLE')

    @Slot()
    def on_cleaning_finished(self):
        self.update_ui_state('CLEANED')
        # [MUDANÇA] Texto do botão sem emoji
        self.clean_button.setText("Limpar Ruído (IA)")
        # [MUDANÇA] Emite sinal de notificação
        self.signals.show_notification.emit("Áudio limpo com sucesso!")

    @Slot()
    def on_playback_finished(self):
        # [MUDANÇA] Emite sinal de notificação em vez de mudar o label
        self.signals.show_notification.emit("Reprodução concluída.")
        self.update_ui_state(self.previous_state_before_play)

    # --- Controle de Estado da UI ---
    @Slot(str)
    def update_ui_state(self, new_state):
        self.current_state = new_state

        # Desabilitar todos por padrão
        self.record_toggle_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.play_original_button.setEnabled(False)
        self.play_clean_button.setEnabled(False)

        # A animação é o padrão
        self.middle_stack.setCurrentWidget(self.visualizer_widget)

        # Reseta o botão de gravação
        self.record_toggle_button.setProperty("recording", False)
        self.record_toggle_button.style().polish(self.record_toggle_button)

        if new_state == 'IDLE':
            self.set_status_label("Pressione 'Gravar' para começar", COLOR_TEXT_SECONDARY)
            self.record_toggle_button.setEnabled(True)
            self.record_toggle_button.setText("Gravar")

        elif new_state == 'RECORDING':
            # O status "Gravando..." é definido pela thread
            self.record_toggle_button.setEnabled(True)
            self.record_toggle_button.setText("Parar")
            self.record_toggle_button.setProperty("recording", True)
            self.record_toggle_button.style().polish(self.record_toggle_button)

        elif new_state == 'IDLE_SAVED':
            # [MUDANÇA] Texto de status genérico (sucesso vem do pop-up)
            self.set_status_label("Pronto para limpar o ruído.", COLOR_TEXT_SECONDARY)
            self.record_toggle_button.setEnabled(True)
            self.record_toggle_button.setText("Gravar")
            self.clean_button.setEnabled(True)
            if os.path.exists(FILENAME_ORIGINAL):
                self.play_original_button.setEnabled(True)

        elif new_state == 'CLEANED':
            # [MUDANÇA] Texto de status genérico (sucesso vem do pop-up)
            self.set_status_label("Áudio limpo. Pronto para gravar ou ouvir.", COLOR_TEXT_SECONDARY)
            self.record_toggle_button.setEnabled(True)
            self.record_toggle_button.setText("Gravar")
            self.clean_button.setEnabled(True)
            if os.path.exists(FILENAME_ORIGINAL):
                self.play_original_button.setEnabled(True)
            if os.path.exists(FILENAME_CLEAN):
                self.play_clean_button.setEnabled(True)

        elif new_state == 'PROCESSING':
            # [MUDANÇA] Texto de status sem emoji
            self.set_status_label("Processando... Limpando ruído (IA)...", COLOR_PRIMARY)
            self.clean_button.setText("Processando...")
            self.middle_stack.setCurrentWidget(self.progress_bar)

        elif new_state == 'PLAYING':
            # O status "Tocando..." é definido pela thread
            if os.path.exists(FILENAME_ORIGINAL):
                self.play_original_button.setEnabled(False)
            if os.path.exists(FILENAME_CLEAN):
                self.play_clean_button.setEnabled(False)
            pass

    # --- Funções de Áudio (em Threads) ---

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording_thread()

    def start_recording_thread(self):
        self.is_recording = True
        self.audio_data = [] # Reseta os dados

        try:
            # Cria o stream ANTES de iniciar a thread
            self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback)
            self.update_ui_state('RECORDING')
            self.visualizer_widget.start() # Inicia a nova animação
            threading.Thread(target=self.recording_task, daemon=True).start()
        except Exception as e:
            # [MUDANÇA] Texto de erro sem emoji
            self.set_status_label(f"Erro no microfone: {e}", COLOR_RECORDING)
            self.is_recording = False


    def recording_task(self):
        # [MUDANÇA] Texto de status sem emoji
        self.signals.update_status.emit("Gravando... Fale agora.", COLOR_RECORDING)
        try:
            # O stream já foi criado, apenas o usamos
            with self.stream:
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            # [MUDANÇA] Texto de erro sem emoji
            self.signals.update_status.emit(f"Erro de gravação: {e}", COLOR_RECORDING)
            print(f"Erro de gravação: {e}")
            if self.is_recording:
                self.is_recording = False # Para a flag em caso de erro

        # A thread emite o sinal 'finished' quando realmente termina
        self.signals.recording_finished.emit()

    # --- [OTIMIZAÇÃO] Nova tarefa de thread para salvar o arquivo ---
    def save_recording_task(self, data_to_save):
        try:
            # 1. Concatena o áudio (processamento pesado)
            recording = np.concatenate(data_to_save, axis=0)
            # 2. Salva no disco (operação de I/O bloqueante)
            sf.write(FILENAME_ORIGINAL, recording, SAMPLE_RATE)
            # 3. Emite sinal de sucesso
            self.signals.saving_finished.emit(True, "")
            
        except Exception as e:
            # 4. Emite sinal de falha com a mensagem de erro
            self.signals.saving_finished.emit(False, str(e))

    # [OTIMIZAÇÃO] Callback agora é um método da classe
    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False # Sinaliza para a thread parar
        self.visualizer_widget.stop() # Para a nova animação
        # O sinal 'recording_finished' será emitido pela própria thread

    def clean_noise_thread(self):
        if not os.path.exists(FILENAME_ORIGINAL):
            # [MUDANÇA] Texto de erro sem emoji
            self.set_status_label("Grave um áudio primeiro.", COLOR_RECORDING)
            return

        self.update_ui_state('PROCESSING')
        threading.Thread(target=self.cleaning_task, daemon=True).start()

    def cleaning_task(self):
        try:
            audio_data_orig, sr = sf.read(FILENAME_ORIGINAL)

            if audio_data_orig.ndim > 1:
                audio_data_mono = np.mean(audio_data_orig, axis=1)
            else:
                audio_data_mono = audio_data_orig

            clean_data = nr.reduce_noise(y=audio_data_mono, sr=sr)
            sf.write(FILENAME_CLEAN, clean_data, sr)
            self.signals.cleaning_finished.emit()

        except Exception as e:
            # [MUDANÇA] Texto de erro sem emoji
            self.signals.update_status.emit(f"Erro ao limpar: {e}", COLOR_RECORDING)
            print(f"Erro no processamento: {e}")
            self.signals.update_state.emit('IDLE_SAVED')

    def play_audio_thread(self, filename):
        if not os.path.exists(filename):
            # [MUDANÇA] Texto de erro sem emoji
            self.set_status_label(f"Arquivo não encontrado.", COLOR_RECORDING)
            return

        self.previous_state_before_play = self.current_state
        self.update_ui_state('PLAYING')

        # [MUDANÇA] Texto de status sem emoji
        if filename == FILENAME_ORIGINAL:
             self.signals.update_status.emit("Tocando Original...", COLOR_TEXT_SECONDARY)
        else:
             self.signals.update_status.emit("Tocando Limpo...", COLOR_TEXT_SECONDARY)

        threading.Thread(target=self.playback_task, args=(filename,), daemon=True).start()

    def playback_task(self, filename):
        try:
            data, sr = sf.read(filename, dtype='float32')
            sd.play(data, sr)
            sd.wait()
            self.signals.playback_finished.emit()
        except Exception as e:
            # [MUDANÇA] Texto de erro sem emoji
            self.signals.update_status.emit(f"Erro ao tocar áudio: {e}", COLOR_RECORDING)
            print(f"Erro de playback: {e}")
            self.signals.update_state.emit(self.previous_state_before_play)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont()
    # [MUDANÇA] Fonte principal mudada para Roboto
    font.setFamily("Roboto")
    app.setFont(font)

    window = VoiceCleanerApp()

    # Atualiza a geometria inicial dos botões animados após a janela ser mostrada
    window.show()
    # É necessário esperar o layout ser processado
    QTimer.singleShot(0, window.record_toggle_button.update_initial_geometry)
    QTimer.singleShot(0, window.clean_button.update_initial_geometry)

    sys.exit(app.exec())