# Vocalis Studio - Release para Linux (x86_64)

Este diretório contém o executável binário independente do **Vocalis Studio** para distribuições Linux (Ubuntu, Debian, Fedora, Arch, Pop!_OS, etc.).

## Como Executar

Não é necessário ter Python instalado na máquina:

```bash
# 1. Dê permissão de execução (se necessário)
chmod +x vocalis

# 2. Execute diretamente:
./vocalis
```

## Requisitos de Sistema
- Servidor de áudio: **PipeWire** ou **PulseAudio** (padrão em qualquer distribuição Linux moderna).
- Biblioteca de áudio PortAudio (`libportaudio2`), caso sua distro não a tenha pré-instalada (`sudo apt install libportaudio2`).
