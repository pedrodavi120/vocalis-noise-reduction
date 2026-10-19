# Contribuindo com o Vocalis

Obrigado pelo interesse em contribuir com o **Vocalis**! Este é um projeto de código aberto voltado para processamento de áudio com inteligência artificial e criação de microfone virtual em tempo real para Linux e Windows.

---

## Como Contribuir

1. **Faça um Fork** do projeto no GitHub.
2. **Crie uma Branch** para sua feature ou correção:
   ```bash
   git checkout -b feature/minha-melhoria
   ```
3. **Instale as dependências** em um ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Escreva testes** e valide com `pytest`:
   ```bash
   pytest
   ```
5. **Abra um Pull Request** detalhando as mudanças realizadas.

---

## Padrões de Código

- Utilize Python 3.10+ com tipagem estática (*type hints*) sempre que possível.
- Separe regras de negócio de áudio das classes de interface gráfica (`PySide6`).
- Não utilize emojis em textos de interface de usuário (UI); utilize ícones vetoriais.
