import os
import re
import json
import datetime
import unicodedata

# Mapeamento de meses
MONTHS = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
}

# Mapeamento de livros bíblicos (Nome extenso -> Abreviatura)
BIBLE_BOOKS = {
    'Gênesis': 'Gên.', 'Êxodo': 'Êx.', 'Levítico': 'Lev.', 'Números': 'Núm.', 'Deuteronômio': 'Deut.',
    'Josué': 'Jos.', 'Juízes': 'Juí.', 'Rute': 'Rute', 'Primeiro Samuel': '1 Sam.', 'Segundo Samuel': '2 Sam.',
    'Primeiro Reis': '1 Reis', 'Segundo Reis': '2 Reis', 'Primeiro Crônicas': '1 Crôn.', 'Segundo Crônicas': '2 Crôn.',
    'Esdras': 'Esd.', 'Neemias': 'Neem.', 'Ester': 'Est.', 'Jó': 'Jó', 'Salmos': 'Sal.', 'Salmo': 'Sal.', 'Provérbios': 'Pro.',
    'Eclesiastes': 'Ecl.', 'Cântico de Salomão': 'Cân.', 'Isaías': 'Isa.', 'Jeremias': 'Jer.', 'Lamentações': 'Lam.',
    'Ezequiel': 'Eze.', 'Daniel': 'Dan.', 'Oseias': 'Ose.', 'Joel': 'Joel', 'Amós': 'Amós', 'Obadias': 'Oba.',
    'Jonas': 'Jon.', 'Miqueias': 'Miq.', 'Naum': 'Naum', 'Habacuque': 'Hab.', 'Sofonias': 'Sof.', 'Ageu': 'Ageu',
    'Zacarias': 'Zac.', 'Malaquias': 'Mal.',
    'Mateus': 'Mat.', 'Marcos': 'Mar.', 'Lucas': 'Luc.', 'João': 'João', 'Atos': 'Atos',
    'Romanos': 'Rom.', 'Primeira Coríntios': '1 Cor.', 'Segunda Coríntios': '2 Cor.', 'Gálatas': 'Gál.',
    'Efésios': 'Efé.', 'Filipenses': 'Fil.', 'Colossenses': 'Col.',
    'Primeira Tessalonicenses': '1 Tes.', 'Segunda Tessalonicenses': '2 Tes.',
    'Primeira Timóteo': '1 Tim.', 'Segunda Timóteo': '2 Tim.', 'Tito': 'Tito', 'Filemom': 'File.',
    'Hebreus': 'Heb.', 'Tiago': 'Tia.', 'Primeira Pedro': '1 Ped.', 'Segunda Pedro': '2 Ped.',
    'Primeira João': '1 João', 'Segunda João': '2 João', 'Terceira João': '3 João',
    'Judas': 'Judas', 'Apocalipse': 'Apo.'
}

def decode_rtf_char(match):
    try:
        val = int(match.group(1))
        return chr(val)
    except:
        return match.group(0)

def clean_rtf(text):
    # Decodificar caracteres unicode \uN?
    text = re.sub(r'\\u(-?\d+)\?', decode_rtf_char, text)
    
    # Substituir \par por quebra de linha
    text = text.replace('\\par', '\n')
    
    # Remover tags RTF
    text = re.sub(r'\\[a-z]+\d*', ' ', text)  # Remove \tag ou \tag123
    text = re.sub(r'\{.*?\}', '', text)       # Remove conteúdo entre chaves (pode ser agressivo demais, ajustar se perder texto)
    
    # Limpeza extra de chaves remanescentes e espaços
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'\s+', ' ', text).strip()
    # Remover caracteres invisíveis comuns
    text = text.replace('\xa0', ' ')
    
    # Normalizar Unicode
    text = unicodedata.normalize('NFC', text)
    
    return text

