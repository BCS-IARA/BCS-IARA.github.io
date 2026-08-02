# Correção: contagem "OK" inflada na Conferência de Inventário

## Diagnóstico (causa raiz)

Em `index.html`, os badges de contagem da conferência (✓ OK, ⚠ Divergência,
✗ Ausente, ⏳ Pendente) são calculados direto sobre `Object.values(conf.itens)`,
**sem checar se o `itemId` ainda corresponde a um item ativo do inventário e
do mesmo `tipoBem` (móvel/bélico) daquela conferência**.

Resultado: se um item foi marcado (ok/divergência/ausente) numa conferência e
depois foi **inativado, excluído ou trocou de categoria** (móvel↔bélico), o
registro continua em `conf.itens` e segue contando no badge — mas some da
lista de itens exibida no modal (que **é** filtrada por `ativo` e `tipoBem`).
Isso explica o caso relatado: badge mostrando "4 OK" com apenas 3 itens
visíveis/conferíveis na tela.

O mesmo padrão de cálculo (sem cruzar com itens válidos) se repete em 4
lugares no código. A correção é uma só lógica, reaproveitada nos 4 pontos.

## Escopo (apenas isto)

1. Criar uma função helper `_invItensValidosConf(conf)`.
2. Usar essa helper para recalcular os badges em **4 locais**:
   - Abertura do modal de conferência (barra de progresso inicial)
   - `_invConfAtualizarBarra()` (barra de progresso ao vivo, ao clicar OK/DIV/AUS)
   - Card da lista de conferências (aba "Conferências")
   - `_invGerarPDFConferencia()` (KPIs do PDF gerado)

**Não alterar mais nada.** Não mexer em `_invGerarFIBM`, `_invGerarFIMB`,
`_invGerarPlanilhaPlaquetas`, nem em qualquer outra função do módulo de
inventário. Não fazer refactors adicionais, não mudar estilo/formatação de
código fora dos trechos indicados.

---

## Passo 1 — Criar a função helper

Localizar a função `_invAbrirConferencia` (cabeçalho `function
_invAbrirConferencia(confId){`) e adicionar a nova função **logo antes dela**:

```js
function _invItensValidosConf(conf){
  var _belicoCats=["material_belico"];
  var tipoBem=(conf&&conf.tipoBem)||"movel";
  return (state.invItens||[]).filter(function(x){
    if(x.ativo===false) return false;
    var isBelico=_belicoCats.some(function(c){return x.categoria===c;});
    return tipoBem==="belico"?isBelico:!isBelico;
  });
}
```

## Passo 2 — Reaproveitar na própria `_invRenderConferencia`

Dentro de `function _invRenderConferencia(conf){`, localizar:

```js
  var tipoBem = conf.tipoBem || "movel";
  var _belicoCats = ["material_belico"];
  var itensAtivos=(state.invItens||[]).filter(function(x){
    if(x.ativo===false) return false;
    var isBelico=_belicoCats.some(function(c){return x.categoria===c;});
    return tipoBem==="belico"?isBelico:!isBelico;
  });
```

Substituir por:

```js
  var tipoBem = conf.tipoBem || "movel";
  var itensAtivos=_invItensValidosConf(conf);
```

(Comportamento idêntico — só elimina duplicação, já que a lógica é igual à da
nova helper.)

## Passo 3 — Corrigir a barra de progresso inicial do modal

Ainda em `_invRenderConferencia`, localizar:

```js
  var _totalConf=Object.values(conf.itens||{}).filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ok"||s==="divergencia"||s==="ausente";}).length;
  var _totalItens=itensAtivos.length;
```

Substituir por:

```js
  var _idsAtivosConf={}; itensAtivos.forEach(function(x){_idsAtivosConf[x.id]=true;});
  var _totalConf=Object.entries(conf.itens||{}).filter(function(e){
    if(!_idsAtivosConf[e[0]]) return false;
    var v=e[1]; var s=(v&&typeof v==="object")?v.status:v;
    return s==="ok"||s==="divergencia"||s==="ausente";
  }).length;
  var _totalItens=itensAtivos.length;
```

## Passo 4 — Corrigir `_invConfAtualizarBarra`

Localizar a função inteira:

```js
function _invConfAtualizarBarra(){
  var conf=window._invConfAtual;
  if(!conf) return;
  var tipoBem=conf.tipoBem||"movel";
  var _belicoCats=["material_belico"];
  var total=(state.invItens||[]).filter(function(x){
    if(x.ativo===false) return false;
    var isBelico=_belicoCats.some(function(c){return x.categoria===c;});
    return tipoBem==="belico"?isBelico:!isBelico;
  }).length;
  var done=Object.values(conf.itens||{}).filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ok"||s==="divergencia"||s==="ausente";}).length;
  var pct=total?Math.round(done/total*100):0;
  var bar=document.querySelector("#modal-inv-conf .inv-conf-bar");
  if(bar){bar.style.width=pct+"%";bar.style.background=pct===100?"#3a7a4a":pct>50?"#d4a87a":"#4a9fd4";}
  var barLbl=document.querySelector("#modal-inv-conf .inv-conf-bar-lbl");
  if(barLbl) barLbl.textContent=done+"/"+total+" itens · "+pct+"%";
}
```

Substituir por:

