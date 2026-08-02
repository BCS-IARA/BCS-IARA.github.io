# Correção definitiva: registro não aparece nas filas Devolutivas / Em Acompanhamento

## Diagnóstico (causa raiz)

Sintoma relatado: o atendente faz o registro numa ocorrência, mas ao abrir a
**fila de Devolutivas** ou **Em Acompanhamento** o item não aparece — só no
**Histórico** (que lista todas as ocorrências, sem filtro de situação).

Duas causas raiz, mais um problema de persistência:

**1. Devolutivas — o status `"pendente"` é invisível.**
Todo encaminhamento criado na triagem (`_salvarTriagem`) e no módulo VCM
(`_vcmEncaminhar`) nasce com `status:"pendente"` e `data_envio` vazio.
As três sub-abas de `renderDevolutivas` filtram apenas
`enviado` / `aguardando_devolutiva` / com `relato_devolutiva` — **"pendente"
não cai em nenhuma**. O item só aparece depois que alguém avança o status
manualmente na aba Encaminhamentos.

**2. Em Acompanhamento — marcar a situação não cria o caso.**
A fila lê exclusivamente `state.db.acompanhamentos`, mas o caso só é criado
por UM caminho: o trilho "Acompanhamento Interno" da triagem. Se o atendente
marca `em_acompanhamento` pelo editor da ocorrência (seção 7, `ed-situacao`)
ou pelo botão rápido `_triarOc`, a situação muda **sem criar caso** → fila
vazia. O fallback de "legados" ainda corta ocorrências com mais de 2 meses
(`o.data >= corteStr`), fazendo casos antigos sumirem por completo.

**3. Persistência silenciosamente quebrada (contrato frontend ↔ Apps Script).**
- O frontend chama `_sheetsGet({acao:"salvarEncaminhamento", dados:...})`,
  mas o Apps Script só roteia `acao=salvar&tipo=encaminhamento`. A chamada é
  um **no-op** (3 ocorrências).
- O frontend chama `acao:"atualizarEncaminhamento"` com campos soltos na
  query (`status`, `relato_devolutiva`...), mas o Apps Script lê apenas
  `e.parameter.campos` (JSON) → atualização **vazia** no servidor
  (4 ocorrências).
Tudo hoje só persiste via blob `bcs_encaminhamentos` no próximo
`sincronizarSheets()` — frágil entre dispositivos.

## Escopo (apenas isto)

**Em `index.html`:**
1. Incluir `"pendente"` (e status vazio) nos filtros da fila Devolutivas e do `_syncDevolutivas`, com selo visual "Link não enviado".
2. Preencher `data_envio` e `criadoEm` na criação dos encaminhamentos (3 pontos).
3. Criar `garantirCasoAcompanhamento(oc)` e chamá-la em todo ponto que setar `situacao="em_acompanhamento"` (3 pontos).
4. Remover o corte de 2 meses dos "legados" (2 pontos).
5. Corrigir o contrato das 7 chamadas `_sheetsGet` de encaminhamento e adicionar envio ao Sheets no `_vcmEncaminhar`.
6. Incrementar `CACHE_NAME` no `sw.js`.

**Em `_appscript/app_script_completo_v4.txt` (e no deploy do Apps Script):**
7. Aceitar `acao=salvarEncaminhamento` como alias e aceitar campos soltos em `atualizarEncaminhamento` (retrocompatibilidade com clientes em cache).

**Não alterar mais nada.** Não normalizar os campos `ocorrencia_id`/`ocorrenciaId`,
`tipo`/`orgao`, `vitima_nome`/`vitimaNome` (fase futura). Não mexer na máquina de
estados dos encaminhamentos, nem em `renderTriagem`, `renderHistoricoAtendimento`,
badges das telas de gestor, nem no merge de blobs do sync. Sem refactors extras.

---

## Passo 1 — Devolutivas: tornar `"pendente"` visível

### 1a. Em `renderDevolutivas` (≈ linha 24217)

Localizar os filtros:

```js
  var _aguard = encs.filter(function(e){
    return (e.status==="aguardando_devolutiva"||e.status==="enviado")&&!e.relato_devolutiva;
  });
```

Substituir por:

```js
  function _stAguard(e){ return e.status==="aguardando_devolutiva"||e.status==="enviado"||e.status==="pendente"||!e.status; }
  var _aguard = encs.filter(function(e){
    return _stAguard(e)&&!e.relato_devolutiva;
  });
```

E no filtro `_venc` (logo abaixo), trocar a mesma condição de status por
`_stAguard(e)`:

```js
  var _venc   = encs.filter(function(e){
    var dtEnv=e.data_envio?new Date(e.data_envio):null;
    return _stAguard(e)&&!e.relato_devolutiva&&dtEnv&&dtEnv<hoje15;
  });
```

### 1b. Selo "Link não enviado" no card Aguardando

