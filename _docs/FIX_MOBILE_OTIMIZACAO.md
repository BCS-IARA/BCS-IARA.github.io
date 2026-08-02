# Otimização Mobile — Reforço (Fase 2)

**Contexto:** o app já tem base mobile sólida — sidebar deslizante, barra de navegação inferior, anti-zoom de input no iOS, e colapso de grids simétricos (`1fr 1fr`, `1fr 1fr 1fr`, `repeat(2/3/4/auto-fit/auto-fill)`) — tudo dentro do `@media(max-width:768px)` já existente (linha ~220-246). Este documento cobre só os buracos que ficaram de fora, com número exato de ocorrências, pra você priorizar.

**Escopo:** 3 mudanças, todas dentro do mesmo bloco `@media(max-width:768px)` que já existe. Nenhuma muda o visual em telas grandes (desktop fica intocado).

## 1. Grids assimétricos não colapsam (38 ocorrências)

O colapso atual só cobre padrões simétricos (`1fr 1fr`, `repeat(...)`). Padrões assimétricos como `1fr 2fr`, `3fr 1fr`, `90px 1fr 120px`, `110px 1fr 140px 34px` — usados em formulários e cabeçalhos de linha por toda a aplicação — continuam lado a lado em tela de celular, ficando espremidos/ilegíveis.

**Correção:** trocar as 5 regras específicas por uma regra universal que pega qualquer grid inline, independente do padrão de colunas:

Localizar (linhas ~233-237):
```css
  div[style*="grid-template-columns:1fr 1fr"]{grid-template-columns:1fr!important;}
  div[style*="grid-template-columns:repeat(2"]{grid-template-columns:1fr!important;}
  div[style*="grid-template-columns:repeat(3"]{grid-template-columns:1fr!important;}
  div[style*="grid-template-columns:repeat(4"]{grid-template-columns:1fr 1fr!important;}
  div[style*="grid-template-columns:repeat(auto-fit"]{grid-template-columns:1fr!important;}
```

Substituir por uma única regra universal:
```css
  [style*="grid-template-columns"]{grid-template-columns:1fr!important;}
```

Isso cobre automaticamente qualquer grid inline existente (incluindo os 38 assimétricos) e qualquer um que for criado no futuro — sem precisar listar padrão por padrão de novo cada vez que aparecer um novo formulário. A regra `.kpi-grid{grid-template-columns:1fr 1fr!important;}` (linha ~229) continua funcionando normalmente, ela não é afetada — confirmei que a classe não está em uso em nenhum lugar do HTML hoje, então é inofensiva, mas deixei como está por segurança.

Se algum grid específico realmente precisar continuar em 2 colunas no celular (ex.: um par valor+unidade bem curto), é só adicionar uma exceção pontual depois, caso a caso — mais simples que manter uma lista de padrões pra colapsar.

## 2. Tabelas sem rolagem horizontal (19 de 36)

19 das 36 tabelas do app não têm `overflow-x:auto`. A regra atual (`table{font-size:11px;}`) só diminui a fonte, não impede a tabela de estourar a largura da tela — em telas de ~360-390px, tabelas com 5+ colunas (ex.: a lista "Por Policial": Matrícula/Posto/Nome/Telefone/Turno/Status/Ações) ficam cortadas ou forçam scroll horizontal da página inteira, não só da tabela.

**Correção:** trocar a regra de tabela (linha ~228) por uma que faz a tabela rolar horizontalmente dentro dela mesma, isolada do resto da página:

Localizar:
```css
  table{font-size:11px;}
```

Substituir por:
```css
  table{font-size:11px;display:block;overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch;}
```

Isso resolve as 36 tabelas de uma vez, sem precisar tocar onde cada uma é gerada no código — inclusive as 17 que já estavam manualmente embrulhadas em `overflow-x:auto` (fica redundante nelas, mas inofensivo).

## 3. Botões pequenos demais pra toque (recomendo QA visual antes de aprovar)

Boa parte dos botões do app (principalmente em listas e tabelas — editar, mover, histórico, etc.) usa padding bem apertado (ex.: `padding:2px 8px` com fonte 10-11px), o que dá uma área de toque bem menor que o recomendado pra dedo (~38-44px é o padrão de mercado). Em telas mobile isso aumenta erro de toque, principalmente quando vários botões ficam colados na mesma linha.

**Correção sugerida (mais arriscada que as duas de cima — pode empurrar layout em linhas com vários botões apertados, recomendo testar visualmente antes de aprovar):**

Adicionar dentro do mesmo media query:
```css
  button{min-height:38px;}
```

Esse valor é um meio-termo deliberado: não é o ideal de 44px (que quebraria várias linhas de botões compactos), mas já é bem melhor que os 24-28px efetivos de hoje. Se quiser, posso deixar esse item pra uma rodada separada — os itens 1 e 2 são mecânicos e de baixo risco, esse aqui é visual e vale conferir numa tela de celular de verdade antes de fechar.

## Teste

Abrir o app num celular real (não só redimensionar o navegador do desktop — o comportamento de zoom de input e toque só aparece de verdade em touchscreen) e percorrer: tela de login, abrir um item de inventário pra editar, abrir uma Conferência, abrir a tabela "Por Policial", abrir qualquer formulário com 3+ campos lado a lado (ex.: cadastro de ocorrência). Confirmar que nada fica cortado, nenhum input dá zoom ao tocar, e as tabelas rolam horizontalmente sem empurrar a página inteira pro lado.
