import pandas as pd, json, re, uuid
from datetime import datetime

df = pd.read_excel('SIGESPOL_01-01-2025_ate_07-05-2026.xlsx')
df.columns = ['Cod','Tipo','Data','Municipio','Local','Responsavel','Descricao','Dinamica','Medidas','Pessoas','Efetivo','Pagina','UltimaEdicao','Objetos','Documentos','Armas','DadosQuant','PostoServico','Drogas','Rotulos']

BAIRROS_ALVO = {
    'alto marom':'Alto Marom','alto maron':'Alto Marom',
    'panorama':'Panorama','alto do panorama':'Panorama',
    'primavera':'Primavera','pedrinhas':'Pedrinhas',
    'europa unida':'Europa Unida','vila brasil':'Vila Brasil',
}

def parse_year(val):
    if pd.isna(val): return None
    m = re.search(r'\d{2}/\d{2}/(\d{4})', str(val))
    return int(m.group(1)) if m else None

def parse_datetime(val):
    if pd.isna(val): return '',''
    s = str(val)
    m = re.search(r'(\d{2}/\d{2}/\d{4})', s)
    t = re.search(r'(\d{2}:\d{2})', s)
    return (m.group(1) if m else ''),(t.group(1) if t else '00:00')

def extract_bairro(local_val):
    if pd.isna(local_val): return None
    parts = re.split(r'\s*-\s*Zona', str(local_val))
    if len(parts) < 2: return None
    for seg in reversed([s.strip() for s in parts[0].split(',')]):
        for k,v in BAIRROS_ALVO.items():
            if seg.lower().strip()==k: return v
    return None

def clean(val):
    if pd.isna(val): return ''
    return str(val).strip()

def parse_pessoas(texto):
    if pd.isna(texto): return {}
    s = str(texto)
    result = {}
    blocos = re.split(r'(?=Tipo\s*:)', s, flags=re.IGNORECASE)
    vitima = None
    autor = None
    for bloco in blocos:
        tipo_m = re.search(r'Tipo\s*:\s*(\w[\w\s]*?)(?:,|\s{2,}|Nome)', bloco, re.IGNORECASE)
        if not tipo_m: continue
        tipo_pessoa = tipo_m.group(1).strip().upper()
        nome_m = re.search(r'Nome\s*:\s*([^,\n]+)', bloco, re.IGNORECASE)
        sexo_m = re.search(r'Sexo\s*:\s*(Feminino|Masculino)', bloco, re.IGNORECASE)
        idade_m = re.search(r'(\d{1,3})\s*anos', bloco, re.IGNORECASE)
        cpf_m = re.search(r'CPF\s*:?\s*([\d\.\-]{11,14})', bloco, re.IGNORECASE)
        tel_m = re.search(r'(\d[\d\s\.\-]{7,13}\d)(?!\s*anos)', bloco)
        end_m = re.search(r'Endere.o\s*:\s*([^\n]+)', bloco, re.IGNORECASE)
        nome = nome_m.group(1).strip() if nome_m else ''
        sexo = sexo_m.group(1).strip() if sexo_m else ''
        idade = idade_m.group(1).strip() if idade_m else ''
        cpf = cpf_m.group(1).strip() if cpf_m else ''
        tel = tel_m.group(1).strip() if (tel_m and not cpf_m) else ''
        endereco = end_m.group(1).strip() if end_m else ''
        pessoa = {'nome':nome,'sexo':sexo,'idade':idade,'cpf':cpf,'tel':tel,'endereco':endereco}
        tipo_upper = tipo_pessoa.upper()
        if 'TIMA' in tipo_upper or 'VITIMA' in tipo_upper:
            if not vitima: vitima = pessoa
        elif 'AUTOR' in tipo_upper:
            if not autor: autor = pessoa
    if vitima:
        result['vitima_nome'] = vitima['nome']
        result['vitima_sexo'] = vitima['sexo']
        result['vitima_idade'] = vitima['idade']
        result['vitima_cpf'] = vitima['cpf']
        result['vitima_telefone'] = vitima['tel']
        result['vitima_endereco'] = vitima['endereco']
    if autor:
        result['suspeito_nome'] = autor['nome']
    return result

def detectar_vd(tipo_str):
    if pd.isna(tipo_str): return False
    s = str(tipo_str).upper()
    return 'MARIA DA PENHA' in s or ('VIOL' in s and 'DOM' in s)

def extrair_medida_protetiva(medidas_str):
    if pd.isna(medidas_str): return ''
    s = str(medidas_str)
    m = re.search(r'[Mm]edida.?\s+[Pp]rotetiva.?[^\n.;]*', s)
    return m.group(0).strip() if m else ''

