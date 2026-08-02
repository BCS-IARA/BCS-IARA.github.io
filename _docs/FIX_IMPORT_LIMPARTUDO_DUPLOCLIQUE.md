# Fix — Limpar Tudo, Importação não sincroniza, e clique duplo no Salvar

Três problemas, todos contribuindo pra duplicação de itens. O da importação é mais sério do que parecia — vem antes dos outros dois em prioridade.

## 1. Importação nunca envia os itens pra planilha (achado novo, crítico)

**Causa:** `_invExecutarImport` (linha 24388) só chama `_invSalvarLocal()` no final — que só grava no `localStorage` do navegador (linha 21783-21785). Em nenhum momento chama `_invEnviarSheets("inv_item", item)` pra cada item importado. Resultado: tudo que é importado **fica só no aparelho de quem importou**. Nenhum outro dispositivo vê esses itens depois de sincronizar, porque eles nunca chegaram na aba `inv_itens` da planilha (a única fonte que `_invSincronizarDoSheets`/conferência leem).

Isso é mais grave que duplicação: é invisibilidade. E é uma porta pra duplicação indireta — se dois aparelhos importarem listas parecidas sem saber que o outro já tinha feito (porque nenhum vê o que o outro importou), ou se alguém usar a ferramenta de "Reenviar inventário ao Sheets" (em Configurações) depois de múltiplos imports acumulados em dispositivos diferentes, tudo se mistura na planilha de uma vez.

**Correção:** dentro do `linhas.forEach` (linha 24410), no final de cada iteração (depois de decidir se foi substituído ou criado, linha 24465 `}` antes do `});` que fecha o forEach), guardar o item pra enviar depois em lote. E enviar tudo em sequência ao final, evitando disparar centenas de chamadas simultâneas.

Localizar (linha 24452-24465):
```javascript
    // Substitui ou adiciona
    if(substituir && tomb && idxTomb[tomb]!==undefined){
      var idx=idxTomb[tomb];
      item.id=state.invItens[idx].id;
      item.criadoEm=state.invItens[idx].criadoEm;
      item.localizacao=state.invItens[idx].localizacao||item.localizacao;
      item.tipo_carga=state.invItens[idx].tipo_carga||"none";
      item.observacoes=state.invItens[idx].observacoes||"";
      state.invItens[idx]=item;
      substituidos++;
    } else {
      state.invItens.push(item);
      importados++;
    }
```

Substituir por (com a melhoria de dedup do item 1b explicada abaixo já incluída):
```javascript
    // Substitui ou adiciona — casa por tombamento OU, na ausência dele, por número de série
    var tombKey=tomb.toUpperCase();
    var serieKey=String(item.numero_serie||"").trim().toUpperCase();
    var idxExistente = substituir && tombKey && idxTomb[tombKey]!==undefined ? idxTomb[tombKey]
                      : substituir && serieKey && idxSerie[serieKey]!==undefined ? idxSerie[serieKey]
                      : -1;
    if(idxExistente>=0){
      var idx=idxExistente;
      item.id=state.invItens[idx].id;
      item.criadoEm=state.invItens[idx].criadoEm;
      item.localizacao=state.invItens[idx].localizacao||item.localizacao;
      item.tipo_carga=state.invItens[idx].tipo_carga||"none";
      item.observacoes=state.invItens[idx].observacoes||"";
      item.atualizadoEm=new Date().toISOString();
      state.invItens[idx]=item;
      substituidos++;
    } else {
      if(!tomb && !serieKey) semIdentificador++;
      item.atualizadoEm=new Date().toISOString();
      state.invItens.push(item);
      importados++;
    }
    _itensParaEnviar.push(item);
```

E logo antes do `linhas.forEach` (linha 24409-24410), declarar as variáveis novas:
```javascript
  var importados=0, substituidos=0, ignorados=0, semIdentificador=0;
  var _itensParaEnviar=[];
  linhas.forEach(function(row){
```

### 1a. Enviar tudo pra planilha depois do loop, em sequência

Substituir o final da função (linha 24466-24476):
```javascript
  });

  _invSalvarLocal();
  document.getElementById("modal-inv-import").remove();
  var msg="✓ "+importados+" importados";
  if(substituidos) msg+=", "+substituidos+" atualizados";
  if(ignorados) msg+=" ("+ignorados+" ignorados)";
  showToast(msg);
  var main=document.getElementById("main-content")||document.getElementById("main");
  if(main) renderInventario(main);
}
```

