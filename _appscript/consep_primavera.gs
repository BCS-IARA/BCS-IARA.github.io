// ══════════════════════════════════════════════════════════════════
//  CONSEP Primavera — Web App separado (registro de chapa + cadastro
//  de membro da Assembleia). Não mexe no Apps Script do IARA nem no
//  de ingestão SIGESPOL.
//
//  Recebe os POSTs de registro-chapa.html e cadastro-assembleia.html:
//    {token, tipo:"registro_chapa_consep_primavera",      registro:{...}}
//    {token, tipo:"cadastro_assembleia_consep_primavera", registro:{...}}
//  Grava cada um numa aba própria e salva as imagens (assinatura,
//  documento, comprovante) como arquivos no Drive, com o link na célula.
//
//  COMO INSTALAR:
//  1. script.google.com → Novo projeto → nome: "CONSEP Primavera"
//  2. Cole este arquivo inteiro, salve (Ctrl+S)
//  3. Executar a função "testeSetup" uma vez (autorize quando pedir)
//     → cria a planilha "CONSEP Primavera — Cadastros" e a pasta de
//       anexos no seu Drive; o log mostra os links
//  4. Implantar → Nova implantação → tipo "App da Web"
//       Executar como: Eu
//       Quem tem acesso: Qualquer pessoa
//  5. Copie a URL /exec gerada e cole no SHEETS_URL das duas páginas.
// ══════════════════════════════════════════════════════════════════

var TOKEN  = "consep-primavera-2026"; // igual ao TOKEN das páginas
var VERSAO = "consep-primavera-1.0";

var TIPOS = {
  registro_chapa_consep_primavera: {
    aba: "Registro de Chapa",
    campos: ["protocolo", "data_registro", "status", "cargo", "nome", "cpf", "rg",
             "telefone", "vinculo_bairro", "declaracao_maioridade",
             "declaracao_sem_condenacao", "declaracao_lgpd",
             "declaracao_sem_outra_chapa", "declaracao_sem_impedimento",
             "comprovante_residencia", "assinatura"]
  },
  cadastro_assembleia_consep_primavera: {
    aba: "Cadastro Assembleia",
    campos: ["protocolo", "data_registro", "status", "nome", "data_nascimento", "cpf",
             "documento", "orgao_emissor", "endereco", "telefone", "email",
             "vinculo_bairro", "declaracao_maioridade", "declaracao_sem_condenacao",
             "declaracao_lgpd", "documento_foto", "comprovante_residencia", "assinatura"]
  }
};
var CAMPOS_IMAGEM = { assinatura: 1, documento_foto: 1, comprovante_residencia: 1 };

function _json(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}

function _props() { return PropertiesService.getScriptProperties(); }

function _planilha() {
  var id = _props().getProperty("SHEET_ID");
  if (id) return SpreadsheetApp.openById(id);
  var ss = SpreadsheetApp.create("CONSEP Primavera — Cadastros");
  _props().setProperty("SHEET_ID", ss.getId());
  return ss;
}

function _pasta() {
  var id = _props().getProperty("FOLDER_ID");
  if (id) return DriveApp.getFolderById(id);
  var pasta = DriveApp.createFolder("CONSEP Primavera — Anexos");
  _props().setProperty("FOLDER_ID", pasta.getId());
  return pasta;
}

function _aba(cfg) {
  var ss  = _planilha();
  var aba = ss.getSheetByName(cfg.aba);
  if (!aba) {
    aba = ss.insertSheet(cfg.aba);
    aba.appendRow(["recebido_em"].concat(cfg.campos));
    aba.setFrozenRows(1);
    var padrao = ss.getSheetByName("Página1") || ss.getSheetByName("Sheet1");
    if (padrao && ss.getSheets().length > 1) ss.deleteSheet(padrao);
  }
  return aba;
}

// Converte "data:image/png;base64,...." em arquivo no Drive; devolve o link.
function _salvarImagem(dataUrl, nome) {
  var m = /^data:([^;]+);base64,(.+)$/.exec(String(dataUrl || ""));
  if (!m) return "";
  var ext  = (m[1].split("/")[1] || "bin").replace("jpeg", "jpg");
  var blob = Utilities.newBlob(Utilities.base64Decode(m[2]), m[1], nome + "." + ext);
  return _pasta().createFile(blob).getUrl();
}

function _achar(aba, protocolo) {
  var ult = aba.getLastRow();
  if (ult < 2) return 0;
  var vals = aba.getRange(2, 2, ult - 1, 1).getValues(); // coluna B = protocolo
  for (var i = 0; i < vals.length; i++) {
    if (String(vals[i][0]).trim() === String(protocolo).trim()) return i + 2;
  }
  return 0;
}

function _gravar(tipo, reg) {
  var cfg = TIPOS[tipo];
  if (!reg || !(reg.protocolo || reg.id)) return { ok: false, erro: "protocolo obrigatório" };
  var protocolo = String(reg.protocolo || reg.id);
  reg.protocolo = protocolo;

  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var aba = _aba(cfg);
    var n   = _achar(aba, protocolo);
    if (n) return { ok: true, protocolo: protocolo, acao: "ja_existia", linha: n };

    var agora = Utilities.formatDate(new Date(), "America/Bahia", "dd/MM/yyyy HH:mm:ss");
    var linha = [agora].concat(cfg.campos.map(function (c) {
      var v = reg[c];
      if (CAMPOS_IMAGEM[c]) return _salvarImagem(v, protocolo + "_" + c);
      if (typeof v === "boolean") return v ? "Sim" : "Não";
      return v == null ? "" : String(v);
    }));
    aba.appendRow(linha);
    SpreadsheetApp.flush();
    n = _achar(aba, protocolo);
    if (!n) return { ok: false, erro: "Gravação não confirmada" };
    return { ok: true, protocolo: protocolo, acao: "inserido", linha: n, confirmado: true };
  } finally {
    lock.releaseLock();
  }
}

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || "{}");
    if (d.token !== TOKEN) return _json({ ok: false, erro: "Token inválido" });
    if (!TIPOS[d.tipo]) return _json({ ok: false, erro: "tipo desconhecido: " + d.tipo });
    return _json(_gravar(d.tipo, d.registro));
  } catch (err) {
    return _json({ ok: false, erro: "Erro doPost: " + err });
  }
}

// GET ?token=...&acao=ping  → confere se está no ar (sem dados pessoais)
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.token !== TOKEN) return _json({ ok: false, erro: "Não autorizado" });
  return _json({ ok: true, versao: VERSAO });
}

// Rode manualmente uma vez para autorizar e criar planilha/pasta.
function testeSetup() {
  var ss = _planilha();
  Object.keys(TIPOS).forEach(function (t) { _aba(TIPOS[t]); });
  Logger.log("Planilha: " + ss.getUrl());
  Logger.log("Anexos:   " + _pasta().getUrl());
}
