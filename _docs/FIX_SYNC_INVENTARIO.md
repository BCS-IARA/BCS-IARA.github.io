# Hotfix — Sincronização do Inventário (IARA)

**Prioridade:** crítica. Bloqueia uso com múltiplos auxiliares fazendo conferência simultânea.
**Não mexer** em UX/visual do `PLANO_IMPLEMENTACAO.md` neste hotfix — escopo isolado.

## Diagnóstico (resumo)

1. `_mergeInv` (index.html ~18161) e `_mergeById` (index.html ~562) só **adicionam** registros com `id` novo vindos do Sheets; nunca atualizam um `id` que já existe localmente. Resultado: edições em item/conferência feitas em outro dispositivo nunca chegam — nem com reload de página, porque o boot sync (`carregarDadosAppDoSheets`, ~678-830) usa a mesma lógica.
2. `_invSalvarConferencia` (~18831) grava o objeto `conf` inteiro (incluindo `conf.itens{}`) de uma vez. Se dois auxiliares editam a **mesma conferência** em dispositivos diferentes, quem salva por último sobrescreve o trabalho do outro — mesmo corrigindo (1), porque o servidor (`_salvarJson`, app_script.txt ~1476) também faz overwrite cego por `id`.
3. Sem botão de sincronizar manual nem indicador de última atualização no módulo (existe no Livro de Parte, não no Inventário). Throttle de sync automático é 5 min e só roda se a tela Inventário estiver aberta.
4. Depois do boot sync, a tela "inventario" não está na lista de re-render automático (index.html ~1154), então mesmo quando o sync traz dado novo, quem está parado na tela não vê sem trocar de aba.

## Mudanças

### 1. Servidor (app_script.txt) — merge seguro para conferências

Esta é a correção que elimina a perda de dado em edição concorrente. Substituir `salvarInvConferencia` (linha ~1659):

```javascript
function salvarInvConferencia(ss, dados) {
  var lock = LockService.getScriptLock();
  lock.waitLock(15000);
  try {
    var copia = Object.assign({}, dados);
    if (copia.assin1 && copia.assin1.length > 2000) copia.assin1 = "[assin_local]";
    if (copia.assin2 && copia.assin2.length > 2000) copia.assin2 = "[assin_local]";
    var aba = _garantirAbaJson(ss, "inv_conferencias", "#0a1a10", "#6ee7b7");
    var nRows = aba.getLastRow() - 1;
    if (nRows > 0) {
      var ids = aba.getRange(2, 1, nRows, 1).getValues();
      for (var i = 0; i < ids.length; i++) {
        if (String(ids[i][0]) === String(copia.id)) {
          var atualRaw = aba.getRange(i+2, 3).getValue();
          var atual = {};
          try { atual = JSON.parse(atualRaw || "{}"); } catch(e) {}
          // União dos itens marcados — ninguém perde marcação feita por outro device
          var itensMesclados = Object.assign({}, atual.itens || {}, copia.itens || {});
          var mesclado = Object.assign({}, atual, copia, { itens: itensMesclados });
          aba.getRange(i+2, 2).setValue(mesclado.criadoEm || new Date().toISOString());
          aba.getRange(i+2, 3).setValue(JSON.stringify(mesclado));
          return { ok: true, id: copia.id, acao: "mesclado", registro: mesclado };
        }
      }
    }
    aba.appendRow([copia.id, copia.criadoEm || new Date().toISOString(), JSON.stringify(copia)]);
    return { ok: true, id: copia.id, acao: "inserido", registro: copia };
  } finally {
    lock.releaseLock();
  }
}
```

Por que funciona: cada salvamento lê o estado atual da planilha, funde o mapa `itens` (união — item marcado por qualquer um dos dois dispositivos permanece marcado) e só então grava de volta, com `LockService` evitando que duas gravações simultâneas colidam. Campos escalares (`responsavel1`, `assin1`, `concluida` etc.) seguem "último a salvar vence", que é aceitável porque normalmente só uma pessoa fecha a conferência.

A resposta do `doGet`/`saida` para `acao==="salvar" && tipo==="inv_conferencia"` (linha ~1238) já repassa o retorno de `salvarInvConferencia` — não precisa mudar a rota, só a função.

### 2. Cliente (index.html) — adicionar timestamp de atualização

Em `_invSalvarItem` (~18456-18489), adicionar ao objeto `item`:
```javascript
atualizadoEm: new Date().toISOString(),
```

Em `_invConfirmarMovimentacao` (~18653), `_invConfirmarDevolucao` (~19274) e `_invEnviarFotoEAtualizarItem` (~18121-18124), logo antes de `_invEnviarSheets("inv_item", state.invItens[idx])`, adicionar:
```javascript
state.invItens[idx].atualizadoEm = new Date().toISOString();
```

Em `_invSalvarConferencia` (~18837, junto com `conf.responsavel1=resp1;`), adicionar:
```javascript
conf.atualizadoEm = new Date().toISOString();
```

### 3. Cliente — merge por timestamp em vez de só-adição

Adicionar função nova (perto de `_mergeById`, linha ~562):

