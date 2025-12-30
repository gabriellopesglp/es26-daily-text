import json
import datetime
import os
from email.utils import format_datetime
from datetime import timezone, timedelta

# Caminhos dos arquivos
SOURCE_FILE = 'daily_text.json'
TARGET_FILE = 'hoje.json'

def update_daily_file():
    # Verificar se o arquivo fonte existe
    if not os.path.exists(SOURCE_FILE):
        print(f"Erro: Arquivo {SOURCE_FILE} não encontrado.")
        return

    # Ler todos os textos
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        all_texts = json.load(f)

    # Obter data de hoje (UTC ou ajustar fuso se necessário)
    # GitHub Actions roda em UTC. Se seu público é BR, talvez queira UTC-3
    # Vou usar UTC por padrão, mas podemos ajustar para timezone BRT
    
    # Ajuste para horário de Brasília (UTC-3) simples
    utc_now = datetime.datetime.utcnow()
    br_time = utc_now - datetime.timedelta(hours=3)
    
    month = f"{br_time.month:02d}"
    day = f"{br_time.day:02d}"
    key = f"{month}-{day}"
    
    print(f"Buscando texto para a data: {key} (Brasília)")

    # Buscar o texto do dia
    daily_content = all_texts.get(key)

    if daily_content:
        # Salvar no arquivo alvo
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(daily_content, f, ensure_ascii=False, indent=2)
        print(f"Sucesso! Arquivo {TARGET_FILE} atualizado com o texto de {key}.")
    else:
        # Fallback ou erro (ex: dia 29 de fev em ano não bissexto se não houver)
        print(f"Aviso: Texto não encontrado para {key}.")
        # Opcional: Criar um JSON vazio ou com erro para não quebrar o app
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump({"error": "Texto não encontrado", "date": key}, f)
        daily_content = {"title": "Texto não encontrado", "content": "Sem conteúdo para a data", "full_date": f"2026-{month}-{day}"}

    pub = format_datetime(br_time.replace(tzinfo=timezone(timedelta(hours=-3))))
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Texto do Dia</title>
    <link>hoje.json</link>
    <description>Texto bíblico diário</description>
    <language>pt-BR</language>
    <lastBuildDate>{pub}</lastBuildDate>
    <item>
      <title><![CDATA[{daily_content['title']}]]></title>
      <description><![CDATA[{daily_content['content']}]]></description>
      <link>hoje.json</link>
      <guid isPermaLink="false">{daily_content['full_date']}</guid>
      <pubDate>{pub}</pubDate>
    </item>
  </channel>
</rss>
'''
    with open('rss.xml', 'w', encoding='utf-8') as f:
        f.write(xml)

if __name__ == "__main__":
    update_daily_file()
