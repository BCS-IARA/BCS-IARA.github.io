# Redesenho visual — Inventário (header, KPIs, abas, card de conferência)

Mockup aprovado por Oséias. Esta instrução cobre **4 blocos** dentro de
`function renderInventario(main){` em `index.html`. Não mexe em mais nada —
o conteúdo das abas (Itens, Movimentações, Por Policial, Localizações) fica
para uma rodada futura, seguindo o plano de fases já em andamento.

Princípio aplicado em tudo: reaproveitar o padrão "moldura escura, conteúdo
claro" que já existe no Painel do Comandante — não inventar paleta nova.

---

## Bloco 1 — Header / toolbar

Localizar (logo após `var h="<div style='padding:16px;max-width:1100px;margin:0 auto'>";`):

```js
  // Header
  h+="<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px'>";
  h+="<div><h2 style='color:#D9A53C;font-size:20px;font-weight:800;margin:0;font-family:Georgia,serif'>📦 Inventário</h2><p style='color:#a07c58;font-size:12px;margin:2px 0 0'>Gestão de patrimônio — 77ª CIPM BCS</p></div>";
  var _invSincTxt=state.sincErro?"⚠ Sem conexão":state.sincronizando?"⟳ Sincronizando...":state._invLastSync?"✓ "+new Date(state._invLastSync).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}):"—";
  var _invSincCor=state.sincErro?"#A8492E":state.sincronizando?"#C8A84B":state._invLastSync?"#6E8F52":"#6B5236";
  h+="<div style='display:flex;gap:8px;flex-wrap:wrap;align-items:center'>";
  h+="<span style='font-size:10px;color:"+_invSincCor+";border:1px solid "+_invSincCor+"44;border-radius:6px;padding:3px 8px'>"+_invSincTxt+"</span>";
  h+="<button onclick='state._invLastSync=0;_invSincronizarDoSheets().then(function(){var m=document.getElementById(\"main-content\")||document.getElementById(\"main\");if(m&&state.tela===\"inventario\")renderInventario(m);showToast(\"✓ Sincronizado\");})' style='background:#1a2a1a;border:1px solid #10b981;color:#10b981;padding:8px 14px;border-radius:7px;font-size:12px;font-weight:700;cursor:pointer'>🔄 Sincronizar"+(state._invLastSync?" <span style=\"opacity:.6\">"+new Date(state._invLastSync).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})+"</span>":"")+"</button>";
  h+="<button onclick='_invAbrirImport()' style='background:#2a1c10;border:1px solid #C8A84B66;color:#C8A84B;padding:8px 14px;border-radius:7px;font-size:12px;cursor:pointer'>📤 Importar Lista</button>";
  if((state.invItens||[]).length) h+="<button onclick='_invLimparTodos()' style='background:#2a0800;border:1px solid #ef444466;color:#ef4444;padding:8px 14px;border-radius:7px;font-size:12px;cursor:pointer'>🗑 Limpar Tudo</button>";
  h+="<button onclick='_invGerarPDF()' style='background:#1a2a3a;border:1px solid #4a9fd4;color:#4a9fd4;padding:8px 14px;border-radius:7px;font-size:12px;cursor:pointer'>📄 Exportar PDF</button>";
  if(state._invFiltLoc) h+="<button onclick='_invGerarPDFSecao(\""+esc(state._invFiltLoc)+"\")' style='background:#1a2a1a;border:1px solid #6E8F52;color:#6E8F52;padding:8px 14px;border-radius:7px;font-size:12px;cursor:pointer'>📄 PDF da Seção</button>";
  h+="<button onclick='_invAbrirItem(null)' style='background:linear-gradient(135deg,#2a1c10,#3a2818);border:1px solid #C8A84B;color:#f5ede0;padding:8px 16px;border-radius:7px;font-size:13px;font-weight:700;cursor:pointer'>+ Novo Item</button>";
  h+="</div></div>";
```

Substituir por (mesmas funções, mesmos `onclick`, só o agrupamento/estilo muda
— os botões secundários viram um grupo neutro de ícones; só "+ Novo Item"
continua como ação primária):

