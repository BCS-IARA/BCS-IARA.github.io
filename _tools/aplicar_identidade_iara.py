#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   IARA — Aplicar Identidade Visual ao index.html             ║
║   BCS Nova Cidade · 77ª CIPM                                 ║
╚══════════════════════════════════════════════════════════════╝

Como usar:
  1. Coloque este script na mesma pasta que o index.html
  2. Execute: python aplicar_identidade_iara.py
  3. O arquivo original vira index_BACKUP.html
  4. O index.html atualizado fica pronto para usar

Mudanças aplicadas:
  ✦ Fonte: DM Sans → Syne (títulos) + Plus Jakarta Sans (interface)
  ✦ Âmbar: #D9A53C → #C47A2B (mais cobre/quente)
  ✦ Badges: border-radius 5px → 20px (estilo pílula)
  ✦ Logo BCS inserida no sidebar header
"""

import os
import shutil

# ── Arquivo alvo ──────────────────────────────────────────────
ARQUIVO = "index.html"
BACKUP  = "index_BACKUP.html"

# ── Verificar existência ───────────────────────────────────────
if not os.path.exists(ARQUIVO):
    print(f"❌  Arquivo '{ARQUIVO}' não encontrado.")
    print("    Execute este script na mesma pasta do index.html")
    exit(1)

# ── Fazer backup ───────────────────────────────────────────────
shutil.copy2(ARQUIVO, BACKUP)
print(f"✓  Backup criado: {BACKUP}")

# ── Ler conteúdo ───────────────────────────────────────────────
with open(ARQUIVO, "r", encoding="utf-8") as f:
    html = f.read()

total_mudancas = 0

def substituir(html, antigo, novo, descricao):
    global total_mudancas
    if antigo in html:
        html = html.replace(antigo, novo)
        total_mudancas += 1
        print(f"✓  {descricao}")
    else:
        print(f"⚠  Não encontrado (pode já estar atualizado): {descricao}")
    return html

# ════════════════════════════════════════════════════════════════
# 1 — FONTES: DM Sans → Syne + Plus Jakarta Sans
# ════════════════════════════════════════════════════════════════
html = substituir(
    html,
    '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>',
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800'
    '&family=Plus+Jakarta+Sans:wght@300;400;500;600;700'
    '&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">',
    "Google Fonts: DM Sans → Syne + Plus Jakarta Sans"
)

# ════════════════════════════════════════════════════════════════
# 2 — BODY: font-family
# ════════════════════════════════════════════════════════════════
html = substituir(
    html,
    "font-family:'DM Sans',sans-serif;",
    "font-family:'Plus Jakarta Sans',sans-serif;",
    "body: font-family DM Sans → Plus Jakarta Sans"
)

# ════════════════════════════════════════════════════════════════
# 3 — HEADINGS: Georgia → Syne
# ════════════════════════════════════════════════════════════════
html = substituir(
    html,
    "h1,h2,h3,.titulo-serif{font-family:Georgia,'Times New Roman',serif;}",
    "h1,h2,h3,.titulo-serif{"
    "font-family:'Syne',sans-serif;"
    "font-weight:700;"
    "letter-spacing:-0.02em;"
    "}",
    "h1/h2/h3: Georgia → Syne"
)

# ════════════════════════════════════════════════════════════════
# 4 — ÂMBAR: calibrar para tom cobre/quente
# ════════════════════════════════════════════════════════════════
html = substituir(
    html,
    "--ambar:         #D9A53C;",
    "--ambar:         #C47A2B;",
    "--ambar: #D9A53C → #C47A2B"
)

html = substituir(
    html,
    "--ambar-2:       #A87B22;",
    "--ambar-2:       #8B5514;",
    "--ambar-2: #A87B22 → #8B5514"
)

html = substituir(
    html,
    "--ambar-claro:   #EFDFC0;",
    "--ambar-claro:   #F5EBD8;",
    "--ambar-claro: #EFDFC0 → #F5EBD8"
)

# Alias gold
html = substituir(
    html,
    "--gold:#D9A53C;",
    "--gold:#C47A2B;",
    "--gold (alias): #D9A53C → #C47A2B"
)

# theme-color no meta
html = substituir(
    html,
    'content="#d4a87a"',
    'content="#C47A2B"',
    "meta theme-color"
)

# ════════════════════════════════════════════════════════════════
# 5 — BADGES: border-radius 5px → 20px (estilo pílula)
# ════════════════════════════════════════════════════════════════
html = substituir(
    html,
    ".tag{display:inline-flex;align-items:center;padding:3px 9px;border-radius:5px;",
    ".tag{display:inline-flex;align-items:center;padding:3px 9px;border-radius:20px;",
    ".tag: border-radius 5px → 20px"
)

# ════════════════════════════════════════════════════════════════
# 6 — SIDEBAR HEADER: adicionar logo + wordmark Syne
#     Procura o padrão do sidebar-header e insere o logo
# ════════════════════════════════════════════════════════════════
SIDEBAR_ANTIGO = "class='sidebar-header'"
SIDEBAR_NOVO_LOGO = """class='sidebar-header' style='display:flex;align-items:center;gap:12px;'"""

# Inserir logo como primeiro elemento dentro do sidebar-header
# Detecta a div sidebar-header e adiciona img antes do conteúdo textual
import re

# Padrão: <div class='sidebar-header'>...conteúdo...
# Vamos tentar localizar e injetar a img
LOGO_HTML = "<img src='logo-bcs.png' style='width:40px;height:40px;object-fit:contain;flex-shrink:0;' alt='BCS'>"

# Busca por "sidebar-header" como classe para identificar o bloco
if "sidebar-header" in html:
    # Injeta o logo no início do primeiro div.sidebar-header
    html = re.sub(
        r"(<div[^>]*class=['\"]sidebar-header['\"][^>]*>)",
        r"\1" + LOGO_HTML,
        html,
        count=1
    )
    total_mudancas += 1
    print("✓  Logo BCS inserida no sidebar-header")
else:
    print("⚠  sidebar-header não encontrado — logo não inserida")

# ════════════════════════════════════════════════════════════════
# SALVAR
# ════════════════════════════════════════════════════════════════
with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(html)

print()
print(f"═══════════════════════════════════════")
print(f"  ✦ {total_mudancas} mudanças aplicadas com sucesso!")
print(f"  ✦ Arquivo salvo: {ARQUIVO}")
print(f"  ✦ Backup em:     {BACKUP}")
print(f"═══════════════════════════════════════")
print()
print("Próximo passo: abra o index.html no browser e confirme as mudanças.")
print("Se algo não ficou certo, restaure com: cp index_BACKUP.html index.html")