def parse_reference(ref_text):
    # Debug para ver o que chega
    original_ref = ref_text
    ref_text = ref_text.replace('\xa0', ' ') # Garantir limpeza de nbsp
    ref_text = unicodedata.normalize('NFC', ref_text)
    
    # Exemplo: "Primeira Coríntios capítulo 14 versículo 2" -> "1 Cor. 14:20"
    
    # Tentar encontrar o livro
    book_abbr = ""
    remaining = ref_text
    
    # Ordenar livros pelo tamanho do nome decrescente para evitar match parcial errado (ex: "João" em "Primeira João")
    sorted_books = sorted(BIBLE_BOOKS.keys(), key=len, reverse=True)
    
    for book in sorted_books:
        # Debug especifico
        if "Salmo 37" in ref_text and book == "Salmo":
             print(f"DEBUG: Testing book '{book}' against '{ref_text}'")
             print(f"DEBUG: '{book.lower()}' in '{ref_text.lower()}' -> {book.lower() in ref_text.lower()}")
              
        if book.lower() in ref_text.lower():
            book_abbr = BIBLE_BOOKS[book]
            if "Salmo 37" in ref_text:
                 print(f"DEBUG: Match found! Abbr: {book_abbr}")
            # Remover o nome do livro para processar capitulo e versiculo
            # Remover o nome do livro para processar capitulo e versiculo
            # Usando regex case insensitive para remover
            remaining = re.sub(re.escape(book), '', ref_text, flags=re.IGNORECASE)
            break
    
    if not book_abbr:
        return ref_text # Falha no match do livro
        
    # Extrair capítulo e versículo
    # Padrões: "capítulo 14 versículo 2", "capítulo 14 versículos 2, 3", etc.
    
    # Simplificar string
    remaining = remaining.lower().replace('capítulo', '').replace('versículos', '').replace('versículo', '').replace('vers.', '')
    
    # Extrair números
    nums = re.findall(r'\d+', remaining)
    
    if len(nums) >= 2:
        chapter = nums[0]
        verse = nums[1]
        # Se houver range (ex: 14:2-4), o regex \d+ pega 2 e 4 separados.
        # Vamos tentar pegar o resto da string como versículos se não for padrão simples
        pass
        return f"{book_abbr} {chapter}:{verse}"
    elif len(nums) == 1:
        # Caso onde só tem versículo (ex: Judas 1 ou Obadias 1 - livros de 1 capitulo)
        # Ou Salmo 119:105 onde o capitulo ja foi pego como numero
        # Se o livro tem capitulos, assume-se Capitulo:Versiculo.
        # Mas em livros de 1 capitulo (Judas, Filemom, 2 João, 3 João, Obadias), as vezes cita-se apenas o versículo ou "versículo X".
        # O padrão do texto é "Judas versículo 2". O nums terá [2].
        if book_abbr in ['Judas', 'File.', '2 João', '3 João', 'Oba.']:
            return f"{book_abbr} {nums[0]}"
        
        # Se for Salmo 23 (sem versiculo citado? Raro texto diario ser assim)
        # Vamos assumir que é versículo se estiver escrito "versículo"
        if 'vers' in ref_text.lower():
             return f"{book_abbr} {nums[0]}"
             
        # Tentar salvar o que der
        return f"{book_abbr} {nums[0]}"

    return ref_text

