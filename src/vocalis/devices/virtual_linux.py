import os
import subprocess
import shutil
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class LinuxVirtualMic:
    """
    Gerenciador de microfone virtual no Linux via PipeWire ou PulseAudio.
    Cria dinamicamente um nó de áudio de loopback/null-sink que aparece no sistema
    como dispositivo de entrada (Microfone Vocalis) e dispositivo de saída para streaming.
    """

    SINK_NAME = "vocalis_virtual_sink"
    SOURCE_NAME = "vocalis_virtual_mic"
    DESCRIPTION = "Vocalis Virtual Microphone"

    def __init__(self):
        self._created_module_id: Optional[str] = None
        self._pipewire_process: Optional[subprocess.Popen] = None
        self.is_active = False

    def is_pipewire(self) -> bool:
        return shutil.which("pw-cli") is not None or shutil.which("pipewire") is not None

    def is_pulseaudio(self) -> bool:
        return shutil.which("pactl") is not None

    def create_virtual_device(self) -> Tuple[bool, str]:
        """
        Cria o dispositivo virtual no Linux.
        """
        if self.is_active:
            return True, "Dispositivo virtual já está ativo."

        # Tentativa 1: PulseAudio / PipeWire-Pulse (pactl)
        if self.is_pulseaudio():
            try:
                # 1. Carrega o null-sink
                cmd_sink = [
                    "pactl", "load-module", "module-null-sink",
                    f"sink_name={self.SINK_NAME}",
                    f"sink_properties=device.description='{self.DESCRIPTION}_Output'"
                ]
                res_sink = subprocess.run(cmd_sink, capture_output=True, text=True, check=True)
                module_id = res_sink.stdout.strip()

                # 2. Carrega o source remap para transformar o monitor em microfone padrão
                cmd_source = [
                    "pactl", "load-module", "module-remap-source",
                    f"master={self.SINK_NAME}.monitor",
                    f"source_name={self.SOURCE_NAME}",
                    f"source_properties=device.description='{self.DESCRIPTION}'"
                ]
                subprocess.run(cmd_source, capture_output=True, text=True, check=True)

                self._created_module_id = module_id
                self.is_active = True
                return True, f"Microfone virtual criado via PulseAudio: {self.DESCRIPTION}"
            except Exception as e:
                logger.warning(f"Falha ao criar via pactl: {e}")

        # Tentativa 2: pw-loopback direto (PipeWire nativo)
        if self.is_pipewire() and shutil.which("pw-loopback"):
            try:
                cmd = [
                    "pw-loopback",
                    "--capture-props=media.class=Audio/Sink node.name=vocalis_sink node.description='Vocalis Stream Input'",
                    "--playback-props=media.class=Audio/Source node.name=vocalis_mic node.description='Vocalis Virtual Microphone'"
                ]
                self._pipewire_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.is_active = True
                return True, f"Microfone virtual criado via PipeWire: {self.DESCRIPTION}"
            except Exception as e:
                return False, f"Erro ao iniciar pw-loopback: {e}"

        return False, "Nenhum servidor de áudio suportado (PipeWire ou PulseAudio/pactl) foi encontrado."

    def remove_virtual_device(self) -> None:
        """
        Descarrega o módulo e remove o microfone virtual do sistema.
        """
        if self.is_pulseaudio():
            try:
                # Localiza e descarrega módulos criados
                res = subprocess.run(["pactl", "list", "short", "modules"], capture_output=True, text=True)
                for line in res.stdout.splitlines():
                    if self.SINK_NAME in line or self.SOURCE_NAME in line:
                        parts = line.split()
                        if parts:
                            mod_id = parts[0]
                            subprocess.run(["pactl", "unload-module", mod_id], capture_output=True)
            except Exception:
                pass

        if self._pipewire_process is not None:
            try:
                self._pipewire_process.terminate()
                self._pipewire_process.wait(timeout=2)
            except Exception:
                try:
                    self._pipewire_process.kill()
                except Exception:
                    pass
            self._pipewire_process = None

        self.is_active = False
        self._created_module_id = None
