import sys
import sounddevice as sd
from typing import List, Dict, Optional, Tuple


class WindowsVirtualCable:
    """
    Auxiliar para detecção e configuração de Cabos de Áudio Virtuais no Windows.
    (VB-Audio Virtual Cable, Virtual Audio Cable, VoiceMeeter, etc.)
    """

    KNOWN_VIRTUAL_CABLE_KEYWORDS = [
        "cable input",
        "vb-audio",
        "virtual audio cable",
        "voicemeeter",
        "line 1 (virtual",
        "cable-a input",
        "cable-b input"
    ]

    @classmethod
    def is_windows(cls) -> bool:
        return sys.platform.startswith("win")

    @classmethod
    def find_installed_cables(cls) -> List[Dict]:
        """
        Retorna todos os dispositivos de saída virtuais reconhecidos no Windows.
        """
        cables = []
        try:
            devices = sd.query_devices()
            for idx, dev in enumerate(devices):
                if dev.get('max_output_channels', 0) > 0:
                    name_lower = dev.get('name', '').lower()
                    if any(kw in name_lower for kw in cls.KNOWN_VIRTUAL_CABLE_KEYWORDS):
                        cables.append({
                            'id': idx,
                            'name': dev.get('name'),
                            'hostapi': dev.get('hostapi'),
                            'channels': dev.get('max_output_channels')
                        })
        except Exception:
            pass
        return cables

    @classmethod
    def get_instructions_url(cls) -> str:
        return "https://vb-audio.com/Cable/"