def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Decodificar unicode primeiro para facilitar regex de texto
    content = re.sub(r'\\u(-?\d+)\?', decode_rtf_char, content)
    
    days = []
    
    # Dividir por dias. O padrão parece ser:
    # \pard ... \b Dia da semana, Dia.º de Mês\par
    # \pard ... \i Texto bíblico. \u8212?
    # HYPERLINK ... Referência
    
    # Vamos tentar uma abordagem linha a linha após limpar tags de formatação básicas mas mantendo estrutura
    
    # Regex para capturar a data
    # Ex: Quinta-feira, 1.º de janeiro
    date_pattern = r'(Domingo|Segunda-feira|Terça-feira|Quarta-feira|Quinta-feira|Sexta-feira|Sábado), (\d+)(?:\.|.º)? de ([a-zç]+)'
    
    # Regex para capturar texto e referência
    # O texto está geralmente entre a data e o travessão (\u8212)
    # A referência está dentro de um field HYPERLINK
    
    # Vou usar splits pelo padrão de data para separar os blocos
    
    # Primeiro, simplificar o RTF mantendo apenas textos e tags essenciais
    # Remover cabeçalho longo
    start_idx = content.find('Janeiro') if 'Janeiro' in content else 0
    if start_idx == -1: start_idx = 0
    
    # Simplificação agressiva para texto plano com marcadores
    # Substituir parágrafos por NEWLINE
    text_content = content.replace('\\par', '\n')
    
    # Extrair hyperlinks separadamente ou processar o texto misturado?
    # O texto do link (referência) está visível no RTF como:
    # {\field{\*\fldinst {HYPERLINK "..." }}{\fldrslt{... TEXTO DA REF ...}}}
    
    # Vou substituir a estrutura do hyperlink apenas pelo texto visível dele
    def replace_hyperlink(match):
        return match.group(1) # O grupo 1 será o texto visível
        
    # Regex para extrair texto do hyperlink: \fldrslt{...texto...}
    # Atenção com chaves aninhadas. RTF é chato.
    # Mas no exemplo parece simples: \fldrslt{\cs4... \ul Texto }
    
    # Vamos tentar extrair blocos de texto que parecem datas
    lines = text_content.split('\n')
    
    current_date = None
    current_text = []
    current_ref = None
    
    extracted_data = []
    
    for line in lines:
        # Limpar a linha de tags RTF para verificação
        clean_line = re.sub(r'\\[a-z]+\d*', '', line)
        clean_line = re.sub(r'\{.*?\}', '', clean_line)
        clean_line = clean_line.replace('}', '').replace('{', '').strip()
        
        # Verificar se é data
        date_match = re.search(date_pattern, clean_line, re.IGNORECASE)
        if date_match:
            # Se já tínhamos um dia processando, salvar
            if current_date:
                full_text = " ".join(current_text).strip()
                # Separar texto da referência se estiverem colados
                # Geralmente o texto termina com travessão "—" (u8212)
                # No RTF cru: \u8212?
                
                # Tentar extrair referência do texto acumulado se não achou separadamente
                # Mas a referência geralmente vem depois
                
                pass
            
            # Novo dia
            day = int(date_match.group(2))
            month_name = date_match.group(3).lower()
            month = MONTHS.get(month_name, 1)
            
            # Assumir ano 2026
            date_str = f"2026-{month:02d}-{day:02d}"
            
            current_date = date_str
            current_text = []
            current_ref = None
            continue
            
        if current_date:
            # Estamos dentro de um bloco de dia
            # Tentar identificar referência e texto
            
            # No RTF, a referência está dentro de um field.
            # Vamos procurar no RAW line (line original) por hyperlinks
            if 'HYPERLINK' in line:
                # Extrair o texto da referência
                # Padrão: \fldrslt{... Primeira Coríntios ...}
                ref_match = re.search(r'\\fldrslt\{(.*?)\}', line)
                if ref_match:
                    raw_ref = ref_match.group(1)
                    # Limpar tags RTF de dentro da ref
                    clean_ref_text = re.sub(r'\\[a-z]+\d*', ' ', raw_ref)
                    clean_ref_text = re.sub(r'[\{\}]', '', clean_ref_text).strip()
                    # Limpar caracteres estranhos
                    clean_ref_text = clean_ref_text.replace(' cs4', '').replace('ulnone', '').strip()
                    
                    parsed_ref = parse_reference(clean_ref_text)
                    current_ref = parsed_ref
            
            # Capturar texto do dia
            # O texto vem antes do hyperlink, geralmente terminando em \u8212?
            # Se a linha não é hyperlink e tem conteúdo
            if 'HYPERLINK' not in line:
                # Limpar linha
                txt = re.sub(r'\\[a-z]+\d*', ' ', line)
                txt = re.sub(r'[\{\}]', '', txt).strip()
                if txt:
                    # Remover travessão se houver
                    txt = txt.replace('—', '').replace('-', '').strip()
                    if len(txt) > 5: # Evitar lixo curto
                        current_text.append(txt)
            
            # Se a linha TEM hyperlink, pode ter parte do texto antes dele
            elif 'HYPERLINK' in line:
                 # Tentar pegar o que vem antes do \field
                 parts = line.split(r'{\field')
                 if len(parts) > 0:
                     pre_text = parts[0]
                     txt = re.sub(r'\\[a-z]+\d*', ' ', pre_text)
                     txt = re.sub(r'[\{\}]', '', txt).strip()
                     # O travessão \u8212 costuma estar aqui
                     txt = txt.replace('—', '').strip()
                     if txt:
                         current_text.append(txt)

            # Verificar se completamos o dia (temos ref e texto)
            # Na verdade, como processamos linha a linha, melhor acumular e salvar no final ou na troca de data
    
    # O loop acima é frágil porque o RTF pode quebrar linha onde não esperamos.
    # Abordagem alternativa: Regex no arquivo inteiro.
    
    return []

