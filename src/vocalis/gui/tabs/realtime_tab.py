import sys
import sounddevice as sd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSlider, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QObject, Slot
from PySide6.QtGui import QColor

from vocalis.core.realtime_engine import RealtimeDenoiseEngine
from vocalis.devices.manager import AudioDeviceManager
from vocalis.gui.components import AnimatedButton
from vocalis.gui.styles import (
    COLOR_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_RECORDING, COLOR_SUCCESS
)


class RealtimeSignals(QObject):
    metrics_updated = Signal(float, float)
    status_updated = Signal(str, str)
    notification_requested = Signal(str)


class RealtimeTab(QWidget):
    """
    Aba para controle do Microfone em Tempo Real e Dispositivo Virtual de Entrada.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = RealtimeSignals()
        self.device_manager = AudioDeviceManager()
        self.engine: RealtimeDenoiseEngine = None
        self.is_active = False

        self._build_ui()
        self._connect_signals()
        self.refresh_devices()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # 1. Card de Configuração de Dispositivos
        dev_frame = QFrame()
        dev_frame.setObjectName("DevCard")
        df_layout = QVBoxLayout(dev_frame)
        df_layout.setContentsMargins(14, 12, 14, 12)
        df_layout.setSpacing(6)

        lbl_input = QLabel("Microfone Físico (Entrada):")
        lbl_input.setStyleSheet("font-size: 12px; font-weight: 600; color: #344054;")
        self.combo_input = QComboBox()
        df_layout.addWidget(lbl_input)
        df_layout.addWidget(self.combo_input)

        lbl_output = QLabel("Dispositivo Virtual de Saída (Cabo / PipeWire):")
        lbl_output.setStyleSheet("font-size: 12px; font-weight: 600; color: #344054;")
        self.combo_output = QComboBox()
        df_layout.addWidget(lbl_output)
        df_layout.addWidget(self.combo_output)

        btn_refresh = QPushButton("Atualizar Lista de Dispositivos")
        btn_refresh.setObjectName("GhostButton")
        btn_refresh.setFixedHeight(30)
        btn_refresh.clicked.connect(self.refresh_devices)
        df_layout.addWidget(btn_refresh, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addWidget(dev_frame)

        # 2. Controles de Processamento
        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("CtrlCard")
        cf_layout = QVBoxLayout(ctrl_frame)
        cf_layout.setContentsMargins(14, 12, 14, 12)
        cf_layout.setSpacing(8)

        # Noise Gate
        self.lbl_gate = QLabel("Sensibilidade do Gate de Ruído: -42 dB")
        self.lbl_gate.setStyleSheet("font-size: 12px; color: #344054;")
        self.slider_gate = QSlider(Qt.Orientation.Horizontal)
        self.slider_gate.setRange(-60, -20)
        self.slider_gate.setValue(-42)
        self.slider_gate.valueChanged.connect(self._on_gate_changed)
        cf_layout.addWidget(self.lbl_gate)
        cf_layout.addWidget(self.slider_gate)

        # Intensidade
        self.lbl_strength = QLabel("Intensidade da Redução Espectral: 85%")
        self.lbl_strength.setStyleSheet("font-size: 12px; color: #344054;")
        self.slider_strength = QSlider(Qt.Orientation.Horizontal)
        self.slider_strength.setRange(20, 100)
        self.slider_strength.setValue(85)
        self.slider_strength.valueChanged.connect(self._on_strength_changed)
        cf_layout.addWidget(self.lbl_strength)
        cf_layout.addWidget(self.slider_strength)

        layout.addWidget(ctrl_frame)

        # 3. Medidor VU de Volume (Entrada vs Saída Limpa)
        vu_box = QWidget()
        vu_layout = QVBoxLayout(vu_box)
        vu_layout.setContentsMargins(0, 0, 0, 0)
        vu_layout.setSpacing(4)

        lbl_vu = QLabel("Nível do Microfone (dB):")
        lbl_vu.setStyleSheet("font-size: 11px; color: #667085; font-weight: 500;")
        self.vu_bar = QProgressBar()
        self.vu_bar.setRange(0, 100)
        self.vu_bar.setValue(0)
        self.vu_bar.setFixedHeight(8)

        vu_layout.addWidget(lbl_vu)
        vu_layout.addWidget(self.vu_bar)
        layout.addWidget(vu_box)

        # Status
        self.status_label = QLabel("Microfone em tempo real parado.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(self.status_label)

        # Botão Ligar/Desligar
        shadow = QColor(COLOR_PRIMARY)
        shadow.setAlpha(100)
        self.btn_toggle = AnimatedButton("Ativar Microfone Virtual", shadow)
        self.btn_toggle.clicked.connect(self.toggle_engine)
        layout.addWidget(self.btn_toggle)

        layout.addStretch()

    def _connect_signals(self):
        self.signals.metrics_updated.connect(self._on_metrics)
        self.signals.status_updated.connect(self.set_status)

    def refresh_devices(self):
        self.combo_input.clear()
        inputs = self.device_manager.get_input_devices()
        for dev in inputs:
            self.combo_input.addItem(f"{dev['name']} [ID: {dev['id']}]", dev['id'])

        self.combo_output.clear()
        outputs = self.device_manager.get_output_devices()
        for dev in outputs:
            self.combo_output.addItem(f"{dev['name']} [ID: {dev['id']}]", dev['id'])

    def _on_gate_changed(self, val: int):
        self.lbl_gate.setText(f"Sensibilidade do Gate de Ruído: {val} dB")
        if self.engine:
            self.engine.set_gate_threshold(float(val))

    def _on_strength_changed(self, val: int):
        self.lbl_strength.setText(f"Intensidade da Redução Espectral: {val}%")
        if self.engine:
            self.engine.set_denoise_strength(val / 100.0)

    @Slot(float, float)
    def _on_metrics(self, in_db: float, out_db: float):
        # Mapeia -60dB a 0dB para 0-100%
        val = int(max(0, min(100, (out_db + 60.0) * (100.0 / 60.0))))
        self.vu_bar.setValue(val)

    def toggle_engine(self):
        if self.is_active:
            self.stop_engine()
        else:
            self.start_engine()

    def start_engine(self):
        in_id = self.combo_input.currentData()
        out_id = self.combo_output.currentData()

        if in_id is None:
            self.set_status("Nenhum microfone de entrada selecionado.", COLOR_RECORDING)
            return

        # Prepara sink virtual se for no Linux
        success, msg, v_sink_id = self.device_manager.setup_virtual_sink()
        if success and v_sink_id is not None:
            out_id = v_sink_id
            self.refresh_devices()

        gate_db = float(self.slider_gate.value())
        strength = self.slider_strength.value() / 100.0

        try:
            self.engine = RealtimeDenoiseEngine(
                input_device_index=in_id,
                output_device_index=out_id,
                sample_rate=44100,
                block_size=512,
                gate_threshold_db=gate_db,
                denoise_strength=strength,
                enable_highpass=True,
                on_metrics_callback=lambda in_rms, out_rms: self.signals.metrics_updated.emit(in_rms, out_rms)
            )
            self.engine.start()
            self.is_active = True
            self.btn_toggle.setText("Desativar Microfone Virtual")
            self.set_status("Microfone Virtual ATIVO e transmitindo.", COLOR_SUCCESS)
            self.signals.notification_requested.emit("Microfone em tempo real ativado.")
        except Exception as e:
            self.set_status(f"Erro ao iniciar streaming: {e}", COLOR_RECORDING)
            self.is_active = False

    def stop_engine(self):
        if self.engine:
            self.engine.stop()
            self.engine = None
        self.device_manager.teardown_virtual_sink()
        self.is_active = False
        self.vu_bar.setValue(0)
        self.btn_toggle.setText("Ativar Microfone Virtual")
        self.set_status("Microfone em tempo real desativado.", COLOR_TEXT_SECONDARY)
        self.signals.notification_requested.emit("Microfone em tempo real desativado.")

    @Slot(str, str)
    def set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px;")

    def cleanup(self):
        self.stop_engine()
