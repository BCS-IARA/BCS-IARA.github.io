# INSTRUÇÃO — Sublocalização + Cadastro de Localizações (IARA)

## Contexto
Hoje `INV_LOCAIS` é um array fixo (hardcoded) de strings usado para popular o
`<select id='inv-local'>` no formulário de item (`_invAbrirItem` ou função
equivalente que monta `locOpts`). O item grava só `item.localizacao` (string
única, sem hierarquia, sem sublocalização).

Esta instrução faz duas coisas:
1. Adiciona campo de **sublocalização**, hierárquico e vinculado à localização-mãe
2. Transforma localização e sublocalização em **dados gerenciáveis pela interface**
   (não mais hardcoded no código), com tela própria de cadastro

NÃO mexer no módulo de conferência desta vez — escopo é só cadastro de item e
gestão de localizações.

---

## 1. Nova estrutura de dados

### 1.1 Migrar `INV_LOCAIS` (array fixo) para `state.invLocais` (dado gerenciável)

```js
// Estrutura nova:
state.invLocais = [
  {
    id: "loc_001",
    nome: "Almoxarifado",
    sublocais: ["Prateleira A", "Prateleira B", "Prateleira C", "Depósito"]
  },
  {
    id: "loc_002",
    nome: "Sala de Plantão",
    sublocais: []
  },
  // ... etc
]
```

**Migração obrigatória na inicialização**: se `state.invLocais` não existir,
criá-lo a partir do array `INV_LOCAIS` atual (cada string vira um objeto
`{id: gerado, nome: string original, sublocais: []}`), preservando todas as
localizações já em uso pelos itens existentes. Não perder nenhum valor que já
esteja gravado em `item.localizacao` no banco atual — se algum item tiver uma
localização que não está no array `INV_LOCAIS` original, adicionar essa
localização também na migração (evitar item "órfão" sem opção correspondente
no novo select).

### 1.2 Campo novo no item

```js
item.sublocalizacao = ""  // string livre? NÃO — selecionada da lista do local-mãe
```

Adicionar `sublocalizacao` em todos os pontos onde o objeto `item` é criado
(cadastro novo, migração de patrimônio, etc.) com valor padrão `""`.

---

## 2. Formulário de cadastro/edição de item (`_invAbrirItem` ou equivalente)

Local atual: o bloco que monta `locOpts` a partir de `INV_LOCAIS` e renderiza
`<select id='inv-local'>`.

### Mudanças:
- `locOpts` agora vem de `state.invLocais.map(l => l.nome)`, mantendo a mesma
  lógica de "selected" se for edição.
- Adicionar logo ao lado (mesmo grid row, ou linha abaixo) um segundo select:
  `<select id='inv-sublocal'>`, populado **dinamicamente** com `sublocais` da
  localização atualmente selecionada em `inv-local`.
- Comportamento: ao trocar o select de localização (`onchange`), recarregar as
  opções do select de sublocalização correspondente (função nova,
  `_invAtualizarSublocais()`, lida no `onchange='_invAtualizarSublocais()'`).
- Se a localização escolhida não tiver nenhuma sublocalização cadastrada,
  mostrar o select desabilitado com a opção única "— Nenhuma sublocalização —".
- Se for edição de item existente e `item.sublocalizacao` não existir mais na
  lista atual de sublocais (foi removida depois), ainda assim mostrar o valor
  salvo como opção selecionada (para não perder o dado), com indicação visual
  sutil (ex: cor diferente) de que está fora da lista atual.
- Salvar `inv-sublocal` no objeto `item.sublocalizacao` junto com o resto do
  formulário (mesmo ponto onde `item.localizacao` é gravado hoje).

### Exibição na listagem de itens
Onde a localização do item já é exibida na lista de itens (`renderInventario`,
no card/linha de cada item), adicionar a sublocalização ao lado, formato:
`Almoxarifado › Prateleira B` (separador `›`). Se não tiver sublocalização,
mostrar só a localização, sem o separador vazio.

---

## 3. Nova tela: Cadastro de Localizações

Criar uma nova aba/seção dentro do módulo Inventário (ao lado das abas já
existentes — Itens, Movimentações, Conferências, Por Policial — verificar o
padrão de abas usado em `state._invTab` e seguir o mesmo estilo visual).

Nome da aba: **"Localizações"**, `state._invTab === "locais"`.

### Conteúdo da tela:
Lista de localizações cadastradas, cada uma expansível mostrando suas
sublocalizações, com:

- **Adicionar localização**: campo de texto + botão "+ Adicionar Localização"
- Para cada localização na lista:
  - Nome (editável inline ou via botão "Editar")
  - Lista de sublocalizações dessa localização, cada uma com botão remover (✕)
  - Campo de texto + botão "+ Adicionar Sublocalização" dentro do bloco daquela
    localização
  - Botão "Remover Localização" (com confirmação) — **bloquear remoção** se
    houver itens (`state.invItens`) atualmente usando essa localização; nesse
    caso mostrar mensagem: "Não é possível remover: X item(ns) usam esta
    localização."
  - Mesma regra de bloqueio para remover uma sublocalização que esteja em uso.

### Persistência
Seguir o mesmo padrão já usado no projeto para salvar estado (`_invSalvarLocal()`
e `_invEnviarSheets` se aplicável a essa entidade — verificar se já existe um
tipo de registro "inv_local" enviado ao Sheets ou se isso fica só local por
enquanto; se não houver padrão claro, manter local primeiro e perguntar antes
de criar uma aba nova na planilha do Google Sheets).

---

## 4. Compatibilidade e não regressão

- Itens já cadastrados sem `sublocalizacao` devem continuar funcionando
  normalmente — tratar `undefined`/`""` como "sem sublocalização", nunca
  quebrar a renderização.
- A função de busca/filtro de itens (`filtBusca` em `renderInventario`) deve
  passar a incluir `sublocalizacao` no campo pesquisável (`hay`), junto com
  descrição, tombamento, marca, modelo, localização.
- Onde quer que `INV_LOCAIS` seja referenciado diretamente no código (fazer
  busca global por esse identificador antes de implementar), substituir pela
  leitura de `state.invLocais.map(l => l.nome)` para manter consistência única
  da fonte de dados.

---

## Ordem de implementação sugerida

1. Migração de `INV_LOCAIS` → `state.invLocais` com preservação de dados existentes
2. Campo `sublocalizacao` no item + atualização do formulário de cadastro/edição
   (select dependente de localização)
3. Exibição da sublocalização na listagem de itens + inclusão na busca
4. Nova aba "Localizações" com CRUD de localização e sublocalização
5. Regras de bloqueio de remoção quando em uso

Testar cada etapa isoladamente. Reportar ao final de cada uma antes de seguir
para a próxima.