Na aba `aguardando`, localizar a linha que insere o selo de atraso:

```js
        if(tarde) h.push("<span style='background:#f59e0b22;color:#f59e0b;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700'>⚠ Atrasado</span>");
```

Adicionar logo após:

```js
        if(e.status==="pendente"||!e.status) h.push("<span style='background:#4a322455;color:#d4a87a;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700'>📋 Link não enviado</span>");
```

### 1c. Em `_syncDevolutivas` (≈ linha 14229)

Localizar:

```js
  var pendentes = (state.encaminhamentos||[]).filter(function(e){
    return (e.status==="enviado"||e.status==="aguardando_devolutiva") && !e.relato_devolutiva;
  });
```

Substituir a condição de status por:

```js
    return (e.status==="enviado"||e.status==="aguardando_devolutiva"||e.status==="pendente"||!e.status) && !e.relato_devolutiva;
```

## Passo 2 — `data_envio` e `criadoEm` na criação

### 2a. `_salvarTriagem` — objeto `encMenor` (≈ linha 14757)

No objeto `encMenor`, após `data: hoje(),` adicionar:

```js
      data_envio: hoje(),
      criadoEm: new Date().toISOString(),
```

### 2b. `_salvarTriagem` — loop `.tri-orgao:checked` (≈ linha 14776)

No objeto `enc`, após `data: hoje(),` adicionar as mesmas duas linhas.

### 2c. `_vcmEncaminhar` (≈ linha 21283)

Localizar `data_envio:""` e trocar por:

```js
    data_envio:new Date().toISOString().slice(0,10),
```

(`criadoEm` já existe nesse objeto — não duplicar.)

## Passo 3 — `garantirCasoAcompanhamento`

### 3a. Criar a função

Localizar `window._criarCasoAcompanhamento = function(oc, tipo, semaforo, dataRevisao, periodicidade){`
(≈ linha 13887) e adicionar **logo após o fechamento dessa função**:

```js
// Garante que toda ocorrência em_acompanhamento tenha um caso na fila.
// Idempotente: não duplica se já existe caso para a ocorrência.
window.garantirCasoAcompanhamento = function(oc){
  if(!oc||!oc.id) return;
  if(!state.db.acompanhamentos) state.db.acompanhamentos=[];
  var ja = state.db.acompanhamentos.some(function(c){return c.origemOcorrenciaId===oc.id;});
  if(ja) return;
  var d=new Date(); d.setDate(d.getDate()+30);
  _criarCasoAcompanhamento(oc, "individuo_obs", "verde", d.toISOString().slice(0,10), "mensal");
  salvarLocal();
  salvarDadoAppSheets("bcs_acompanhamentos", state.db.acompanhamentos).catch(function(){});
};
```

### 3b. Chamar em `_triarOc` (≈ linha 14882)

Após `state.db.ocorrencias[idx].situacao = situacao;` adicionar:

```js
  if(situacao==="em_acompanhamento") garantirCasoAcompanhamento(state.db.ocorrencias[idx]);
```

### 3c. Chamar em `_salvarTriagem` (≈ linha 14869)

Após `oc.situacao = situacao;` adicionar:

```js
  if(situacao==="em_acompanhamento") garantirCasoAcompanhamento(oc);
```

(Se o trilho de acompanhamento já criou o caso, a função não duplica.)

### 3d. Chamar no editor da ocorrência

Buscar onde o valor de `ed-situacao` é lido e aplicado à ocorrência
(handler do botão `btn-salvar-editar`; buscar por `ed-situacao` — o readback
fica no bloco de salvamento do modal de edição). Após a linha que atribui a
situação à ocorrência, adicionar:

```js
      if(<variável da ocorrência>.situacao==="em_acompanhamento") garantirCasoAcompanhamento(<variável da ocorrência>);
```

(usar o nome real da variável no escopo — provavelmente `ocM` ou similar).

## Passo 4 — Legados sem corte de 2 meses

### 4a. Em `renderAcompanhamento` (≈ linha 13686–13691)

Localizar:

```js
  var corte=new Date(); corte.setMonth(corte.getMonth()-2);
  var corteStr=corte.toISOString().slice(0,10);
  var jaTemAcomp=new Set((state.db.acompanhamentos||[]).map(function(c){return c.origemOcorrenciaId;}));
  var legados=(state.db.ocorrencias||[]).filter(function(o){
    return o.situacao==="em_acompanhamento"&&!jaTemAcomp.has(o.id)&&(o.data||"")>=corteStr;
  });
```

Remover as duas linhas de `corte` e o trecho `&&(o.data||"")>=corteStr`.

### 4b. Em `_renderMigracaoLegados` (≈ linha 13908–13913)

Mesmo padrão se repete — remover o corte da mesma forma.

## Passo 5 — Contrato `_sheetsGet` (7 chamadas + 1 nova)

