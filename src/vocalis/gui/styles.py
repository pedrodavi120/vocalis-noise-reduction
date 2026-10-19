import os
import sys

def resource_path(relative_path: str) -> str:
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller e modo desenvolvimento."""
    if hasattr(sys, "_MEIPASS"):
        meipass_candidate = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(meipass_candidate):
            return meipass_candidate

    # 1. Diretório do módulo gui
    gui_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_gui = os.path.join(gui_dir, relative_path)
    if os.path.exists(candidate_gui):
        return candidate_gui

    # 2. Raiz do repositório
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(gui_dir)))
    candidate_repo = os.path.join(repo_root, relative_path)
    if os.path.exists(candidate_repo):
        return candidate_repo

    # 3. Diretório de execução atual
    cwd_candidate = os.path.abspath(relative_path)
    if os.path.exists(cwd_candidate):
        return cwd_candidate

    return candidate_gui

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
COLOR_MAC_CLOSE_BORDER = "#E0443E"
COLOR_MAC_MINIMIZE = "#FFBD2E"
COLOR_MAC_MINIMIZE_BORDER = "#DEA123"
COLOR_MAC_ZOOM = "#27C93F"
COLOR_MAC_ZOOM_BORDER = "#1AAB29"
COLOR_MAC_CLOSE_ICON = "#4D0000"
COLOR_MAC_MINIMIZE_ICON = "#5E3900"
COLOR_MAC_ZOOM_ICON = "#00470A"

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
        height: 36px;
    }}

    #MacCloseButton, #MacMinimizeButton, #MacZoomButton {{
        border-radius: 6px;
        min-width: 12px;
        max-width: 12px;
        width: 12px;
        min-height: 12px;
        max-height: 12px;
        height: 12px;
        padding: 0px;
        margin: 0px;
        color: transparent;
        font-size: 8px;
        font-weight: 800;
        text-align: center;
        line-height: 12px;
    }}

    #MacCloseButton {{
        background: {COLOR_MAC_CLOSE};
        border: 1px solid {COLOR_MAC_CLOSE_BORDER};
    }}
    #MacCloseButton:hover {{
        color: {COLOR_MAC_CLOSE_ICON};
    }}

    #MacMinimizeButton {{
        background: {COLOR_MAC_MINIMIZE};
        border: 1px solid {COLOR_MAC_MINIMIZE_BORDER};
    }}
    #MacMinimizeButton:hover {{
        color: {COLOR_MAC_MINIMIZE_ICON};
    }}

    #MacZoomButton {{
        background: {COLOR_MAC_ZOOM};
        border: 1px solid {COLOR_MAC_ZOOM_BORDER};
    }}
    #MacZoomButton:hover {{
        color: {COLOR_MAC_ZOOM_ICON};
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

    /* Botões Principais */
    QPushButton {{
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
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY_LIGHT}, stop:1 {COLOR_PRIMARY});
    }}
    QPushButton:disabled {{
        background: {COLOR_DISABLED};
        color: {COLOR_DISABLED_TEXT};
    }}

    /* Botão Fantasma / Secundário */
    QPushButton#GhostButton, QPushButton[class="GhostButton"] {{
        background-color: transparent;
        border: 1px solid {COLOR_PRIMARY};
        color: {COLOR_PRIMARY};
        height: 38px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        padding: 0 12px;
    }}
    QPushButton#GhostButton:hover, QPushButton[class="GhostButton"]:hover {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_CARD};
    }}
    QPushButton#GhostButton:disabled, QPushButton[class="GhostButton"]:disabled {{
        border-color: {COLOR_DISABLED_TEXT};
        color: {COLOR_DISABLED_TEXT};
        background-color: transparent;
    }}

    /* Botão de Gravação */
    QPushButton#RecordButton[recording="true"], QPushButton[recording="true"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_RECORDING}, stop:1 {COLOR_STOP});
        color: white;
    }}

    /* Cards e Containers internos (usando IDs para evitar propagação para filhos) */
    QFrame#CardBox, QFrame#DevCard, QFrame#CtrlCard {{
        background-color: #FAFAFA;
        border: 1px solid #E4E7EC;
        border-radius: 10px;
    }}

    QFrame#FileDropCard {{
        background-color: #FBFBFC;
        border: 2px dashed #D0D5DD;
        border-radius: 12px;
    }}

    QComboBox {{
        background-color: #FFFFFF;
        border: 1px solid #D0D5DD;
        border-radius: 8px;
        padding: 6px 10px;
        min-height: 24px;
        font-size: 13px;
        color: {COLOR_TEXT};
    }}
    QComboBox:hover {{
        border: 1px solid {COLOR_PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: #FFFFFF;
        color: {COLOR_TEXT};
        selection-background-color: {COLOR_PRIMARY};
        selection-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
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
