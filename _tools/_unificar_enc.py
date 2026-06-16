import re

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

changes = 0

# 1. Migração na inicialização de state.encaminhamentos
OLD = "  encaminhamentos: JSON.parse(localStorage.getItem(\"bcs_encaminhamentos\")||\"[]\"),"
NEW = """  encaminhamentos: (function(){
    var _enc=JSON.parse(localStorage.getItem("bcs_encaminhamentos")||"[]");
    try{
      var _vcm=JSON.parse(localStorage.getItem("bcs_vcm_enc")||"[]");
      if(_vcm.length){
        var _encIds=new Set(_enc.map(function(e){return e.id;}));
        _vcm.forEach(function(v){
          if(_encIds.has(v.id)) return;
          _enc.push({id:v.id,ocorrenciaId:v.ocorrenciaId,
            tipo:v.servico||"crav",orgao:v.servico||"crav",
            vitimaNome:v.vitimaNome||"",vitimaBairro:v.vitimaBairro||"",
            ocNumero:v.ocNumero||"",
            data:v.dataRegistro?v.dataRegistro.slice(0,10):"",
            criadoEm:v.dataRegistro||"",
            data_envio:v.dataEnvio?v.dataEnvio.slice(0,10):"",
            status:v.status==="enviado"?"enviado":"pendente",
            observacoes:v.obs||"",vcm:true});
        });
        localStorage.setItem("bcs_encaminhamentos",JSON.stringify(_enc));
        localStorage.removeItem("bcs_vcm_enc");
      }
    }catch(e){}
    return _enc;
  })(),"""
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: init encaminhamentos")

# 2. _vcmEncaminhar — escreve em state.encaminhamentos
OLD = 'state.vcmEncaminhamentos.push(enc);\n  localStorage.setItem("bcs_vcm_enc",JSON.stringify(state.vcmEncaminhamentos));'
NEW = 'state.encaminhamentos.push(enc);\n  localStorage.setItem("bcs_encaminhamentos",JSON.stringify(state.encaminhamentos));'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: vcmEncaminhamentos.push")

# 3. Campos do objeto enc criado em _vcmEncaminhar
OLD = '  var enc={\n    id:"enc_"+Date.now(), ocorrenciaId:ocId,\n    vitimaNome:oc.vitima_nome||"", vitimaBairro:oc.bairro||"",\n    ocNumero:oc.numero||oc.id||"", servico:servico||"crav",\n    dataRegistro:new Date().toISOString(), status:"pendente",\n    dataEnvio:"", obs:""\n  };'
NEW = '  var enc={\n    id:"enc_"+Date.now(), ocorrenciaId:ocId,\n    vitimaNome:oc.vitima_nome||"", vitimaBairro:oc.bairro||"",\n    ocNumero:oc.numero||oc.id||"", tipo:servico||"crav", orgao:servico||"crav",\n    data:new Date().toISOString().slice(0,10),\n    criadoEm:new Date().toISOString(), status:"pendente",\n    data_envio:"", observacoes:"", vcm:true\n  };'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: enc object literal")

# 4. Verificação de duplicata em _vcmEncaminhar
OLD = '  var jaPendente=state.vcmEncaminhamentos.some(function(e){\n    return e.ocorrenciaId===ocId && e.servico===servico && e.status==="pendente";\n  });'
NEW = '  var jaPendente=state.encaminhamentos.some(function(e){\n    return e.ocorrenciaId===ocId && (e.orgao===servico||e.tipo===servico) && e.vcm && e.status==="pendente";\n  });'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: jaPendente check")

# 5. if(!state.vcmEncaminhamentos) state.vcmEncaminhamentos=[];
OLD = '  if(!state.vcmEncaminhamentos) state.vcmEncaminhamentos=[];'
NEW = '  if(!state.encaminhamentos) state.encaminhamentos=[];'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: init guard vcmEncaminhamentos")

# 6. _vcmMarcarEnviado
OLD = ('function _vcmMarcarEnviado(encId){\n'
       '  if(!state.vcmEncaminhamentos) return;\n'
       '  var idx=state.vcmEncaminhamentos.findIndex(function(e){return e.id===encId;});\n'
       '  if(idx<0) return;\n'
       '  state.vcmEncaminhamentos[idx].status="enviado";\n'
       '  state.vcmEncaminhamentos[idx].dataEnvio=new Date().toISOString();\n'
       '  localStorage.setItem("bcs_vcm_enc",JSON.stringify(state.vcmEncaminhamentos));')
NEW = ('function _vcmMarcarEnviado(encId){\n'
       '  if(!state.encaminhamentos) return;\n'
       '  var idx=state.encaminhamentos.findIndex(function(e){return e.id===encId;});\n'
       '  if(idx<0) return;\n'
       '  state.encaminhamentos[idx].status="enviado";\n'
       '  state.encaminhamentos[idx].data_envio=new Date().toISOString().slice(0,10);\n'
       '  localStorage.setItem("bcs_encaminhamentos",JSON.stringify(state.encaminhamentos));')
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: _vcmMarcarEnviado")

