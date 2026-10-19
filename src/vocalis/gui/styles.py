import os
import sys

def resource_path(relative_path: str) -> str:
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Tenta localizar a partir da raiz do repositório ou diretório atual
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if os.path.exists(os.path.join(current_dir, relative_path)):
            return os.path.join(current_dir, relative_path)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Paleta "Clean White"
COLOR_BG = "transparent"
COLOR_CARD = "#FFFFFF"
COLOR_PRIMARY = "#9F55FF"
COLOR_PRIMARY_LIGHT = "#B57FFF"
COLOR_ACCENT = "#D0A0FF"
COLOR_TEXT = "#111111"
COLOR_TEXT_SECONDARY = "#666666"
COLOR_BORDER = "#EEEEEE"
COLOR_RECORDING = "#FF4500"
COLOR_STOP = "#FF6347"
COLOR_DISABLED = "#F5F5F5"
COLOR_DISABLED_TEXT = "#BBBBBB"
COLOR_SUCCESS = "#27C93F"

# Controles macOS
COLOR_MAC_CLOSE = "#FF5F56"
COLOR_MAC_MINIMIZE = "#FFBD2E"
COLOR_MAC_CLOSE_ICON = "#990000"
COLOR_MAC_MINIMIZE_ICON = "#995700"

STYLESHEET = f"""
    #JanelaPrincipal {{
        background-color: {COLOR_BG};
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

    #TitleBar {{
        background-color: transparent;
        height: 40px;
    }}

    #TitleLabel {{
        color: {COLOR_TEXT};
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}

    #MacCloseButton, #MacMinimizeButton {{
        background: none;
        border: none;
        min-width: 12px;
        max-width: 12px;
        min-height: 12px;
        max-height: 12px;
        border-radius: 6px;
        padding: 0px;
        margin: 0px;
        color: transparent;
        font-size: 9px;
        font-weight: 700;
    }}

    #MacCloseButton {{
        background-color: {COLOR_MAC_CLOSE};
    }}
    #MacCloseButton:hover {{
        color: {COLOR_MAC_CLOSE_ICON};
    }}

    #MacMinimizeButton {{
        background-color: {COLOR_MAC_MINIMIZE};
    }}
    #MacMinimizeButton:hover {{
        color: {COLOR_MAC_MINIMIZE_ICON};
    }}

    /* Abas de Navegação Superiores */
    #TabNav {{
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 4px;
    }}

    QPushButton.NavTabButton {{
        background: transparent;
        color: {COLOR_TEXT_SECONDARY};
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        height: 34px;
        padding: 0 12px;
    }}
    QPushButton.NavTabButton:hover {{
        background-color: #EFEFEF;
        color: {COLOR_TEXT};
    }}
    QPushButton.NavTabButton[active="true"] {{
        background-color: {COLOR_CARD};
        color: {COLOR_PRIMARY};
        font-weight: 600;
        border: 1px solid {COLOR_BORDER};
    }}

    /* Botão Principal */
    QPushButton.PrimaryButton {{
        font-size: 15px;
        font-weight: 600;
        color: {COLOR_CARD};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_PRIMARY_LIGHT});
        border: none;
        border-radius: 8px;
        height: 44px;
        padding: 0 16px;
    }}
    QPushButton.PrimaryButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY_LIGHT}, stop:1 {COLOR_PRIMARY});
    }}
    QPushButton.PrimaryButton:disabled {{
        background: {COLOR_DISABLED};
        color: {COLOR_DISABLED_TEXT};
    }}

    /* Botão Fantasma / Secundário */
    QPushButton.GhostButton {{
        background-color: transparent;
        border: 1px solid {COLOR_PRIMARY};
        color: {COLOR_PRIMARY};
        height: 38px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        padding: 0 12px;
    }}
    QPushButton.GhostButton:hover {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_CARD};
    }}
    QPushButton.GhostButton:disabled {{
        border-color: {COLOR_DISABLED_TEXT};
        color: {COLOR_DISABLED_TEXT};
    }}

    /* Botão de Gravação */
    QPushButton.RecordButton[recording="true"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_RECORDING}, stop:1 {COLOR_STOP});
        color: white;
    }}

    QComboBox {{
        background-color: #FAFAFA;
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: {COLOR_TEXT};
    }}
    QComboBox::drop-down {{
        border: none;
    }}

    QSlider::groove:horizontal {{
        height: 6px;
        background: #E5E5E5;
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: {COLOR_PRIMARY};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {COLOR_PRIMARY};
        border: 2px solid white;
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}

    QProgressBar {{
        height: 8px;
        text-align: center;
        border: 1px solid {COLOR_BORDER};
        background-color: {COLOR_DISABLED};
        border-radius: 4px;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {COLOR_PRIMARY};
        border-radius: 4px;
    }}

    #NotificationPopup {{
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_SUCCESS};
        border-radius: 8px;
    }}
    #NotificationPopup QLabel {{
        color: {COLOR_SUCCESS};
        font-size: 13px;
        font-weight: 500;
        padding: 8px 14px;
    }}
"""
