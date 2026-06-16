import re

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

changes = 0

# ══════════════════════════════════════════════════════════════════
# 1. renderDashboardVCM — remover sub-nav interna + routing de abas
# ══════════════════════════════════════════════════════════════════

OLD = '''  if(!state.vcmFiltro) state.vcmFiltro="todas";
  if(!state.vcmTab) state.vcmTab="dashboard";
  var tab=state.vcmTab;
  var nEnc=(state.encaminhamentos||[]).filter(function(e){return e.vcm&&e.status==="pendente";}).length;

  // Roteador de abas
  if(tab==="encaminhamentos"){ _renderVcmEncaminhamentos(main); return; }'''
NEW = '  if(!state.vcmFiltro) state.vcmFiltro="todas";'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: vcmTab init + routing")

# ══════════════════════════════════════════════════════════════════
# 2. Remover o bloco HTML da sub-nav (Dashboard | Encaminhamentos)
# ══════════════════════════════════════════════════════════════════

OLD = (
    "  var h=\"<div style='max-width:1200px;margin:0 auto;padding:16px'>\";\n"
    "  // ── ABAS PRINCIPAIS ─────────────────────────────────────────────\n"
    "  h+=\"<div style='display:flex;gap:0;margin-bottom:18px;border-bottom:2px solid #3a1a2a'>\";\n"
    "  h+=\"<button onclick=\\\"state.vcmTab='dashboard';renderDashboardVCM(document.getElementById('main')||document.getElementById('main-content'))\\\" style='padding:9px 20px;border:none;border-bottom:3px solid \\\"+(tab===\\\"dashboard\\\"?\\\"#ff1493\\\":\\\"transparent\\\")+\\\";margin-bottom:-2px;background:transparent;color:\\\"+(tab===\\\"dashboard\\\"?\\\"#ff69b4\\\":\\\"#7a5050\\\")+\\\";font-size:13px;font-weight:\\\"+(tab===\\\"dashboard\\\"?\\\"700\\\":\\\"400\\\")+\\\";cursor:pointer'>📊 Dashboard</button>\";\n"
    "  h+=\"<button onclick=\\\"state.vcmTab='encaminhamentos';renderDashboardVCM(document.getElementById('main')||document.getElementById('main-content'))\\\" style='padding:9px 20px;border:none;border-bottom:3px solid \\\"+(tab===\\\"encaminhamentos\\\"?\\\"#ff1493\\\":\\\"transparent\\\")+\\\";margin-bottom:-2px;background:transparent;color:\\\"+(tab===\\\"encaminhamentos\\\"?\\\"#ff69b4\\\":\\\"#7a5050\\\")+\\\";font-size:13px;font-weight:\\\"+(tab===\\\"encaminhamentos\\\"?\\\"700\\\":\\\"400\\\")+\\\";cursor:pointer;display:flex;align-items:center;gap:6px'>📤 Encaminhamentos\\\"+(nEnc>0?\\\" <span style='background:#ff1493;color:#fff;border-radius:10px;padding:1px 7px;font-size:10px;font-weight:700'>\\\"+nEnc+\\\"</span>\\\":\\\"\\\")+\\\"</button>\";\n"
    "  h+=\"</div>\";\n"
)
NEW_HEADER = "  var h=\"<div style='max-width:1200px;margin:0 auto;padding:16px'>\";\n"
if OLD in src:
    src = src.replace(OLD, NEW_HEADER, 1); changes += 1
else:
    print("NAO ACHOU: sub-nav HTML block")

# ══════════════════════════════════════════════════════════════════
# 3. Atualizar título principal e cor do cabeçalho
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<div><h2 style='font-size:20px;font-weight:700;color:#ff69b4;margin:0 0 2px'>🌸 Dashboard VCM</h2>\";"
NEW = "h+=\"<div><h2 style='font-size:20px;font-weight:700;color:#c06080;margin:0 0 2px'>🛡 Proteção VCM</h2>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: titulo Dashboard VCM")

