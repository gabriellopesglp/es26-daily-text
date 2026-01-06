import os
import re
import json
import unicodedata

MONTHS_ES = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'setiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

BIBLE_BOOKS_ES = {
    'Génesis': 'Gén.', 'Éxodo': 'Éx.', 'Levítico': 'Lev.', 'Números': 'Núm.', 'Deuteronomio': 'Deut.',
    'Josué': 'Jos.', 'Jueces': 'Juec.', 'Rut': 'Rut', 'Primero de Samuel': '1 Sam.', 'Segundo de Samuel': '2 Sam.',
    'Primer Libro de los Reyes': '1 Rey.', 'Segundo Libro de los Reyes': '2 Rey.', 'Primer Libro de Reyes': '1 Rey.', 'Segundo Libro de Reyes': '2 Rey.',
    'Primera de Crónicas': '1 Crón.', 'Segunda de Crónicas': '2 Crón.',
    'Esdras': 'Esd.', 'Nehemías': 'Neem.', 'Ester': 'Est.', 'Job': 'Job', 'Salmos': 'Sal.', 'Salmo': 'Sal.',
    'Proverbios': 'Prov.', 'Eclesiastés': 'Ecl.', 'Cantar de los Cantares': 'Cant.',
    'Isaías': 'Isa.', 'Jeremías': 'Jer.', 'Lamentaciones': 'Lam.', 'Ezequiel': 'Eze.', 'Daniel': 'Dan.',
    'Oseas': 'Ose.', 'Joel': 'Joel', 'Amós': 'Amós', 'Abdías': 'Abd.', 'Jonás': 'Jon.', 'Miqueas': 'Miq.',
    'Nahúm': 'Nah.', 'Habacuc': 'Hab.', 'Sofonías': 'Sof.', 'Hageo': 'Hag.', 'Zacarías': 'Zac.', 'Malaquías': 'Mal.',
    'Mateo': 'Mat.', 'Marcos': 'Mar.', 'Lucas': 'Luc.', 'Juan': 'Juan', 'Hechos': 'Hech.',
    'Romanos': 'Rom.', 'Primera a los Corintios': '1 Cor.', 'Primera de los Corintios': '1 Cor.', '1 Corintios': '1 Cor.',
    'Segunda a los Corintios': '2 Cor.', 'Gálatas': 'Gál.', 'Efesios': 'Efes.', 'Filipenses': 'Fil.',
    'Colosenses': 'Col.', 'Primera a los Tesalonicenses': '1 Tes.', 'Segunda a los Tesalonicenses': '2 Tes.',
    'Primera a Timoteo': '1 Tim.', 'Segunda a Timoteo': '2 Tim.', 'Tito': 'Tito', 'Filemón': 'File.',
    'Hebreos': 'Heb.', 'Santiago': 'Sant.', 'Primera de Pedro': '1 Ped.', 'Segunda de Pedro': '2 Ped.',
    'Primera de Juan': '1 Juan', 'Segunda de Juan': '2 Juan', 'Tercera de Juan': '3 Juan',
    'Judas': 'Judas', 'Apocalipsis': 'Apo.'
}

BOOK_INDEX_ABBR_ES = {
    1: 'Gén.', 2: 'Éx.', 3: 'Lev.', 4: 'Núm.', 5: 'Deut.', 6: 'Jos.', 7: 'Juec.', 8: 'Rut',
    9: '1 Sam.', 10: '2 Sam.', 11: '1 Rey.', 12: '2 Rey.', 13: '1 Crón.', 14: '2 Crón.',
    15: 'Esd.', 16: 'Neem.', 17: 'Est.', 18: 'Job', 19: 'Sal.', 20: 'Prov.', 21: 'Ecl.', 22: 'Cant.',
    23: 'Isa.', 24: 'Jer.', 25: 'Lam.', 26: 'Eze.', 27: 'Dan.', 28: 'Ose.', 29: 'Joel', 30: 'Amós',
    31: 'Abd.', 32: 'Jon.', 33: 'Miq.', 34: 'Nah.', 35: 'Hab.', 36: 'Sof.', 37: 'Hag.', 38: 'Zac.',
    39: 'Mal.', 40: 'Mat.', 41: 'Mar.', 42: 'Luc.', 43: 'Juan', 44: 'Hech.', 45: 'Rom.',
    46: '1 Cor.', 47: '2 Cor.', 48: 'Gál.', 49: 'Efes.', 50: 'Fil.', 51: 'Col.',
    52: '1 Tes.', 53: '2 Tes.', 54: '1 Tim.', 55: '2 Tim.', 56: 'Tito', 57: 'File.',
    58: 'Heb.', 59: 'Sant.', 60: '1 Ped.', 61: '2 Ped.', 62: '1 Juan', 63: '2 Juan',
    64: '3 Juan', 65: 'Judas', 66: 'Apo.'
}

