"""
Bot que verifica "A day in the life" em beatlesperu.com,
entra em cada notícia do dia, pega o título e envia tudo pro Telegram.

Requisitos:
    pip install requests beautifulsoup4 --break-system-packages

Configuração:
    Preencha as variáveis TELEGRAM_TOKEN e TELEGRAM_CHAT_ID abaixo
    (ou defina como variáveis de ambiente, veja o final do arquivo).
"""

import os
import time
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------

SITE_URL = "https://web.beatlesperu.com/"

# Pegue com o @BotFather no Telegram (crie um bot e copie o token)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8869715381:AAHOoaprOrw80WF36BzmtTbuz_TC-xJNUdM")

# ID do chat/canal/grupo para onde enviar as mensagens.
# Para descobrir o seu chat_id, mande uma mensagem para o bot e acesse:
# https://api.telegram.org/bot<TOKEN>/getUpdates
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "338839574")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 15


# ---------------------------------------------------------------------------
# SCRAPING
# ---------------------------------------------------------------------------

def buscar_noticias_do_dia():
    """Acessa a home do site e extrai a lista de notícias da classe 'aday'."""
    resp = requests.get(SITE_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    lista = soup.find("ul", class_="aday")

    if lista is None:
        print("Não encontrei a classe 'aday' na página. O site pode ter mudado.")
        return []

    noticias = []
    for li in lista.find_all("li"):
        ano_tag = li.find("b")
        link_tag = li.find("a")

        if not link_tag or not link_tag.get("href"):
            continue

        ano = ano_tag.get_text(strip=True).rstrip(":").strip() if ano_tag else ""
        texto_link = link_tag.get_text(strip=True)
        url = link_tag["href"]

        noticias.append({
            "ano": ano,
            "titulo_lista": texto_link,
            "url": url,
        })

    return noticias


def buscar_titulo_da_noticia(url):
    """Entra na página da notícia e tenta extrair o título real do artigo."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Tenta achar o título de várias formas comuns em sites WordPress
    candidatos = [
        soup.find("h1", class_="entry-title"),
        soup.find("h1", class_="post-title"),
        soup.find("h1"),
        soup.find("meta", property="og:title"),
        soup.title,
    ]

    for c in candidatos:
        if c is None:
            continue
        if c.name == "meta":
            texto = c.get("content", "").strip()
        else:
            texto = c.get_text(strip=True)
        if texto:
            return texto

    return None


def montar_lista_completa():
    """Junta o scraping da home com o título de cada notícia individual."""
    noticias = buscar_noticias_do_dia()
    resultado = []

    for n in noticias:
        titulo_real = buscar_titulo_da_noticia(n["url"])
        titulo_final = titulo_real or n["titulo_lista"]

        resultado.append({
            "ano": n["ano"],
            "titulo": titulo_final,
            "url": n["url"],
        })

        # pequena pausa pra não sobrecarregar o site
        time.sleep(0.5)

    return resultado


# ---------------------------------------------------------------------------
# TELEGRAM
# ---------------------------------------------------------------------------

def enviar_mensagem_telegram(texto):
    """Envia uma mensagem de texto para o chat configurado."""
    api_url = f"https://api.telegram.org/bot{"8869715381:AAHOoaprOrw80WF36BzmtTbuz_TC-xJNUdM"}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    resp = requests.post(api_url, data=payload, timeout=REQUEST_TIMEOUT)

    if resp.status_code != 200:
        print(f"Erro ao enviar mensagem: {resp.status_code} - {resp.text}")
    return resp.ok


def montar_texto_mensagem(noticias):
    """Formata a lista de notícias em texto pronto para o Telegram (HTML)."""
    if not noticias:
        return "Nenhuma notícia encontrada hoje na seção 'A day in the life'."

    linhas = ["<b>📅 A day in the life — Hoje na história dos Beatles</b>\n"]
    for n in noticias:
        linhas.append(f"<b>{n['ano']}:</b> {n['titulo']}\n{n['url']}\n")

    return "\n".join(linhas)


# O Telegram limita mensagens a 4096 caracteres. Se a lista for grande,
# quebramos em vários envios.
def enviar_em_blocos(noticias, tamanho_maximo=4000):
    bloco_atual = ["<b>📅 A day in the life — Hoje na história dos Beatles</b>\n"]
    tamanho_atual = len(bloco_atual[0])

    for n in noticias:
        item = f"<b>{n['ano']}:</b> {n['titulo']}\n{n['url']}\n"
        if tamanho_atual + len(item) > tamanho_maximo:
            enviar_mensagem_telegram("\n".join(bloco_atual))
            bloco_atual = []
            tamanho_atual = 0
        bloco_atual.append(item)
        tamanho_atual += len(item)

    if bloco_atual:
        enviar_mensagem_telegram("\n".join(bloco_atual))


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("Buscando notícias do dia...")
    noticias = montar_lista_completa()

    print(f"{len(noticias)} notícias encontradas. Enviando para o Telegram...")
    enviar_em_blocos(noticias)

    print("Concluído.")


if __name__ == "__main__":
    main()