"""
IARA / BCS — Parser do relatório de turno do SIGESPOL (PDF -> registros de ocorrência)

Uso:
  pdftotext -layout "RELATORIO-....pdf" - | python3 parse_sigespol_relatorio.py

ou

  python3 parse_sigespol_relatorio.py arquivo.txt   (texto já extraído)

Imprime uma lista JSON de registros no schema da aba "oc" da planilha IARA/BCS,
já com "sig_<numero>" como id (dedup por número oficial da ocorrência — o backend
faz upsert por id, então reprocessar o mesmo relatório é seguro/idempotente).

Campos auxiliares prefixados com "_" (ex: "_tipo_generico_flag") NÃO fazem parte
do schema da planilha — servem apenas para quem monta o lançamento final decidir
sobre reclassificação de tipo genérico e não devem ser enviados ao backend.

Criado em 31/07/2026 a partir de um relatório real de amostra (5 ocorrências,
turno 18:00-06:00 de 29-30/07/2026). Ver histórico de decisões em
"🗂 Projeto - IARA_BCS.md" para o contexto completo da migração WhatsApp -> SIGESPOL.

Ajustado em 01/08/2026: "Medidas Adotadas pela Guarnição" não tem campo próprio na
UI de edição/criação de ocorrência do index.html — só existia como coluna solta no
backend, nunca editável. Passa a viver dentro do relato único (descricao_dinamica/
texto_original), junto com "Documentos Gerados" e "Entrada/Saída da DP" (que também
não tinham representação própria e ficariam perdidos se só desanexados de "medidas").
O campo "medidas" continua no dict só por compatibilidade de schema — sempre vazio.
"""
import sys, re, json

MUNICIPIO = "Vitória da Conquista"


def limpar_paginacao(bloco):
    """Remove linhas que são só número de página (artefato do pdftotext -layout)."""
    linhas = bloco.split("\n")
    out = []
    for l in linhas:
        if re.fullmatch(r"\s*\d{1,3}\s*", l):
            continue
        out.append(l)
    return "\n".join(out)


def juntar(txt):
    """Junta quebras de linha simples em espaço (mantém parágrafos), remove espaços duplicados."""
    txt = limpar_paginacao(txt)
    txt = re.sub(r"\s*\n\s*", " ", txt)
    txt = re.sub(r"\s{2,}", " ", txt)
    return txt.strip()


def bairro_de(endereco):
    """Extrai um bairro plausível do campo ENDEREÇO (formato SIGESPOL)."""
    if not endereco:
        return ""
    m = re.search(r"BAIRRO:\s*([^,]+)", endereco, re.IGNORECASE)
    if m:
        return m.group(1).strip().title()
    e = re.split(r",?\s*PONTO DE REFER[ÊE]NCIA", endereco, flags=re.IGNORECASE)[0]
    e = re.sub(r",?\s*VIT[ÓO]RIA DA CONQUISTA\s*/?\s*BA?\.?$", "", e, flags=re.IGNORECASE).strip()
    partes = [p.strip() for p in e.split(",") if p.strip()]
    for p in reversed(partes):
        p2 = re.sub(r"\s*-\s*ZONA (URBANA|RURAL).*$", "", p, flags=re.IGNORECASE).strip()
        if p2 and not re.fullmatch(r"ZONA (URBANA|RURAL)", p2, re.IGNORECASE):
            return p2.title()
    return partes[-1].title() if partes else ""


