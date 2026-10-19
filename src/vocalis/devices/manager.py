import sys
import sounddevice as sd
from typing import List, Dict, Optional, Tuple
from vocalis.devices.virtual_linux import LinuxVirtualMic
from vocalis.devices.virtual_windows import WindowsVirtualCable


class AudioDeviceManager:
    """
    Gerenciador multiplataforma de dispositivos de entrada e saída.
    """

    def __init__(self):
        self.linux_mic = LinuxVirtualMic() if sys.platform.startswith("linux") else None

    @staticmethod
    def get_input_devices() -> List[Dict]:
        """
        Retorna todos os microfones físicos/entradas disponíveis.
        """
        devices = []
        try:
            for idx, dev in enumerate(sd.query_devices()):
                if dev.get('max_input_channels', 0) > 0:
                    # Filtra monitores no Linux para deixar a lista limpa
                    name = dev.get('name', '')
                    devices.append({
                        'id': idx,
                        'name': name,
                        'channels': dev.get('max_input_channels'),
                        'samplerate': dev.get('default_samplerate', 44100)
                    })
        except Exception:
            pass
        return devices

    @staticmethod
    def get_output_devices() -> List[Dict]:
        """
        Retorna todos os dispositivos de saída de áudio disponíveis.
        """
        devices = []
        try:
            for idx, dev in enumerate(sd.query_devices()):
                if dev.get('max_output_channels', 0) > 0:
                    devices.append({
                        'id': idx,
                        'name': dev.get('name', ''),
                        'channels': dev.get('max_output_channels'),
                        'samplerate': dev.get('default_samplerate', 44100)
                    })
        except Exception:
            pass
        return devices

    def setup_virtual_sink(self) -> Tuple[bool, str, Optional[int]]:
        """
        Garante a existência de um destino de saída virtual.
        Retorna (sucesso, mensagem, device_index_de_saida).
        """
        if sys.platform.startswith("linux"):
            if self.linux_mic:
                success, msg = self.linux_mic.create_virtual_device()
                # Atualiza a lista de dispositivos para encontrar o sink criado
                outputs = self.get_output_devices()
                target_id = None
                for out in outputs:
                    if "vocalis" in out['name'].lower():
                        target_id = out['id']
                        break
                return success, msg, target_id
            return False, "LinuxVirtualMic indisponível", None

        elif sys.platform.startswith("win"):
            cables = WindowsVirtualCable.find_installed_cables()
            if cables:
                return True, f"Cabo virtual detectado: {cables[0]['name']}", cables[0]['id']
            else:
                return False, "Nenhum cabo de áudio virtual detectado (ex: VB-Audio Cable). Instale-o para criar a saída do microfone.", None

        return False, "Sistema operacional não suportado para microfone virtual.", None

    def teardown_virtual_sink(self) -> None:
        if self.linux_mic:
            self.linux_mic.remove_virtual_device()