# ══════════════════════════════════════════════════════════════════
# 4. Cor dos filtros de período (botões pill)
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<button onclick=\\\"state.vcmFiltro='\"+f.k+\"';renderDashboardVCM(document.getElementById('main'))\\\" style='padding:5px 13px;border-radius:20px;border:1px solid \\\"+(ativo?\\\"#ff69b4\\\":\\\"#3a1a1a\\\")+\\\";background:\\\"+(ativo?\\\"#ff1493\\\":\\\"transparent\\\")+\\\";color:\\\"+(ativo?\\\"#fff\\\":\\\"#7a5050\\\")+\\\";font-size:11px;font-weight:\\\"+(ativo?\\\"700\\\":\\\"400\\\")+\\\";cursor:pointer'>\"+f.label+\"</button>\";"
NEW = "h+=\"<button onclick=\\\"state.vcmFiltro='\"+f.k+\"';renderDashboardVCM(document.getElementById('main'))\\\" style='padding:5px 13px;border-radius:20px;border:1px solid \\\"+(ativo?\\\"#c06080\\\":\\\"#2a1a2a\\\")+\\\";background:\\\"+(ativo?\\\"#a03050\\\":\\\"transparent\\\")+\\\";color:\\\"+(ativo?\\\"#fff\\\":\\\"#7a6070\\\")+\\\";font-size:11px;font-weight:\\\"+(ativo?\\\"700\\\":\\\"400\\\")+\\\";cursor:pointer'>\"+f.label+\"</button>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: filtros periodo")

# ══════════════════════════════════════════════════════════════════
# 5. Cor do filtro de bairro (linha de cor passada como parâmetro)
# ══════════════════════════════════════════════════════════════════

OLD = 'h+=_htmlFiltrosBairro("renderDashboardVCM(document.getElementById(\'main-content\'))","#ff69b4");'
NEW = 'h+=_htmlFiltrosBairro("renderDashboardVCM(document.getElementById(\'main-content\'))","#c06080");'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: filtrosBairro cor")

# ══════════════════════════════════════════════════════════════════
# 6. Cor do label "Acompanhamento Ativo" na tabela
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<p style='color:#ff69b4;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0'>Acompanhamento Ativo</p>\";"
NEW = "h+=\"<p style='color:#c06080;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0'>Acompanhamento Ativo</p>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: label acompanhamento ativo")

# ══════════════════════════════════════════════════════════════════
# 7. Cor dos labels dos gráficos (3 occurrências de #ff69b4 nos títulos)
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<p style='color:#ff69b4;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 8px'>Casos VD por mês — 2025 vs 2026</p>\";"
NEW = "h+=\"<p style='color:#c06080;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 8px'>Casos VD por mês — 2025 vs 2026</p>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: grafico label 1")

OLD = "h+=\"<p style='color:#ff69b4;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 8px'>Medidas Protetivas — evolução</p>\";"
NEW = "h+=\"<p style='color:#c06080;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 8px'>Medidas Protetivas — evolução</p>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: grafico label 2")

OLD = "h+=\"<p style='color:#ff69b4;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 8px'>Cobertura FRIDA %</p>\";"
NEW = "h+=\"<p style='color:#c06080;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 8px'>Cobertura FRIDA %</p>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: grafico label 3")

# ══════════════════════════════════════════════════════════════════
# 8. Cor do link clicável de vítima na tabela
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<p style='margin:0'><button onclick=\\\"abrirMonitorVCM('\"+v.ocBase.id+\"')\\\" style='background:none;border:none;padding:0;cursor:pointer;color:#ff69b4;font-weight:700;font-size:11px;text-decoration:underline;text-align:left'>\"+esc(v.ocBase.vitima_nome||\"--\")+\"</button></p>\";"
NEW = "h+=\"<p style='margin:0'><button onclick=\\\"abrirMonitorVCM('\"+v.ocBase.id+\"')\\\" style='background:none;border:none;padding:0;cursor:pointer;color:#c06080;font-weight:700;font-size:11px;text-decoration:underline;text-align:left'>\"+esc(v.ocBase.vitima_nome||\"--\")+\"</button></p>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: link vitima tabela")

# ══════════════════════════════════════════════════════════════════
# 9. Cabeçalho da "Fila de Ações" — gradient e texto
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<div style='background:linear-gradient(135deg,#3a0a18,#5a1020);padding:12px 16px;display:flex;align-items:center;justify-content:space-between'>\";"
NEW = "h+=\"<div style='background:linear-gradient(135deg,#1e0a20,#3a0a30);padding:12px 16px;display:flex;align-items:center;justify-content:space-between'>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: fila header gradient")

OLD = "h+=\"<span style='color:#ffb3c8;font-size:13px;font-weight:700'>Fila de Ações — o que fazer agora</span></div>\";"
NEW = "h+=\"<span style='color:#d8a8c0;font-size:13px;font-weight:700'>⚡ Atenção Hoje — o que fazer agora</span></div>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: fila header texto")

# ══════════════════════════════════════════════════════════════════
# 10. Botão "Atender →" dentro da fila de ações
# ══════════════════════════════════════════════════════════════════

