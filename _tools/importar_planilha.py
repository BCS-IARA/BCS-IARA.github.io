"""
IMPORTADOR BCS — combina SIGESPOL (JSON) + WhatsApp e envia para a planilha Google.
Execute: python importar_planilha.py
"""

import json, re, time, requests, hashlib

# ── Configuração ─────────────────────────────────────────────────────
SHEETS_URL   = "https://script.google.com/macros/s/AKfycbwMTA3z7Yva7ccjvv0laIIsKKiKePYLPLrAi5Ss3ZV1JhzxKv-UECROdWuD4mkCYQTW5w/exec"
TOKEN        = "bcs-token-secreto-2025"
ARQUIVO_JSON = "BCS_importacao_sigespol.json"
ARQUIVO_ZAP  = "Conversa do WhatsApp com Adjuntos e Guarda.txt"
PAUSA        = 0.4

# ── Envio HTTP ───────────────────────────────────────────────────────
def enviar(tipo, registro):
    payload = json.dumps({"token": TOKEN, "tipo": tipo, "registro": registro})
    try:
        r = requests.post(SHEETS_URL, data=payload,
                          headers={"Content-Type": "text/plain"}, timeout=30)
        if r.status_code == 200:
            try:    return r.json()
            except: return {"ok": True}
        return {"ok": False, "erro": f"HTTP {r.status_code}"}
    except Exception as ex:
        return {"ok": False, "erro": str(ex)}

# ── Normaliza booleano ───────────────────────────────────────────────
def norm_bool(v):
    if isinstance(v, bool): return v
    return str(v).strip().lower() in ("true", "sim", "1", "yes")

