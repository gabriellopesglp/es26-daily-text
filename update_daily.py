import json
import datetime
import os

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

if __name__ == "__main__":
    update_daily_file()
