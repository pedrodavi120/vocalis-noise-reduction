import os
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QObject, Slot
from PySide6.QtGui import QColor

from vocalis.core.file_processor import AudioFileProcessor
from vocalis.gui.components import AnimatedButton, VisualizerWidget
from vocalis.gui.styles import (
    COLOR_RECORDING, COLOR_PRIMARY, COLOR_TEXT_SECONDARY
)

FILENAME_ORIGINAL = "gravacao_original.wav"
FILENAME_CLEAN = "gravacao_limpa.wav"
SAMPLE_RATE = 44100


class RecorderSignals(QObject):
    update_status = Signal(str, str)
    recording_finished = Signal()
    saving_finished = Signal(bool, str)
    cleaning_finished = Signal()
    playback_finished = Signal()
    show_notification = Signal(str)


class RecorderTab(QWidget):
    """
    Aba de gravação e limpeza rápida direta do microfone.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = RecorderSignals()

        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.current_state = 'IDLE'
        self.prev_state = 'IDLE'

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        self.status_label = QLabel("Pressione 'Gravar' para começar")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(self.status_label)

        self.middle_stack = QStackedWidget()
        self.middle_stack.setMinimumHeight(100)

        self.visualizer = VisualizerWidget()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(8)

        progress_container = QWidget()
        p_layout = QVBoxLayout(progress_container)
        p_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(self.progress_bar)

        self.middle_stack.addWidget(self.visualizer)
        self.middle_stack.addWidget(progress_container)
        layout.addWidget(self.middle_stack)

        # Botão Gravar
        shadow_record = QColor(COLOR_RECORDING)
        shadow_record.setAlpha(100)
        self.record_button = AnimatedButton("Gravar", shadow_record)
        self.record_button.setProperty("class", "PrimaryButton")
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        # Botão Limpar
        shadow_clean = QColor(COLOR_PRIMARY)
        shadow_clean.setAlpha(100)
        self.clean_button = AnimatedButton("Limpar Ruído (IA)", shadow_clean)
        self.clean_button.clicked.connect(self.clean_noise)
        layout.addWidget(self.clean_button)

        # Botões de Playback
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(12)

        self.play_orig_button = QPushButton("Ouvir Original")
        self.play_orig_button.setObjectName("GhostButton")
        self.play_orig_button.clicked.connect(lambda: self.play_audio(FILENAME_ORIGINAL))

        self.play_clean_button = QPushButton("Ouvir Limpo")
        self.play_clean_button.setObjectName("GhostButton")
        self.play_clean_button.clicked.connect(lambda: self.play_audio(FILENAME_CLEAN))

        playback_layout.addWidget(self.play_orig_button)
        playback_layout.addWidget(self.play_clean_button)
        layout.addLayout(playback_layout)

        layout.addStretch()
        self.update_state('IDLE')

    def _connect_signals(self):
        self.signals.recording_finished.connect(self.on_recording_finished)
        self.signals.saving_finished.connect(self.on_saving_finished)
        self.signals.cleaning_finished.connect(self.on_cleaning_finished)
        self.signals.playback_finished.connect(self.on_playback_finished)
        self.signals.update_status.connect(self.set_status)

    @Slot(str, str)
    def set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 14px;")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.audio_data = []
        try:
            self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback)
            self.update_state('RECORDING')
            self.visualizer.start()
            threading.Thread(target=self._recording_loop, daemon=True).start()
        except Exception as e:
            self.set_status(f"Erro no microfone: {e}", COLOR_RECORDING)
            self.is_recording = False

    def audio_callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def _recording_loop(self):
        self.signals.update_status.emit("Gravando... Fale no microfone.", COLOR_RECORDING)
        try:
            with self.stream:
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            self.signals.update_status.emit(f"Erro na gravação: {e}", COLOR_RECORDING)
            self.is_recording = False
        self.signals.recording_finished.emit()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.visualizer.stop()

    @Slot()
    def on_recording_finished(self):
        self.signals.update_status.emit("Salvando gravação...", COLOR_TEXT_SECONDARY)
        if not self.audio_data:
            self.set_status("Gravação muito curta.", COLOR_TEXT_SECONDARY)
            self.update_state('IDLE')
            return

        to_save = self.audio_data[:]
        self.audio_data = []
        threading.Thread(target=self._save_task, args=(to_save,), daemon=True).start()

    def _save_task(self, data):
        try:
            recording = np.concatenate(data, axis=0)
            AudioFileProcessor.save_audio(FILENAME_ORIGINAL, recording, SAMPLE_RATE)
            self.signals.saving_finished.emit(True, "")
        except Exception as e:
            self.signals.saving_finished.emit(False, str(e))

    @Slot(bool, str)
    def on_saving_finished(self, success: bool, err: str):
        if success:
            self.update_state('IDLE_SAVED')
            self.signals.show_notification.emit("Gravação salva com sucesso.")
        else:
            self.set_status(f"Erro ao salvar: {err}", COLOR_RECORDING)
            self.update_state('IDLE')

    def clean_noise(self):
        if not os.path.exists(FILENAME_ORIGINAL):
            self.set_status("Nenhuma gravação encontrada.", COLOR_RECORDING)
            return

        self.update_state('PROCESSING')
        threading.Thread(target=self._clean_task, daemon=True).start()

    def _clean_task(self):
        try:
            AudioFileProcessor.clean_file(
                FILENAME_ORIGINAL,
                FILENAME_CLEAN,
                prop_decrease=0.95,
                apply_highpass=True,
                apply_gate=True
            )
            self.signals.cleaning_finished.emit()
        except Exception as e:
            self.signals.update_status.emit(f"Erro ao limpar: {e}", COLOR_RECORDING)
            self.signals.saving_finished.emit(False, str(e))

    @Slot()
    def on_cleaning_finished(self):
        self.update_state('CLEANED')
        self.clean_button.setText("Limpar Ruído (IA)")
        self.signals.show_notification.emit("Áudio limpo com sucesso.")

    def play_audio(self, filename: str):
        if not os.path.exists(filename):
            self.set_status("Arquivo não encontrado.", COLOR_RECORDING)
            return

        self.prev_state = self.current_state
        self.update_state('PLAYING')
        label = "Tocando Original..." if filename == FILENAME_ORIGINAL else "Tocando Limpo..."
        self.signals.update_status.emit(label, COLOR_TEXT_SECONDARY)
        threading.Thread(target=self._play_task, args=(filename,), daemon=True).start()

    def _play_task(self, filename):
        try:
            data, sr = sf.read(filename, dtype='float32')
            sd.play(data, sr)
            sd.wait()
            self.signals.playback_finished.emit()
        except Exception as e:
            self.signals.update_status.emit(f"Erro no playback: {e}", COLOR_RECORDING)
            self.signals.playback_finished.emit()

    @Slot()
    def on_playback_finished(self):
        self.update_state(self.prev_state)

    def update_state(self, state: str):
        self.current_state = state
        self.record_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.play_orig_button.setEnabled(False)
        self.play_clean_button.setEnabled(False)
        self.middle_stack.setCurrentWidget(self.visualizer)

        if state == 'IDLE':
            self.set_status("Pressione 'Gravar' para começar", COLOR_TEXT_SECONDARY)
            self.record_button.setEnabled(True)
            self.record_button.setText("Gravar")
            self.record_button.setProperty("recording", False)

        elif state == 'RECORDING':
            self.record_button.setEnabled(True)
            self.record_button.setText("Parar")
            self.record_button.setProperty("recording", True)

        elif state == 'IDLE_SAVED':
            self.set_status("Pronto para limpar o ruído.", COLOR_TEXT_SECONDARY)
            self.record_button.setEnabled(True)
            self.record_button.setText("Gravar")
            self.clean_button.setEnabled(True)
            self.play_orig_button.setEnabled(True)

        elif state == 'CLEANED':
            self.set_status("Áudio limpo disponível para audição.", COLOR_TEXT_SECONDARY)
            self.record_button.setEnabled(True)
            self.record_button.setText("Gravar")
            self.clean_button.setEnabled(True)
            self.play_orig_button.setEnabled(True)
            self.play_clean_button.setEnabled(True)

        elif state == 'PROCESSING':
            self.set_status("Processando redução de ruído via IA...", COLOR_PRIMARY)
            self.clean_button.setText("Processando...")
            self.middle_stack.setCurrentWidget(self.progress_bar)

        elif state == 'PLAYING':
            pass

        self.record_button.style().polish(self.record_button)
