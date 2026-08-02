# Fix — Lista de policiais lenta + foto do item na Conferência

**Baseado no `index.html` atual enviado (25.067 linhas) — versão diferente da que está no Project Knowledge.
Recomendo atualizar o arquivo do projeto com essa versão depois desse fix, pra eu não diagnosticar em cima de código velho.**

Substitui o `FIX_FOTO_CONFERENCIA.md` anterior (a Conferência foi reestruturada — agora tem seleção de tipo de bem, conferente, painel expansível por item — o patch antigo não bate mais com o código atual).

## 1. Lista de policiais demora a aparecer no "Quem está conferindo?"

**Causa:** `_invAbrirConferencia2` (linha 22610) lê `state.policiais`, que só fica pronto depois que `carregarDadosAppDoSheets` (linha 766) terminar — uma função com 13 chamadas sequenciais ao Sheets antes de chegar em `bcs_policiais` (linha 792). O dropdown fica refém dessa fila inteira mesmo sendo um dado pequeno.

**Correção:** ao abrir o modal, buscar os policiais direto (1 chamada rápida, `acao=listar&tipo=policiais`, que já existe no Apps Script — não passa pelo mecanismo de chunks lento), sem esperar o boot. Mostra a lista que já tiver na hora, e atualiza sozinho quando a busca rápida voltar.

Substituir `_invAbrirConferencia2` (linha 22610-22639) por:

```javascript
function _invAbrirConferencia2(conf){
  // Sempre pede quem está conferindo (não persiste — sempre pergunta ao abrir)
  function _polAtivos(){
    return (state.policiais||[]).filter(function(p){return (p.status||"ativo")==="ativo";})
      .sort(function(a,b){return (a.nome||"").localeCompare(b.nome||"");});
  }
  var polOpts=_polAtivos();
  var IS="width:100%;background:#EAD9B8;border:1px solid #A87B22;color:#3D2B1A;padding:9px;border-radius:6px;font-size:13px;box-sizing:border-box;min-height:42px";
  var mc=document.createElement("div");
  mc.id="modal-inv-conferente";
  mc.style.cssText="position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:9450;display:flex;align-items:center;justify-content:center;padding:20px";
  mc.innerHTML="<div style='background:#F2E4C8;border:1px solid #5e4636;border-radius:14px;padding:28px 32px;max-width:400px;width:100%'>" +
    "<h3 style='color:#3D2B1A;font-size:16px;font-weight:700;margin:0 0 6px;text-align:center'>👤 Quem está conferindo?</h3>" +
    "<p style='color:#6B5236;font-size:12px;margin:0 0 14px;text-align:center'>Selecione seu nome para registrar quem verificou cada item.</p>" +
    "<select id='sel-conferente' style='"+IS+"'>" +
    "<option value=''>— selecione —</option>" +
    polOpts.map(function(p){return "<option value='"+esc(p.matricula)+"'>"+esc((p.posto?p.posto+" ":"")+p.nome+" ("+p.matricula+")")+"</option>";}).join("") +
    "</select>" +
    "<p id='conf-pol-status' style='color:#a07c58;font-size:10px;margin:6px 0 0;text-align:center'>Atualizando lista…</p>" +
    "<div style='margin-top:14px;display:flex;gap:10px;justify-content:center'>" +
    "<button onclick='document.getElementById(\"modal-inv-conferente\").remove()' style='background:transparent;border:1px solid #DBC79E;color:#6B5236;padding:9px 20px;border-radius:7px;font-size:13px;cursor:pointer'>Cancelar</button>" +
    "<button onclick='_invConfirmarConferente()' style='background:#1a3a1a;border:2px solid #3a7a4a;color:#a0d0a0;padding:9px 22px;border-radius:7px;font-size:13px;font-weight:700;cursor:pointer;min-height:42px'>Confirmar</button>" +
    "</div></div>";
  document.body.appendChild(mc);

  // Busca a lista de policiais direto do Sheets — 1 chamada, sem esperar a fila do boot
  _sheetsGet({acao:"listar",tipo:"policiais"}).then(function(r){
    var statusEl=document.getElementById("conf-pol-status");
    if(r&&r.ok&&Array.isArray(r.dados)&&r.dados.length){
      state.policiais=_mergeByIdTimestamp(state.policiais||[], r.dados);
      _invSalvarLocal();
      var selEl=document.getElementById("sel-conferente");
      if(selEl){
        var valorAtual=selEl.value;
        polOpts=_polAtivos();
        selEl.innerHTML="<option value=''>— selecione —</option>"+polOpts.map(function(p){return "<option value='"+esc(p.matricula)+"'"+(p.matricula===valorAtual?" selected":"")+">"+esc((p.posto?p.posto+" ":"")+p.nome+" ("+p.matricula+")")+"</option>";}).join("");
      }
    }
    if(statusEl) statusEl.remove();
  });

  var _confRef=conf;
  window._invConfirmarConferente=function(){
    var mat=document.getElementById("sel-conferente").value;
    var pol=polOpts.find(function(p){return p.matricula===mat;});
    if(!pol){showToast("Selecione o conferente","error");return;}
    window._invConferenteAtual={nome:pol.nome,matricula:pol.matricula,posto:pol.posto||""};
    mc.remove();
    _invRenderConferencia(_confRef);
  };
}
```