```js
  // Header
  h+="<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px'>";
  h+="<div><h2 style='color:#D9A53C;font-size:20px;font-weight:800;margin:0;font-family:Georgia,serif'>📦 Inventário</h2><p style='color:#a07c58;font-size:12px;margin:2px 0 0'>Gestão de patrimônio — 77ª CIPM BCS</p></div>";
  var _invSincTxt=state.sincErro?"⚠ Sem conexão":state.sincronizando?"⟳ Sincronizando...":state._invLastSync?"✓ "+new Date(state._invLastSync).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}):"—";
  var _invSincCor=state.sincErro?"#A8492E":state.sincronizando?"#C8A84B":state._invLastSync?"#6E8F52":"#6B5236";
  h+="<div style='display:flex;gap:8px;flex-wrap:wrap;align-items:center'>";
  h+="<span style='font-size:10px;color:"+_invSincCor+";background:"+_invSincCor+"18;border:1px solid "+_invSincCor+"44;border-radius:6px;padding:4px 9px'>"+_invSincTxt+"</span>";
  h+="<div style='display:flex;border:1px solid #5e4636;border-radius:8px;overflow:hidden'>";
  h+="<button onclick='state._invLastSync=0;_invSincronizarDoSheets().then(function(){var m=document.getElementById(\"main-content\")||document.getElementById(\"main\");if(m&&state.tela===\"inventario\")renderInventario(m);showToast(\"✓ Sincronizado\");})' title='Sincronizar"+(state._invLastSync?" — última: "+new Date(state._invLastSync).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}):"")+"' style='background:transparent;border:none;border-right:1px solid #5e4636;color:#a07c58;padding:8px 12px;font-size:13px;cursor:pointer'>🔄</button>";
  h+="<button onclick='_invAbrirImport()' title='Importar Lista' style='background:transparent;border:none;border-right:1px solid #5e4636;color:#a07c58;padding:8px 12px;font-size:13px;cursor:pointer'>📤</button>";
  if((state.invItens||[]).length) h+="<button onclick='_invLimparTodos()' title='Limpar Tudo' style='background:transparent;border:none;border-right:1px solid #5e4636;color:#A8492E;padding:8px 12px;font-size:13px;cursor:pointer'>🗑</button>";
  h+="<button onclick='_invGerarPDF()' title='Exportar PDF' style='background:transparent;border:none;color:#a07c58;padding:8px 12px;font-size:13px;cursor:pointer'>📄</button>";
  if(state._invFiltLoc) h+="<button onclick='_invGerarPDFSecao(\""+esc(state._invFiltLoc)+"\")' title='PDF da Seção' style='background:transparent;border:none;border-left:1px solid #5e4636;color:#6E8F52;padding:8px 12px;font-size:13px;cursor:pointer'>📄+</button>";
  h+="</div>";
  h+="<button onclick='_invAbrirItem(null)' style='background:linear-gradient(135deg,#2a1c10,#3a2818);border:1px solid #C8A84B;color:#f5ede0;padding:8px 16px;border-radius:7px;font-size:13px;font-weight:700;cursor:pointer'>+ Novo Item</button>";
  h+="</div></div>";
```

---

## Bloco 2 — KPIs

Localizar:

```js
  // KPIs
  h+="<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:20px'>";
  h+="<div style='background:#F2E4C8;border:1px solid #5e4636;border-radius:10px;padding:12px;text-align:center'><div style='color:#D9A53C;font-size:24px;font-weight:800'>"+total+"</div><div style='color:#a07c58;font-size:10px;text-transform:uppercase;letter-spacing:.5px'>Total de Itens</div></div>";
  Object.keys(INV_CATS).forEach(function(k){
    h+="<div style='background:#F2E4C8;border:1px solid "+INV_CATS[k].cor+"55;border-radius:10px;padding:12px;text-align:center'>";
    h+="<div style='color:"+INV_CATS[k].cor+";font-size:20px;font-weight:800'>"+INV_CATS[k].icon+" "+(totalCats[k]||0)+"</div>";
    h+="<div style='color:#888;font-size:10px;text-transform:uppercase;letter-spacing:.5px'>"+INV_CATS[k].label+"</div>";
    h+="</div>";
  });
  var nConf=(state.invConferencias||[]).length;
  h+="<div style='background:#F2E4C8;border:1px solid #d4a87a55;border-radius:10px;padding:12px;text-align:center'><div style='color:#d4a87a;font-size:20px;font-weight:800'>📋 "+nConf+"</div><div style='color:#a07c58;font-size:10px;text-transform:uppercase;letter-spacing:.5px'>Conferências</div></div>";
  h+="</div>";
```