def merge_descricao(desc, dinamica):
    """Retorna (descricao_curta, descricao_dinamica_completa)"""
    d = clean(desc)
    di = clean(dinamica)
    # Campo curto: só o resumo (Descricao)
    # Campo dinâmica: Descricao + Dinâmica juntos (conteúdo completo)
    if d and di:
        return d, d + '\n\n' + di
    elif d:
        return d, d
    elif di:
        return di[:120], di
    return '', ''

df['year'] = df['Data'].apply(parse_year)
df['bairro'] = df['Local'].apply(extract_bairro)
df_f = df[(df['year']==2026) & (df['bairro'].notna())].copy()

ocorrencias = []
stats = {'com_vitima':0,'com_suspeito':0,'vd':0}

for _, row in df_f.iterrows():
    data_str, hora_str = parse_datetime(row['Data'])
    local_full = clean(row['Local'])
    local_parts = re.split(r'\s*-\s*Zona', local_full)
    logradouro = local_parts[0].strip() if local_parts else local_full

    pessoas = parse_pessoas(row['Pessoas'])
    vd = detectar_vd(row['Tipo'])
    mp = extrair_medida_protetiva(row['Medidas'])
    descricao_curta, descricao_completa = merge_descricao(row['Descricao'], row['Dinamica'])

    if pessoas.get('vitima_nome'): stats['com_vitima'] += 1
    if pessoas.get('suspeito_nome'): stats['com_suspeito'] += 1
    if vd: stats['vd'] += 1

    oc = {
        'id': str(uuid.uuid4()),
        'numero': clean(row['Cod']),
        'tipo': clean(row['Tipo']),
        'data': data_str,
        'hora': hora_str,
        'bairro': row['bairro'],
        'local': logradouro,
        'municipio': clean(row['Municipio']),
        'vitima_nome': pessoas.get('vitima_nome',''),
        'vitima_sexo': pessoas.get('vitima_sexo',''),
        'vitima_idade': pessoas.get('vitima_idade',''),
        'vitima_telefone': pessoas.get('vitima_telefone',''),
        'vitima_cpf': pessoas.get('vitima_cpf',''),
        'vitima_endereco': pessoas.get('vitima_endereco','') or logradouro,
        'suspeito_nome': pessoas.get('suspeito_nome',''),
        'suspeito_apelido': '',
        'suspeito_caracteristicas': '',
        'descricao': descricao_curta,
        'descricao_dinamica': descricao_completa,
        'medidas': clean(row['Medidas']),
        'medida_protetiva': mp,
        'violencia_domestica': vd,
        'requer_visita': vd,
        'policiais': clean(row['Efetivo']),
        'pessoas_envolvidas': clean(row['Pessoas']),
        'objetos': clean(row['Objetos']),
        'armas': clean(row['Armas']),
        'drogas': clean(row['Drogas']),
        'responsavel': clean(row['Responsavel']),
        'rotulos': clean(row['Rotulos']),
        'reincidente': False,
        'fonte': 'SIGESPOL',
        'status': 'importado',
        'criadoEm': datetime.now().isoformat()
    }
    ocorrencias.append(oc)

payload = {
    'versao': 'BCS_sigespol_2026',
    'exportadoEm': datetime.now().isoformat(),
    'descricao': 'Dados SIGESPOL 01/01/2026 a 07/05/2026 - Bairros da Base',
    'db': {
        'ocorrencias': ocorrencias,
        'atendimentos': [],
        'visitas': [],
        'agendamentos': []
    }
}

with open('BCS_importacao_sigespol_2026.json','w',encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

import os
size = os.path.getsize('BCS_importacao_sigespol_2026.json')
print(f"Arquivo: BCS_importacao_sigespol_2026.json")
print(f"Registros: {len(ocorrencias)}")
print(f"Com vitima identificada: {stats['com_vitima']} ({stats['com_vitima']*100//len(ocorrencias)}%)")
print(f"Com suspeito identificado: {stats['com_suspeito']} ({stats['com_suspeito']*100//len(ocorrencias)}%)")
print(f"Violencia domestica: {stats['vd']}")
print(f"Tamanho: {size/1024:.1f} KB")
print()
print("=== AMOSTRA ===")
for oc in ocorrencias[1:4]:
    print(f"Nr {oc['numero']} | {oc['data']} {oc['hora']} | {oc['bairro']}")
    print(f"  Tipo: {oc['tipo'][:60]}")
    print(f"  Vitima: {oc['vitima_nome']} | {oc['vitima_sexo']} | {oc['vitima_idade']}a")
    print(f"  Suspeito: {oc['suspeito_nome'] or 'nao identificado'}")
    print(f"  VD: {oc['violencia_domestica']}")
    print(f"  Descricao (trecho): {oc['descricao'][:100]}")
    print()
