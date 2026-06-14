# REVISÃO_ESTEIRA — Bloco C: Ocorrências / Triagem / Central de Atendimento
> Gerado autonomamente em 2026-06-14. NÃO altera código. Aguarda aprovação.

---

## O que a especificação manda (seções 23 / Bloco C)

| Item | Especificação |
|------|--------------|
| Triagem | Tela `state.tela = 'triagem'` — fila de OCs com `situacao === 'nova'`, VDs primeiro |
| Badge nav | Contagem de OCs novas na nav do gestor |
| Busca de vítima | Componente `buscaVitima(onSelect)` com debounce 300ms no form de OC |
| Ficha da vítima | Tela com timeline de OCs e encaminhamentos |
| Fila auxiliar | `state.tela = 'fila_auxiliar'` como tela padrão do gestor |
| Modal atendimento | Atendimento unificado vinculado à OC (não ao formulário solto atual) |
| Fila encaminhamentos | Lista de encaminhamentos pendentes (a_encaminhar / encaminhado) |

---

## O que existe hoje no código

### Tela de ocorrências
- `renderOcorrenciasGestor(el, perfil)` (linha 16458) — tela de listagem e busca de OCs
- Acesso via `state.tela = "ocorrencias"` (linha 12243)
- Tem busca por texto livre, filtros por tipo/VD/requer_visita/reincidente
- **NÃO tem**: filtro por `situacao`, fila de triagem, badge de novos

### Atendimentos
- Formulário simples em `tela === "atendimentos"` (linha 12249–12272)
- Campos: data, hora, nome, telefone, tipo, descrição, encaminhamento
- **NÃO tem**: vínculo com OC, vínculo com vítima, gestão de situação

### Tela de lançar OC
- `tela === "lancar"` renderizado para operador e gestor
- Formulário completo (tipo, vítima, suspeito, etc.)
- **NÃO tem**: busca de vítima existente, campo `situacao` visível, `vitima_id`

### Vítimas e encaminhamentos
- `state.vitimas` e `state.encaminhamentos` já existem no estado (desde a sessão anterior)
- Backend pronto: `salvarVitima`, `buscarVitima`, `salvarEncaminhamento`, etc.
- **NÃO tem**: UI de nenhum desses — nenhuma tela de ficha de vítima, nenhuma fila de encaminhamentos

### Nav do gestor (linha 12854)
- Botão "🔍 Analisar Ocorrências" → `setTela('ocorrencias')`
- **NÃO tem**: badge de OCs novas, botão de triagem

---

## Divergências entre especificação e código atual

| # | Especificação | Código atual | Gap |
|---|--------------|-------------|-----|
| 1 | Badge "N para triar" na nav | Não existe | **Novo** |
| 2 | Tela `triagem` (fila de novas) | Não existe | **Novo** |
| 3 | Busca de vítima no form OC | Não existe | **Novo** |
| 4 | Ficha da vítima | Não existe | **Novo** |
| 5 | `fila_auxiliar` como default gestor | Não existe — default é `dashboard` | **Novo** |
| 6 | Atendimento unificado c/ OC | Form avulso sem vínculo | **Refatoração** |
| 7 | Fila de encaminhamentos | Não existe | **Novo** |
| 8 | Campo `situacao` no form de OC | Campo existe no backend, não aparece na UI | **Exposição de campo existente** |

---

## Pontos que precisam de decisão antes de implementar

1. **`fila_auxiliar` como tela padrão do gestor**: hoje ao logar como gestor cai no `dashboard`.
   Mudar o default quebra o fluxo atual de quem está acostumado. Confirmar?

2. **Atendimento unificado**: o formulário atual de atendimentos (`tela === "atendimentos"`)
   tem dados diferentes do "Modal de Atendimento" da especificação (que vincula OC e vítima).
   Proposta: manter formulário antigo como acesso rápido + criar o novo modal vinculado à OC.
   Ou substituir? Precisa de decisão.

3. **Ordem da fila de triagem**: especificação diz "VDs primeiro". Após VDs, ordenar por data
   (mais antigas primeiro = mais urgentes) ou por data de lançamento (FIFO)?

4. **Fila auxiliar × dashboard**: a tela `fila_auxiliar` seria o novo "home" do gestor,
   substituindo o dashboard de KPIs? Ou coexiste?

---

## Proposta de implementação (ordem segura)

1. Badge "N para triar" na nav → 1 linha de código, zero risco
2. Tela `triagem` (fila simples de OCs novas) → nova função `renderTriagem(main)`
3. Campo `situacao` exposto no form de OC → campo select existente no backend, só falta UI
4. Busca de vítima no form (`buscaVitima`) → componente novo, debounce 300ms
5. Ficha da vítima → nova tela `state.tela = 'vitima'`
6. Fila de encaminhamentos → nova tela
7. `fila_auxiliar` e atendimento unificado → após confirmar decisões 1 e 2 acima

Itens 1–4 são independentes e de baixo risco.
Itens 5–7 dependem de decisões do usuário.