### 5a. `acao:"salvarEncaminhamento"` → `acao:"salvar", tipo:"encaminhamento"`

Três ocorrências (≈ linhas 12802, 14768, 14788). Padrão:

```js
// ANTES
_sheetsGet({acao:"salvarEncaminhamento", dados:JSON.stringify(enc)}).catch(function(){});
// DEPOIS
_sheetsGet({acao:"salvar", tipo:"encaminhamento", dados:JSON.stringify(enc)}).catch(function(){});
```

### 5b. `atualizarEncaminhamento` — embrulhar campos em `campos` (JSON)

Quatro ocorrências:

```js
// ≈ 13245  ANTES: {acao:"atualizarEncaminhamento", id:encId, status:"concluido"}
_sheetsGet({acao:"atualizarEncaminhamento", id:encId, campos:JSON.stringify({status:"concluido"})}).catch(function(){});

// ≈ 14139  ANTES: {acao:"atualizarEncaminhamento", id:encId, status:novoStatus}
_sheetsGet({acao:"atualizarEncaminhamento", id:encId, campos:JSON.stringify({status:novoStatus})}).catch(function(){});

// ≈ 14179  ANTES: {acao:"atualizarEncaminhamento", id:encId, vitima_id:vitimaId}
_sheetsGet({acao:"atualizarEncaminhamento", id:encId, campos:JSON.stringify({vitima_id:vitimaId})}).catch(function(){});

// ≈ 24391  ANTES: {acao:"atualizarEncaminhamento", id:encId, relato_devolutiva:texto, status:"aguardando_devolutiva"}
_sheetsGet({acao:"atualizarEncaminhamento", id:encId, campos:JSON.stringify({relato_devolutiva:texto, status:"aguardando_devolutiva", data_devolutiva:new Date().toISOString().slice(0,10)})}).catch(function(){});
```

### 5c. `_vcmEncaminhar` — enviar ao Sheets na criação

Em `_vcmEncaminhar` (≈ linha 21291), após
`state.encaminhamentos.push(enc);` adicionar:

```js
  _sheetsGet({acao:"salvar", tipo:"encaminhamento", dados:JSON.stringify(enc)}).catch(function(){});
```

## Passo 6 — `sw.js`

Incrementar a versão em `CACHE_NAME` (padrão do projeto após qualquer deploy).

## Passo 7 — Apps Script (deploy + arquivo de referência)

Aplicar no script implantado **e** em `_appscript/app_script_completo_v4.txt`.

### 7a. Alias `salvarEncaminhamento`

Junto às rotas de encaminhamento (bloco `// ── ENCAMINHAMENTOS ──`, ≈ linha 922),
adicionar:

```js
    if(acao==="salvarEncaminhamento"){var dENC2={};try{dENC2=JSON.parse(e.parameter.dados||"{}");}catch(ex){}return saida(salvarEncaminhamento(ss,dENC2),cb);}
```

### 7b. `atualizarEncaminhamento` — aceitar campos soltos

Substituir a rota atual (≈ linha 925) por:

```js
    if(acao==="atualizarEncaminhamento"){
      var camposEnc={};try{camposEnc=JSON.parse(e.parameter.campos||"{}");}catch(ex){}
      if(!Object.keys(camposEnc).length){
        ["status","relato_devolutiva","data_devolutiva","responsavel_devolutiva","vitima_id","data_envio"].forEach(function(k){
          if(e.parameter[k]!==undefined&&e.parameter[k]!=="") camposEnc[k]=e.parameter[k];
        });
      }
      return saida(atualizarEncaminhamento(ss,e.parameter.id||"",camposEnc),cb);
    }
```

Isso mantém clientes antigos (PWA em cache) funcionando enquanto o novo
`index.html` propaga.

---

## Teste de aceitação

1. **Devolutivas:** criar ocorrência → concluir triagem com trilho
   "Encaminhar a Órgão Externo" (CRAV) → abrir Central de Filas › Devolutivas
   → o item aparece em **Aguardando** com selo "📋 Link não enviado".
2. **Acompanhamento (editor):** abrir uma ocorrência no editor, seção 7 →
   situação "Em acompanhamento" → salvar → Central de Filas › Em Acompanhamento
   mostra o caso (semáforo verde, revisão em +30 dias).
3. **Acompanhamento (botão rápido):** repetir via `_triarOc` (botão da triagem)
   → mesmo resultado, sem duplicar caso se já existir.
4. **Legados:** ocorrência com `data` de 3+ meses atrás e
   `situacao=em_acompanhamento` sem caso → aparece no aviso de legados.
5. **Persistência:** registrar devolutiva manual → aba Recebidas + conferir na
   planilha (aba `encaminhamentos`) que `relato_devolutiva` e `status` foram
   gravados. Avançar status na aba Encaminhamentos → coluna `status` muda na
   planilha.
6. **Regressão:** Histórico, Triagem e badges continuam renderizando sem erro
   de console.
