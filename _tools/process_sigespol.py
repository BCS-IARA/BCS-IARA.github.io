import sys
import pandas as pd
import json
import re
from datetime import datetime, timezone

# Force UTF-8 output on Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_FILE  = r"C:\Users\oseia\Downloads\BCS\SIGESPOL_01-01-2025_ate_07-05-2026.xlsx"
OUTPUT_XLSX = r"C:\Users\oseia\Downloads\BCS\BCS_ocorrencias_filtradas.xlsx"
OUTPUT_JSON = r"C:\Users\oseia\Downloads\BCS\BCS_importacao_sigespol.json"

BAIRRO_KEYWORDS = [
    "Primavera",
    "Alto Maron",
    "Alto Marom",
    "Alto do Panorama",
    "Panorama",
    "Guarani",
    "Cruzeiro",
    "Pedrinhas",
    "Europa Unida",
]

NORMALIZE = {
    "Alto Maron":       "Alto Marom",
    "Alto do Panorama": "Panorama",
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def extract_bairro(local_str):
    """
    Extract bairro from strings like:
      "Rua B 38, Primavera - Zona Urbana"
      "Av. X, S/N, Alto Maron - Zona Urbana"
    Strategy:
      1. Grab the segment before ' - Zona' (after last comma before it).
      2. If that segment contains a known keyword, use the matching keyword.
      3. Otherwise return the segment as-is.
    """
    if not isinstance(local_str, str):
        return ""

    # Find segment before " - Zona"
    zona_match = re.search(r",\s*([^,]+?)\s*-\s*Zona", local_str)
    if zona_match:
        candidate = zona_match.group(1).strip()
        # Check if any bairro keyword appears in it (prefer longer match)
        matched = [kw for kw in BAIRRO_KEYWORDS if kw.lower() in candidate.lower()]
        if matched:
            # Return the longest matching keyword (most specific)
            return max(matched, key=len)
        return candidate

    # Fallback: check entire string for known keywords
    matched = [kw for kw in BAIRRO_KEYWORDS if kw.lower() in local_str.lower()]
    if matched:
        return max(matched, key=len)

    # Last resort: after last comma
    parts = local_str.rsplit(",", 1)
    if len(parts) == 2:
        return parts[1].strip()
    return local_str.strip()


def normalize_bairro(bairro):
    for raw, canonical in NORMALIZE.items():
        if raw.lower() == bairro.lower():
            return canonical
    return bairro


def local_contains_bairro(local_str):
    if not isinstance(local_str, str):
        return False
    local_lower = local_str.lower()
    return any(kw.lower() in local_lower for kw in BAIRRO_KEYWORDS)


def parse_datetime(dt_str):
    """
    Parse strings like '07/05/2026 às 11:50' or '07/05/2026 11:50'
    Returns (date_str 'YYYY-MM-DD', time_str 'HH:MM')
    """
    if not isinstance(dt_str, str):
        if isinstance(dt_str, datetime):
            return dt_str.strftime("%Y-%m-%d"), dt_str.strftime("%H:%M")
        return ("", "")
    # strip "às"
    clean = dt_str.replace(" às ", " ").replace("às ", "").strip()
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(clean, fmt)
            return parsed.strftime("%Y-%m-%d"), parsed.strftime("%H:%M")
        except ValueError:
            pass
    return ("", "")


def to_str(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


def build_occurrence(row):
    cod      = to_str(row.get("Cód"))
    tipo     = to_str(row.get("Tipo")).title()
    data_raw = to_str(row.get("Data"))
    municipio= "Vitória da Conquista"
    local    = to_str(row.get("Local"))
    bairro   = normalize_bairro(extract_bairro(local))
    resp     = to_str(row.get("Responsável"))
    desc     = to_str(row.get("Descrição"))
    din      = to_str(row.get("Dinâmica dos fatos"))
    medidas  = to_str(row.get("Medidas adotadas"))
    efetivo  = to_str(row.get("Efetivo Empregado"))
    objetos  = to_str(row.get("Objetos Relacionados"))
    armas    = to_str(row.get("Armas Apreendidas"))
    drogas   = to_str(row.get("Drogas Apreendidas"))
    rotulos  = to_str(row.get("Rótulos"))

    data_str, hora_str = parse_datetime(data_raw)

    # Build objetos field
    obj_parts = [p for p in [objetos] if p]
    if armas:
        obj_parts.append(f"Armas: {armas}")
    if drogas:
        obj_parts.append(f"Drogas: {drogas}")
    objetos_final = "; ".join(obj_parts)

    # ISO timestamp
    if data_str and hora_str:
        try:
            ts = datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M")
            criado_em = ts.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            criado_em = ""
    elif data_str:
        criado_em = f"{data_str}T00:00:00"
    else:
        criado_em = ""

    return {
        "id":                   f"oc_sigespol_{cod}",
        "numero":               cod,
        "tipo":                 tipo,
        "data":                 data_str,
        "hora":                 hora_str,
        "municipio":            municipio,
        "local":                local,
        "bairro":               bairro,
        "responsavel":          resp,
        "descricao":            desc,
        "descricao_dinamica":   din,
        "medidas":              medidas,
        "policiais":            efetivo,
        "objetos":              objetos_final,
        "classificacao_sigespol": rotulos,
        "fonte":                "SIGESPOL",
        "criadoEm":             criado_em,
    }


# ─── MAIN ──────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PROCESSANDO PLANILHA SIGESPOL")
print("=" * 60)

# 1. Load
print(f"\nCarregando: {INPUT_FILE}")
df = pd.read_excel(INPUT_FILE, dtype=str)
print(f"Colunas encontradas: {list(df.columns)}")
total_original = len(df)
print(f"Total de linhas no original: {total_original}")

# 2. Filter
mask = df["Local"].apply(local_contains_bairro)
df_filtered = df[mask].copy()

# 3. Extract & normalize bairro column
df_filtered["Bairro"] = df_filtered["Local"].apply(
    lambda x: normalize_bairro(extract_bairro(x))
)

total_filtered = len(df_filtered)
print(f"Total após filtro de bairros: {total_filtered}")

# 4. Count per bairro
print("\nContagem por bairro:")
bairro_counts = df_filtered["Bairro"].value_counts()
for bairro, count in bairro_counts.items():
    print(f"  {bairro}: {count}")

# 5. Save filtered xlsx
print(f"\nSalvando planilha filtrada em: {OUTPUT_XLSX}")
df_filtered.to_excel(OUTPUT_XLSX, index=False)
print("Planilha salva com sucesso.")

# 6. Build JSON objects
print("\nConvertendo para formato BCS JSON...")
occurrences = []
for _, row in df_filtered.iterrows():
    occurrences.append(build_occurrence(row))

export_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

bcs_json = {
    "versao":      "bcs_backup_v1",
    "exportadoEm": export_ts,
    "db": {
        "ocorrencias":  occurrences,
        "atendimentos": [],
        "visitas":      [],
        "agendamentos": [],
    }
}

# 7. Save JSON
print(f"Salvando JSON em: {OUTPUT_JSON}")
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(bcs_json, f, ensure_ascii=False, indent=2)
print("JSON salvo com sucesso.")

# 8. Summary
print("\n" + "=" * 60)
print("RESUMO FINAL")
print("=" * 60)
print(f"Total original:         {total_original}")
print(f"Total filtrado:         {total_filtered}")
print(f"Ocorrências no JSON:    {len(occurrences)}")
print(f"Exportado em:           {export_ts}")

print("\nContagem por bairro:")
for bairro, count in bairro_counts.items():
    print(f"  {bairro}: {count}")

print("\n--- Amostra: 2 primeiros objetos JSON ---\n")
for obj in occurrences[:2]:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    print()

print("=" * 60)
print("CONCLUÍDO COM SUCESSO")
print("=" * 60)