Substituir por (o card "Total" vira destaque em moldura escura; os demais
ganham selo circular colorido + borda superior fina na cor da categoria, em
vez do número inteiro pintado — resolve o card "0 Material de Consumo" que
ficava quase invisível):

```js
  // KPIs
  h+="<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:20px'>";
  h+="<div style='background:#2a1c10;border-radius:10px;padding:14px;text-align:center'><div style='color:#D9A53C;font-size:24px;font-weight:800'>"+total+"</div><div style='color:#a07c58;font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-top:3px'>Total de Itens</div></div>";
  Object.keys(INV_CATS).forEach(function(k){
    h+="<div style='background:#F2E4C8;border:1px solid #DBC79E;border-top:3px solid "+INV_CATS[k].cor+";border-radius:10px;padding:14px;text-align:center'>";
    h+="<div style='width:26px;height:26px;border-radius:50%;background:"+INV_CATS[k].cor+"22;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;font-size:14px'>"+INV_CATS[k].icon+"</div>";
    h+="<div style='color:#3D2B1A;font-size:19px;font-weight:800'>"+(totalCats[k]||0)+"</div>";
    h+="<div style='color:#6B5236;font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-top:2px'>"+INV_CATS[k].label+"</div>";
    h+="</div>";
  });
  var nConf=(state.invConferencias||[]).length;
  h+="<div style='background:#F2E4C8;border:1px solid #DBC79E;border-top:3px solid #A87B22;border-radius:10px;padding:14px;text-align:center'>";
  h+="<div style='width:26px;height:26px;border-radius:50%;background:#A87B2222;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;font-size:14px'>📋</div>";
  h+="<div style='color:#3D2B1A;font-size:19px;font-weight:800'>"+nConf+"</div>";
  h+="<div style='color:#6B5236;font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-top:2px'>Conferências</div>";
  h+="</div>";
  h+="</div>";
```

---

## Bloco 3 — Abas (Itens / Movimentações / Conferências / Por Policial / Localizações)

Localizar:

```js
  // Tabs
  h+="<div style='display:flex;gap:0;margin-bottom:16px;border-bottom:1px solid #5e4636;overflow-x:auto'>";
  [["itens","📋 Itens"],["movimentacoes","🚛 Movimentações"],["conferencias","📊 Conferências"],["policiais","👮 Por Policial"],["locais","📍 Localizações"]].forEach(function(pair){
    var active=tab===pair[0];
    h+="<button onclick='state._invTab=\""+pair[0]+"\";_invAplicarFiltros()' style='padding:8px 16px;border:none;border-bottom:3px solid "+(active?"#D9A53C":"transparent")+";background:transparent;color:"+(active?"#D9A53C":"#a07c58")+";font-size:12px;cursor:pointer;font-weight:"+(active?"700":"400")+";white-space:nowrap'>"+pair[1]+"</button>";
  });
  h+="</div>";
```

Substituir por (mesma fórmula de pílula já usada nas abas do Painel do
Comandante — `renderDashComandante`, variável `tabAtiva`/`_cmdTab` — só
trocando o estado para `tab`/`_invTab`):

