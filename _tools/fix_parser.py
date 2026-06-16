import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('C:/Users/oseia/Downloads/BCS/index.html', encoding='utf-8').read()

# Find old parser
start = content.index('function _parsearWhatsApp(texto) {')
end   = content.index('\nfunction renderImportarZap(main) {')
old_parser = content[start:end]

new_parser = '''function _parsearWhatsApp(texto) {
  var blocos = texto.split(/\\n(?=\\d{2}\\/\\d{2}\\/\\d{4} \\d{2}:\\d{2} - )/);
  var registros = [];

  function bairroDe(local) {
    var m = local.match(/,\\s*([^,\\-]+?)(?:\\s*-\\s*Zona|\\s*Ponto de|\\s*$)/i);
    if (m) return m[1].trim();
    var partes = local.split(',').map(function(p){ return p.trim(); }).filter(Boolean);
    return partes.length >= 2 ? partes[partes.length - 1] : local.trim();
  }

  function gerarId(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) { h = ((h << 5) - h + s.charCodeAt(i)) | 0; }
    return 'zap_' + Math.abs(h).toString(36);
  }

  function isVD(t) {
    return /maria da penha|viol[e\\xea]ncia dom[e\\xe9]stica|medida protetiva/i.test(t);
  }

  // ── FORMATO ANTIGO: *CAMPO:*  valor ──────────────────────────
  function parsearAntigo(bloco) {
    if (bloco.indexOf('*TIPO:*') < 0 || bloco.indexOf('DESCRI') < 0) return null;
    function campo(nome) {
      var re = new RegExp('\\\\*' + nome + ':\\\\*\\\\s*(.*?)(?=\\\\n\\\\s*\\\\*|$)', 'is');
      var m = bloco.match(re); return m ? m[1].replace(/\\*/g,'').trim() : '';
    }
    var descRaw = (function(){
      var m = bloco.match(/\\*DESCRI[^\\*]*:\\*\\s*([\\s\\S]*?)(?=\\n\\s*\\*FONTE|\\n\\s*\\*Instagram|$)/i);
      return m ? m[1].trim() : '';
    })();
    var tipo = campo('TIPO'); if (!tipo || !descRaw) return null;
    var ts = bloco.match(/^(\\d{2}\\/\\d{2}\\/\\d{4}) (\\d{2}:\\d{2})/);
    var dataOc = campo('DATA') || (ts ? ts[1] : '');
    var horaOc = campo('HORA') || (ts ? ts[2] : '');
    var local  = campo('LOCAL');
    var resp   = campo('RESPONS');
    var rDin = /din[\\xc3\\xa2a]mica dos fatos\\s*:?\\s*/i, rMed = /medidas?\\s+adotadas?\\s*:?\\s*/i;
    var iD = descRaw.search(rDin), iM = descRaw.search(rMed);
    var resumo = descRaw, dinamica = '', medidas = '';
    if (iD > -1 && iM > -1 && iD < iM) {
      resumo = descRaw.slice(0,iD).trim();
      dinamica = descRaw.slice(iD + descRaw.match(rDin)[0].length, iM).trim();
      medidas = descRaw.slice(iM + descRaw.match(rMed)[0].length).trim();
    } else if (iD > -1) {
      resumo = descRaw.slice(0,iD).trim(); dinamica = descRaw.slice(iD + descRaw.match(rDin)[0].length).trim();
    } else if (iM > -1) {
      resumo = descRaw.slice(0,iM).trim(); medidas = descRaw.slice(iM + descRaw.match(rMed)[0].length).trim();
    }
    var vd = isVD(tipo + ' ' + resumo);
    return { id: gerarId(dataOc+horaOc+tipo.slice(0,15)+resumo.slice(0,20)),
      numero:'', data:dataOc, hora:horaOc, tipo:tipo, bairro:bairroDe(local),
      municipio:'Vitória da Conquista', vitima_nome:'', vitima_sexo:'', vitima_idade:'',
      vitima_telefone:'', vitima_cpf:'', vitima_endereco:local,
      suspeito_nome:'', suspeito_apelido:'', suspeito_caracteristicas:'', veiculo:'',
      medida_protetiva:vd?'Sim':'Não', violencia_domestica:vd, requer_visita:vd, reincidente:false,
      descricao:resumo.slice(0,150), descricao_dinamica:dinamica, medidas:medidas,
      texto_original:dinamica, policiais:resp, fonte:'WhatsApp' };
  }

  // ── FORMATO NOVO: Campo:\\tvalor (SIGESPOL colado no grupo) ───
  function parsearNovo(bloco) {
    if (!/^Tipo:\\t/m.test(bloco)) return null;
    function tab(campo) {
      var re = new RegExp('^' + campo + ':\\t([\\\\s\\\\S]*?)(?=\\n\\\\S[^\\n]*:\\t|$)', 'm');
      var m = bloco.match(re); return m ? m[1].trim() : '';
    }
    var tipo = tab('Tipo'); if (!tipo) return null;
    var num  = tab('Cód') || tab('Cod');
    var dataHora = tab('Data');
    var dataOc = '', horaOc = '';
    var dhM = dataHora.match(/(\\d{2}\\/\\d{2}\\/\\d{4})(?:\\s+[\\xe0a]s?\\s*(\\d{2}:\\d{2}))?/);
    if (dhM) { dataOc = dhM[1]; horaOc = dhM[2] || ''; }
    var ts = bloco.match(/^(\\d{2}\\/\\d{2}\\/\\d{4}) (\\d{2}:\\d{2})/);
    if (!dataOc && ts) dataOc = ts[1];
    if (!horaOc && ts) horaOc = ts[2];
    var local    = tab('Local');
    var descricao= tab('Descri\\xE7\\xE3o') || tab('Descricao') || tab('Descrição');
    var dinamica = tab('Din\\xE2mica dos fatos') || tab('Dinamica dos fatos') || tab('Dinâmica dos fatos');
    var medidas  = tab('Medidas adotadas') || tab('Medidas adotadas pela guarnição') || tab('Medidas adotadas pela guarnicao');
    var pessoas  = tab('Pessoas Envolvidas');
    var efetivo  = tab('Efetivo Empregado');
    var vitNome='', vitSexo='', vitIdade='', vitCpf='', vitEnd='', suspNome='';
    if (pessoas) {
      var vNM = pessoas.match(/V[ÍI]TIMA[\\s\\S]*?Nome:\\s*([^,]+)/i);
      if (vNM) vitNome = vNM[1].trim();
      var vSM = pessoas.match(/V[ÍI]TIMA[\\s\\S]*?Sexo:\\s*([^,]+)/i);
      if (vSM) vitSexo = vSM[1].trim() === 'Masculino' ? 'M' : vSM[1].trim() === 'Feminino' ? 'F' : vSM[1].trim();
      var vIM = pessoas.match(/V[ÍI]TIMA[\\s\\S]*?(\\d+)\\s*anos/i);
      if (vIM) vitIdade = vIM[1];
      var vCM = pessoas.match(/V[ÍI]TIMA[\\s\\S]*?(\\d{9}-\\d{2})/i);
      if (vCM) vitCpf = vCM[1];
      var vEM = pessoas.match(/Endere[çc]o:\\s*([^\\n]+)/i);
      if (vEM) vitEnd = vEM[1].trim();
      var aNM = pessoas.match(/AUTOR[\\s\\S]*?Nome:\\s*([^,]+)/i);
      if (aNM) suspNome = aNM[1].trim();
    }
    var vd = isVD(tipo + ' ' + descricao + ' ' + dinamica);
    var id = num ? 'cod_' + num.replace(/\\D/g,'') : gerarId(dataOc+horaOc+tipo.slice(0,15)+descricao.slice(0,20));
    return { id:id, numero:num, data:dataOc, hora:horaOc, tipo:tipo,
      bairro:bairroDe(local), municipio:'Vitória da Conquista',
      vitima_nome:vitNome, vitima_sexo:vitSexo, vitima_idade:vitIdade,
      vitima_telefone:'', vitima_cpf:vitCpf, vitima_endereco:vitEnd||local,
      suspeito_nome:suspNome, suspeito_apelido:'', suspeito_caracteristicas:'', veiculo:'',
      medida_protetiva:vd?'Sim':'Não', violencia_domestica:vd, requer_visita:vd, reincidente:false,
      descricao:(descricao||dinamica).slice(0,150), descricao_dinamica:dinamica, medidas:medidas,
      texto_original:dinamica||descricao, policiais:efetivo, fonte:'WhatsApp' };
  }

  blocos.forEach(function(bloco) {
    var reg = parsearNovo(bloco) || parsearAntigo(bloco);
    if (reg && reg.tipo && (reg.descricao || reg.descricao_dinamica)) {
      registros.push(reg);
    }
  });

  return registros;
}
'''

content = content.replace(old_parser, new_parser)
open('C:/Users/oseia/Downloads/BCS/index.html', 'w', encoding='utf-8').write(content)
print("Salvo!")
idx2 = content.index('function _parsearWhatsApp')
print("Novo parser preview:", content[idx2:idx2+100])