```js
function _invConfAtualizarBarra(){
  var conf=window._invConfAtual;
  if(!conf) return;
  var itensValidos=_invItensValidosConf(conf);
  var total=itensValidos.length;
  var idsValidos={}; itensValidos.forEach(function(x){idsValidos[x.id]=true;});
  var done=Object.entries(conf.itens||{}).filter(function(e){
    if(!idsValidos[e[0]]) return false;
    var v=e[1]; var s=(v&&typeof v==="object")?v.status:v;
    return s==="ok"||s==="divergencia"||s==="ausente";
  }).length;
  var pct=total?Math.round(done/total*100):0;
  var bar=document.querySelector("#modal-inv-conf .inv-conf-bar");
  if(bar){bar.style.width=pct+"%";bar.style.background=pct===100?"#3a7a4a":pct>50?"#d4a87a":"#4a9fd4";}
  var barLbl=document.querySelector("#modal-inv-conf .inv-conf-bar-lbl");
  if(barLbl) barLbl.textContent=done+"/"+total+" itens · "+pct+"%";
}
```

## Passo 5 — Corrigir o card na aba "Conferências" (lista de conferências)

Dentro do bloco `} else if(tab==="conferencias"){ ... confs.forEach(function(conf){`,
localizar:

```js
        var dt=conf.criadoEm?new Date(conf.criadoEm).toLocaleString("pt-BR"):"—";
        var vals=Object.values(conf.itens||{});
        var nOk=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ok";}).length;
        var nDiv=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="divergencia";}).length;
        var nAus=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ausente";}).length;
        var nPend=itens.length-vals.length;
```

Substituir por:

```js
        var dt=conf.criadoEm?new Date(conf.criadoEm).toLocaleString("pt-BR"):"—";
        var itensValidosConf=_invItensValidosConf(conf);
        var idsValidosConf={}; itensValidosConf.forEach(function(x){idsValidosConf[x.id]=true;});
        var vals=Object.entries(conf.itens||{}).filter(function(e){return idsValidosConf[e[0]];}).map(function(e){return e[1];});
        var nOk=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ok";}).length;
        var nDiv=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="divergencia";}).length;
        var nAus=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ausente";}).length;
        var nPend=itensValidosConf.length-vals.length;
```

**Atenção:** essa troca também corrige um bug secundário — antes, `nPend`
usava a variável global `itens` (todos os itens ativos, **somando móvel +
bélico juntos**) para qualquer conferência da lista, então uma conferência de
material bélico exibia "pendente" baseado no total errado (móvel+bélico
misturados). Agora cada card usa só os itens do seu próprio `tipoBem`.

## Passo 6 — Corrigir os KPIs do PDF (`_invGerarPDFConferencia`)

Localizar, dentro de `function _invGerarPDFConferencia(confId){`:

```js
  var itens=(state.invItens||[]).filter(function(x){return x.ativo!==false;});
  var dt=new Date(conf.criadoEm).toLocaleString("pt-BR");
  var dtConc=conf.concluidaEm?new Date(conf.concluidaEm).toLocaleString("pt-BR"):"—";
  var vals=Object.values(conf.itens||{});
  var nOk=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ok";}).length;
  var nDiv=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="divergencia";}).length;
  var nAus=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ausente";}).length;
```

Substituir por:

```js
  var itens=_invItensValidosConf(conf);
  var dt=new Date(conf.criadoEm).toLocaleString("pt-BR");
  var dtConc=conf.concluidaEm?new Date(conf.concluidaEm).toLocaleString("pt-BR"):"—";
  var idsValidosPdf={}; itens.forEach(function(x){idsValidosPdf[x.id]=true;});
  var vals=Object.entries(conf.itens||{}).filter(function(e){return idsValidosPdf[e[0]];}).map(function(e){return e[1];});
  var nOk=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ok";}).length;
  var nDiv=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="divergencia";}).length;
  var nAus=vals.filter(function(v){var s=(v&&typeof v==="object")?v.status:v;return s==="ausente";}).length;
```

**Atenção:** isso também corrige um segundo bug encontrado durante a
investigação — o PDF de conferência hoje lista **todos os itens ativos do
inventário, móveis e bélicos misturados**, na tabela "Itens Conferidos",
independente do `tipoBem` daquela conferência específica (porque `itens`
vinha de `state.invItens` sem filtro de tipo). Com a troca acima, o PDF passa
a listar apenas os itens do tipo de bem correspondente à conferência — que é
o comportamento esperado, já que o modal de conferência também só permite
conferir itens de um tipo por vez.

---

## Teste manual após a correção

1. Abrir uma conferência "Em andamento" existente (a mesma do print, se
   ainda existir) e conferir se o badge da lista passa a bater com o número
   de itens realmente marcados e visíveis no modal.
2. Marcar OK/DIV/AUS em 2-3 itens numa conferência nova e confirmar que a
   barra de progresso do modal e o badge da lista mostram o mesmo número.
3. Gerar o PDF (botão "📄 PDF") de uma conferência com itens conferidos e
   conferir que os KPIs do topo (OK/Divergência/Ausente/Total) batem com os
   badges da lista, e que a tabela só lista itens do tipo de bem correto
   (móvel ou bélico, não os dois misturados).
4. Se possível, achar (via o snippet de console já usado no diagnóstico) um
   caso real com item órfão/inativado e confirmar que ele some da contagem
   após a correção.

## Fora de escopo (não mexer agora)

- `_invGerarFIBM`, `_invGerarFIMB`, `_invGerarPlanilhaPlaquetas`: também
  fazem `Object.entries(conf.itens)` sem checar se o item ainda existe — se
  um item com divergência/ausência for excluído depois, pode gerar uma linha
  em branco na planilha. É o mesmo tipo de causa raiz, mas é uma planilha
  separada (FIBM/FIMB), não o badge reportado. Fica registrado aqui para uma
  rodada futura, se confirmado que está acontecendo.