```js
  // Tabs
  h+="<div style='display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap'>";
  [["itens","📋 Itens"],["movimentacoes","🚛 Movimentações"],["conferencias","📊 Conferências"],["policiais","👮 Por Policial"],["locais","📍 Localizações"]].forEach(function(pair){
    var active=tab===pair[0];
    h+="<button onclick='state._invTab=\""+pair[0]+"\";_invAplicarFiltros()' style='padding:9px 16px;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;border:1px solid "+(active?"#D9A53C":"#5e4636")+";background:"+(active?"#D9A53C22":"#2a1c10")+";color:"+(active?"#D9A53C":"#a07c58")+";white-space:nowrap'>"+pair[1]+"</button>";
  });
  h+="</div>";
```

---

## Bloco 4 — Card de conferência (aba Conferências)

Localizar, dentro de `confs.forEach(function(conf){...})`:

```js
        h+="<div style='background:#F2E4C8;border:1px solid #5e4636;border-radius:10px;padding:14px'>";
        h+="<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px'>";
        h+="<div><span style='color:#d4a87a;font-size:11px'>"+dt+"</span><br><span style='color:#3D2B1A;font-size:13px;font-weight:700'>Conferência "+(conf.concluida?"<span style='color:#3a7a4a;font-size:11px'>✅ Concluída</span>":"<span style='color:#f59e0b;font-size:11px'>⏳ Em andamento</span>")+"</span></div>";
        h+="<div style='display:flex;gap:6px'>";
        if(!conf.concluida) h+="<button onclick='_invAbrirConferencia(\""+conf.id+"\")' style='background:#EAD9B8;border:1px solid #A87B22;color:#6B5236;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>▶ Continuar</button>";
        h+="<button onclick='_invGerarPDFConferencia(\""+conf.id+"\")' style='background:#1a1a2a;border:1px solid #4a9fd433;color:#4a9fd4;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>📄 PDF</button>";
        if(conf.concluida) h+="<button onclick='_invAbrirParecerModal(\""+conf.id+"\")' style='background:#2a1c10;border:1px solid #C8A84B66;color:#C8A84B;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>📋 Parecer</button>";
        h+="<button onclick='_invExcluirConferencia(\""+conf.id+"\")' style='background:#1a0808;border:1px solid #ef444466;color:#ef4444;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>🗑 Excluir</button>";
        h+="</div></div>";
        h+="<div style='display:flex;gap:8px;flex-wrap:wrap'>";
        if(nOk) h+="<span style='background:#22c55e22;color:#22c55e;padding:3px 10px;border-radius:8px;font-size:12px'>✓ "+nOk+" OK</span>";
        if(nDiv) h+="<span style='background:#f59e0b22;color:#f59e0b;padding:3px 10px;border-radius:8px;font-size:12px'>⚠ "+nDiv+" Divergência</span>";
        if(nAus) h+="<span style='background:#ef444422;color:#ef4444;padding:3px 10px;border-radius:8px;font-size:12px'>✗ "+nAus+" Ausente</span>";
        if(nPend>0) h+="<span style='background:#88888822;color:#888;padding:3px 10px;border-radius:8px;font-size:12px'>⏳ "+nPend+" Pendente</span>";
        h+="</div>";
        if(conf.responsavel1) h+="<div style='color:#666;font-size:11px;margin-top:8px'>Resp: "+esc(conf.responsavel1)+(conf.responsavel2?" / "+esc(conf.responsavel2):"")+"</div>";
        h+="</div>";
```

Substituir por (mesma lógica e badges, agora com faixa escura no topo
agrupando data/status/ações — mesmo padrão usado no cabeçalho do modal de
conferência):