Por:
```javascript
  });

  _invSalvarLocal();
  document.getElementById("modal-inv-import").remove();
  var msg="✓ "+importados+" importados";
  if(substituidos) msg+=", "+substituidos+" atualizados";
  if(ignorados) msg+=" ("+ignorados+" ignorados)";
  if(semIdentificador) msg+=" — ⚠ "+semIdentificador+" sem tombamento/série, revisar manualmente";
  showToast(msg);
  var main=document.getElementById("main-content")||document.getElementById("main");
  if(main) renderInventario(main);

  // Envia pra planilha em sequência (evita rajada de chamadas simultâneas)
  if(_itensParaEnviar.length){
    showToast("Enviando "+_itensParaEnviar.length+" item(s) à planilha...");
    var _ie=0;
    (function _enviarProximo(){
      if(_ie>=_itensParaEnviar.length){ showToast("✓ Importação sincronizada com a planilha"); return; }
      _invEnviarSheets("inv_item", _itensParaEnviar[_ie]);
      _ie++;
      setTimeout(_enviarProximo, 250);
    })();
  }
}
```

### 1b. Índice de dedup também por número de série

Localizar (linha 24403-24407):
```javascript
  // Índice por tombamento para substituição
  var idxTomb={};
  if(substituir){
    state.invItens.forEach(function(x,i){ if(x.tombamento) idxTomb[String(x.tombamento).trim()]=i; });
  }
```

Substituir por:
```javascript
  // Índice por tombamento (forte) e por número de série (fallback quando não há tombamento)
  var idxTomb={}, idxSerie={};
  if(substituir){
    state.invItens.forEach(function(x,i){
      if(x.tombamento) idxTomb[String(x.tombamento).trim().toUpperCase()]=i;
      if(x.numero_serie) idxSerie[String(x.numero_serie).trim().toUpperCase()]=i;
    });
  }
```

Importante: itens sem tombamento E sem número de série continuam sendo sempre criados como novos (não dá pra deduplicar com segurança só pela descrição — duas cadeiras iguais em salas diferentes são itens legítimos, não duplicata). O contador `semIdentificador` no toast final serve justamente pra avisar quantos caíram nessa situação, pra revisão manual.

## 2. "🗑 Limpar Tudo" não apaga da planilha

Mesmo bug do Excluir Item/Conferência que já corrigi (`FIX_EXCLUIR_INVENTARIO.md`) — se ainda não aplicou aquele arquivo, aplique junto com este, os dois usam o mesmo `state._invDeletedItemIds`.

Substituir `_invLimparTodos` (linha 22179-22187):
```javascript
function _invLimparTodos(){
  var itensAtuais=(state.invItens||[]).slice();
  var n=itensAtuais.filter(function(x){return x.ativo!==false;}).length;
  if(!confirm("Excluir TODOS os "+n+" itens do inventário?\n\nUse esta opção para limpar uma importação errada e reimportar corretamente.")) return;
  if(!state._invDeletedItemIds) state._invDeletedItemIds=new Set();
  itensAtuais.forEach(function(x){ state._invDeletedItemIds.add(x.id); });
  state.invItens=[];
  _invSalvarLocal();
  var main=document.getElementById("main-content")||document.getElementById("main");
  if(main) renderInventario(main);
  showToast("Inventário limpo — apagando da planilha...");
  var _li=0;
  (function _apagarProximo(){
    if(_li>=itensAtuais.length){ showToast("✓ "+itensAtuais.length+" item(s) removido(s) da planilha — pode reimportar"); return; }
    _sheetsGet({acao:"deletar",tipo:"inv_item",id:itensAtuais[_li].id});
    _li++;
    setTimeout(_apagarProximo, 250);
  })();
}
```

## 3. Clique duplo no "💾 Salvar" cria item repetido

Localizar (linha 22125):
```javascript
  html += "<button onclick='_invSalvarItem(\""+esc(id||"")+"\")'  style='background:linear-gradient(135deg,#2a1c10,#3a2818);border:1px solid #C8A84B;color:#f5ede0;padding:9px 22px;border-radius:7px;font-size:13px;font-weight:700;cursor:pointer'>💾 Salvar</button>";
```

Substituir por (desabilita o botão assim que clicado, evitando segundo disparo):
```javascript
  html += "<button id='btn-inv-salvar' onclick=\"this.disabled=true;this.style.opacity='0.6';_invSalvarItem('"+esc(id||"")+"')\"  style='background:linear-gradient(135deg,#2a1c10,#3a2818);border:1px solid #C8A84B;color:#f5ede0;padding:9px 22px;border-radius:7px;font-size:13px;font-weight:700;cursor:pointer'>💾 Salvar</button>";
```

Não precisa reabilitar o botão depois — `_invSalvarItem` já remove o modal inteiro (`document.getElementById('modal-inv-item').remove()`) ao terminar, então o botão desaparece junto.

## Teste

- Importar uma planilha pequena de teste, conferir no toast final se aparece "Importação sincronizada com a planilha"; abrir em outro aparelho/aba anônima e confirmar que os itens aparecem lá também depois do sync.
- Reimportar a mesma planilha de teste em cima — itens com tombamento/série não devem duplicar, só atualizar.
- Limpar Tudo num inventário de teste, aguardar a mensagem de confirmação, dar F5 — itens não devem voltar.
- Abrir "Novo Item", preencher, clicar duas vezes rápido em Salvar — deve criar só um item.