# Abordagem 2: Regex no conteúdo inteiro
def extract_all_days(base_path):
    all_data = []
    
    files = sorted([f for f in os.listdir(base_path) if f.endswith('.rtf')])
    
    for filename in files:
        file_path = os.path.join(base_path, filename)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
            
        # 1. Decodificar Unicode
        content = re.sub(r'\\u(-?\d+)\?', decode_rtf_char, raw_content)
        
        # 2. Simplificar estrutura RTF para algo processável
        # Remover headers antes do primeiro dia
        # Padrão de dia: "Quinta-feira, 1.º de janeiro"
        # Vamos achar todos os indices de datas
        
        date_pattern = r'(Domingo|Segunda-feira|Terça-feira|Quarta-feira|Quinta-feira|Sexta-feira|Sábado), (\d+)(?:\.|.º)? de ([a-zç]+)'
        
        # Encontrar todas as datas e suas posições
        matches = list(re.finditer(date_pattern, content, re.IGNORECASE))
        
        # Descobrir o ano pelo nome do arquivo (ex: es26_T_12.rtf -> 2026, es25_T_12.rtf -> 2025)
        year_match = re.search(r'es(\d{2})_T_\d{2}\.rtf', filename)
        year = 2026
        if year_match:
            year = 2000 + int(year_match.group(1))
        
        for i, match in enumerate(matches):
            day = int(match.group(2))
            month_name = match.group(3).lower()
            month = MONTHS.get(month_name, 1)
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            start_pos = match.end()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(content)
            
            # Texto do bloco deste dia
            day_block = content[start_pos:end_pos]
            
            # Extrair Referência (está dentro de HYPERLINK ou fldrslt)
            # Procurar por \fldrslt{...}
            ref_match = re.search(r'\\fldrslt\{(.*?)\}', day_block, re.DOTALL)
            reference = ""
            raw_ref = ""
            if ref_match:
                raw_ref = ref_match.group(1)
                # Limpar a referencia
                clean_ref = re.sub(r'\\[a-z]+\d*', ' ', raw_ref) # remove tags rtf
                clean_ref = re.sub(r'[\{\}]', '', clean_ref)
                clean_ref = re.sub(r'\s+', ' ', clean_ref).strip()
                reference = parse_reference(clean_ref)
            
            # Extrair Texto do dia
            # Está antes da referência, e termina com travessão (— ou \u8212)
            # Vamos pegar tudo antes do \field (que inicia o hyperlink)
            text_part = day_block.split(r'{\field')[0]
            
            # Limpar texto
            clean_text = re.sub(r'\\[a-z]+\d*', ' ', text_part)
            clean_text = re.sub(r'[\{\}]', '', clean_text)
            clean_text = clean_text.replace('—', '').strip()
            # Remover travessão final se sobrar
            if clean_text.endswith('—') or clean_text.endswith('-'):
                 clean_text = clean_text[:-1].strip()
            
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if reference and clean_text:
                all_data.append({
                    "date": date_str,
                    "title": reference,
                    "content": clean_text
                })
                
    return all_data

if __name__ == "__main__":
    base_dir = "/Users/GABERA/projetos/es26/arquivos/"
    data = extract_all_days(base_dir)
    
    # Criar estrutura final (dicionário ou lista, usuario pediu json com todos os textos)
    # Vou fazer um dicionário indexado pela data "MM-DD" para fácil acesso no JS, ou array
    # O usuário pediu "dia 1 de janeiro deve aparecer...". Se o JSON for um array, o JS tem que filtrar.
    # Se for um objeto {"01-01": {...}}, é acesso direto O(1).
    # Vou fazer objeto com chaves "MM-DD".
    
    json_output = {}
    for item in data:
        # Extrair MM-DD da data YYYY-MM-DD
        year = item['date'][:4]
        key = item['date'][5:] # 01-01
        if year not in json_output:
            json_output[year] = {}
        json_output[year][key] = {
            "title": item['title'],
            "content": item['content'],
            "full_date": item['date'] # opcional, mas útil
        }
        
    output_path = "/Users/GABERA/projetos/es26/daily_text_by_year.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
        
    print(f"JSON gerado com sucesso em: {output_path}")
    print(f"Total de dias processados: {len(data)}")