```js
        h+="<div style='border-radius:10px;overflow:hidden;border:1px solid #5e4636'>";
        h+="<div style='background:#2a1c10;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>";
        h+="<div><span style='color:#a07c58;font-size:11px'>"+dt+"</span><br><span style='color:#f5ede0;font-size:13px;font-weight:700'>Conferência "+(conf.concluida?"<span style='color:#6E8F52;font-size:11px'>✅ Concluída</span>":"<span style='color:#f59e0b;font-size:11px'>⏳ Em andamento</span>")+"</span></div>";
        h+="<div style='display:flex;gap:6px;flex-wrap:wrap'>";
        if(!conf.concluida) h+="<button onclick='_invAbrirConferencia(\""+conf.id+"\")' style='background:transparent;border:1px solid #C8A84B;color:#D9A53C;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>▶ Continuar</button>";
        h+="<button onclick='_invGerarPDFConferencia(\""+conf.id+"\")' style='background:transparent;border:1px solid #4a3224;color:#a07c58;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>📄 PDF</button>";
        if(conf.concluida) h+="<button onclick='_invAbrirParecerModal(\""+conf.id+"\")' style='background:transparent;border:1px solid #4a3224;color:#a07c58;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>📋 Parecer</button>";
        h+="<button onclick='_invExcluirConferencia(\""+conf.id+"\")' style='background:transparent;border:1px solid #7a3a3a;color:#d0a0a0;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>🗑 Excluir</button>";
        h+="</div></div>";
        h+="<div style='background:#F2E4C8;padding:14px 16px'>";
        h+="<div style='display:flex;gap:8px;flex-wrap:wrap'>";
        if(nOk) h+="<span style='background:#22c55e22;color:#22c55e;padding:3px 10px;border-radius:8px;font-size:12px'>✓ "+nOk+" OK</span>";
        if(nDiv) h+="<span style='background:#f59e0b22;color:#f59e0b;padding:3px 10px;border-radius:8px;font-size:12px'>⚠ "+nDiv+" Divergência</span>";
        if(nAus) h+="<span style='background:#ef444422;color:#ef4444;padding:3px 10px;border-radius:8px;font-size:12px'>✗ "+nAus+" Ausente</span>";
        if(nPend>0) h+="<span style='background:#88888822;color:#888;padding:3px 10px;border-radius:8px;font-size:12px'>⏳ "+nPend+" Pendente</span>";
        h+="</div>";
        if(conf.responsavel1) h+="<div style='color:#6B5236;font-size:11px;margin-top:8px'>Resp: "+esc(conf.responsavel1)+(conf.responsavel2?" / "+esc(conf.responsavel2):"")+"</div>";
        h+="</div>";
        h+="</div>";
```

**Atenção:** este bloco fica logo depois das linhas que calculam `nOk`,
`nDiv`, `nAus`, `nPend` (que podem já ter sido alteradas pela instrução
anterior de correção de contagem — `INSTRUCAO_CODE_FIX_CONTAGEM_CONFERENCIA.md`).
Não mexer nessas linhas de cálculo agora; o trecho a substituir aqui começa
exatamente em `h+="<div style='background:#F2E4C8;border:1px solid #5e4636;border-radius:10px;padding:14px'>";`,
que é puramente visual e não depende de qual versão do cálculo está em vigor.

---

## Fora de escopo (não mexer agora)

- Conteúdo interno das abas Itens, Movimentações, Por Policial, Localizações
  (filtros, listas, tabelas) — fica para as próximas fases do
  `PLANO_IMPLEMENTACAO.md`.
- Modal de conferência (`_invRenderConferencia`) — já segue o padrão moldura
  escura/conteúdo claro, não precisa de ajuste agora.
- Alertas de validade vencida / sem conferência há 30 dias (logo abaixo dos
  KPIs) — mantidos como estão.

## Teste manual após a correção

1. Abrir Inventário e conferir: card "Total" escuro se destacando, demais
   cards com selo circular colorido e borda superior fina.
2. Conferir grupo de ícones do header (sincronizar/importar/limpar/PDF) — só
   "+ Novo Item" deve continuar com destaque (moldura escura + dourado).
3. Clicar em cada aba (Itens, Movimentações, Conferências, Por Policial,
   Localizações) e confirmar que a aba ativa aparece como pílula
   preenchida/dourada e as demais como pílulas escuras neutras.
4. Na aba Conferências, conferir que o card tem a faixa escura no topo (data
   + status + ações) e o conteúdo claro abaixo (badges + responsáveis),
   testando os botões Continuar/PDF/Parecer/Excluir.
5. Testar em mobile (largura estreita) — os grupos usam `flex-wrap`, então
   devem quebrar linha sem cortar texto.
