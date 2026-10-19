# Vocalis Studio - Release para Windows (x86_64)

Este diretório contém as instruções e scripts para compilação e download do executável `vocalis.exe` para Windows.

## Download do Executável (.exe)
O arquivo `vocalis.exe` é gerado automaticamente pelo **GitHub Actions** em cada release do repositório:
👉 [Acessar GitHub Releases](https://github.com/pedrodavi120/vocalis-noise-reduction/releases)

---

## Como Gerar o `vocalis.exe` no Windows Localmente

Caso você esteja em uma máquina com Windows e queira compilar seu próprio executável independente:

```bat
:: 1. Clone o repositório
git clone https://github.com/pedrodavi120/vocalis-noise-reduction.git
cd vocalis-noise-reduction

:: 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

:: 3. Instale os requisitos e o PyInstaller
pip install -r requirements.txt
pip install pyinstaller

:: 4. Gere o executável
pyinstaller vocalis.spec
```

O arquivo `vocalis.exe` estará pronto no diretório `dist/vocalis.exe` (ou você pode movê-lo para esta pasta `releases/windows/`).

---

## Microfone Virtual no Windows
Para utilizar o Vocalis em tempo real no Discord, OBS ou Zoom no Windows, certifique-se de instalar o driver gratuito:
- **VB-Audio Virtual Cable**: <https://vb-audio.com/Cable/>
