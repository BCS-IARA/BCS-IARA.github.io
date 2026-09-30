# Plano — Envio de encaminhamentos por e-mail direto do IARA

**Situação:** fluxo manual implantado (30/09/2026). Envio automático aguardando os e-mails dos órgãos e o acesso ao Apps Script.
**Registrado em:** 30/09/2026

## Objetivo

Hoje os encaminhamentos são mandados por e-mail fora do sistema. Os órgãos atendem e depois mandam a devolutiva. A ideia é enviar o e-mail **direto do IARA, com um clique**, com o ofício em PDF anexado, e deixar o encaminhamento marcado como enviado.

## Como vai funcionar

1. Na **Minha Mesa**, depois de escolher o órgão e o prazo, aparece o botão **✉ Enviar por e-mail**.
2. O IARA monta o **ofício em PDF**, com três partes:
   - o ofício numerado;
   - o dossiê do caso;
   - o link/QR do formulário de devolutiva, com o código certo do órgão.
3. O **Google Apps Script** envia o e-mail com o PDF anexado pelo Gmail da conta dona da planilha (`GmailApp`/`MailApp`).
4. O encaminhamento fica **"enviado em dd/mm por <atendente>, ofício nº X"**. O prazo da devolutiva passa a contar **a partir do envio**.
5. Quando a devolutiva chega pelo formulário, o **🔔 sino** avisa (já funciona).

### Complementos previstos
- **Pilha "A enviar"** na Minha Mesa: encaminhamentos criados e ainda não enviados. A pilha "Cobrar" só conta depois do envio.
- **Plano B, se o envio automático falhar:** botões "📄 Baixar ofício", "✉ Abrir e-mail" (com destinatário, assunto e texto já preenchidos) e "✅ Marcar como enviado".
- **PDF consolidado do caso:** cada encaminhamento mostra o nº do ofício e os dados de envio.

## Já implantado (fluxo manual, 30/09/2026)

- **Pilha "📤 Encaminhamentos" na Minha Mesa**, com os filtros ⏳ A enviar · 🔴 Vencidos · 📨 Aguardando · ✅ Devolutiva chegou, filtro por órgão e ações na própria linha.
- **Cadastro de e-mails dos órgãos** (botão "✉ E-mails dos órgãos"), salvo no aparelho e no Sheets (chave `bcs_orgaos`). O CRAV já vem preenchido. Quando um órgão ainda não tem e-mail, o botão ✉ pergunta o endereço e guarda para as próximas vezes.
- **Botão ✉ E-mail**, que abre o e-mail com destinatário, assunto e texto preenchidos, incluindo o link de devolutiva. O PDF do ofício ainda precisa ser anexado à mão. Para encaminhamento já enviado, abre um e-mail de cobrança.
- **Marcar como enviado:** grava `enviado_em` e `enviado_por`, e o prazo conta a partir do envio.
- **Botão único** para marcar como enviados os encaminhamentos antigos criados antes de hoje.

O envio automático vai reaproveitar esse cadastro de e-mails (`bcs_orgaos`).

## Pendências — antes do envio automático

- [ ] **E-mails dos órgãos.** Lista a preencher:

  | Órgão | E-mail | Telefone | Responsável |
  |---|---|---|---|
  | CRAV | crav.pmvc@gmail.com | | |
  | CRAS | | | |
  | CREAS | | | |
  | DEAM | | | |
  | Conselho Tutelar | | | |
  | UBS | | | |
  | Defensoria Pública | | | |
  | Ministério Público | | | |

- [ ] **Conta Google dona da planilha/Apps Script.** O e-mail sai dela. O ideal é uma conta da unidade, não pessoal.
- [ ] **Alguém com acesso ao Apps Script** para, uma única vez: colar o código novo, clicar em **Implantar** e **autorizar o envio de e-mails**. Leva uns 5 minutos, com passo a passo.
- [ ] **Formato do nº do ofício** usado pela unidade (ex.: `014/2026-BCS/77ªCIPM`).

## O que será implementado (quando as pendências forem resolvidas)

- **Cadastro de órgãos** em Configurações: nome, e-mail, telefone, responsável e código do formulário de devolutiva.
- **Numeração automática de ofício** por ano.
- **Nova rota no Apps Script** (`enviarEncaminhamentoEmail`): recebe o HTML do ofício, gera o PDF (`HtmlService` → `getAs('application/pdf')`), envia com anexo e devolve ok/erro.
- **Na Minha Mesa:** o botão "✉ Enviar por e-mail", a pilha "A enviar" e o registro de envio (data, atendente, nº do ofício).
- **Publicar o formulário de devolutiva v75**, que está parado na beta (branch `claude/kind-gauss-m08o90`). Ele corrige os nomes de CRAS, CREAS, UBS e DEAM. Também ajustar os links para usar o código de cada órgão.

## Limites a saber

- O Gmail tem limite diário: cerca de **100 e-mails/dia** numa conta comum (1.500 no Google Workspace).
- O remetente é a conta dona do Apps Script. As cópias ficam em "Enviados", o que serve de comprovante.