Mudanças em relação ao original: a lista de policiais foi extraída pra função `_polAtivos()` (pra poder recalcular depois); foi adicionado o `<p id='conf-pol-status'>` como indicador de carregamento; e depois de montar o modal, dispara `_sheetsGet({acao:"listar",tipo:"policiais"})` que mescla qualquer policial novo/atualizado via `_mergeByIdTimestamp` (já existe no código, linha 644) e repõe as `<option>` do select preservando a seleção atual, se houver.

**Opcional, baixo risco, recomendo incluir:** trocar o merge de policiais no boot (linha 876) de `_mergeById` pra `_mergeByIdTimestamp`, só por consistência com o resto do app — não resolve a demora sozinho (esse é o ponto 1 acima), mas evita o mesmo problema de edição que já corrigimos pra itens/conferências.

```javascript
// linha 876, trocar:
state.policiais        = _mergeById(state.policiais||[],         policiaisSheets);
// por:
state.policiais        = _mergeByIdTimestamp(state.policiais||[], policiaisSheets);
```

## 2. Foto do item na Conferência

**Correção:** no painel expansível de cada item (dentro de `_invRenderConferencia`, bloco "// foto", linha ~22719-22723), mostrar a foto já cadastrada no item (`item.foto_url`/`item.foto`) como referência, e renomear o link existente pra deixar claro que é uma foto separada (tirada durante a conferência, não a foto de cadastro).

Localizar este trecho:
```javascript
      html+="<div><label style='color:#6B5236;font-size:10px'>Observações</label><input id='inv-ci-obs-"+iid+"' value='"+esc(det.observacoes||"")+"' placeholder='Observações, desgastes, irregularidades…' oninput='_invConfDetalhe(\""+iid+"\",\"observacoes\",this.value)' style='"+ISci+"'></div>";
      // foto
      html+="<div style='display:flex;align-items:center;gap:8px'>";
      if(det.foto_link){html+="<a href='"+esc(det.foto_link)+"' target='_blank' style='color:#D9A53C;font-size:11px'>📷 Ver foto</a>";}
      html+="<label style='cursor:pointer;padding:3px 10px;background:transparent;border:1px solid #5e4636;border-radius:5px;color:#a07c58;font-size:11px'>📷 Anexar foto<input type='file' accept='image/*' capture='environment' style='display:none' onchange='_invConfFoto(\""+iid+"\",this)'></label>";
      html+="</div>";
```

Substituir por:
```javascript
      html+="<div><label style='color:#6B5236;font-size:10px'>Observações</label><input id='inv-ci-obs-"+iid+"' value='"+esc(det.observacoes||"")+"' placeholder='Observações, desgastes, irregularidades…' oninput='_invConfDetalhe(\""+iid+"\",\"observacoes\",this.value)' style='"+ISci+"'></div>";
      // foto
      var _fotoItemSrc=item.foto_url||(item.foto&&item.foto!=="[foto_drive]"&&item.foto!=="[foto_local]"?item.foto:null);
      html+="<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap'>";
      if(_fotoItemSrc){
        html+="<img src='"+_fotoItemSrc+"' title='Foto cadastrada do item' onclick=\"window.open('"+_fotoItemSrc+"','_blank')\" style='width:54px;height:42px;object-fit:cover;border-radius:6px;border:1px solid #A87B22;cursor:pointer;flex-shrink:0'>";
      } else {
        html+="<span style='color:#a07c58;font-size:10px'>Item sem foto cadastrada</span>";
      }
      if(det.foto_link){html+="<a href='"+esc(det.foto_link)+"' target='_blank' style='color:#D9A53C;font-size:11px'>📷 Ver foto da conferência</a>";}
      html+="<label style='cursor:pointer;padding:3px 10px;background:transparent;border:1px solid #5e4636;border-radius:5px;color:#a07c58;font-size:11px'>📷 Anexar foto de divergência<input type='file' accept='image/*' capture='environment' style='display:none' onchange='_invConfFoto(\""+iid+"\",this)'></label>";
      html+="</div>";
```

Não precisa mudar `_invConfFoto` (linha 22949) nem o trecho que reescreve o link depois do upload (linha 22955-22960) — eles continuam funcionando igual, só que agora coexistem com a miniatura da foto de cadastro em vez de ser a única foto visível.

## Teste

- Abrir "Nova Conferência": dropdown de policiais já aparece populado rapidamente (não esperar 10+ segundos); se a lista mudar depois (chamada rápida traz algo novo), o select atualiza sem perder o que já estava selecionado.
- Expandir um item que tem `foto_url` cadastrada: aparece a miniatura clicável. Item sem foto: aparece "Item sem foto cadastrada". Anexar uma foto de divergência continua funcionando e aparece como link separado, "Ver foto da conferência".
