# DÚVIDAS — Para decisão do responsável
> Gerado autonomamente em 2026-06-14.

## Bloco C — Esteira de Ocorrências

### D1: `fila_auxiliar` como tela padrão do gestor?
Hoje ao logar como gestor cai no `dashboard` de KPIs.
A especificação indica `fila_auxiliar` como tela padrão.
**Mudar o default** pode desorientar usuários acostumados.
→ **Confirme se deve mudar o default ou manter o dashboard.**

### D2: Atendimento unificado × formulário atual
O formulário atual de atendimentos é avulso (sem vínculo com OC ou vítima).
A especificação pede um "modal de atendimento unificado" que vincula à OC.
→ **Substituir o form atual ou manter os dois coexistindo?**

### D3: Ordenação da fila de triagem após VDs
Especificação: VDs primeiro. Restante: por data mais antiga (urgência) ou FIFO (lançamento)?
→ **Confirmar ordenação.**

## Bloco A — Inventário

### D4: Migração dos itens do Trilho A (materiais_patrimonio)
Antes de desabilitar a sincronização do Trilho A, itens ativos precisam ser copiados para `inv_itens`.
→ **Confirme se há itens importantes em `materiais_patrimonio` que devem ser preservados.**
→ **Pode rodar a migração agora ou prefere revisar os dados primeiro?**

### D5: Munição — reclassificação de itens seriais existentes
Se já há munição cadastrada em `inv_itens` como item serial (com tombamento), precisa ser re-classificada para o modelo lote.
→ **Há munição cadastrada? Deseja que o sistema faça a conversão automaticamente?**