def decode_rtf_char(m):
    try:
        return chr(int(m.group(1)))
    except:
        return m.group(0)

def clean_rtf(text):
    text = re.sub(r'\\u(-?\d+)\?', decode_rtf_char, text)
    text = text.replace('\\par', '\n')
    text = re.sub(r'\\[a-z]+\\d*', ' ', text)
    text = re.sub(r'\\{.*?\\}', '', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'\\s+', ' ', text).strip()
    text = text.replace('\xa0', ' ')
    text = unicodedata.normalize('NFC', text)
    return text

def parse_reference_es(ref_text):
    ref_text = unicodedata.normalize('NFC', ref_text.replace('\xa0', ' '))
    book_abbr = ''
    remaining = ref_text
    sorted_books = sorted(BIBLE_BOOKS_ES.keys(), key=len, reverse=True)
    for book in sorted_books:
        if book.lower() in ref_text.lower():
            book_abbr = BIBLE_BOOKS_ES[book]
            remaining = re.sub(re.escape(book), '', ref_text, flags=re.IGNORECASE)
            break
    if not book_abbr:
        return ref_text
    remaining = remaining.lower()
    for w in ['capítulo', 'capitulo', 'versículo', 'versiculo', 'vers.', 'de', 'los', 'las', 'la', 'el', 'a']:
        remaining = remaining.replace(w, '')
    remaining = re.sub(r'\b(?=\w*\d)(?=\w*[A-Za-z])\w+\b', ' ', remaining)
    remaining = re.sub(r'\s+', ' ', remaining).strip()
    nums = re.findall(r'\d+', remaining)
    if len(nums) >= 2:
        return f'{book_abbr} {nums[0]}:{nums[1]}'
    if len(nums) == 1:
        if book_abbr in ['Judas', 'File.', '2 Juan', '3 Juan', 'Abd.']:
            return f'{book_abbr} {nums[0]}'
        return f'{book_abbr} {nums[0]}'
    return ref_text