# 7. _renderVcmEncaminhamentos: remover releitura de bcs_vcm_enc
OLD = ('function _renderVcmEncaminhamentos(main){\n'
       '  // Relê localStorage para capturar encaminhamentos adicionados pelo monitor VCM\n'
       '  try{\n'
       '    var _locEnc=JSON.parse(localStorage.getItem("bcs_vcm_enc")||"[]");\n'
       '    if(_locEnc.length>0){\n'
       '      // Sempre usa localStorage como fonte de verdade para encaminhamentos\n'
       '      state.vcmEncaminhamentos=_locEnc;\n'
       '    }\n'
       '  }catch(e){}\n'
       '  var encs=(state.vcmEncaminhamentos||[]).slice().sort(function(a,b){')
NEW = ('function _renderVcmEncaminhamentos(main){\n'
       '  var encs=(state.encaminhamentos||[]).filter(function(e){return e.vcm;}).slice().sort(function(a,b){')
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: _renderVcmEncaminhamentos header")

# 8. Campos usados dentro da renderização
OLD = 'var dt=enc.dataRegistro?new Date(enc.dataRegistro).toLocaleDateString("pt-BR"):"—";'
NEW = 'var dt=(enc.criadoEm||enc.data)?new Date(enc.criadoEm||enc.data+"T12:00").toLocaleDateString("pt-BR"):"—";'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: dataRegistro render")

OLD = 'var orgLabel=_orgaoLabels[enc.servico]||enc.servico;'
NEW = 'var orgLabel=_orgaoLabels[enc.orgao||enc.tipo||enc.servico]||(enc.orgao||enc.tipo||enc.servico||"—");'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: orgLabel")

OLD = '(b.dataRegistro||"")>(a.dataRegistro||"")?1:-1;'
NEW = '(b.criadoEm||b.data||"")>(a.criadoEm||a.data||"")?1:-1;'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: sort dataRegistro")

# 9. Badge VCM (dois lugares)
OLD = 'var nEnc=(state.vcmEncaminhamentos||[]).filter(function(e){return e.status==="pendente";}).length;'
NEW = 'var nEnc=(state.encaminhamentos||[]).filter(function(e){return e.vcm&&e.status==="pendente";}).length;'
count = src.count(OLD)
if count:
    src = src.replace(OLD, NEW); changes += count
else:
    print("NAO ACHOU: nEnc badge")

OLD = 'var _nEncPend=(state.vcmEncaminhamentos||[]).filter(function(e){return e.status==="pendente";}).length;'
NEW = 'var _nEncPend=(state.encaminhamentos||[]).filter(function(e){return e.vcm&&e.status==="pendente";}).length;'
if OLD in src:
    src = src.replace(OLD, NEW, 1); changes += 1
else:
    print("NAO ACHOU: _nEncPend")

# 10. Remover de salvarLocal (dois lugares)
for old in [
    '    if(state.vcmEncaminhamentos) localStorage.setItem("bcs_vcm_enc",JSON.stringify(state.vcmEncaminhamentos));\n',
    '    if(state.vcmEncaminhamentos)  localStorage.setItem("bcs_vcm_enc",             JSON.stringify(state.vcmEncaminhamentos));\n',
]:
    if old in src:
        src = src.replace(old, '', 1); changes += 1
    else:
        print("NAO ACHOU salvarLocal:", repr(old[:60]))

# 11. Remover de exportar/importar
OLD = '    vcmEncaminhamentos: state.vcmEncaminhamentos||[],\n'
if OLD in src:
    src = src.replace(OLD, '', 1); changes += 1
else:
    print("NAO ACHOU: exportar vcmEncaminhamentos")

OLD = '      if(dados.vcmEncaminhamentos) state.vcmEncaminhamentos=dados.vcmEncaminhamentos;\n'
if OLD in src:
    src = src.replace(OLD, '', 1); changes += 1
else:
    print("NAO ACHOU: importar vcmEncaminhamentos")

# 12. Remover do sync Sheets
OLD = '    await salvarDadoAppSheets("bcs_vcm_enc",           state.vcmEncaminhamentos||[]);\n'
if OLD in src:
    src = src.replace(OLD, '', 1); changes += 1
else:
    print("NAO ACHOU: sync vcm_enc")

# 13. Merge no callback de sync
OLD = ('    // 📤 Encaminhamentos VCM (merge por id)\n'
       '    state.vcmEncaminhamentos = _mergeById(state.vcmEncaminhamentos||[], vcmEncsSheets);\n'
       '    localStorage.setItem("bcs_vcm_enc", JSON.stringify(state.vcmEncaminhamentos));\n')
if OLD in src:
    src = src.replace(OLD, '', 1); changes += 1
else:
    print("NAO ACHOU: merge vcmEncsSheets")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print(f"Concluido — {changes} substituicoes aplicadas")