OLD = "h+=\"<button onclick=\\\"abrirMonitorVCM('\"+v.ocBase.id+\"')\\\" style='background:linear-gradient(135deg,#5a1020,#8a1838);border:1px solid #ff1493;color:#ffb3c8;padding:7px 14px;border-radius:7px;font-size:11px;font-weight:700;cursor:pointer;white-space:nowrap'>Atender →</button>\";"
NEW = "h+=\"<button onclick=\\\"abrirMonitorVCM('\"+v.ocBase.id+\"')\\\" style='background:linear-gradient(135deg,#3a0a30,#5a1050);border:1px solid #a03050;color:#d8a8c0;padding:7px 14px;border-radius:7px;font-size:11px;font-weight:700;cursor:pointer;white-space:nowrap'>Atender →</button>\";"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: botao atender")

# ══════════════════════════════════════════════════════════════════
# 11. Cor do card de métricas — cor passada como parâmetro "#ff69b4"
# ══════════════════════════════════════════════════════════════════

OLD = 'h+=_metrica("card-ativas",ativas.length,"Casos VD Ativos","👩","#ff69b4","acompanhamento em curso",ativas,_novosMes-_novosPrev,null);'
NEW = 'h+=_metrica("card-ativas",ativas.length,"Casos VD Ativos","👥","#c06080","acompanhamento em curso",ativas,_novosMes-_novosPrev,null);'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: metrica card-ativas")

# ══════════════════════════════════════════════════════════════════
# 12. Ícone VCM na sidebar (de 🌸 para 🛡)
# ══════════════════════════════════════════════════════════════════

OLD = "{k:\"dashvcm\",icon:\"🌸\",label:\"VCM\",badge:_nVcmUrg,cor:\"#ff1493\",fn:function(){setTela(\"dashvcm\");}}"
NEW = "{k:\"dashvcm\",icon:\"🛡\",label:\"VCM\",badge:_nVcmUrg,cor:\"#a03050\",fn:function(){setTela(\"dashvcm\");}}"
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: sidebar icon VCM")

# ══════════════════════════════════════════════════════════════════
# 13. Cor VCM na aba da Fila do Dia (renderFilaDia)
# ══════════════════════════════════════════════════════════════════

OLD = '{k:"vcm",           label:"VCM",               badge:_nVcm,  cor:"#ff69b4"},'
NEW = '{k:"vcm",           label:"VCM",               badge:_nVcm,  cor:"#a03050"},'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: aba vcm cor renderFilaDia")

# ══════════════════════════════════════════════════════════════════
# 14. Badge VCM na Fila do Dia — corrigir contagem
#     Atual: !uf || uf.nivel==="E"  → conta tudo sem FRIDA + elevado (77 casos)
#     Novo:  uf && uf.nivel==="E"   → só risco elevado confirmado
#     + encaminhamentos VCM pendentes
# ══════════════════════════════════════════════════════════════════

OLD = '''  var _nVcm  = (state.db.ocorrencias||[]).filter(function(o){
    if(!(o.violencia_domestica||/maria da penha|violên?cia dom[eé]stica/i.test(o.tipo||"")))return false;
    var fs=(state.db.frida||[]).filter(function(f){return f.ocorrenciaId===o.id;});
    var uf=fs.sort(function(a,b){return(b.data||"")>(a.data||"")?1:-1;})[0];
    return !uf||uf.nivel==="E";
  }).length;'''
NEW = '''  var _nVcm  = (state.db.ocorrencias||[]).filter(function(o){
    if(!(o.violencia_domestica||/maria da penha|violên?cia dom[eé]stica/i.test(o.tipo||"")))return false;
    var fs=(state.db.frida||[]).filter(function(f){return f.ocorrenciaId===o.id;});
    var uf=fs.sort(function(a,b){return(b.data||"")>(a.data||"")?1:-1;})[0];
    return uf&&uf.nivel==="E";
  }).length + (state.encaminhamentos||[]).filter(function(e){return e.vcm&&e.status==="pendente";}).length;'''
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: badge _nVcm renderFilaDia")

# ══════════════════════════════════════════════════════════════════
# 15. Cor da linha no termômetro de risco (links de vítima)
#     Esses estão dentro de _renderVcmEncaminhamentos / termômetro
# ══════════════════════════════════════════════════════════════════
# Os links de vítima no termômetro de risco usam cor padrão (#f5ede0) — OK, não precisa mudar

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print(f"Concluido — {changes} substituicoes aplicadas")
