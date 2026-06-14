# PLANO_INVENTARIO — Blocos A e B
> Gerado autonomamente em 2026-06-14. NÃO altera código. Aguarda aprovação.

## Decisão vigente (INSTRUCOES_CODE.md)
- **Trilho B = `inv_itens`** é o inventário real (front + back completos).
- **NÃO criar** `inventario_patrimonio` — seções 50/52/53 da auditoria estão superadas.
- Trilho A (`materiais_patrimonio`) é paralelo e legado — sobrevive só para os itens já cadastrados lá.

---

## BLOCO A — Correção funcional: unificar no Trilho B

### O que está errado hoje
`_armAtualizarInventarioAposCarga` (index.html linha 13838–13869) atualiza `state.invItens`
quando uma carga de armamento é processada. Isso está **correto** — já usa o Trilho B.

O problema real é que `materiais_patrimonio` é sincronizado separadamente via
`_sincSheets("materiais_patrimonio", ...)` (linha 968) e exibido em
`_renderPatrimonioCadastro` (linha 13871) como um segundo inventário paralelo.

Isso cria dois inventários ativos simultaneamente:
- `inv_itens` — armas, coletes, rádios (via formulário de inventário)
- `materiais_patrimonio` — itens cadastrados antes do Trilho B existir

### O que mudar

| # | Arquivo | Linha aprox | Ação |
|---|---------|-------------|------|
| 1 | index.html | ~968 | Remover `_sincSheets("materiais_patrimonio", ...)` — parar de sincronizar o Trilho A |
| 2 | index.html | ~1266 | Manter `state.materiaisPatrimonio` no estado (não quebra dados antigos) mas marcar como legado |
| 3 | index.html | ~13871 | Em `_renderPatrimonioCadastro`: adicionar banner "Use o Inventário (Trilho B) para novos itens" |
| 4 | index.html | ~14550 | `_armAtualizarInventarioAposCarga` — já correto, nada a mudar |
| 5 | index.html | nav | Remover ou ocultar o sub-menu "Patrimônio (legado)" se existir — deixar só "Inventário" |

### Riscos
- Itens em `materiais_patrimonio` que não foram migrados para `inv_itens` ficam órfãos.
  **Mitigação**: antes de desligar a sincronização, rodar um script de migração que copia
  os ativos de `materiais_patrimonio` para `inv_itens` com campo `origem: "legado_mat_patrimonio"`.
- **Não deletar** `materiais_patrimonio` do estado — só parar de sincronizar para frente.

### Ordem proposta
1. Script de migração (frontend one-shot): copia ativos do Trilho A para Trilho B
2. Desabilitar `_sincSheets("materiais_patrimonio", ...)` (comentar linha ~968)
3. Ajustar UI do módulo Patrimônio com banner informativo
4. Commit: `inventario: unifica no trilho B (inv_itens)`

---

## BLOCO B — Novas saídas do Inventário

### B1: Relatório PDF de carga/descarga
- Por policial: todos os itens carregados/descarregados no período
- Por item: histórico de quem portou
- Formato: tabela imprimível (usar `@media print` + `window.print()`)
- Arquivo: dentro de `renderInventario` ou `renderLivroParteArmamento`
- Risco: baixo (geração local sem escrita de dados)

### B2: Parecer da Comissão de Inventário
- Aparece ao fechar uma conferência (`inv_conferencias`)
- Campos: membros da comissão (2 assinaturas), data, resultado (aprovado/pendência/reprovado), obs
- Estrutura já documentada na auditoria (seção "Parecer da Comissão")
- Já existe `salvarInvConferencia` no backend (assin1, assin2)
- O que falta: UI do parecer na tela de encerramento da conferência

### B3: Munição como saldo/lote
- Munição não tem número de série — é gerenciada por quantidade (lote, guia de descarga, saldo atual)
- Estado atual: munição pode estar sendo cadastrada como item serial em `inv_itens` (errado)
- Proposta: campo `tipo_gestao: "serial" | "lote"` em `inv_itens`
  - Se `"lote"`: exibe campos `qtd_inicial`, `guia_entrada`, `baixas[]`, `saldo_atual` (calculado)
  - Se `"serial"`: fluxo atual (tombamento, carga por item)
- Risco: médio — requer migração de itens de munição já cadastrados

### B4: Perfis de importação das 4 listas oficiais
- Arma (SIAP), Colete, Munição (lote), Material geral
- Implementação: botão "Importar lista" no módulo de inventário
- Formato de entrada: CSV ou planilha (já temos `importar_planilha.py` como referência)
- Risco: baixo (leitura, não escrita destrutiva)

---

## Decisões necessárias antes de implementar

1. **Migração Trilho A→B**: fazer agora ou deixar órfão? (sugestão: fazer — ~poucos itens)
2. **Munição como lote**: confirmar se já há itens de munição em `inv_itens` que precisem ser re-classificados
3. **PDF**: usar `window.print()` (simples, offline) ou biblioteca externa?