def extract_all_days_es(base_path):
    all_data = []
    files = sorted([f for f in os.listdir(base_path) if f.endswith('.rtf')])
    def final_clean_es(txt):
        txt = re.sub(r'u(-?\d+)\??', lambda m: chr(int(m.group(1))), txt)
        txt = re.sub(r'field\\*fldinst.*?(?=\\})', ' ', txt, flags=re.DOTALL)
        txt = re.sub(r'field\\*fldinst\\s*\"[^\"]*\"', ' ', txt, flags=re.DOTALL)
        txt = re.sub(r'HYPERLINK', ' ', txt)
        txt = re.sub(r'fldrslt[a-z0-9]*', ' ', txt, flags=re.IGNORECASE)
        txt = re.sub(r'\b(cs\d+|af\d+|cf\d+|lang\w+|fcs\d+|ltrch|rtlch|ulnone|ul|i|b|plain|qlfi\d+|ql|fi\d+|s\d+|qc)\b', ' ', txt, flags=re.IGNORECASE)
        txt = re.sub(r'\b\w*\d+\w*\b', ' ', txt)
        txt = re.sub(r'\s*[A-Za-z]*\d+[A-Za-z]*\s*', ' ', txt)
        txt = re.sub(r'^\s*[a-z]\s+', ' ', txt)
        txt = re.sub(r'\s+', ' ', txt).strip()
        txt = txt.replace('—', '').strip()
        return txt
    for filename in files:
        file_path = os.path.join(base_path, filename)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
        content = re.sub(r'\\u(-?\\d+)\\?', decode_rtf_char, raw_content)
        content_clean = content.replace('\\par', '\n')
        date_pattern = r'(Lunes|Martes|Miércoles|Miercoles|Jueves|Viernes|Sábado|Sabado|Domingo),?\s+(\d+)(?:\.|º)?\s+de\s+([a-záéíóú]+)'
        matches = list(re.finditer(date_pattern, content_clean, re.IGNORECASE))
        y_m = re.search(r'es(\\d{2})_S_\\d{2}\\.rtf', filename)
        year = 2026
        if y_m:
            year = 2000 + int(y_m.group(1))
        for i, match in enumerate(matches):
            day = int(match.group(2))
            month_name = match.group(3).lower()
            month = MONTHS_ES.get(month_name, 1)
            date_str = f'{year}-{month:02d}-{day:02d}'
            start_pos = match.end()
            end_pos = matches[i+1].start() if i+1 < len(matches) else len(content_clean)
            day_block = content_clean[start_pos:end_pos]
            reference = ''
            # Extrair de URL se disponível
            url_code = None
            url_match = re.search(r'bible=(\d+)', day_block)
            if url_match:
                code = url_match.group(1)
                if len(code) >= 8:
                    try:
                        book_idx = int(code[:2])
                        chapter = int(code[2:5])
                        verse = int(code[5:])
                        abbr = BOOK_INDEX_ABBR_ES.get(book_idx)
                        if abbr:
                            reference = f'{abbr} {chapter}:{verse}'
                    except:
                        pass
            ref_match = re.search(r'\\fldrslt\\{(.*?)\\}', day_block, re.DOTALL)
            if ref_match:
                raw_ref = ref_match.group(1)
                clean_ref = re.sub(r'\\[a-z]+\\d*', ' ', raw_ref)
                clean_ref = re.sub(r'[\\{\\}]', '', clean_ref)
                clean_ref = re.sub(r'\\s+', ' ', clean_ref).strip()
                clean_ref = re.sub(r'u(-?\\d+)\\??', lambda m: chr(int(m.group(1))), clean_ref)
                mref = re.search(r'([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúÑñ ]+?)\s+cap[ií]tulo\s+(\d+)\s+vers[ií]culo[s]?\s+(\d+)', clean_ref)
                if mref:
                    book_str = mref.group(1).strip()
                    chapter = mref.group(2)
                    verse = mref.group(3)
                    abbr = ''
                    for bk in sorted(BIBLE_BOOKS_ES.keys(), key=len, reverse=True):
                        if bk.lower() in book_str.lower():
                            abbr = BIBLE_BOOKS_ES[bk]
                            break
                    if abbr:
                        reference = f'{abbr} {chapter}:{verse}'
                if not reference:
                    reference = parse_reference_es(clean_ref)
            # preferir extrair diretamente do bloco visível (mais robusto)
            visible_block = re.sub(r'\\[a-z]+\\d*', ' ', day_block)
            visible_block = re.sub(r'[\\{\\}]', '', visible_block)
            visible_block = re.sub(r'\\s+', ' ', visible_block).strip()
            visible_block = re.sub(r'u(-?\\d+)\\??', lambda m: chr(int(m.group(1))), visible_block)
            m = re.search(r'([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúÑñ ]+?)\s+cap[ií]tulo\s+(\d+)\s+vers[ií]culo[s]?\s+(\d+)', visible_block)
            if m:
                book_str = m.group(1).strip()
                chapter = m.group(2)
                verse = m.group(3)
                abbr = ''
                for bk in sorted(BIBLE_BOOKS_ES.keys(), key=len, reverse=True):
                    if bk.lower() in book_str.lower():
                        abbr = BIBLE_BOOKS_ES[bk]
                        break
                if abbr:
                    reference = f'{abbr} {chapter}:{verse}'
            if not reference:
                reference = parse_reference_es(visible_block)
            # Capturar apenas o texto visível antes do primeiro field ou do primeiro parêntese (inicio da referência)
            # Tentar capturar texto em itálico antes da referência/parênteses
            italic_match = re.search(r'\\i\\s(.*?)(?=(?:\\{\\field|\\u8212\\?|\\x28|\\()))', day_block, re.DOTALL)
            if italic_match:
                text_part = italic_match.group(1)
            else:
                pre_visible = re.split(r'\\x28|\\\(|\\u8212\\?|\\{\\field', day_block, maxsplit=1)[0]
                text_part = pre_visible
            clean_text = re.sub(r'\\[a-z]+\\d*', ' ', text_part)
            clean_text = re.sub(r'[\\{\\}]', '', clean_text)
            clean_text = clean_text.replace('—', '').strip()
            if clean_text.endswith('—') or clean_text.endswith('-'):
                clean_text = clean_text[:-1].strip()
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            clean_text = final_clean_es(clean_text)
            # Manter apenas a frase inicial antes da referência/paren
            content_only = re.split(r'\s*\(', clean_text, maxsplit=1)[0]
            content_only = re.sub(r'^\s*[a-z]\s+', '', content_only)
            content_only = re.sub(r'u(-?\d+)\??', lambda m: chr(int(m.group(1))), content_only)
            if not content_only:
                simple = re.sub(r'\\[a-z]+\\d*', ' ', day_block)
                simple = re.sub(r'[\\{\\}]', '', simple)
                simple = re.sub(r'\s+', ' ', simple).strip()
                simple = simple.replace('—', '').strip()
                content_only = re.split(r'\s*\(', simple, maxsplit=1)[0].strip()
            content_f = content_only or clean_text or simple
            all_data.append({'date': date_str, 'title': reference, 'content': content_f})
    return all_data

