
# ⚔️ BOT Clash of Clans – [PRE-ALPHA] 🛠️

![Status](https://img.shields.io/badge/status-Em%20Desenvolvimento-orange)
![Versão](https://img.shields.io/badge/vers%C3%A3o-Pre--Alpha-blue)
![Feito com Python](https://img.shields.io/badge/feito%20com-Python%203.x-yellow)
![Licença](https://img.shields.io/badge/licen%C3%A7a-A%20Escolher%20depois-lightgrey)

> Um bot experimental automatizado para Clash of Clans, focado em ataques com Super Goblins 💥  
> Totalmente insano, visual, inteligente, com **modo de depuração avançado**, deploy simétrico e pronto para destruir vilas!  
> **Ainda em fase Pre-Alpha, mas já mostrando os dentes! 😈**

[🔗 Repositório no GitHub](https://github.com/AkumaHalls/ClashZ-COC-Simple-farm-BOT)

---

## 🚀 Funcionalidades (em desenvolvimento)

- 🔍 **Reconhecimento de tela** com OpenCV para identificar botões do jogo.
- 🎯 **Deploy automático e inteligente** de Super Goblins nas bordas da vila.
- 🕹️ **Ciclos completos de ataque** com encerramento e retorno à base.
- 🛠️ **Modo Debug ativado!** Imagens de falhas são salvas para ajuste fino do bot.
- 🧠 **Área de deploy adaptável** ao tamanho da sua tela ou personalizada manualmente.

---

## 📷 Pré-requisitos

- 🖥️ Emulador LDPlayer aberto com o Clash of Clans visível na tela.
- 📁 Pasta `imagens/` com os seguintes arquivos:
  - `atacar_vila.png`
  - `buscar_agora.png`
  - `super_goblin.png`
  - `encerrar_batalha.png`
  - `confirmar_encerrar.png`
  - `retornar_base.png`
- 💻 Python 3.x com as libs:
  ```bash
  pip install pyautogui opencv-python pillow numpy
  ```

---

## 🧪 Como Rodar (modo teste)

```bash
python bot_clash.py
```

⚠️ **Importante:** o bot atualmente só executa **1 ataque por vez** e está com **debug ativado** para facilitar os testes!

---

## 📁 Estrutura do Projeto

```
📦 ClashZ-COC-Simple-farm-BOT/
├── bot_clash.py
├── imagens/
│   ├── atacar_vila.png
│   ├── buscar_agora.png
│   └── ... (restante)
├── imagens_debug/
│   └── (debug screenshots salvos aqui)
```

---

## ⏳ Roadmap (o que vem por aí)

- [ ] Múltiplos ataques em sequência
- [ ] Relatórios automáticos após cada ciclo
- [ ] Modo stealth (sem mouse mexendo)
- [ ] Painel de configuração amigável
- [ ] Suporte a diferentes tropas (além dos Goblins)

---

## ⚠️ Aviso

> Este bot é um **projeto experimental** com fins **educacionais**.  
> O uso de bots é contra os Termos de Serviço da Supercell.  
> **Use por sua conta e risco. Não me responsabilizo por vilas banidas!**

---

## 🧙‍♂️ Desenvolvedor

Feito com 💻, raiva de farmar manualmente e umas boas xícaras de café ☕  
por **[@AkumaHalls](https://github.com/AkumaHalls)**

---

## 📜 Licença

Escolha sua licença (MIT, GPLv3, etc) e substitua esta seção.  
Recomendo [MIT](https://choosealicense.com/licenses/mit/) se quiser liberdade total para quem for usar.

---

🔥 **Deixe uma ⭐ se você curte automação em Clash of Clans!**
