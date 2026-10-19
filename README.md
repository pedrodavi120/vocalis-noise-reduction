# Vocalis - AI-Powered Noise Reduction Studio & Virtual Microphone

<p align="center">
  <img src="logo.png" alt="Vocalis Logo" width="360" />
</p>

<p align="center">
  <strong>Estúdio profissional de remoção de ruídos de áudio por IA e microfone virtual em tempo real para Linux e Windows.</strong>
</p>

<p align="center">
  <a href="https://github.com/pedrodavi120/vocalis-noise-reduction/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-purple.svg" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/UI-PySide6%20%28Qt6%29-green.svg" alt="PySide6 Qt6" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-orange.svg" alt="Windows & Linux" />
</p>

---

## Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Arquitetura de Áudio](#arquitetura-de-áudio)
- [Como Funciona o Microfone Virtual](#como-funciona-o-microfone-virtual)
  - [No Linux](#no-linux)
  - [No Windows](#no-windows)
- [Instaladores Oficiais (Windows e Linux)](#instaladores-oficiais-windows-e-linux)
- [Instalação e Execução via Código](#instalação-e-execução-via-código)
- [Geração dos Instaladores e Binários](#geração-dos-instaladores-e-binários)
- [Testes Automatizados](#testes-automatizados)
- [Como Contribuir](#como-contribuir)
- [Licença](#licença)

---

## Visão Geral

O **Vocalis** é um estúdio de engenharia e processamento acústico que combina algoritmos de **subtração espectral estocástica por IA**, **filtros acústicos passa-alta Butterworth** e **Noise Gates adaptativos**. 

Além de gravar e processar arquivos de áudio gravados, o Vocalis atua como uma ponte de baixa latência em tempo real, permitindo utilizar sua voz tratada diretamente no **Discord**, **OBS Studio**, **Zoom**, **Google Meet**, **Teams** e jogos online.

---

## Funcionalidades Principais

1. **Gravação Rápida & Limpeza**:
   - Grave sua voz com animação de onda em tempo real (*Visualizer*).
   - Limpe ruídos de fundo (ventiladores, ruído elétrico, trânsito) com um único clique.
   - Ouça o comparativo imediato entre o original e o áudio limpo.

2. **Processamento de Arquivos de Áudio (Batch / File Mode)**:
   - Suporte para carregar qualquer arquivo de áudio (`.wav`, `.mp3`, `.ogg`, `.flac`, `.m4a`).
   - Controle granular da intensidade da redução de ruído (0% a 100%).
   - Pré-escuta do áudio antes e depois da limpeza.
   - Exportação do arquivo tratado em alta fidelidade.

3. **Microfone Virtual em Tempo Real (Low-Latency Streaming)**:
   - Captura do microfone físico com monitoramento em tempo real.
   - Pipeline acústico completo:
     - **High-Pass Filter (80Hz)**: elimina ruídos subsônicos, batidas na mesa e hum elétrico.
     - **Noise Gate com Histerese**: silencia ruídos de teclado mecânico e respiração quando o usuário não estiver falando.
     - **Atenuação Espectral por IA**: remove zumbidos constantes e ruído de fundo.
   - Medidor de nível VU Meter em tempo real com decibéis (dBFS).

---

## Como Funciona o Microfone Virtual

### No Linux
No Linux, o Vocalis cria dinamicamente em tempo de execução nós de áudio virtuais compatíveis com **PipeWire** e **PulseAudio**:
- Cria automaticamente o sink virtual `Vocalis Stream Input` e o microfone virtual `Vocalis Virtual Microphone`.
- O dispositivo fica imediatamente visível nas configurações de som do sistema operacional, navegadores, Discord e OBS.
- Ao encerrar a aplicação, os módulos e nós virtuais são liberados automaticamente, sem deixar lixo no sistema.

### No Windows
No Windows, o Vocalis roteia o streaming tratado para um cabo de áudio virtual padrão de mercado:
1. Instale o driver gratuito [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) (ou Virtual Audio Cable - VAC).
2. Abra o Vocalis na aba **Tempo Real**. O aplicativo detectará automaticamente o dispositivo de saída virtual (ex: `CABLE Input`).
3. Clique em **Ativar Microfone Virtual**.
4. No seu aplicativo favorito (Discord, Zoom, Meet, OBS), selecione **CABLE Output** como seu dispositivo de entrada (Microfone).

---

## Instaladores Oficiais (Windows e Linux)

Na aba [Releases](https://github.com/pedrodavi120/vocalis-noise-reduction/releases) estão disponíveis pacotes e instaladores prontos para uso em ambiente de produção:

| Plataforma | Formato | Descrição |
| :--- | :--- | :--- |
| **Windows 10 / 11** (x64) | `Vocalis-Setup-vX.Y.Z-x64.exe` | **Instalador com assistente**, atalhos no Menu Iniciar/Área de Trabalho e desinstalador limpo. |
| **Windows 10 / 11** (x64) | `vocalis.exe` | Binário standalone portátil (sem necessidade de instalação). |
| **Linux (Debian, Ubuntu, Mint)** | `vocalis_X.Y.Z_amd64.deb` | **Instalador de pacote nativo** com integração com o menu de aplicativos e dependências de áudio. |
| **Linux (Universal)** | `Vocalis-X.Y.Z-x86_64.AppImage` | Pacote universal executável em qualquer distribuição Linux sem root. |
| **Linux (Standalone)** | `vocalis` | Binário executável independente para linha de comando / scripts. |

---

## Instalação e Execução via Código

### Pré-requisitos
- Python 3.10 ou superior.
- Git.

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/pedrodavi120/vocalis-noise-reduction.git
cd vocalis-noise-reduction

# 2. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o Vocalis
python run.py
```

---

## Geração dos Instaladores e Binários

### 1. Windows (10 e 11)

Para gerar o instalador do Windows localmente, é necessário ter o [Inno Setup 6](https://jrsoftware.org/isdl.php) instalado (ou via `winget install JRSoftware.InnoSetup` / `choco install innosetup`):

```powershell
# 1. Compilar executável base com PyInstaller
pyinstaller vocalis.spec

# 2. Compilar instalador oficial Inno Setup
powershell -ExecutionPolicy Bypass -File packaging/windows/build_installer.ps1
```
O instalador final `Vocalis-Setup-v1.0.0-x64.exe` será gerado em `dist/`.

### 2. Linux (Debian `.deb` e AppImage)

No ambiente Linux:

```bash
# 1. Compilar executável base com PyInstaller
pyinstaller vocalis.spec

# 2. Gerar pacote Debian / Ubuntu (.deb)
chmod +x packaging/linux/build_deb.sh
./packaging/linux/build_deb.sh 1.0.0

# 3. Gerar pacote universal AppImage
chmod +x packaging/linux/build_appimage.sh
./packaging/linux/build_appimage.sh 1.0.0
```
Os arquivos gerados estarão disponíveis em `dist/`:
- `vocalis_1.0.0_amd64.deb`
- `Vocalis-1.0.0-x86_64.AppImage`
- `vocalis` (binário nativo)

---

## Testes Automatizados

O projeto conta com suíte de testes unitários para filtros matemáticos, atenuação e processamento de arquivos:

```bash
pytest -v
```

---

## Como Contribuir

Contribuições são muito bem-vindas! Consulte o guia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre fluxo de trabalho, boas práticas e estilo de código.

---

## Autoria e Propriedade

- **Proprietária do Projeto**: [Void Studio](https://www.voidstudio.com.br)
- **Desenvolvedor Responsável & CEO**: [Pedro Davi](https://github.com/pedrodavi120) (<pedrodavi120@gmail.com>)

---

## Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

Copyright © 2024-2026 **[Void Studio](https://www.voidstudio.com.br)** & **Pedro Davi**. Todos os direitos reservados.
