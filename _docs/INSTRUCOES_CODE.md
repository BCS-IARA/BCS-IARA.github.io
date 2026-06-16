# INSTRUÇÕES PARA O CLAUDE CODE — Implementação do IARA

> Leia este arquivo primeiro. Ele diz **por onde começar**, **em que ordem** e **o que NÃO fazer**.
> O documento de referência completo é `AUDITORIA_IARA_CONSOLIDADO.md`.

---

## 0. ANTES DE QUALQUER COISA

1. **Leia o "⚠️ AVISO DE PRECEDÊNCIA"** no topo do `AUDITORIA_IARA_CONSOLIDADO.md`. Ele resolve conflitos entre seções antigas e decisões novas. Ignorá-lo leva a implementar o inventário errado.
2. **Trabalhe com git.** Faça um commit por bloco (ver abaixo). Assim dá para reverter se algo quebrar.
3. **Não implemente tudo de uma vez.** Faça bloco por bloco e PARE ao fim de cada um para revisão.
4. **Separe funcionalidade de aparência.** Nunca misture mudança de comportamento e redesign visual no mesmo commit.

---

## 1. REGRA CRÍTICA DO INVENTÁRIO (não erre isto)

As seções 50, 52 e 53 do documento mandam criar a aba `inventario_patrimonio`. **ISSO ESTÁ SUPERADO.**
- O inventário real é o **Trilho B: `inv_itens`** (já existe, completo, front + back).
- **NÃO crie** a aba `inventario_patrimonio`.
- Onde as seções antigas disserem `inventario_patrimonio`, **leia `inv_itens`**.
- O acoplamento a remover é só no **frontend**: `_armAtualizarInventarioAposCarga` (`index.html`, ~linha 14469). O backend já está correto.
- A decisão vigente é **"Opção 1 — unificar no Trilho B"** (ver "Nota de reconciliação com o código real").

---

## 2. ORDEM DE IMPLEMENTAÇÃO (blocos)

### BLOCO A — Correções funcionais do Inventário/Armamento
- Aplicar a decisão Opção 1 (unificar no Trilho B `inv_itens`).
- Neutralizar `_armAtualizarInventarioAposCarga` no frontend; armar passa a refletir em `inv_itens`.
- Migrar os itens do Trilho A (`materiais_patrimonio`) que ainda estejam ativos para `inv_itens`.
- Referência: seções 45, 50, 52, 53, 54 + "Nota de reconciliação" + "Verificação das funções".
- **Commit:** `inventario: unifica no trilho B (inv_itens)`

### BLOCO B — Novas saídas do Inventário
- Relatório PDF de carga/descarga (por policial e por item).
- Parecer da Comissão de Inventário ao fim da conferência (ver seção "Parecer da Comissão" — estrutura completa documentada).
- Suporte a munição como saldo/lote (guia, qtd, baixa, saldo) — não item serial.
- Perfis de importação das 4 listas oficiais (arma, colete, munição, SIAP).
- **Commit:** `inventario: relatorios, parecer da comissao e municao`

### BLOCO C — Pendências funcionais gerais
- Aplicar as decisões das seções de Ocorrências/Triagem/Central/Calendário conforme o documento.
- ⚠️ **Antes de implementar a esteira (Ocorrências/Triagem/Central):** leia o código atual dessas telas e confirme se a especificação bate. Essa parte NÃO foi reverificada contra código na auditoria. Relate divergências antes de executar.
- Remover telas extintas (seção 44) e ajustar o menu (seções 36, 42, 44).
- **Commit:** `fluxo: esteira de ocorrencias e central de atendimento`

### BLOCO D — Redesign visual (FASE SEPARADA, por último)
- Implementar a identidade "Pergaminho e Madeira" (seção 24) — hoje 0% no código.
- Seguir os 4 passos da "PENDÊNCIA TRANSVERSAL — Migração de identidade visual".
- Ordem por visibilidade: Central/Calendário/Ocorrências → Projetos Sociais → Painel do Comandante → Módulos administrativos.
- Meta de varredura final: **0 ocorrências** das cores antigas (`#1a0a28`, `#130d24`, `#2a1040`, `#a78bfa`, `#c89ae8`, `#0e0820`).
- **Commits:** um por módulo, ex.: `design: pergaminho na central de atendimento`

---

## 3. O QUE ESTÁ FORA DO ALCANCE DO CODE (precisa de ação sua)

Estas páginas **não estão na pasta** e o Code não consegue editá-las até serem adicionadas:
- Portfólio público (`bcs-iara.github.io/projetos`) — há protótipo aprovado em `PORTFOLIO_PROTOTIPO.html`.
- Formulário de inscrição (`inscricao.html`).

Para o Code reconstruí-las no padrão pergaminho, **adicione os arquivos-fonte à pasta primeiro**.

---

## 4. O QUE JÁ ESTÁ BOM (não refazer)

- **Projetos Sociais — fluxo:** aprovado, funciona front+back. Só precisa do redesign visual (Bloco D). Não mexer na lógica.
- **Solicitações:** funcionando bem.
- **Backend de `carga_armamento` e `inv_itens`:** corretos.

---

## 5. COMO PEDIR AO CODE (sugestão de primeira mensagem)

> "Leia o INSTRUCOES_CODE.md e o AVISO DE PRECEDÊNCIA no topo do AUDITORIA_IARA_CONSOLIDADO.md.
> Comece pelo BLOCO A. Antes de escrever código, me explique o que vai mudar e em quais arquivos/linhas.
> Faça um commit ao final e pare para eu revisar antes do BLOCO B."

Peça sempre que ele **explique antes de executar** e **pare entre blocos**.
