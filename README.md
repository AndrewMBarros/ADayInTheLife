# 📅 A Day in the Life Bot

Bot que verifica diariamente a seção **"A day in the life"** do site [BeatlesPerú](https://web.beatlesperu.com/) e envia para o Telegram os acontecimentos históricos relacionados aos Beatles que ocorreram nesse mesmo dia, em anos anteriores — com título e link da matéria completa.

Roda automaticamente 1x por dia via **GitHub Actions**, sem precisar de servidor.

---

## Como funciona

1. Acessa a home do site e localiza a lista `<ul class="aday">`
2. Extrai ano, título e link de cada acontecimento listado
3. Entra em cada link individual para capturar o título completo da matéria
4. Envia tudo formatado para um chat/canal do Telegram via Bot API

---

## Stack

- Python 3.11
- [requests](https://pypi.org/project/requests/) — requisições HTTP
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) — parsing de HTML
- [GitHub Actions](https://github.com/features/actions) — agendamento e execução (cron)
- [Telegram Bot API](https://core.telegram.org/bots/api) — envio das mensagens

---

## Configuração

### 1. Criar o bot no Telegram
Fale com [@BotFather](https://t.me/BotFather), use `/newbot` e guarde o token gerado.

### 2. Descobrir seu chat_id
Envie uma mensagem para o seu bot e acesse:
```
https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
```
O `chat_id` estará no campo `"chat":{"id": ...}`.

### 3. Instalar dependências (uso local)
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
export TELEGRAM_TOKEN="seu_token_aqui"
export TELEGRAM_CHAT_ID="seu_chat_id_aqui"
```

### 5. Rodar localmente
```bash
python beatles_bot.py
```

---

## Automação (GitHub Actions)

O workflow em [`.github/workflows/daily.yml`](.github/workflows/daily.yml) roda o bot automaticamente todos os dias.

**Configurar secrets do repositório:**
`Settings → Secrets and variables → Actions → New repository secret`

| Nome | Valor |
|---|---|
| `TELEGRAM_TOKEN` | Token do seu bot |
| `TELEGRAM_CHAT_ID` | ID do chat/canal de destino |

O horário padrão está configurado em UTC no arquivo do workflow — ajuste conforme necessário.

Também é possível rodar manualmente a qualquer momento pela aba **Actions** do repositório, usando o botão **Run workflow**.

---

## Estrutura do repositório

```
.
├── beatles_bot.py              # Script principal
├── requirements.txt            # Dependências Python
└── .github/
    └── workflows/
        └── daily.yml           # Agendamento diário via GitHub Actions
```

---

## Aviso

Este projeto faz web scraping de um site de terceiros ([beatlesperu.com](https://web.beatlesperu.com/)) para fins pessoais e educacionais. Caso a estrutura do site seja alterada, o script pode precisar de ajustes na extração de dados.

---

## Licença

Uso livre para fins pessoais e educacionais.