if __name__ == '__main__':
    base_dir = '/Users/GABERA/projetos/es26/arquivos/espanhol/'
    data = extract_all_days_es(base_dir)
    def cleanup_final(s):
        s = re.sub(r'u(-?\d+)\\??', lambda m: chr(int(m.group(1))), s)
        s = re.sub(r'(field\\*fldinst|HYPERLINK|fldrslt\\w*)', ' ', s, flags=re.IGNORECASE)
        s = re.sub(r'\\b\\w*\\d+\\w*\\b', ' ', s)
        s = re.sub(r'^\s*[a-z]\s+', ' ', s)
        s = re.sub(r'\\s+', ' ', s).strip()
        s = re.split(r'\s*\(', s, maxsplit=1)[0].strip()
        return s
    out = {}
    for item in data:
        year = item['date'][:4]
        key = item['date'][5:]
        if year not in out:
            out[year] = {}
        out[year][key] = {'title': item['title'], 'content': cleanup_final(item['content']), 'full_date': item['date']}
    # Fallback: garantir 365 dias preenchendo ausentes diretamente dos arquivos
    expected_year = str(list(out.keys())[0]) if out else str(year)
    base_dir_scan = base_dir
    files = sorted([f for f in os.listdir(base_dir_scan) if f.endswith('.rtf')])
    date_pat = re.compile(r'(Lunes|Martes|Miércoles|Miercoles|Jueves|Viernes|Sábado|Sabado|Domingo),?\s+(\d+)(?:\.|º)?\s+de\s+([a-záéíóú]+)', re.IGNORECASE)
    for filename in files:
        with open(os.path.join(base_dir_scan, filename), 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
        raw = re.sub(r'\\u(-?\d+)\?', lambda m: chr(int(m.group(1))), raw)
        raw = raw.replace('\\par', '\n')
        for m in date_pat.finditer(raw):
            day = int(m.group(2))
            month_name = m.group(3).lower()
            month = MONTHS_ES.get(month_name, 1)
            key = f'{month:02d}-{day:02d}'
            if expected_year not in out:
                out[expected_year] = {}
            if key in out[expected_year]:
                continue
            start = m.end()
            end = len(raw)
            # next match start
            # find next by scanning pattern from position
            nm = date_pat.search(raw, start)
            if nm:
                end = nm.start()
            blk = raw[start:end]
            # title via URL code
            ref = ''
            um = re.search(r'bible=(\d+)', blk)
            if um:
                code = um.group(1)
                if len(code) >= 8:
                    try:
                        book_idx = int(code[:2]); chapter = int(code[2:5]); verse = int(code[5:])
                        abbr = BOOK_INDEX_ABBR_ES.get(book_idx)
                        if abbr:
                            ref = f'{abbr} {chapter}:{verse}'
                    except:
                        pass
            # content simplificado
            simple = re.sub(r'\\[a-z]+\d*', ' ', blk)
            simple = re.sub(r'[\{\}]', '', simple)
            simple = re.sub(r'\s+', ' ', simple).strip()
            simple = simple.replace('—', '').strip()
            content = re.split(r'\s*\(', simple, maxsplit=1)[0].strip()
            out[expected_year][key] = {'title': ref, 'content': cleanup_final(content), 'full_date': f'{expected_year}-{key}'}
    output_path = '/Users/GABERA/projetos/es26/daily_text_by_year_es.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'JSON ES gerado: {output_path} com {len(data)} dias')