# ── Extrai campo no formato *CAMPO:*  valor ──────────────────────────
def campo(bloco, nome):
    """Extrai valor de campo no formato *NOME:*  valor\n"""
    m = re.search(r'\*' + re.escape(nome) + r':\*\s*(.*?)(?=\n\s*\*|\Z)',
                  bloco, re.IGNORECASE | re.DOTALL)
    if not m:
        # Fallback: *NOME:	*  ou  *NOME* :
        m = re.search(r'\*' + re.escape(nome) + r'[:\t]+\*?\s*(.*?)(?=\n\s*\*|\Z)',
                      bloco, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""

# ── Extrai DESCRIÇÃO (vai até *FONTE:*) ──────────────────────────────
def campo_descricao(bloco):
    m = re.search(r'\*DESCRI.*?:\*\s*(.*?)(?=\n\s*\*FONTE|\Z)',
                  bloco, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""

# ── Divide DESCRIÇÃO em resumo | dinâmica | medidas ──────────────────
def dividir(texto):
    re_din = re.compile(r'Din[âa]mica dos fatos\s*:?\s*', re.IGNORECASE)
    re_med = re.compile(r'Medidas?\s+adotadas?\s*:?\s*', re.IGNORECASE)
    resumo = texto; dinamica = ""; medidas = ""
    m_d = re_din.search(texto)
    m_m = re_med.search(texto)
    if m_d and m_m and m_d.start() < m_m.start():
        resumo   = texto[:m_d.start()].strip()
        dinamica = texto[m_d.end():m_m.start()].strip()
        medidas  = texto[m_m.end():].strip()
    elif m_d:
        resumo   = texto[:m_d.start()].strip()
        dinamica = texto[m_d.end():].strip()
    elif m_m:
        resumo   = texto[:m_m.start()].strip()
        medidas  = texto[m_m.end():].strip()
    return resumo, dinamica, medidas

# ── Bairro: última parte após vírgula ────────────────────────────────
def bairro_de(local):
    partes = [p.strip() for p in local.split(",") if p.strip()]
    return partes[-1] if len(partes) >= 2 else local.strip()

# ── ID estável ───────────────────────────────────────────────────────
def gerar_id(prefixo, *partes):
    h = hashlib.md5("|".join(str(p) for p in partes).encode()).hexdigest()[:10]
    return f"{prefixo}_{h}"

# ════════════════════════════════════════════════════════════════════
#  FONTE 1 — JSON SIGESPOL
# ════════════════════════════════════════════════════════════════════
def converter_data(data_str):
    """Converte 2025-01-02 → 02/01/2025 se necessário"""
    s = str(data_str).strip()
    if re.match(r'\d{4}-\d{2}-\d{2}', s):
        partes = s[:10].split('-')
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return s

def carregar_sigespol():
    try:
        with open(ARQUIVO_JSON, encoding="utf-8") as f:
            dados = json.load(f)
        db  = dados.get("db", dados)
        ocs = db.get("ocorrencias", [])
        resultado = []
        for reg in ocs:
            # Converte data ISO para formato brasileiro
            if "data" in reg:
                reg["data"] = converter_data(reg["data"])

            # Garante campos booleanos
            for cb in ("violencia_domestica", "requer_visita", "reincidente"):
                reg[cb] = norm_bool(reg.get(cb, False))

            # Detecta violência doméstica pelo tipo/descrição se não marcado
            if not reg["violencia_domestica"]:
                busca = str(reg.get("tipo","")) + " " + str(reg.get("descricao",""))
                if re.search(r'maria da penha|viol[êe]ncia dom[eé]stica', busca, re.IGNORECASE):
                    reg["violencia_domestica"] = True
                    reg["requer_visita"]        = True
                    reg["medida_protetiva"]     = "Sim"

            # Campos que podem estar ausentes neste JSON
            reg.setdefault("vitima_nome",    "")
            reg.setdefault("vitima_sexo",    "")
            reg.setdefault("vitima_idade",   "")
            reg.setdefault("vitima_telefone","")
            reg.setdefault("vitima_cpf",     "")
            reg.setdefault("vitima_endereco", reg.get("local",""))
            reg.setdefault("suspeito_nome",  "")
            reg.setdefault("suspeito_apelido","")
            reg.setdefault("suspeito_caracteristicas","")
            reg.setdefault("veiculo",        "")
            reg.setdefault("medida_protetiva","Não")
            reg.setdefault("numero",         "")
            reg.setdefault("municipio",      "Vitória da Conquista")

            # Limpa município
            reg["municipio"] = re.sub(r"\s*/[A-Z]{2}$", "", str(reg["municipio"])).strip()

            # descricao_dinamica tem prioridade; fallback para descricao
            if not reg.get("descricao_dinamica"):
                reg["descricao_dinamica"] = reg.get("descricao","")
            reg.setdefault("texto_original", reg.get("descricao_dinamica",""))
            reg.setdefault("medidas", "")

            resultado.append(reg)

        print(f"  SIGESPOL JSON : {len(resultado)} ocorrencias ({converter_data(resultado[-1]['data'])} ate {converter_data(resultado[0]['data'])})")
        return resultado
    except FileNotFoundError:
        print(f"  [AVISO] {ARQUIVO_JSON} nao encontrado")
        return []

# ════════════════════════════════════════════════════════════════════
#  FONTE 2 — WhatsApp
# ════════════════════════════════════════════════════════════════════
def carregar_whatsapp():
    try:
        with open(ARQUIVO_ZAP, encoding="utf-8") as f:
            texto = f.read()
    except FileNotFoundError:
        print(f"  [AVISO] {ARQUIVO_ZAP} nao encontrado")
        return []

    blocos = re.split(r'\n(?=\d{2}/\d{2}/\d{4} \d{2}:\d{2} - )', texto)
    registros = []

    for bloco in blocos:
        # Filtra só blocos de ocorrência (têm CIPM + TIPO + DESCRI)
        if "CIPM" not in bloco:     continue
        if "*TIPO:*" not in bloco:  continue
        if "DESCRI" not in bloco:   continue

        # Timestamp do envio (data/hora da mensagem WhatsApp)
        ts = re.match(r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})', bloco)
        ts_data = ts.group(1) if ts else ""
        ts_hora = ts.group(2) if ts else ""

        tipo     = re.sub(r'\*', '', campo(bloco, "TIPO")).strip()
        data_oc  = re.sub(r'\*', '', campo(bloco, "DATA")).strip()  or ts_data
        hora_oc  = re.sub(r'\*', '', campo(bloco, "HORA")).strip()  or ts_hora
        local    = re.sub(r'\*', '', campo(bloco, "LOCAL")).strip()
        resp     = re.sub(r'\*', '', campo(bloco, "RESPONSÁVEL")).strip()

        desc_raw = campo_descricao(bloco)
        if not tipo or not desc_raw:
            continue

        resumo, dinamica, medidas = dividir(desc_raw)

        vd = bool(re.search(
            r'maria da penha|viol[êe]ncia dom[eé]stica|medida protetiva',
            tipo + " " + resumo, re.IGNORECASE))

        id_reg = gerar_id("zap", data_oc, hora_oc, tipo[:20], resumo[:30])

        registros.append({
            "id":                    id_reg,
            "numero":                "",
            "data":                  data_oc,
            "hora":                  hora_oc,
            "tipo":                  tipo,
            "bairro":                bairro_de(local),
            "municipio":             "Vitória da Conquista",
            "vitima_nome":           "",
            "vitima_idade":          "",
            "vitima_sexo":           "",
            "vitima_telefone":       "",
            "vitima_cpf":            "",
            "vitima_endereco":       local,
            "suspeito_nome":         "",
            "suspeito_apelido":      "",
            "suspeito_caracteristicas": "",
            "veiculo":               "",
            "medida_protetiva":      "Sim" if vd else "Não",
            "violencia_domestica":   vd,
            "requer_visita":         vd,
            "reincidente":           False,
            "descricao":             resumo[:150],
            "descricao_dinamica":    dinamica,
            "medidas":               medidas,
            "texto_original":        dinamica,
            "policiais":             resp,
            "fonte":                 "WhatsApp",
        })

    print(f"  WhatsApp      : {len(registros)} ocorrencias")
    return registros

# ════════════════════════════════════════════════════════════════════
#  IMPORTAR
# ════════════════════════════════════════════════════════════════════
def importar_lote(registros, label):
    ok = err = 0
    total = len(registros)
    for i, reg in enumerate(registros):
        res = enviar("ocorrencias", reg)
        num = i + 1
        if res.get("ok"):
            ok += 1
            print(f"  [{num:>3}/{total}] OK   {reg['id'][:28]:<28}  {str(reg.get('tipo',''))[:45]}")
        else:
            err += 1
            print(f"  [{num:>3}/{total}] ERRO {reg['id'][:28]:<28}  {res.get('erro','?')}")
        time.sleep(PAUSA)
    print(f"\n  {label}: {ok} importados, {err} erros\n")
    return ok, err

# ════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  IMPORTADOR BCS — SIGESPOL + WhatsApp")
    print("=" * 60)

    # Testa conexão
    print("\nTestando conexao com o Apps Script...")
    try:
        r = requests.get(SHEETS_URL + f"?token={TOKEN}&acao=ping", timeout=15)
        dados = r.json()
        if dados.get("ok"):
            print(f"  OK — {dados.get('total', 0)} registros existentes na planilha\n")
        else:
            print(f"  ERRO: {dados}")
            print("  >> Corrija o deploy: Implantar > Gerenciar > Quem tem acesso: 'Qualquer pessoa'")
            return
    except Exception as ex:
        print(f"  ERRO de conexao: {ex}")
        print("  >> Verifique o deploy do Apps Script.")
        return

    # Carrega
    print("Carregando dados...")
    sig_ocs = carregar_sigespol()
    zap_ocs = carregar_whatsapp()
    total   = len(sig_ocs) + len(zap_ocs)
    print(f"\nTotal a importar: {total} ocorrencias\n")

    ok_t = err_t = 0

    if sig_ocs:
        print("=" * 60)
        print(f"  SIGESPOL ({len(sig_ocs)} registros)")
        print("=" * 60)
        ok, err = importar_lote(sig_ocs, "SIGESPOL")
        ok_t += ok; err_t += err

    if zap_ocs:
        print("=" * 60)
        print(f"  WhatsApp ({len(zap_ocs)} registros)")
        print("=" * 60)
        ok, err = importar_lote(zap_ocs, "WhatsApp")
        ok_t += ok; err_t += err

    print("=" * 60)
    print(f"  CONCLUIDO: {ok_t} importados, {err_t} erros")
    print(f"  Abra o Google Drive e verifique a planilha 'IARA - BCS'")
    print("=" * 60)

if __name__ == "__main__":
    main()