```javascript
function _mergeByIdTimestamp(local, remoto, campo){
  campo = campo || "atualizadoEm";
  if(!remoto || !Array.isArray(remoto) || !remoto.length) return local||[];
  var map = {};
  (local||[]).forEach(function(x){ if(x&&x.id) map[String(x.id)] = x; });
  remoto.forEach(function(r){
    if(!r || !r.id) return;
    var k = String(r.id);
    var loc = map[k];
    if(!loc || (r[campo]||r.criadoEm||"") > (loc[campo]||loc.criadoEm||"")) map[k] = r;
  });
  return Object.keys(map).map(function(k){ return map[k]; });
}
```

Trocar as chamadas que usam `state.invItens` e `state.invConferencias`:
- Linha ~807: `state.invItens = _mergeById(state.invItens||[], invItensSheets);` → `_mergeByIdTimestamp(...)`
- Linha ~809: `state.invConferencias = _mergeById(state.invConferencias||[], invConfSheets);` → `_mergeByIdTimestamp(...)`
- Dentro de `_invSincronizarDoSheets` (~18161-18170), trocar o uso de `_mergeInv` por `_mergeByIdTimestamp` para `rItens`→`state.invItens` e `rConfs`→`state.invConferencias`. Manter `_mergeInv` (só-adição) para `invMovimentacoes`, que é log imutável — não precisa de merge por timestamp.

### 4. UI — visibilidade e velocidade do sync

No header do Inventário (`renderInventario`, perto de onde estão os botões "Importar Lista"/"Exportar PDF", ~18897), adicionar botão de sync manual + selo de última atualização, no mesmo padrão do Livro de Parte (referência: linha ~13306):
```javascript
h+="<button onclick='state._invLastSync=0;_invSincronizarDoSheets().then(function(){_invAplicarFiltros();showToast(\"✓ Sincronizado\");})' style='background:#1a2a1a;border:1px solid #10b98166;color:#10b981;padding:8px 14px;border-radius:7px;font-size:12px;cursor:pointer'>🔄 Sincronizar"+(state._invLastSync?" <span style=\"opacity:.6\">"+new Date(state._invLastSync).toLocaleTimeString(\"pt-BR\",{hour:\"2-digit\",minute:\"2-digit\"})+"</span>":"")+"</button>";
```

No mesmo `renderInventario` (~18874-18881), reduzir o throttle de `300000` para `60000` e adicionar polling ativo enquanto a tela estiver aberta, igual ao padrão do armamento (~13283-13289):
```javascript
if(state._invPollTimer) clearInterval(state._invPollTimer);
state._invPollTimer=setInterval(function(){
  if(state.tela!=="inventario"){ clearInterval(state._invPollTimer); return; }
  state._invLastSync=0;
  _invSincronizarDoSheets().then(function(){
    var m=document.getElementById("main-content")||document.getElementById("main");
    if(m&&state.tela==="inventario") renderInventario(m);
  });
},30000);
```

Linha ~1154: adicionar `"inventario"` na lista de telas que re-renderizam após o boot sync:
```javascript
if(mRe&&(state.tela==="projetos"||state.tela==="dashprojetos"||state.tela==="calendario"||state.tela==="escolas"||state.tela==="dashvcm"||state.tela==="inventario")) renderTela();
```

### 5. Modal de Conferência reativo

Em `_invSincronizarDoSheets`, no `.then()` que já existe em `renderInventario` (~18877-18880) — e também no callback do botão manual do item 4 — se o modal `#modal-inv-conf` estiver aberto, reabrir para refletir dado novo sem perder o que já foi preenchido na sessão atual:
```javascript
var modalAberto = document.getElementById("modal-inv-conf");
if(modalAberto && window._invConfAtual){
  var idAtual = window._invConfAtual.id;
  modalAberto.remove();
  _invAbrirConferencia(idAtual);
}
```
Atenção: isso descarta marcações feitas na sessão atual e ainda não salvas (não há "Salvar Progresso" automático). Se preferir não perder digitação em andamento, só fazer esse refresh quando `concluida !== true` E não houver marcações pendentes não salvas — ou simplesmente orientar o usuário a clicar "💾 Salvar Progresso" com frequência. Recomendo manter simples por agora: refresh direto, e reforçar para os auxiliares salvarem progresso a cada poucos itens marcados (o merge do item 1 já garante que ninguém perde o que foi salvo).

## Checklist de teste antes de liberar para os auxiliares

- Dois navegadores diferentes, mesma conferência ("▶ Continuar"): marcar itens diferentes em cada um, salvar nos dois, sincronizar — confirmar que os itens marcados nos dois aparecem somados, nenhum se perde.
- Editar localização de um item num dispositivo, confirmar que aparece atualizado no outro em até ~30-60s sem precisar dar F5.
- Adicionar item novo (ex.: o televisor) num dispositivo, confirmar que aparece no outro dentro do mesmo intervalo, tanto na aba Itens quanto numa Conferência recém-aberta.
- Botão "🔄 Sincronizar" funciona e atualiza o selo de horário.
