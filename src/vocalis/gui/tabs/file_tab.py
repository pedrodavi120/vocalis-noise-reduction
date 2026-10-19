import os
import threading
import sounddevice as sd
import soundfile as sf
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar, QSlider, QFrame
)
from PySide6.QtCore import Qt, Signal, QObject, Slot
from PySide6.QtGui import QColor

from vocalis.core.file_processor import AudioFileProcessor
from vocalis.gui.components import AnimatedButton
from vocalis.gui.styles import (
    COLOR_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_CARD, COLOR_RECORDING
)


class FileSignals(QObject):
    update_status = Signal(str, str)
    processing_finished = Signal(str, float)
    error_occurred = Signal(str)
    playback_finished = Signal()
    show_notification = Signal(str)


class FileTab(QWidget):
    """
    Aba para processar qualquer arquivo de áudio no computador (.wav, .mp3, .flac, .ogg).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = FileSignals()

        self.input_file: str = ""
        self.output_file: str = ""
        self.is_playing = False

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)

        # Card de Seleção de Arquivo
        file_box = QFrame()
        file_box.setStyleSheet("background-color: #FBFBFC; border: 1px dashed #D0D5DD; border-radius: 12px; padding: 10px;")
        fb_layout = QVBoxLayout(file_box)
        fb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.file_label = QLabel("Nenhum arquivo selecionado\n(Clique abaixo para escolher um arquivo de áudio)")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("color: #475467; font-size: 13px; font-weight: 500;")
        fb_layout.addWidget(self.file_label)

        btn_select = QPushButton("Selecionar Arquivo")
        btn_select.setProperty("class", "GhostButton")
        btn_select.clicked.connect(self.select_file)
        fb_layout.addWidget(btn_select, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(file_box)

        # Ajuste de Intensidade de Redução
        slider_box = QWidget()
        s_layout = QVBoxLayout(slider_box)
        s_layout.setContentsMargins(0, 0, 0, 0)
        s_layout.setSpacing(4)

        self.slider_label = QLabel("Intensidade da Redução de Ruído: 90%")
        self.slider_label.setStyleSheet("color: #344054; font-size: 12px; font-weight: 500;")
        s_layout.addWidget(self.slider_label)

        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(10, 100)
        self.strength_slider.setValue(90)
        self.strength_slider.valueChanged.connect(self._on_slider_changed)
        s_layout.addWidget(self.strength_slider)

        layout.addWidget(slider_box)

        # Status & Barra de Progresso
        self.status_label = QLabel("Aguardando arquivo.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Botão Principal Processar
        shadow = QColor(COLOR_PRIMARY)
        shadow.setAlpha(100)
        self.btn_process = AnimatedButton("Limpar Arquivo de Áudio", shadow)
        self.btn_process.setEnabled(False)
        self.btn_process.clicked.connect(self.process_file)
        layout.addWidget(self.btn_process)

        # Playbacks e Exportar
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        self.btn_play_orig = QPushButton("Ouvir Original")
        self.btn_play_orig.setProperty("class", "GhostButton")
        self.btn_play_orig.setEnabled(False)
        self.btn_play_orig.clicked.connect(lambda: self.play_audio(self.input_file))

        self.btn_play_clean = QPushButton("Ouvir Limpo")
        self.btn_play_clean.setProperty("class", "GhostButton")
        self.btn_play_clean.setEnabled(False)
        self.btn_play_clean.clicked.connect(lambda: self.play_audio(self.output_file))

        self.btn_export = QPushButton("Exportar Como...")
        self.btn_export.setProperty("class", "GhostButton")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_file)

        actions_layout.addWidget(self.btn_play_orig)
        actions_layout.addWidget(self.btn_play_clean)
        actions_layout.addWidget(self.btn_export)
        layout.addLayout(actions_layout)

        layout.addStretch()

    def _connect_signals(self):
        self.signals.update_status.connect(self.set_status)
        self.signals.processing_finished.connect(self.on_processing_finished)
        self.signals.error_occurred.connect(self.on_error)
        self.signals.playback_finished.connect(self.on_playback_finished)

    def _on_slider_changed(self, val: int):
        self.slider_label.setText(f"Intensidade da Redução de Ruído: {val}%")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo de Áudio",
            "",
            "Arquivos de Áudio (*.wav *.mp3 *.ogg *.flac *.m4a);;Todos os Arquivos (*)"
        )
        if file_path:
            self.input_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(f"Arquivo selecionado:\n{filename}")
            self.btn_process.setEnabled(True)
            self.btn_play_orig.setEnabled(True)
            self.btn_play_clean.setEnabled(False)
            self.btn_export.setEnabled(False)
            self.set_status("Pronto para processar.", COLOR_TEXT_SECONDARY)

    def process_file(self):
        if not self.input_file or not os.path.exists(self.input_file):
            return

        self.btn_process.setEnabled(False)
        self.progress_bar.show()
        self.set_status("Removendo ruído do áudio...", COLOR_PRIMARY)

        # Destino temporário limpo
        base_dir = os.path.dirname(self.input_file)
        self.output_file = os.path.join(base_dir, f"limpo_{os.path.splitext(os.path.basename(self.input_file))[0]}.wav")
        strength = self.strength_slider.value() / 100.0

        threading.Thread(
            target=self._process_worker,
            args=(self.input_file, self.output_file, strength),
            daemon=True
        ).start()

    def _process_worker(self, in_p: str, out_p: str, strength: float):
        try:
            _, dur = AudioFileProcessor.clean_file(
                in_p,
                out_p,
                prop_decrease=strength,
                apply_highpass=True,
                apply_gate=True
            )
            self.signals.processing_finished.emit(out_p, dur)
        except Exception as e:
            self.signals.error_occurred.emit(str(e))

    @Slot(str, float)
    def on_processing_finished(self, out_path: str, duration: float):
        self.progress_bar.hide()
        self.btn_process.setEnabled(True)
        self.btn_play_clean.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.set_status(f"Processado com sucesso ({duration:.1f}s)", COLOR_TEXT_SECONDARY)
        self.signals.show_notification.emit("Arquivo limpo com sucesso!")

    @Slot(str)
    def on_error(self, err: str):
        self.progress_bar.hide()
        self.btn_process.setEnabled(True)
        self.set_status(f"Erro no processamento: {err}", COLOR_RECORDING)

    def play_audio(self, path: str):
        if not path or not os.path.exists(path):
            return

        self.set_status(f"Reproduzindo: {os.path.basename(path)}", COLOR_TEXT_SECONDARY)
        threading.Thread(target=self._play_worker, args=(path,), daemon=True).start()

    def _play_worker(self, path: str):
        try:
            data, sr = sf.read(path, dtype='float32')
            sd.play(data, sr)
            sd.wait()
            self.signals.playback_finished.emit()
        except Exception as e:
            self.signals.error_occurred.emit(f"Erro ao tocar áudio: {e}")

    @Slot()
    def on_playback_finished(self):
        self.set_status("Reprodução finalizada.", COLOR_TEXT_SECONDARY)

    def export_file(self):
        if not self.output_file or not os.path.exists(self.output_file):
            return

        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Áudio Limpo",
            os.path.basename(self.output_file),
            "Arquivo WAV (*.wav);;Todos os Arquivos (*)"
        )
        if dest_path:
            try:
                import shutil
                shutil.copyfile(self.output_file, dest_path)
                self.signals.show_notification.emit("Arquivo exportado com sucesso!")
            except Exception as e:
                self.set_status(f"Erro ao exportar: {e}", COLOR_RECORDING)

    @Slot(str, str)
    def set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px;")