def extrair_pessoa(bloco, papel):
    """Extrai NOME, SEXO, IDADE, DOCUMENTO/CPF, ENDEREÇO de uma linha tipo:
    'SOLICITANTE: FULANO, SEXO FEMININO , 32 ANOS , DOCUMENTO CPF: 000... , ENDEREÇO RUA X'
    """
    pat = re.compile(
        papel + r":\s*(.*?),\s*SEXO\s+(MASCULINO|FEMININO)\s*,\s*(\d+)\s*ANOS\s*,\s*DOCUMENTO\s*(?:CPF:?)?\s*([\d./\- ]*)\s*,\s*ENDERE[ÇC]O\s*(.*?)(?=\n\n|\nDESCRI|\n[A-ZÀ-Ú]+:|$)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pat.search(bloco)
    if not m:
        return None
    nome, sexo, idade, doc, endereco = m.groups()
    return {
        "nome": juntar(nome),
        "sexo": "Feminino" if sexo.upper() == "FEMININO" else "Masculino",
        "idade": idade.strip(),
        "documento": re.sub(r"\s+", "", doc.strip()),
        "endereco": juntar(endereco),
    }


def parsear_bloco(bloco):
    m = re.search(r"TIPO\(S\):\s*(.*?)\s*\|\s*Nº\s*DA\s*OCORR[ÊE]NCIA:\s*(\S+)", bloco)
    if not m:
        return None
    tipo_original = m.group(1).strip()
    numero = m.group(2).strip()

    m = re.search(r"DATA:\s*(\d{2}/\d{2}/\d{4})\s*,\s*(\d{2}:\d{2})H", bloco)
    data = m.group(1) if m else ""
    hora = m.group(2) if m else ""

    m = re.search(r"RESPONS[ÁA]VEL:\s*(.*?)\n", bloco)
    responsavel = juntar(m.group(1)) if m else ""

    m = re.search(r"ENDERE[ÇC]O:\s*(.*?)\n\s*\n", bloco, re.DOTALL)
    endereco = juntar(m.group(1)) if m else ""

    m = re.search(r"N[ºo]\s*DO\s*BOLETIM\s*DE\s*OCORR[ÊE]NCIA:\s*\]?\s*\n?\s*(.*?)\]", bloco, re.IGNORECASE | re.DOTALL)
    bo = juntar(m.group(1)) if m else ""

    vitima = extrair_pessoa(bloco, "V[ÍI]TIMA") or extrair_pessoa(bloco, "SOLICITANTE")
    autor = extrair_pessoa(bloco, "AUTOR") or extrair_pessoa(bloco, "SUSPEITO") or extrair_pessoa(bloco, "CONDUTOR")

    m = re.search(r"DESCRI[ÇC][ÃA]O:\s*(.*?)(?:DIN[ÂA]MICA DOS FATOS:|MEDIDAS ADOTADAS)", bloco, re.DOTALL)
    descricao = juntar(m.group(1)) if m else ""

    m = re.search(r"DIN[ÂA]MICA DOS FATOS:\s*(.*?)MEDIDAS ADOTADAS PELA GUARNI[ÇC][ÃA]O:", bloco, re.DOTALL)
    dinamica = juntar(m.group(1)) if m else ""

    m = re.search(
        r"MEDIDAS ADOTADAS PELA GUARNI[ÇC][ÃA]O:\s*(.*?)(?:DOCUMENTOS GERADOS:|ENTRADA NA DP:|POLICIAIS QUE ATENDERAM|$)",
        bloco, re.DOTALL,
    )
    medidas = juntar(m.group(1)) if m else ""

    m = re.search(r"DOCUMENTOS GERADOS:\s*\[?(.*?)\]", bloco, re.IGNORECASE | re.DOTALL)
    documentos = juntar(m.group(1)) if m else ""

    m = re.search(r"ENTRADA NA DP:\s*([\d:HÀàas ]+?)\s*SA[ÍI]DA DA DP:\s*([\d:HÀàas ]+?)\s*PERMAN[ÊE]NCIA", bloco)
    entrada_saida = f"Entrada DP: {m.group(1).strip()} | Saída DP: {m.group(2).strip()}" if m else ""

    # "Medidas Adotadas" não tem campo próprio na UI — passa a viver dentro do relato
    # único junto com Documentos Gerados e Entrada/Saída da DP (mesma situação: nunca
    # tiveram representação própria; se só fossem desanexados de "medidas", se perderiam).
    dinamica_completa = dinamica
    if medidas:
        dinamica_completa += f"\n\nMEDIDAS ADOTADAS: {medidas}"
    if documentos:
        dinamica_completa += f"\n\nDOCUMENTOS GERADOS: {documentos}"
    if entrada_saida:
        dinamica_completa += f"\n\n{entrada_saida}"

    m = re.search(r"POLICIAIS QUE ATENDERAM A OCORR[ÊE]NCIA:\s*(.*?)(?:\n\s*\n|\Z)", bloco, re.DOTALL)
    policiais = ""
    if m:
        linhas = [l.strip() for l in m.group(1).split("\n") if l.strip()]
        policiais = ", ".join(linhas)

    # Regra (Oséias, 31/07/2026): tipos genéricos precisam de reclassificação manual/LLM
    tipos_genericos = {"AVERIGUAÇÃO", "OUTROS", "OUTRAS OCORRÊNCIAS NÃO RELACIONADAS", "OCORRÊNCIA DIVERSA", "OCORRÊNCIA AVULSA"}
    generico = tipo_original.upper() in tipos_genericos

    # Regra (Oséias, 31/07/2026): violência de homem contra mulher = Maria da Penha, sempre
    # (heurística — quem monta o lançamento final deve conferir lendo a dinâmica dos fatos)
    vd_regex = re.compile(r"maria da penha|viol[êe]ncia dom[eé]stica|medida protetiva|contra a mulher", re.IGNORECASE)
    texto_para_vd = tipo_original + " " + descricao + " " + dinamica
    eh_homem_contra_mulher = bool(
        autor and autor["sexo"] == "Masculino" and vitima and vitima["sexo"] == "Feminino"
        and re.search(r"agress|viol[êe]ncia|amea|golpe|soco|tapa|les[ãa]o|bateu|agredi", dinamica, re.IGNORECASE)
    )
    vd = bool(vd_regex.search(texto_para_vd)) or eh_homem_contra_mulher

    return {
        "id": f"sig_{numero}",
        "numero": numero,
        "data": data,
        "hora": hora,
        "tipo": tipo_original,
        "_tipo_generico_flag": generico,
        "bairro": bairro_de(endereco),
        "municipio": MUNICIPIO,
        "vitima_nome": vitima["nome"] if vitima else "",
        "vitima_idade": vitima["idade"] if vitima else "",
        "vitima_sexo": vitima["sexo"] if vitima else "",
        "vitima_telefone": "",
        "vitima_cpf": vitima["documento"] if vitima else "",
        "vitima_endereco": vitima["endereco"] if vitima else endereco,
        "suspeito_nome": autor["nome"] if autor else "",
        "suspeito_apelido": "",
        "suspeito_caracteristicas": (
            f"{autor['idade']} anos, sexo {autor['sexo'].lower()}, documento {autor['documento']}, endereço {autor['endereco']}"
            if autor else ""
        ),
        "veiculo": "",
        "medida_protetiva": "Sim" if vd else "Não",
        "violencia_domestica": vd,
        "requer_visita": vd,
        "reincidente": bool(re.search(r"reincid|j[áa] (possu[ií]a|tinha) medida protetiva|descumpr", dinamica, re.IGNORECASE)),
        "descricao": descricao[:150],
        "descricao_dinamica": dinamica_completa,
        "medidas": "",
        "texto_original": dinamica_completa,
        "policiais": policiais,
        "fonte": "SIGESPOL",
        "_boletim": bo,
        "_responsavel_pelotao": responsavel,
        "_endereco_completo": endereco,
    }


def parsear_relatorio(texto):
    m = re.search(r"DETALHAMENTO DAS OCORR[ÊE]NCIAS(.*?)(?:\nPRODUTIVIDADE|\Z)", texto, re.DOTALL)
    corpo = m.group(1) if m else texto

    blocos = re.split(r"(?=TIPO\(S\):)", corpo)
    registros = []
    for bloco in blocos:
        if "TIPO(S):" not in bloco:
            continue
        reg = parsear_bloco(bloco)
        if reg:
            registros.append(reg)
    return registros


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            texto = f.read()
    else:
        texto = sys.stdin.read()

    registros = parsear_relatorio(texto)
    print(json.dumps(registros, ensure_ascii=False, indent=2))
    print(f"\n# Total extraído: {len(registros)}", file=sys.stderr)


if __name__ == "__main__":
    main()
