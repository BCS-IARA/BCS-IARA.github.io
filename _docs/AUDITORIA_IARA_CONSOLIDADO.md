<!-- CONSOLIDADO 14/06/2026 — original v1.0 + adições da sessão de auditoria de Inventário/Armamento e verificação de Projetos Sociais. Pronto para Claude Code. -->

# AUDITORIA IARA — Módulo de Ocorrências
**Versão:** 1.0 · **Data:** 11/06/2026  
**Contexto:** Sistema em operação — 77ª CIPM / Base Comunitária de Segurança Nova Cidade  
**Dados reais:** 765 ocorrências, 2.530 agendamentos, 35 FRIDAs, 193 visitas realizadas

---

## ⚠️ AVISO DE PRECEDÊNCIA — leia antes de implementar

Este documento é a versão consolidada (v1.0 original + adições de auditoria de junho/2026). Algumas seções originais foram escritas **antes** da inspeção do código real e foram **superadas** por notas de reconciliação posteriores. Em caso de conflito, **vale sempre a decisão mais recente** (as notas marcadas com ⚠️ ou ✅ no fim das seções de inventário e projetos).

**Conflitos conhecidos e qual instrução seguir:**

1. **Inventário — aba de destino (CRÍTICO).** As seções 50, 52 e 53 mandam *criar a aba `inventario_patrimonio`* e escrever nela. Isso está **SUPERADO**. A inspeção do código real mostrou que essa aba não existe e não deve ser criada: o inventário real é o **Trilho B `inv_itens`**, que já está completo front+back. **Seguir a "Nota de reconciliação com o código real" e a decisão "Opção 1 — unificar no Trilho B".** Onde as seções 50/52/53 disserem `inventario_patrimonio`, leia `inv_itens`. O acoplamento a remover é só no frontend (`_armAtualizarInventarioAposCarga`, index.html ~14469), não no backend.

2. **Numeração de seções.** Existem **duas seções numeradas "53"** (uma "cirurgia no código", outra "correção cirúrgica — linhas exatas"). São complementares, não substitutas; ambas tratam da separação Armamento×Inventário e ambas estão sujeitas ao item 1 acima (alvo = `inv_itens`).

3. **Módulo Escolar.** A seção 36 lista "🏫 Escolar" no menu, mas a seção 44 define a tela `escolas` como **extinta** (rondas viram subtipo `ronda_escolar` de visita, seção 37). **Decisão pendente do responsável** se o item de menu permanece como atalho de relatórios de ronda ou é removido. Até lá, tratar ronda escolar como subtipo de visita.

4. **Páginas públicas externas.** O portfólio (`bcs-iara.github.io/projetos`) e o formulário (`inscricao.html`) **não estão no pacote** e não podem ser reconstruídos pelo Code sem serem adicionados. Ver "identidade visual da jornada pública" e "Portfólio público — direção visual aprovada".

As adições de junho/2026 estão ao fim das seções de inventário (após a seção 53) e cobrem: reconciliação dos dois trilhos, decisão Opção 1, verificação de funções, adequação às 4 listas oficiais, Parecer da Comissão, verificação de Projetos Sociais, jornada pública e direção visual do portfólio.

---

## 1. Diagnóstico do estado atual

### O que existe hoje

| Componente | Situação |
|---|---|
| Lançamento de ocorrência | Funciona, mas sem campo de relato obrigatório e sem vínculo de vítima |
| Tela "Atendimentos" genérica | Existe, mas desconectada de vítimas e ocorrências |
| Atendimento VCM no monitor FRIDA | Mais completo, mas exclusivo do trilho VCM |
| Atendimento de Projetos Sociais | Terceiro formulário isolado com lógica própria |
| Ficha VCM PDF | Existe, consolida FRIDA + visitas, mas não inclui atendimentos e depende de fuzzy match por nome |
| Encaminhamento a órgãos | Campo de texto sem ciclo de vida — aba `devolutivas_crav` com 0 linhas |
| Calendário | Funciona como agenda passiva — sem visão de guarnição por dia |

### Três buracos críticos (confirmados pelos dados)

1. **Identidade da vítima não capturada:** 694 de 765 ocorrências (91%) sem nome de vítima estruturado. O nome está dentro do texto livre "Dinâmica dos fatos". Todo vínculo entre ocorrências depende de fuzzy match frágil por nome.

2. **FRIDA subaplicado e incompleto:** 35 FRIDAs para 165 ocorrências de VD (cobertura de 21%). Dos 35, **19 não têm nível registrado** — a priorização da fila VCM depende do nível e não funciona para mais da metade.

3. **Encaminhamento sem retorno:** O campo "Encaminhamento" dos 139 atendimentos está vazio. A devolutiva dos órgãos nunca chegou ao sistema. A auxiliar envia toda sexta, mas nada fecha o ciclo.

### Fronteira de dados

- **Até março/2026:** dados importados, campos incompletos. Tratar como **"histórico"** — manter quieto.
- **A partir de abril/2026 (últimos 15 dias):** lançamento manual, dados completos. Tratar como **"completo"**.
- A migração **não toca o histórico**. O enriquecimento é progressivo: quando um caso histórico reabre, a auxiliar vincula a vítima naquele momento.

---

## 2. Modelo de dados novo

### Entidade Vítima (nova — hoje não existe)

```
vitima {
  id              string  PK
  nome            string  obrigatório
  sexo            string  F | M
  idade           number  obrigatório
  telefone        string
  endereco        string
  cpf             string
  bairro          string
  criadoEm        datetime
  atualizadoEm    datetime
}
```

**Regra:** ao buscar no lançamento, se nome+sexo+idade baterem com vítima existente → vincula. Se não encontrar → cria nova ao salvar. O CPF é comparação definitiva quando presente.

### Ocorrência — campos alterados

```
ocorrencia {
  -- campos existentes mantidos --
  id, numero, data, hora, tipo, bairro, municipio
  suspeito_nome, suspeito_apelido, suspeito_caracteristicas
  veiculo, medida_protetiva

  -- campos renomeados/reorganizados --
  vitima_id       string  FK → vitima.id   (substitui campos vitima_* soltos)
  relato          string  (era "Dinâmica dos fatos" — agora nomeado e visível)
  medidas_adotadas string

  -- campo novo --
  situacao        string  nova | em_triagem | em_acompanhamento | encerrada | historico
  menor_envolvido boolean  (true quando vitima.idade < 18)
  violencia_domestica boolean  (auto: true para tipos Maria da Penha, ameaça, agressão, VCM)
  requer_visita   boolean
  fonte           string  manual | importado  (importado = histórico até março)
}
```

### Atendimento — unificado (substitui os três atuais)

```
atendimento {
  id              string  PK
  vitima_id       string  FK → vitima.id
  ocorrencia_id   string  FK → ocorrencia.id  (opcional — pode ser contato avulso)
  data            date    obrigatório
  hora            time
  tipo            string  visita_solidaria | visita_comunitaria | contato_telefonico
                          | frida | encaminhamento | retorno_orgao | ronda_escolar
  resultado       string
  relato          string
  responsavel     string
  proxima_acao    string
  proxima_data    date    → gera agendamento automaticamente
  criadoEm        datetime
}
```

### Encaminhamento — ciclo de vida próprio

```
encaminhamento {
  id              string  PK
  vitima_id       string  FK
  ocorrencia_id   string  FK
  orgao           string  CRAV | CREAS | MP | Conselho_Tutelar | UBS | outro
  situacao        string  a_encaminhar | enviado | aguardando_devolutiva | encerrado
  data_envio      date
  data_devolutiva date
  relato_devolutiva string
  responsavel     string
  criadoEm        datetime
}
```

**Regra:** toda sexta a auxiliar abre a fila `situacao = a_encaminhar`, envia em lote por órgão, muda para `enviado`. Quando o órgão responde, ela registra a devolutiva e fecha com `encerrado`.

---

## 3. Fluxo completo — esteira de triagem

```
LANÇAR → TRIAGEM → [trilhos] → CALENDÁRIO DA GUARNIÇÃO
                                    ↓
                             ATENDIMENTO (realizar)
                                    ↓
                             FICHA DA VÍTIMA (histórico)
                                    ↓
                             DOSSIÊ PDF (encaminhar)
```

### Situações da ocorrência

| Situação | Significado |
|---|---|
| `nova` | Acabou de ser lançada — aguarda triagem |
| `em_triagem` | Triagem aberta, não salva ainda |
| `em_acompanhamento` | Triagem concluída — há visita, FRIDA ou encaminhamento pendente |
| `encerrada` | Sem desdobramento (ex.: averiguação simples) |
| `historico` | Importada até março/2026 — não exige triagem |

---

## 4. As quatro telas do módulo

### 4.1 Lançar ocorrência

**Objetivo:** registrar o fato rapidamente.  
**Obrigatório:** tipo, data, hora, bairro, vítima (busca), sexo, idade.  
**Opcional no lançamento:** relato (pode ser colado agora ou preenchido na triagem).

**Campo de vítima — comportamento:**
- Usuário começa a digitar → sistema busca em tempo real nas vítimas cadastradas.
- Se encontrar → mostra card com "X ocorrência(s) · vincular" → clique vincula.
- Se não encontrar → opção "Nova vítima: [nome digitado]" → cria ao salvar.
- Ao vincular → mostra automaticamente histórico resumido (nº de ocorrências, última data, se é reincidente).

**Automático ao salvar:**
- Tipo contém "Maria da Penha", "ameaça", "agressão", "VCM", "lesão corporal" → `violencia_domestica = true` + aviso visual.
- `vitima.idade < 18` → `menor_envolvido = true` + aviso visual.
- Situação nasce como `nova`.

**Campo relato:**
- Exibido abaixo dos campos obrigatórios, com placeholder: "Dinâmica dos fatos — cole o texto do BO ou descreva".
- Não é bloqueante: pode salvar sem preencher.

---

### 4.2 Triagem

**Objetivo:** classificar o caso e rotear para ações concretas.  
**Quem acessa:** auxiliar (perfil gestor/operador com acesso à triagem).  
**Quando:** logo após o lançamento, ou a qualquer momento enquanto `situacao = nova`.

**Bloco 1 — Vítima e contexto (topo)**
- Card com nome, idade, sexo, bairro, telefone da vítima vinculada.
- Badge de reincidência ("3ª ocorrência") quando há histórico.
- Últimas 2 ocorrências com data e resultado do FRIDA quando houver.
- Relato completo: `textarea` grande pré-preenchido com o que foi colado no lançamento (editável).

**Bloco 2 — Classificação (quatro trilhos)**

| Trilho | Pré-marcado quando | Abre |
|---|---|---|
| Violência doméstica / VCM | `violencia_domestica = true` | Botão "Aplicar FRIDA" (obrigatório) |
| Menor envolvido | `menor_envolvido = true` | Botão "Encaminhar ao Conselho Tutelar" |
| Encaminhar a órgão | Manual | Seleção de órgãos → entra na fila de sexta |
| Agendar visita | Manual | Escolha solidária/comunitária + responsável + data → calendário |

**Regras dos trilhos:**
- Trilho VD: FRIDA é **obrigatório** antes de salvar. Não deixa concluir a triagem sem nível registrado (B/M/E).
- Trilho menor: ao marcar, cria automaticamente encaminhamento `situacao = a_encaminhar` para Conselho Tutelar.
- Trilho encaminhamento: múltiplos órgãos permitidos. Cada um vira um registro em `encaminhamento`.
- Trilho visita: tipo solidária se foco é a vítima; comunitária se foco é o território. Gera agendamento direto com `responsavel` e `data`.

**Bloco 3 — Decisão**
- Situação: `em_acompanhamento` (padrão quando qualquer trilho foi ativado) ou `encerrada`.
- Próxima ação + data: campo livre que vira agendamento no calendário.

**Ao salvar:**
- Cada ação vira um item concreto: FRIDA → `atendimento.tipo = frida` agendado; visita → `agendamento` no calendário da guarnição; encaminhamento → `encaminhamento.situacao = a_encaminhar`; próxima ação → `agendamento`.
- Nada sai como flag solta.

---

### 4.3 Atendimento (registrar contato / resultado)

**Objetivo:** fechar o ciclo de um item do calendário — a guarnição realizou, registra o que foi feito.  
**Acesso:** pelo item do calendário ("Realizar") ou pela ficha da vítima ("Novo contato").

**Campos:**
- Data, hora, responsável (preenchido automaticamente pelo usuário logado).
- Tipo (visita solidária, comunitária, contato telefônico, FRIDA, retorno de órgão, ronda escolar).
- Resultado (campo estruturado: realizada / não encontrada / recusou / reagendada).
- Relato (campo livre — o que aconteceu, o que a vítima disse, o que foi observado).
- Próxima ação + data → gera o próximo agendamento automaticamente.

**Casos especiais:**
- Tipo `frida`: abre formulário FRIDA embutido. Nível (B/M/E) é obrigatório. Resultado salvo em `atendimento` + tabela FRIDA.
- Tipo `retorno_orgao`: registra a devolutiva → muda `encaminhamento.situacao = encerrado`.
- Resultado `reagendada`: abre seletor de nova data → cria agendamento substituto.

**Ao salvar:**
- Item do calendário marcado como realizado.
- `atendimento` salvo e aparece na linha do tempo da vítima.
- Se definiu próxima ação → novo agendamento criado.
- Caso VCM com FRIDA nível E → alerta na fila de urgências do Dashboard VCM.

---

### 4.4 Ficha da vítima (histórico + dossiê)

**Objetivo:** visão consolidada de tudo que aconteceu com a vítima.  
**Acesso:** pelo card da vítima em qualquer tela, ou pelo botão "Ver ficha" na triagem/atendimento.

**Estrutura da ficha (de cima para baixo):**

1. **Identidade:** nome, sexo, idade, telefone, endereço, CPF (quando preenchido). Botão editar.
2. **Situação atual:** nível de risco FRIDA mais recente (B/M/E), próxima ação datada, responsável.
3. **Linha do tempo:** todos os `atendimentos` ordenados do mais recente para o mais antigo. Cada item mostra data, tipo, responsável, resultado e relato colapsável.
4. **Ocorrências:** lista de todas as ocorrências vinculadas, com tipo, data e situação.
5. **Encaminhamentos:** lista de todos os encaminhamentos com órgão, situação e devolutiva quando houver.
6. **Próximas ações:** agendamentos futuros desta vítima.

**Botão "Gerar dossiê PDF":**
- Monta um documento formal com: identificação da vítima, histórico de ocorrências, avaliações FRIDA (com níveis), linha do tempo de atendimentos, encaminhamentos e devolutivas.
- Esse dossiê é o artefato que a auxiliar anexa ao envio de sexta para os órgãos.
- Evolução futura: gerar o PDF no servidor via Apps Script (mais confiável que `window.print()`, especialmente no celular).

---

## 5. Calendário — painel operacional da guarnição

### Visão "Dia da guarnição" (entrada padrão para perfil operador)

Ao assumir o serviço, a guarnição abre o calendário e vê a lista do dia, pronta para agir:

- Ordenada por urgência (vencidas primeiro, depois urgentes, depois agendadas).
- Cada item mostra: nome da vítima ou local, endereço, telefone, tipo de visita e objetivo.
- Botão **"Realizar"** abre diretamente a tela de Atendimento (4.3).
- Botão **"Reagendar"** desloca para nova data sem perder o histórico.

### Marcador semanal automático

- Toda sexta-feira: badge na entrada do dia com "N encaminhamentos a enviar".
- A auxiliar clica → abre fila filtrada por `situacao = a_encaminhar`, agrupada por órgão.
- Ela confere, marca "Enviado em lote" → todos mudam para `aguardando_devolutiva` + data de envio registrada.

### Tipos de evento no calendário

| Cor | Tipo |
|---|---|
| Rosa | Visita solidária (vítima VCM/VD) |
| Verde | Visita comunitária (território) |
| Azul | Ronda escolar |
| Âmbar | FRIDA agendado |
| Roxo | Retorno / acompanhamento |
| Cinza | Evento avulso |

---

## 6. Fluxo VCM completo

```
Ocorrência tipo VD/VCM
       ↓
Triagem — trilho VD ligado
       ↓
Aplicar FRIDA (obrigatório, nível B/M/E)
       ↓
Nível define cadência:
  B (baixo)  → contato em 30 dias
  M (médio)  → contato em 15 dias
  E (elevado) → contato em 7 dias / urgente
       ↓
Agendamento automático no calendário
       ↓
Guarnição realiza visita → Atendimento registrado
       ↓
Encaminhamento ao órgão (CRAV, CREAS, MP…)
       ↓
Sexta-feira: auxiliar envia lote → situacao = aguardando_devolutiva
       ↓
Órgão responde → auxiliar registra devolutiva → caso documentado
       ↓
Novo FRIDA se nível mudou / caso encerrado se risco cessou
```

---

## 7. Fluxo de menor

```
Ocorrência com vítima idade < 18
       ↓
Triagem — trilho "menor" pré-marcado
       ↓
Encaminhamento automático: Conselho Tutelar (situacao = a_encaminhar)
       ↓
Entra na fila de sexta junto com os demais
       ↓
Ciclo de devolutiva igual ao fluxo VCM
```

---

## 8. Plano de migração

### Regras

1. **Não alterar dados históricos** (anteriores a abril/2026). Marcar com `fonte = importado` e `situacao = historico`. Eles continuam visíveis nos relatórios e na ficha da vítima, mas não aparecem na fila de triagem.

2. **Criar tabela `vitimas` vazia.** Os registros históricos mantêm os campos `vitima_nome/idade/sexo` soltos como estão. A entidade vítima só é criada quando a ocorrência é acessada na nova triagem.

3. **Registros de abril em diante** já nascem com `vitima_id` obrigatório e entram na fila de triagem com `situacao = nova`.

4. **Migração progressiva do histórico:** quando a auxiliar abre um caso histórico para dar continuidade, o sistema detecta que não tem `vitima_id` e pede vinculação antes de continuar. O enriquecimento acontece naturalmente ao longo das semanas, sem mutirão.

5. **FRIDA sem nível:** os 19 registros com nível `?` devem ser marcados para revisão — aparecem como "FRIDA incompleto" na ficha da vítima com botão "Completar".

### Aba nova no Sheets

Adicionar aba `vitimas` com colunas: `id | nome | sexo | idade | telefone | endereco | cpf | bairro | criadoEm | atualizadoEm`

Adicionar aba `encaminhamentos` com colunas: `id | vitima_id | ocorrencia_id | orgao | situacao | data_envio | data_devolutiva | relato_devolutiva | responsavel | criadoEm`

Aba `atendimentos` — já existe, ajustar schema para incluir `vitima_id` e `tipo` estruturado.

---

## 9. Checklist para o Claude Code

### Fase 1 — Backend (Apps Script)

- [ ] Criar função `salvarVitima(ss, dados)` e `listarVitimas(ss)`
- [ ] Criar função `buscarVitima(ss, nome, sexo, idade)` — retorna candidatas para o campo de busca
- [ ] Criar aba `vitimas` na planilha via `criarTodasAbasNovas()`
- [ ] Criar aba `encaminhamentos` com as colunas do modelo
- [ ] Alterar `salvar(ss, "oc", reg)` para aceitar `vitima_id` e `situacao`
- [ ] Criar função `salvarEncaminhamento(ss, dados)` e `listarEncaminhamentos(ss, vitimaId)`
- [ ] Criar função `atualizarEncaminhamento(ss, id, campos)` — para mudar situação e registrar devolutiva
- [ ] Criar função `listarEncaminhamentosPendentes(ss)` — filtra `situacao = a_encaminhar` para fila de sexta
- [ ] Atualizar `salvarAtendimento` para gravar `vitima_id` e `tipo` estruturado
- [ ] Adicionar rota `acao=buscarVitima` no `doGet`
- [ ] Adicionar rotas `salvar/listar/atualizar` para `vitimas` e `encaminhamentos` no `doGet`
- [ ] Marcar registros anteriores a 2026-04-01 com `fonte=importado` e `situacao=historico` via script de migração one-shot

### Fase 2 — Frontend (index.html)

- [ ] Criar componente `buscaVitima(onSelect)` — input com debounce 300ms, lista de sugestões, opção "nova vítima"
- [ ] Refatorar tela "Lançar ocorrência" para usar `buscaVitima` e incluir campo `relato` (opcional)
- [ ] Criar tela "Triagem" como estado `state.tela = 'triagem'` com `state.triagemOcId`
  - Bloco 1: vítima vinculada com histórico resumido + textarea de relato
  - Bloco 2: quatro interruptores de trilho (VD, menor, encaminhamento, visita)
  - Bloco 3: decisão (situação + próxima ação datada)
  - Validação: trilho VD só salva se FRIDA aplicado com nível
- [ ] Criar tela/modal "Atendimento" unificado — substituir os três atuais
- [ ] Criar tela "Ficha da vítima" com linha do tempo, ocorrências, encaminhamentos e botão "Gerar dossiê PDF"
- [ ] Refatorar `gerarFichaVCMPDF` para usar `vitima_id` em vez de fuzzy match e incluir atendimentos + encaminhamentos
- [ ] Refatorar calendário para adicionar:
  - Visão "Dia da guarnição" como entrada padrão para `perfil = operador`
  - Badge de sexta-feira com contagem de encaminhamentos pendentes
  - Botão "Realizar" em cada item → abre tela de Atendimento pré-preenchida
  - Código de cores por tipo de visita (tabela na seção 5)
- [ ] Criar tela "Fila de encaminhamentos" (acesso pelo calendário na sexta ou pelo menu)
  - Agrupa por órgão
  - Botão "Marcar lote como enviado"
  - Formulário de devolutiva por item
- [ ] Criar fila de triagem: lista de ocorrências com `situacao = nova`, ordenada por data, com botão "Triar"
- [ ] Atualizar `state` inicial para incluir `vitimas: []`, `encaminhamentos: []`
- [ ] Atualizar `_sincSheets` para carregar vitimas e encaminhamentos
- [ ] Adicionar badge na nav: "N para triar" quando houver ocorrências com `situacao = nova`
- [ ] Mostrar "FRIDA incompleto" na ficha da vítima para os 19 registros sem nível

### Fase 3 — Limpeza

- [ ] Remover as três telas de atendimento redundantes (genérica, VCM e Projetos Sociais) após unificação
- [ ] Remover fuzzy match de nomes nos locais que passarem a usar `vitima_id`
- [ ] Limpar os 5 tipos de visita (consolidar em 2 famílias: vítima e território)
- [ ] Revisar/remover `CONCEITO_VISITA` e `COR_VISITA` para refletir novo modelo

---

## 10. O que NÃO muda agora

- Token fixo e PINs hardcoded — endereçar numa auditoria de segurança separada.
- SIGESPOL — extração automática suspensa. Lançamento manual é o fluxo definitivo.
- Módulos: Inventário, Armamento, Escolar, Projetos Sociais, Conselho — auditados em sessão separada.
- Design visual (CSS, cores, tipografia) — refatorar após estabilizar os fluxos.

---

## 11. Próximos módulos a auditar

1. Calendário (detalhar além do que está no módulo de Ocorrências)
2. Dashboard VCM
3. Módulo Escolar + Ronda Escolar
4. Projetos Sociais
5. Armamento / Inventário
6. Segurança (token, PINs, controle de acesso)
7. Design / UX global

---

*Documento gerado em sessão de auditoria com Claude — 11/06/2026*  
*Levar ao Claude Code para execução por fases. Começar pela Fase 1 (backend) antes de qualquer mudança no frontend.*

---

## 12. Módulo de Auditoria do Comandante

### Conceito

Tela sob demanda — o comandante abre quando quer saber se o fluxo está funcionando. Não é painel aberto o dia todo. Cada indicador tem semáforo automático (verde/amarelo/vermelho) e botão "Cobrar" que dispara um Aviso para a auxiliar dentro do próprio IARA.

### Seis indicadores

| Indicador | Vermelho | Amarelo | Verde |
|---|---|---|---|
| Triagem | ocorrências `nova` há > 48h | ocorrências `nova` há 24–48h | todas triadas em < 24h |
| FRIDA | cobertura < 50% ou nível sem registro | cobertura 50–80% | cobertura ≥ 80% e todos com nível |
| Visitas | itens vencidos sem resultado | itens vencendo hoje | tudo em dia |
| Encaminhamentos | fluxo de sexta inativo | devolutivas > 15 dias sem resposta | fluxo ativo e devolutivas em dia |
| Calendário da guarnição | > 30% dos itens do dia sem fechar | 10–30% sem fechar | < 10% sem fechar |
| Lançamentos | campos obrigatórios incompletos | — | 100% completos |

### Mecanismo de cobrança

- Botão "Cobrar auxiliar" na auditoria → cria Aviso com texto automático + prazo de 24h.
- Aviso aparece para a auxiliar com sino piscando ao abrir o IARA.
- Texto do aviso inclui: o que está pendente, a quantidade, e a assinatura "Cmte".
- Após a auxiliar resolver, o indicador volta ao verde automaticamente — sem precisar fechar o aviso manualmente.

### Implementação (Apps Script)

- Reutilizar `salvar(ss, "av", aviso)` já existente — o Aviso é o mecanismo de cobrança.
- Adicionar campo `origem` no aviso: `auditoria_comandante` — para diferenciar de avisos manuais.
- Adicionar campo `indicador` — para a auxiliar saber exatamente o que tratar.

---

## 13. Fluxo corrigido da guarnição

### Como funciona na prática

A guarnição **não acessa o IARA**. O fluxo é:

```
Auxiliar imprime / abre roteiro do dia (calendário)
       ↓
Passa o roteiro para a guarnição de campo
       ↓
Guarnição realiza visitas / ligações / rondas
       ↓
Guarnição manda relatório para a auxiliar
(papel, foto, WhatsApp — qualquer meio)
       ↓
Auxiliar abre o item no calendário do IARA
       ↓
Lança o resultado (atendimento) com o relato recebido
       ↓
Sistema fecha o ciclo: próxima ação gerada automaticamente
```

### Implicações no design

- O calendário é um **roteiro para imprimir / visualizar** — não requer interação da guarnição.
- O botão "Realizar" na tela do calendário é **da auxiliar**, não da guarnição.
- A auxiliar lança atendimentos em lote no fim do dia (ou conforme os relatórios chegam).
- A ligação solidária a auxiliar pode fechar ela mesma — sem depender da guarnição.

---

## 14. Subtipos de agendamento / visita solidária

| Subtipo | Ícone | Quem executa | Como a auxiliar fecha |
|---|---|---|---|
| Ligação solidária | Telefone | Auxiliar liga diretamente | Lança o resultado na hora |
| Visita in loco | Mapa | Guarnição vai ao local | Lança o relato que recebeu |
| Visita comunitária | Pessoas | Guarnição | Lança o relato que recebeu |
| Ronda escolar | Escola | Guarnição | Lança o relato que recebeu |

### Campo "subtipo" no agendamento

Adicionar campo `subtipo` em `agendamentos`:
- `ligacao` — contato remoto
- `in_loco` — presença física
- `comunitaria` — território
- `ronda_escolar` — escola

O tipo principal permanece `Visita Solidária` ou `Visita Comunitária` para manter compatibilidade com os 2.530 agendamentos existentes. O subtipo é refinamento adicional.

---

## 15. Painel da auxiliar — fila de trabalho do dia

### Conceito

Quando a auxiliar abre o IARA, a primeira tela é a **fila do dia** — não o dashboard genérico. Ela organiza o trabalho por prioridade sem precisar de instrução externa.

### Seções da fila (de cima para baixo)

1. **Avisos do comandante** — sino piscando, leitura obrigatória antes de tudo.
2. **Para lançar agora** — relatórios da guarnição que chegaram (itens do calendário de hoje sem resultado).
3. **Para triar** — ocorrências com `situacao = nova` ordenadas por antiguidade e urgência (VD primeiro).
4. **Encaminhamentos desta sexta** — visível só às sextas, com lista por órgão pronta para envio.
5. **FRIDAs incompletos** — avaliações sem nível registrado.

### Checklist para o Claude Code

- [ ] Criar tela `state.tela = 'fila_auxiliar'` como entrada padrão para `perfil = gestor`
- [ ] Seção 1: filtrar avisos com `origem = auditoria_comandante` no topo, depois avisos gerais
- [ ] Seção 2: agendamentos do dia com `status = Agendado` e data = hoje, sem resultado
- [ ] Seção 3: `ocorrencias.situacao = nova` ordenadas — VD sem FRIDA primeiro
- [ ] Seção 4: visível apenas se `diaSemana = 5` (sexta) — encaminhamentos `a_encaminhar`
- [ ] Seção 5: FRIDAs com `nivel = ?` ou nível vazio
- [ ] Botão "Cobrar auxiliar" na auditoria → `salvar(ss, "av", {texto, expira, origem: 'auditoria_comandante', indicador})`

---

## 16. Mecanismo de cobrança — especificação detalhada

### Fluxo em quatro passos

```
Comandante clica "Cobrar auxiliar"
       ↓
Sistema lê dados em tempo real e monta aviso automático
(sem o comandante digitar nada)
       ↓
Aviso salvo na aba Avisos com metadados de auditoria
       ↓
Auxiliar abre o IARA → sino vermelho → aviso em destaque
       ↓
Auxiliar abre a fila → age nas pendências
       ↓
Pendências zeradas → aviso some → semáforo verde na auditoria
```

### Estrutura do aviso gerado

```json
{
  "texto": "18 ocorrências sem triagem há mais de 48h — 4 delas são VD. Priorizar hoje.",
  "origem": "auditoria_comandante",
  "indicador": "triagem",
  "autor": "Cmte",
  "expira": "2026-06-11T18:00",
  "prioridade": "alta"
}
```

O texto é gerado automaticamente a partir dos dados reais — o comandante não digita nada.  
O prazo padrão é o fim do dia corrente (18h).

### Textos automáticos por indicador

| Indicador | Texto gerado |
|---|---|
| triagem | "N ocorrências sem triagem há mais de Xh — Y delas são VD. Priorizar hoje." |
| frida | "N casos VD sem FRIDA aplicado. Y avaliações sem nível registrado. Completar hoje." |
| visitas | "N visitas com data passada sem resultado registrado. Lançar os relatórios da guarnição." |
| encaminhamentos | "Fluxo de encaminhamentos inativo. Abrir fila e enviar lote desta semana." |

### Comportamento na tela da auxiliar

- Sino com badge vermelho visível em qualquer tela do IARA.
- Avisos com `origem = auditoria_comandante` aparecem **no topo**, antes dos avisos gerais.
- Ícone de triângulo vermelho diferencia visualmente do aviso azul de informação.
- Dois botões: **"Abrir fila"** (atalho direto para a pendência) e **"Marcar lida"** (reconhece sem agir).
- Prazo visível com ícone de relógio.

### Fechamento automático do ciclo

- O aviso **não precisa ser fechado manualmente**.
- O sistema verifica a cada carregamento: se o indicador voltou ao verde → aviso marcado como resolvido automaticamente.
- Comandante vê o verde na próxima abertura da auditoria, sem precisar de confirmação da auxiliar.

### Checklist para o Claude Code

- [ ] Adicionar campo `origem` na aba Avisos: `manual | auditoria_comandante`
- [ ] Adicionar campo `indicador` na aba Avisos: `triagem | frida | visitas | encaminhamentos`
- [ ] Adicionar campo `prioridade` na aba Avisos: `normal | alta`
- [ ] Criar função `cobrarAuxiliar(indicador, dados)` que monta e salva o aviso automaticamente
- [ ] Botão "Cobrar auxiliar" na auditoria chama `cobrarAuxiliar` com os dados do indicador atual
- [ ] Na tela de avisos: filtrar `origem = auditoria_comandante` para o topo
- [ ] Lógica de fechamento automático: ao carregar avisos, verificar se indicador voltou ao verde → marcar `resolvido = true`
- [ ] Badge do sino: contar apenas avisos não lidos e não resolvidos


---

## 17. Banco de dados — decisão arquitetural

### Decisão: manter Google Sheets + Apps Script

O sistema permanece com Sheets como banco de dados. Motivações:

- Sistema já em operação com dados reais — zero risco de migração.
- Volume atual (765 ocorrências, 2.530 agendamentos) dentro do limite confortável.
- Você visualiza e audita os dados diretamente na planilha.
- Custo zero.

**Revisão futura:** quando o sistema expandir para outras bases ou o número de usuários simultâneos aumentar, avaliar migração para Firebase Firestore (sincronização em tempo real nativa, ainda gratuito, ainda Google). A planilha pode continuar como espelho de leitura via exportação periódica.

---

## 18. Sincronização — correção do problema atual

### Problema

O IARA usa duas camadas que nem sempre conversam:

- **localStorage** — dados locais do navegador de cada usuário. Rápido, mas isolado.
- **Google Sheets** — banco real compartilhado. Atualizado só quando alguém recarrega a página ou força sincronização manual.

Resultado: a auxiliar lança um dado → vai para o Sheets → mas o comandante ainda vê a versão antiga do localStorage até recarregar manualmente.

### Solução — três mudanças cirúrgicas

**1. Polling automático a cada 2 minutos**

```javascript
// Adicionar após o carregamento inicial
setInterval(async () => {
  await sincronizarDoSheets(); // já existe: _sincSheets()
  render(); // re-renderiza com dados frescos
}, 2 * 60 * 1000);
```

Silencioso — não interrompe o uso. Se houver dados novos, a tela atualiza automaticamente.

**2. Busca fresca ao abrir telas críticas**

Nas funções `renderTelaAuditoria()`, `renderDashboard()` e `renderDashVCM()`, forçar busca do Sheets antes de renderizar os números:

```javascript
async function renderTelaAuditoria() {
  await _sincSheets(); // garante dados atuais
  // ... renderização normal
}
```

O comandante sempre vê o estado real ao abrir a auditoria — sem precisar recarregar.

**3. Indicador visual de sincronização**

Badge discreto no canto da tela mostrando "Atualizado às HH:MM". O usuário sabe quando os dados foram puxados pela última vez. Se o Sheets estiver inacessível (sem internet), aparece "Dados locais — reconectando…".

### Checklist para o Claude Code

- [ ] Adicionar `setInterval(_sincSheets, 120000)` após o carregamento inicial
- [ ] Chamar `await _sincSheets()` no início de `renderTelaAuditoria()`, `renderDashboard()` e `renderDashVCM()`
- [ ] Salvar `state.ultimaSinc = new Date()` após cada sincronização bem-sucedida
- [ ] Exibir badge "Atualizado às HH:MM" no rodapé ou canto superior
- [ ] Exibir "Dados locais" quando `_sincSheets()` falhar (sem internet / Sheets indisponível)
- [ ] Garantir que o polling não dispara nova requisição se uma já estiver em andamento (`state.sincronizando = true/false`)

### Limitação conhecida

O polling resolve o problema de defasagem mas não é instantâneo — há até 2 minutos de atraso. Para o fluxo do IARA (auxiliar lança, comandante verifica periodicamente) isso é suficiente. Sincronização instantânea real só com Firebase — decisão adiada conforme seção 17.


---

## 19. Design e UX — auditoria pendente

### Decisão: design depois dos fluxos

O redesign visual será executado **após** a estabilização do módulo de Ocorrências e dos módulos dependentes (Calendário, VCM, Escolar). Motivo: o `index.html` tem CSS inline misturado com lógica em 20 mil linhas — mexer no visual antes de estabilizar os fluxos gera retrabalho duplo.

### Problemas identificados — para tratar na auditoria de design

**1. Hierarquia visual ausente**
Tudo tem o mesmo peso — títulos, labels, valores, botões primários e secundários competem entre si. O olho não sabe onde ir primeiro. Impacto real: a auxiliar demora mais para encontrar a ação correta em cada tela.

**2. Feedback de estado inexistente ou inconsistente**
O usuário não sabe se o dado foi salvo, se está carregando dados do Sheets, ou se ocorreu um erro silencioso. Em alguns módulos há um toast de confirmação; em outros, nada. Isso gera insegurança — a auxiliar fica em dúvida se precisa salvar de novo.

**3. Mobile irregular**
Algumas telas quebram em telas pequenas. A guarnição e o comandante provavelmente acessam pelo celular — o sistema precisa funcionar bem em viewport de 390px. Telas críticas (calendário do dia, auditoria, avisos) devem ter prioridade no ajuste mobile.

**4. Tema claro/escuro inconsistente**
Nem todos os módulos respeitam o tema selecionado. Alguns elementos ficam ilegíveis no modo escuro.

**5. Estados vazios sem orientação**
Quando uma lista está vazia (nenhuma ocorrência, nenhum agendamento), a tela mostra em branco sem explicar o motivo ou o que fazer. Um estado vazio bem desenhado orienta ("Nenhuma ocorrência nova — tudo triado ✓" vs. silêncio).

**6. Formulários longos sem divisão visual**
O formulário de lançamento e a triagem têm muitos campos em sequência sem agrupamento claro. Os blocos que desenhamos (vítima, classificação, decisão) precisam ter separação visual real — não só um `<hr>`.

### O que NÃO muda no redesign

- Paleta de cores base — o sistema já tem variáveis CSS (`--color-*`) bem definidas. A paleta é ajustada, não substituída.
- Estrutura de navegação — menu lateral permanece. Só reorganização dos itens conforme módulos novos.
- Identidade — IARA continua sendo IARA. Não é rebranding.

### Prioridade dos ajustes quando chegar a hora

| Prioridade | Ajuste |
|---|---|
| Alta | Feedback de estado (salvo / carregando / erro) |
| Alta | Mobile das telas críticas (calendário, auditoria, avisos) |
| Média | Hierarquia visual — peso dos elementos |
| Média | Estados vazios com orientação |
| Baixa | Tema escuro consistente |
| Baixa | Formulários com agrupamento visual |

---

## 20. Processo de deploy — o que o Claude Code não faz sozinho

### Apps Script

O Claude Code edita o `app_script.txt` local, mas **não publica no Google**. O processo manual após cada alteração no backend:

1. Code edita e confirma o `app_script.txt`
2. Você copia o conteúdo
3. Cola no editor do Google Apps Script (script.google.com)
4. Clica em **Implantar → Gerenciar implantações → Nova versão**
5. Confirma a nova versão do Web App

### Frontend (index.html)

O Code edita o `index.html` local. O deploy é automático via GitHub Pages:

1. Code edita e confirma o `index.html`
2. Você faz `git add . && git commit -m "descrição" && git push`
3. GitHub Pages publica automaticamente em alguns segundos

### Recomendação antes de começar

Criar uma branch de desenvolvimento antes de implementar as fases:

```bash
git checkout -b desenvolvimento
```

Implementar e testar nessa branch. Só fazer merge para `main` (que está no ar) quando cada fase estiver validada. Assim o sistema em produção nunca quebra durante a implementação.


---

## 21. Estado real dos dados — revisão do diagnóstico

### O que a planilha realmente mostra

Análise feita em 11/06/2026 sobre as 764 ocorrências:

| Indicador | Valor |
|---|---|
| Total de ocorrências | 764 |
| Com nome de vítima preenchido | 71 (9%) |
| Com relato preenchido | 0 (0%) |
| Marcadas como VD | 165 (22%) |
| Registros com colunas misturadas | Sim — coluna "Bairro" contém datas em vários registros |
| IDs com prefixo `zap_` | Origem WhatsApp |
| IDs com prefixo `pl_` | Origem planilha/importação |

### Revisão da fronteira "histórico x manual"

A fronteira "até março = histórico / abril = manual" **não existe na prática**. Todos os 764 registros foram lançados em 2026 mas vieram de importações com qualidade variada. Não há dois grupos distintos — há um único grupo com dados incompletos em graus diferentes.

### Tratamento unificado

Todas as 764 ocorrências entram com `situacao = nova`. A fila de triagem as organiza por urgência:
1. VD sem FRIDA — primeiro
2. Com nome de vítima — mais fácil de vincular
3. Sem nome — aviso "vítima não identificada, preencher na triagem"

A auxiliar tria por ordem de urgência, sem pressão de resolver tudo de uma vez.

### Prioridade zero para o Claude Code — limpeza de dados

Antes de qualquer implementação de novas funcionalidades, executar script de diagnóstico e limpeza:

- [ ] Identificar todos os registros onde "Bairro" contém data (sinal de colunas misturadas na importação)
- [ ] Mapear quais colunas foram trocadas em cada prefixo de ID (`zap_` vs `pl_`)
- [ ] Corrigir o mapeamento de colunas nesses registros
- [ ] Gerar relatório de quantos registros foram corrigidos vs. quantos precisam de revisão manual
- [ ] **Não alterar** os dados sem backup — fazer `git commit` antes de qualquer limpeza

### Como a vinculação de vítima acontece nos registros existentes

- Registros com nome preenchido (71): sistema sugere automaticamente ao abrir a triagem
- Registros sem nome (693): campo de busca aparece vazio com aviso "vítima não identificada — preencher na triagem"
- A auxiliar preenche conforme consulta o BO físico ou o sistema de origem
- Enriquecimento progressivo — não é mutirão


---

## 22. Devolutiva dos órgãos externos — especificação completa

### Conceito

Quando a 77ª CIPM encaminha um caso a um órgão parceiro (CRAV, CREAS, MP, Conselho Tutelar…), o profissional externo recebe junto com o ofício um **link único de formulário**. Ele preenche o resultado do atendimento diretamente nesse link — sem precisar de login no IARA. O sistema recebe automaticamente e a devolutiva aparece na ficha da vítima.

### Segurança do link

- Link contém o ID do encaminhamento, não o nome da vítima na URL
- Nome da vítima é exibido **dentro** do formulário (o profissional precisa para identificar o caso)
- Link expira em **30 dias** após o envio
- Link é de **uso único** — após o envio, exibe "Este formulário já foi respondido"
- Se o link expirar sem resposta → auxiliar gera novo link pelo painel de devolutivas

### Campos do formulário externo

| Campo | Obrigatório | Tipo |
|---|---|---|
| Resultado | Sim | Seleção: Atendida / Em andamento / Não localizada / Recusou |
| Relato do atendimento | Sim | Texto livre |
| Próximos passos | Não | Texto livre |
| Nome e função do responsável | Não | Texto livre |

### O que aparece no formulário (visível para o profissional externo)

- Nome da vítima
- Tipo do caso (ex.: Maria da Penha)
- Órgão destinatário
- Data do encaminhamento e origem (77ª CIPM)
- Prazo de validade do link

### Fluxo técnico (Apps Script)

```
Auxiliar marca encaminhamento na triagem
       ↓
Sistema gera token único: enc_{id}_{orgao}_{timestamp}
Salva token + expira_em na aba encaminhamentos
       ↓
Link gerado: [URL_WEBAPP]?page=devolutiva&token={token}
       ↓
Auxiliar envia link junto com o ofício/email ao órgão
       ↓
Profissional abre o link → doGet verifica token (válido e não usado)
→ Exibe formulário com dados do caso
       ↓
Profissional preenche e envia → doPost grava devolutiva
→ Marca token como usado
→ Atualiza encaminhamento: situacao = encerrado, data_devolutiva, relato_devolutiva
       ↓
Auxiliar abre painel de devolutivas → vê card verde "novo"
→ Clica "Registrar na ficha" → devolutiva aparece na linha do tempo da vítima
```

### Painel de devolutivas da auxiliar

Tela acessível pelo menu principal. Três abas:

| Aba | Conteúdo |
|---|---|
| Aguardando | Encaminhamentos enviados sem resposta, ordenados por tempo de espera. Badge âmbar após 7 dias. |
| Recebidas | Devolutivas chegadas. Card em destaque verde com botão "Registrar na ficha". |
| Vencidas | Sem resposta há mais de 15 dias. Botão "Reenviar link" gera novo token e reenvia. |

### Integração com auditoria do Comandante

- Encaminhamentos vencidos (> 15 dias sem resposta) → semáforo amarelo no indicador "Encaminhamentos"
- Fluxo inativo (nenhum enviado na semana) → semáforo vermelho

### Checklist para o Claude Code

- [ ] Adicionar campo `token` e `token_expira` na aba `encaminhamentos`
- [ ] Adicionar campo `token_usado` (boolean) na aba `encaminhamentos`
- [ ] Criar função `gerarTokenEncaminhamento(encId, orgao)` — gera token único + define expiração em 30 dias
- [ ] Criar rota `page=devolutiva&token={token}` no `doGet` — renderiza formulário HTML externo
- [ ] Formulário externo: HTML simples sem autenticação, responsivo, com nome da vítima visível
- [ ] Criar rota `doPost` para receber devolutiva → validar token → gravar → marcar usado
- [ ] Criar tela `state.tela = 'devolutivas'` com três abas (aguardando / recebidas / vencidas)
- [ ] Badge "N novo" na nav quando houver devolutivas não registradas na ficha
- [ ] Botão "Registrar na ficha" → atualiza linha do tempo da vítima + fecha encaminhamento
- [ ] Botão "Reenviar link" → gera novo token + exibe link para copiar/enviar
- [ ] Integrar vencidos (> 15 dias) no indicador de encaminhamentos da auditoria do Comandante

---

## 23. Estratégia de implementação — virada única no final do mês

### Decisão

Todas as mudanças sobem de uma vez, no final de junho/2026. Motivos:

- Evita período de "meio a meio" onde a auxiliar não sabe qual tela usar
- Treinamento acontece uma única vez, com o manual em mãos
- Dados ficam consistentes desde o início — sem registros com `vitima_id` e sem ele misturados
- Sistema em produção não é afetado durante o desenvolvimento

### Cronograma

| Período | O que acontece |
|---|---|
| Agora | Branch `desenvolvimento` criada no GitHub |
| Até ~20/jun | Claude Code implementa na branch: limpeza → backend → frontend |
| 20–28/jun | Testes locais — você e a auxiliar verificam tudo |
| Final de junho | Merge para `main` → virada para produção |

### Ambiente de teste

- **Frontend:** Claude Code sobe servidor local (`python3 -m http.server 8080`) — acesso em `http://localhost:8080`
- **Backend:** Apps Script de teste separado, apontando para abas de teste na planilha — dados reais não são tocados
- **Na virada:** script definitivo publicado, URL atualizada no `index.html`, merge para `main`

### Como criar a branch pelo GitHub (passo a passo)

1. Acessar github.com/oseiasvarges-lgtm/bcs-vigilia
2. Clicar no botão `main` (seletor de branches, canto superior esquerdo)
3. Digitar `desenvolvimento` no campo
4. Clicar em "Create branch: desenvolvimento from main"

### O que dizer ao Claude Code para começar

> "Leia o AUDITORIA_IARA.md na raiz do projeto. Mude para a branch desenvolvimento. Siga esta ordem: (1) seção 21 — limpeza de dados, com relatório antes de alterar qualquer coisa; (2) seção 18 — sincronização; (3) Fase 1 da seção 9 — backend Apps Script, usando script de teste separado; (4) Fase 2 — frontend completo. Sobe servidor local em http://localhost:8080 para eu testar. Confirme cada fase antes de avançar."


---

## 24. Design — Padrão Visual "Pergaminho e Madeira"

### Decisão

O IARA adota o padrão visual "pergaminho e madeira" — fundo creme, moldura escura, destaques âmbar dourado, tipografia serifada. Identidade forte, ar de documento oficial, confortável para leitura longa. Aplicar na Fase 2 (frontend), já construindo as telas novas nesse visual.

### Paleta de cores

```css
:root {
  --madeira:       #3E2A1A;  /* fundo da moldura, sidebar, titlebar */
  --madeira-2:     #5A3D26;  /* bordas internas, separadores */
  --madeira-3:     #2E1F12;  /* fundo externo da app */
  --papel:         #F2E4C8;  /* fundo do conteúdo principal */
  --papel-2:       #EAD9B8;  /* painéis, trilhos, cards */
  --papel-3:       #DBC79E;  /* bordas de inputs, chips inativos */
  --tinta:         #3D2B1A;  /* texto principal */
  --tinta-2:       #6B5236;  /* texto secundário, labels */
  --ambar:         #D9A53C;  /* ativo, selecionado, botão primário */
  --ambar-2:       #A87B22;  /* bordas âmbar, hover */
  --ambar-claro:   #EFDFC0;  /* texto sobre fundo escuro */
  --verde:         #6E8F52;  /* visita solidária selecionada */
  --verde-2:       #4F6B38;  /* borda verde */
  --verm:          #A8492E;  /* VD, urgente, badge de perigo */
  --verm-2:        #7E351F;  /* texto sobre fundo vermelho */
}
```

### Tipografia

- **Família:** Georgia, 'Times New Roman', serif
- **Títulos de seção:** 13–14px · 700 · CAIXA ALTA · letter-spacing 1.2px
- **Corpo:** 13–14px · 400 · normal
- **Labels:** 10.5–11px · 700 · CAIXA ALTA · letter-spacing 0.6px · cor --tinta-2
- **Breadcrumb:** 12.5px · itálico · cor --tinta-2

### Layout desktop (padrão)

```
┌─────────────────────────────────────────────────┐
│  TITLEBAR — madeira escura · título · sino · user│
├──────────────┬──────────────────────────────────┤
│   SIDEBAR    │   CONTEÚDO                        │
│   230px      │   fundo papel                     │
│   madeira    │                                   │
│   nav items  │   breadcrumb                      │
│   com badges │                                   │
│              │   [fila 330px] [tela principal]   │
└──────────────┴──────────────────────────────────┘
```

- Sidebar: 230px fixo, fundo gradiente madeira, nav items com borda esquerda âmbar quando ativo
- Titlebar: gradiente madeira, borda inferior 3px âmbar, título em caixa alta
- Conteúdo: fundo --papel, padding 22px 28px
- Telas com fila (triagem, devolutivas): duas colunas — 330px fila + 1fr conteúdo

### Componentes

**Seção numerada:**
```
● número (círculo escuro 24px) + TÍTULO EM CAIXA ALTA sublinhado
```

**Painel (card de informação):**
```
background: --papel-2
border: 1.5px solid --papel-3
border-radius: 6px
box-shadow: inset 0 1px 0 rgba(255,255,255,.45)
```

**Trilho de ação:**
- Inativo: igual ao painel, opacity 0.55
- Ativo: border-color --ambar-2, background #F0DFB5, box-shadow âmbar

**Toggle (interruptor):**
- Ligado: background --ambar, bolinha à direita
- Desligado: background --papel-3, bolinha à esquerda

**Chip (seleção):**
- Normal: background #F8EFDC, border --papel-3, cor --tinta-2
- Selecionado: background --ambar, border --ambar-2, cor escura, bold
- Verde (visita solidária): background --verde, cor --ambar-claro

**Botão primário:**
```
background: linear-gradient(180deg, #E3B453, #C9962F)
border: 1.5px solid --ambar-2
box-shadow: inset 0 1px 0 rgba(255,255,255,.5)
```

**Badge de pendência:**
- Urgente/VD: background --verm, cor clara
- Atenção: background --ambar, cor escura

**Input:**
```
background: #F8EFDC
border: 1.5px solid --papel-3
box-shadow: inset 0 1px 3px rgba(61,43,26,.13)
font-family: Georgia, serif
```

**Alerta dashed:**
```
border: 1.5px dashed --verm
background: #EDD6C8
color: --verm-2
```

### Acessibilidade — cuidados

- Texto principal (--tinta sobre --papel): contraste 9.8:1 ✅
- Âmbar sobre escuro (--ambar-claro sobre --madeira): contraste 7.2:1 ✅
- Chip âmbar ativo (texto escuro sobre âmbar): verificar — usar #2E2010 sobre --ambar para garantir 4.5:1
- Não usar âmbar sobre papel para textos longos — só para destaques pequenos (chips, badges)

### Arquivos de referência

- `mockup_desktop_pergaminho.html` — layout desktop completo (sidebar + fila + triagem)
- `mockup_estilo_pergaminho.html` — versão estreita (referência de componentes)

---

## 25. FRIDA — correção do fluxo no trilho VD

### Como funciona de verdade

O nível do FRIDA **não é escolhido pela auxiliar**. É calculado automaticamente pelo sistema a partir de um questionário de 21 perguntas respondidas pela vítima.

### O questionário

21 perguntas sobre situação da vítima e comportamento do agressor. Exemplos:
- "A violência vem aumentando de gravidade e/ou frequência no último mês?"
- "O agressor já tentou estrangular, sufocar ou afogar a vítima?"
- "O agressor já fez ameaças de morte ou tentou matar a vítima?"
- "O agressor já descumpriu medida protetiva de afastamento?"
- "A vítima se separou recentemente, tentou ou tem intenção de se separar?"

Cada resposta: **Sim / Não / Não sabe ou não se aplica**

### Cálculo do nível

O sistema conta os "Sim" e os "Não sabe" e cruza numa matriz interna:
- Poucos "Sim" (0–2) → **B (Baixo)**
- "Sim" intermediários → **M (Médio)**
- 8 ou mais "Sim" → **E (Elevado)** quase sempre

A auxiliar não interfere no resultado — ela coleta as respostas honestamente. Isso protege a vítima (o risco não depende de julgamento subjetivo) e protege a auxiliar (não carrega a responsabilidade sozinha).

### Como o FRIDA entra na triagem (correto)

O trilho VD **não mostra chips B/M/E para escolha**. Mostra o botão **"Aplicar FRIDA"** que abre o questionário completo. Ao responder todas as 21 perguntas, o sistema calcula e exibe o nível — que aparece na triagem como resultado, não como campo editável.

```
Trilho VD ligado
       ↓
Botão "Aplicar FRIDA" → abre questionário 21 perguntas
       ↓
Auxiliar entrevista a vítima (por telefone, presencial
ou com base no relato da guarnição) e marca as respostas
       ↓
Sistema calcula: N respostas Sim + M Não sabe → nível B/M/E
       ↓
Nível exibido na triagem como resultado (não editável)
       ↓
Triagem só pode ser salva com FRIDA completo (21 respostas)
```

### Por que os 19 FRIDAs estão sem nível

Questionários começados e não terminados, ou registros antigos onde as respostas não foram salvas. A correção é: validar que todas as 21 perguntas foram respondidas antes de permitir o cálculo — e não deixar salvar a triagem sem o FRIDA completo quando o trilho VD está ligado.

### Checklist para o Claude Code

- [ ] Trilho VD na triagem: remover chips B/M/E de seleção manual
- [ ] Adicionar botão "Aplicar FRIDA" que abre o questionário embutido (já existe como `FRIDA_PERGUNTAS` no código)
- [ ] Validar que todas as 21 perguntas foram respondidas antes de calcular
- [ ] Exibir o nível calculado como resultado somente leitura (badge colorido, não editável)
- [ ] Não permitir salvar triagem com trilho VD ligado sem FRIDA completo
- [ ] Para os 19 registros sem nível: marcar como "FRIDA incompleto" na ficha da vítima com botão "Completar"


---

## 26. Módulo Calendário — diagnóstico e redesign

### Diagnóstico — problema de sincronização

O calendário usa duas camadas que não conversam direito:
- **localStorage** — cópia local de cada aparelho (celular e desktop têm cópias independentes)
- **Sheets (`bcs_eventos_avulsos`)** — banco compartilhado, deveria ser a fonte da verdade

**Três causas do problema:**

| Causa | Efeito |
|---|---|
| Merge só adiciona novos — nunca substitui o local pelo remoto | Evento editado num aparelho não atualiza no outro |
| Eventos avulsos não têm campo `_editadoEm` | Sem como saber qual versão é mais recente |
| `_deletedEvIds` é Set em memória — não persiste entre sessões | Evento deletado "volta dos mortos" na próxima sincronização |

### Correções — checklist para o Claude Code

- [ ] Adicionar campo `_editadoEm` (timestamp ISO) em todos os eventos avulsos ao criar/editar
- [ ] Na sincronização: se Sheets tem versão mais recente do mesmo ID (`_editadoEm` maior) → versão remota vence
- [ ] Persistir `_deletedEvIds` no localStorage (`bcs_deleted_ev_ids`) — carregar ao iniciar
- [ ] Forçar busca fresca ao abrir a tela do calendário (igual ao que já está na seção 18 para auditoria e dashboard)
- [ ] Exibir badge de sincronização discreto em cada evento: "✓ sincronizado · criado em [aparelho] · [data]"
- [ ] Badge "✓ Atualizado às HH:MM" no cabeçalho do calendário

### Design — padrão pergaminho aplicado

**Arquivo de referência:** `mockup_calendario_pergaminho.html`

**Estrutura da tela (desktop):**
```
Cabeçalho: mês + nav + botão Hoje + badge sincronização + botão + Evento
Grade mensal (2/3 da largura) | Painel do dia (1/3 — 320px)
Legenda de cores abaixo da grade
Bloco âmbar "Próxima sexta" abaixo do painel
```

**Código de cores dos eventos (adaptado para creme):**

```css
--c-vcm:        #A8492E;  /* Visita solidária VCM / VD */
--c-solidaria:  #8B4513;  /* Visita solidária / ligação */
--c-comunitaria:#5A7A3A;  /* Visita comunitária */
--c-escolar:    #2A5A8A;  /* Ronda / visita escolar */
--c-avulso:     #6A4A8A;  /* Evento avulso */
--c-realizada:  #3A7A5A;  /* Visita realizada ✓ */
--c-frida:      #A8492E;  /* FRIDA urgente nível E — borda vermelha no topo do dia */
```

**Comportamento visual por prioridade:**
- Dia com FRIDA nível E → borda vermelha no topo da célula (`border-top: 3px solid var(--verm)`)
- Dia de hoje → borda âmbar no topo + número âmbar
- Dia selecionado → fundo levemente dourado + borda tinta escura
- Sextas-feiras → fundo #EEE3C0 + número âmbar + contador "📤 N" no canto inferior direito

**Painel do dia (coluna direita):**
- Cabeçalho madeira escura com data e botão "+ Evento neste dia"
- Cada evento: borda esquerda colorida por tipo + tipo em caixa alta + hora + nome + endereço + responsável + status (Agendado / Concluída) + badge de sincronização
- Rodapé: "N eventos · N realizados · N pendentes"
- Bloco âmbar abaixo do painel mostrando próxima sexta com resumo por órgão

**Legenda:**
- Grade 2 colunas abaixo da grade mensal
- 8 itens com quadrado colorido + descrição

### Checklist de implementação — Claude Code

- [ ] Refatorar `renderCalendar()` para aplicar paleta pergaminho
- [ ] Sextas-feiras: fundo #EEE3C0 + contador de encaminhamentos `a_encaminhar` no canto
- [ ] Dias com FRIDA nível E: `border-top: 3px solid var(--verm)`
- [ ] Painel do dia: abrir ao clicar, mostrar eventos com badge de sincronização
- [ ] Consolidar `COR_VISITA` para as 2 famílias (vítima / território) + subtipos
- [ ] Bloco âmbar "Próxima sexta" com contagem por órgão
- [ ] Badge "✓ Atualizado às HH:MM" no cabeçalho
- [ ] Estado vazio orientado: "Nenhum evento neste dia — tudo em dia ✓"


---

## 27. Módulo Gestão e Planejamento

### Nome e posicionamento

- **Nome do módulo:** Gestão e Planejamento
- **Menu lateral:** Gestão › 📁 Gestão e Planejamento
- **Subtítulo da tela:** Operações, capacitações e metas institucionais · 77ª CIPM
- **Substituí:** "Projetos da Base" (nome anterior rejeitado)

### Diagnóstico do estado atual

- Aba `projetos_gestor` na planilha tem **0 registros** — módulo nunca foi realmente usado
- O módulo de projetos existente no código tem Kanban, mas sem entregas como agrupador — tarefas ficam soltas
- Sem campo de prioridade
- Sem histórico de resultado ao concluir

### Modelo de dados

```javascript
projeto {
  id              string    PK
  nome            string    obrigatório
  tipo            string    Operação | Capacitação | Comunitário
                            | Meta Institucional | Administrativo | Outro
  prioridade      string    Critica | Alta | Media | Baixa  // NOVO
  status          string    Planejamento | Em Andamento | Crítico | Concluído | Cancelado
  responsavel     string
  dataInicio      date
  dataFim         date      obrigatório
  objetivo        string
  resultado       string    preenchido ao concluir
  entregas        Entrega[] // NOVO — agrupador de tarefas
  criadoEm        datetime
  _editadoEm      datetime
}

entrega {
  id              string    PK
  nome            string
  prazo           date
  status          string    Não iniciada | Em Andamento | Concluída
  tarefas         Tarefa[]
}

tarefa {
  id              string    PK
  nome            string
  responsavel     string
  prazo           date
  prioridade      string    Critica | Alta | Media | Baixa
  status          string    A Fazer | Em Andamento | Concluída
  observacao      string
}
```

### Três visões da tela

**Grade** — visão panorâmica. Cards com borda esquerda colorida por status, barra de progresso, prioridade, prazo e responsável. Card "+ Novo projeto" no último slot. Padrão ao abrir a tela.

**Kanban** — visão de fluxo. Colunas: Planejamento / Em Andamento / Crítico / Concluído. Útil para mover projetos entre fases visualmente.

**Lista** — visão de comparação. Tabela com: projeto, tipo, responsável, prazo, prioridade, status. Ordenada automaticamente por criticidade. Ideal para revisão rápida em reunião.

Alternância entre visões pelo toolbar: `⊞ Grade · 🗂 Kanban · ≡ Lista`

### Campo Prioridade

| Valor | Cor | Quando usar |
|---|---|---|
| Crítica | Vermelho | Prazo vencendo ou meta em risco |
| Alta | Laranja | Impacto alto, precisa de atenção |
| Média | Azul | Andamento normal |
| Baixa | Verde | Pode aguardar |

Filtros rápidos no toolbar por prioridade e por tipo.

### Detalhe do projeto

Ao abrir um projeto, mostra:
- Cabeçalho: nome, tipo, prioridade, status, responsável, prazo, progresso geral
- Botões: + Entrega, + Tarefa, Gerar PDF, Planejar com IA
- Entregas em sequência, cada uma com barra de progresso própria
- Tarefas dentro de cada entrega com responsável, prazo e status
- Tarefa atrasada: fundo vermelho claro — destaque imediato
- Entrega não iniciada: opacidade reduzida — não polui o foco

### Status automático "Crítico"

O sistema marca automaticamente `status = Crítico` quando:
- Há tarefas com prazo vencido (`status != Concluída` e `prazo < hoje`)
- O projeto tem `dataFim` nos próximos 7 dias e progresso < 70%

Badge "N tarefas atrasadas" aparece no card da grade.

### Planejar com IA — integração Claude

**Botão "✦ Planejar com IA"** ao lado de "+ Novo" na tela principal.

Ao clicar, abre painel de chat lateral (380px) com o Assistente de Planejamento. O comandante descreve o projeto em linguagem natural — digitando ou por voz. O Claude estrutura em tempo real e mostra o preview completo antes de confirmar.

**Fluxo:**
```
Comandante clica "Planejar com IA"
       ↓
Painel de chat abre à direita
       ↓
Comandante descreve o projeto (voz ou texto)
       ↓
Claude estrutura: nome, tipo, prioridade, entregas, tarefas, prazos
       ↓
Preview aparece no chat para revisão
       ↓
"Criar projeto no IARA" → salva diretamente
ou "Ajustar" → continua conversando
       ↓
Projeto aparece na grade com destaque roxo
pulsando até ser confirmado
```

**Implementação técnica:**
- Reutilizar a infraestrutura do "Assistente IA" já existente no código
- System prompt especializado com o schema JSON do módulo
- Ao confirmar: Claude retorna JSON → `salvarProjeto()` grava na planilha
- O projeto fica com `origem: 'assistente_ia'` para rastreabilidade

**System prompt do assistente de planejamento (adicionar ao código):**
```
Você é o Assistente de Planejamento do IARA, sistema da 77ª CIPM.
Quando o usuário descrever um projeto, estruture no formato JSON
do IARA com: nome, tipo, prioridade, status, responsavel, dataInicio,
dataFim, objetivo, e um array de entregas com tarefas dentro.
Mostre o preview em linguagem natural antes de gerar o JSON.
Tipos válidos: Operação, Capacitação, Comunitário, Meta Institucional,
Administrativo, Outro.
Prioridades: Critica, Alta, Media, Baixa.
Status de tarefa: A Fazer, Em Andamento, Concluída.
```

### Importação via JSON (alternativa)

Para projetos planejados fora do IARA (ex.: neste projeto Claude):
- Botão "Importar JSON" na tela de projetos
- Aceita o arquivo `.json` gerado pelo Claude
- Monta o projeto completo com todas as entregas e tarefas
- Compatível com o schema acima

### Arquivos de referência

- `mockup_projetos_visoes.html` — três visões (grade, kanban, lista) com campo prioridade
- `mockup_planejar_com_ia.html` — painel "Planejar com IA" integrado
- `projeto_comunidade_viva.json` — exemplo de JSON gerado pelo Claude

### Checklist para o Claude Code

**Backend (Apps Script):**
- [ ] Adicionar campo `prioridade` na aba `projetos_gestor`
- [ ] Adicionar campo `entregas` (JSON array) na estrutura do projeto
- [ ] Adicionar campo `origem` (manual | assistente_ia | importacao_json)
- [ ] Criar função `salvarProjeto(ss, dados)` com suporte a entregas e tarefas
- [ ] Lógica de status automático "Crítico" baseada em tarefas vencidas

**Frontend:**
- [ ] Renomear módulo: "Projetos da Base" → "Gestão e Planejamento"
- [ ] Atualizar menu lateral com novo nome
- [ ] Implementar três visões: Grade / Kanban / Lista com toolbar de alternância
- [ ] Filtros rápidos por prioridade e tipo
- [ ] Cards com campo prioridade + barra de progresso + badge "N atrasadas"
- [ ] Detalhe do projeto com entregas agrupando tarefas
- [ ] Destaque visual: tarefa atrasada (fundo vermelho), entrega não iniciada (opacidade)
- [ ] Botão "✦ Planejar com IA" → painel de chat lateral
- [ ] System prompt especializado para planejamento de projetos
- [ ] Preview do projeto no chat antes de confirmar
- [ ] Botão "Criar projeto no IARA" → `salvarProjeto()` direto
- [ ] Botão "Importar JSON" para projetos externos
- [ ] Aplicar paleta pergaminho (seção 24)


---

## 28. Calendário como coração do IARA — decisão arquitetural

### Decisão

O calendário é a **visão unificada de tudo que tem data no IARA**. Nenhuma data é lançada duas vezes — ela nasce no módulo de origem e aparece automaticamente no calendário.

### As seis fontes de dados do calendário

| Fonte | O que aparece | Cor |
|---|---|---|
| Gestão e Planejamento | Prazos de entregas e tarefas | Roxo |
| Projetos Sociais | Atividades e eventos | Verde escuro |
| Ocorrências / Triagem | Visitas solidárias, ligações, FRIDAs | Bordô / Vermelho |
| Encaminhamentos | Sextas com lote a enviar | Âmbar |
| Módulo Escolar | Rondas e visitas escolares | Azul |
| Eventos avulsos | Reuniões e compromissos | Cinza/roxo claro |

### Comportamento

- Tarefa criada em Gestão e Planejamento com prazo → aparece no calendário automaticamente
- Visita agendada na triagem → aparece no calendário automaticamente
- FRIDA agendado → aparece no calendário automaticamente
- Ronda escolar → aparece no calendário automaticamente
- **Nada é lançado duas vezes**

### Filtros do calendário

O usuário pode ver:
- Tudo junto (visão padrão)
- Só uma fonte (ex.: "só Gestão e Planejamento")
- Só um tipo (ex.: "só visitas VCM")
- Só urgentes (itens vencidos ou com prazo hoje)

### Prazo vencido

Tarefa ou entrega com prazo vencido e não concluída → aparece em vermelho no calendário automaticamente. O comandante abre o calendário de segunda e vê o que estava para ser entregue na semana passada e não foi — sem abrir cada projeto.

### Implicações técnicas

A função `renderCalendar()` precisa agregar dados de:
```javascript
// Fontes a integrar
const fontes = [
  state.agendamentos,          // visitas, FRIDAs, ligações
  state.projetos.flatMap(p =>
    p.entregas.flatMap(e =>
      e.tarefas.map(t => ({
        ...t,
        fonte: 'gestao_planejamento',
        projeto: p.nome,
        entrega: e.nome
      }))
    )
  ),
  state.projetosSociais.flatMap(/* atividades */),
  state.atividadesEscolares,
  state.encaminhamentos.filter(e => e.situacao === 'a_encaminhar'),
  state.eventosAvulsos
]
```

### Checklist para o Claude Code

- [ ] Refatorar `renderCalendar()` para agregar as seis fontes
- [ ] Adicionar campo `fonte` em cada evento renderizado (para filtros e cores)
- [ ] Filtros no toolbar do calendário por fonte e por tipo
- [ ] Tarefas vencidas de Gestão e Planejamento → cor vermelha no calendário
- [ ] Tarefas de Gestão e Planejamento → ícone 📁 + nome do projeto no tooltip
- [ ] Ao clicar num item de projeto no calendário → abre o detalhe da tarefa no módulo
- [ ] Ao clicar numa visita → abre o registro de atendimento
- [ ] Badge de contagem por fonte no toolbar (ex.: "3 tarefas · 2 visitas · 1 FRIDA")


---

## 29. Painel do Comandante — especificação completa

### Conceito

Tela inicial do perfil Comandante. Abre todo dia ao assumir o serviço. Lida em 30 segundos — o que exige atenção salta aos olhos, o que está bem fica discreto.

### Estrutura — três faixas

```
TOPO: data + saudação + 4 badges de estado geral
      (para triar · FRIDA nível E · projetos críticos · calendário)

FAIXA 1 — O que está acontecendo agora
  4 métricas com seta de tendência
  Cards VCM nível E com nome, bairro e dias de atraso

FAIXA 2 — Projetos e metas
  Lista compacta de Gestão e Planejamento
  Barra de progresso + prioridade + prazo + badge crítico

FAIXA 3 — Estatísticas e tendências
  Gráfico 1: Ocorrências por semana (linha) — últimas 8 semanas
  Gráfico 2: VCM mensal comparativo ano atual vs anterior (barras)
  Gráfico 3: Tipos de ocorrência — últimos 30 dias (rosca)
```

### Badges do topo

| Badge | Verde | Âmbar | Vermelho |
|---|---|---|---|
| Para triar | 0 novas | 1–5 novas | 6+ novas ou VD > 48h |
| FRIDA nível E | 0 urgentes | 1–3 urgentes | 4+ urgentes |
| Projetos críticos | 0 críticos | 1 crítico | 2+ críticos |
| Calendário | Tudo em dia | Itens vencendo hoje | Itens vencidos |

### Métricas da Faixa 1

| Métrica | Fonte | Alerta |
|---|---|---|
| Ocorrências sem triagem | `situacao = nova` | Vermelho se > 5 |
| Casos VD ativos | `violencia_domestica = true` | Âmbar se FRIDA < 50% |
| Cobertura FRIDA | FRIDAs / casos VD | Vermelho se < 50% |
| Total ocorrências | Contagem geral | Delta vs mês anterior |

### Gráficos — dados reais da planilha

- **Ocorrências por semana:** agrupar por semana ISO, últimas 8
- **VCM comparativo:** agrupar por mês, ano atual vs ano anterior
- **Tipos de ocorrência:** top 5 tipos + "Outros", últimos 30 dias

### Arquivo de referência

`mockup_painel_comandante.html`

### Checklist para o Claude Code

- [ ] Criar tela `state.tela = 'painel_comandante'` como entrada padrão para `perfil = comandante`
- [ ] Badges do topo com semáforo automático (verde/âmbar/vermelho)
- [ ] Faixa 1: métricas com delta vs período anterior + cards VCM nível E
- [ ] Faixa 2: lista de projetos de Gestão e Planejamento com progresso
- [ ] Faixa 3: três gráficos Chart.js com dados reais da planilha
- [ ] Forçar `_sincSheets()` ao abrir o painel (dados sempre frescos)
- [ ] Aplicar paleta pergaminho (seção 24)

---

## 30. Sincronização — prioridade zero e solução definitiva

### O problema raiz

O IARA salva em dois lugares ao mesmo tempo:
- **localStorage** — local, só naquele aparelho, imediato
- **Google Sheets** — compartilhado, fonte da verdade, assíncrono

Quando os dois divergem, cada aparelho vê uma versão diferente. A sincronização atual é **passiva** — só puxa dados novos quando alguém recarrega manualmente.

### Impacto real

- Auxiliar lança uma ocorrência → Comandante não vê até recarregar
- Comandante vê calendário desatualizado → toma decisões com dados velhos
- Evento deletado num aparelho → "ressuscita" no outro na próxima abertura
- Dois aparelhos editam o mesmo registro → um sobrescreve o outro sem aviso

### Solução definitiva — três camadas obrigatórias

**Camada 1 — Sincronização ao abrir (imediata)**
```javascript
// Ao inicializar o IARA — ANTES de renderizar qualquer tela
async function inicializar() {
  mostrarLoading('Sincronizando dados...');
  await _sincSheets(); // busca completa no Sheets
  state.ultimaSinc = new Date();
  render(); // só renderiza depois de ter dados frescos
}
```
Toda vez que qualquer pessoa abre o IARA em qualquer aparelho, a primeira coisa é buscar os dados mais recentes no Sheets. O localStorage é sobrescrito. Ninguém vê dados velhos.

**Camada 2 — Polling automático a cada 2 minutos (silencioso)**
```javascript
setInterval(async () => {
  if (state.sincronizando) return; // mutex — evita chamadas paralelas
  if (document.hidden) return;     // só sincroniza se aba visível
  state.sincronizando = true;
  try {
    await _sincSheets();
    state.ultimaSinc = new Date();
    render(); // atualiza a tela se houver mudanças
  } finally {
    state.sincronizando = false;
  }
}, 2 * 60 * 1000);
```

**Camada 3 — Confirmação antes de mostrar "salvo"**
```javascript
async function salvarEConfirmar(tipo, dados) {
  mostrarBadge('Salvando...');
  const local = salvarLocal(tipo, dados);  // salva local imediatamente
  try {
    await salvarDadoAppSheets(tipo, dados); // confirma no Sheets
    mostrarBadge('✓ Salvo e sincronizado');
  } catch {
    mostrarBadge('⚠ Salvo localmente — sincronizando...', 'ambar');
    agendarRetentativa(tipo, dados); // tenta de novo em 30s
  }
}
```
Quando a auxiliar salva, o sistema confirma que chegou no Sheets antes de mostrar "salvo". Se o Sheets demorar, mostra "salvando…" em âmbar — nunca mente com um "salvo" falso.

### Correções específicas do calendário

- Adicionar `_editadoEm` em todos os eventos avulsos ao criar/editar
- Na sincronização: versão com `_editadoEm` mais recente vence
- Persistir `_deletedEvIds` no localStorage (`bcs_deleted_ev_ids`)
- Carregar IDs deletados ao inicializar — nunca ressuscitar eventos deletados

### Badge de sincronização (visível em todas as telas)

```
✓ Atualizado às 14:32        → verde, dados frescos
⟳ Sincronizando...           → âmbar, aguardar
⚠ Dados locais · reconectando → âmbar, sem internet
```

Posicionado no rodapé ou canto superior — discreto mas sempre visível.

### Esta é a prioridade zero

Antes de qualquer nova funcionalidade, o Claude Code implementa as três camadas. Sem sincronização confiável, tudo o mais construído terá o mesmo problema de fundo.

### Ordem de implementação obrigatória

1. **Camada 1** — sincronização ao abrir (1 hora de trabalho)
2. **Camada 2** — polling automático com mutex (2 horas)
3. **Camada 3** — confirmação antes de "salvo" (3 horas)
4. **Calendário** — `_editadoEm` + `_deletedEvIds` persistidos (2 horas)
5. **Badge visual** — indicador em todas as telas (1 hora)

### Checklist para o Claude Code

- [ ] Refatorar `inicializar()` para aguardar `_sincSheets()` antes de renderizar
- [ ] Adicionar `setInterval` com mutex `state.sincronizando` e verificação `document.hidden`
- [ ] Refatorar todas as funções de salvar para usar `salvarEConfirmar()`
- [ ] Adicionar retentativa automática para salvamentos que falharam
- [ ] Adicionar campo `_editadoEm` em eventos avulsos
- [ ] Persistir e carregar `bcs_deleted_ev_ids` no localStorage
- [ ] Badge de sincronização no layout base (visível em todas as telas)
- [ ] Tela de loading inicial "Sincronizando dados..." antes do primeiro render
- [ ] `state.ultimaSinc` — salvar e exibir no badge


---

## 31. Gestão e Planejamento — abas completas

### Cinco abas do módulo

| Aba | Ícone | Função |
|---|---|---|
| Projetos | ⊞ | Grade / Kanban / Lista com campo prioridade |
| Kanban | 🗂 | Visão de fluxo por status |
| Lista | ≡ | Comparação tabular ordenada por criticidade |
| Chuva de Ideias | 💡 | Bloco de notas livre → transformar em projeto |
| Relatório Semanal | 📋 | Gerador de inteligência com IA |

### Aba Chuva de Ideias

**Conceito:** etapa zero antes do projeto. Espaço livre para esboçar ideias sem estrutura obrigatória. Quando a ideia estiver madura, um clique transforma em projeto via assistente IA.

**Layout:** duas colunas — lista de rascunhos à esquerda (280px) + editor livre à direita.

**Rascunho:**
- Título livre
- Tag de categoria (Operação / Capacitação / Comunitário / Meta Institucional / Livre)
- Área de texto com formatação básica (negrito, itálico, listas, títulos)
- Salvo automaticamente — sem botão obrigatório
- Rodapé: "✓ Salvo automaticamente · HH:MM · N palavras"

**Botão "✦ Transformar em projeto":**
- Abre o painel do Assistente IA com o texto do rascunho já carregado
- A IA lê o conteúdo e estrutura entregas e tarefas automaticamente
- O comandante revisa o preview e confirma com um clique
- O rascunho é marcado como "convertido" mas não deletado (histórico)

**Arquivo de referência:** `mockup_chuva_ideias.html`

**Checklist para o Claude Code:**
- [ ] Criar aba "💡 Chuva de Ideias" em Gestão e Planejamento
- [ ] Lista de rascunhos com tags de categoria e preview do texto
- [ ] Editor com formatação básica (toolbar: negrito, itálico, listas, H1/H2)
- [ ] Auto-save a cada 30 segundos no localStorage + Sheets
- [ ] Botão "✦ Transformar em projeto" → abre assistente IA com texto pré-carregado
- [ ] Marcar rascunho como "convertido" após criação do projeto

---

### Aba Relatório Semanal

**Conceito:** a IA analisa os dados da semana e gera dois formatos prontos — PDF completo (para arquivo) e texto WhatsApp (para postar no grupo das guarnições).

**Layout:** duas colunas — gerador à esquerda + preview à direita.

**Configurações do gerador:**
- Período: Esta semana / Semana passada / Personalizado (campo de data)
- Seções selecionáveis (todas marcadas por padrão):
  - 📍 Bairros e ruas quentes
  - ⏰ Horários de pico
  - 🔍 Tipos prevalentes
  - ⚠️ Alertas nominais (suspeitos e locais)
  - 🛡️ VCM urgentes
  - ✦ Orientação da semana (gerada pela IA)
- Formato: PDF / Texto WhatsApp / Ambos

**Conteúdo do relatório — sete blocos:**

| Bloco | Fonte dos dados | Observação |
|---|---|---|
| Manchete da semana | IA analisa variações | Frase de inteligência contextualizada |
| Bairros em alerta | Coluna Bairro + contagem | Após limpeza da col. 6 (seção 21) |
| Horários de pico | Coluna Hora (659/765 preenchidos) | Faixas de 2h agrupadas |
| Tipos prevalentes | Coluna Tipo | Top 5 + crimes graves destacados |
| Alertas nominais | IA extrai da Dinâmica dos fatos | Citações no texto — não identificações formais |
| VCM urgentes | FRIDA nível E + prazo | Só bairro no WhatsApp (privacidade) |
| Orientação da semana | IA sintetiza tudo | Recomendação direta para a guarnição |

**Nota sobre suspeitos:** hoje apenas 3 de 765 registros têm suspeito formal preenchido. A IA extrai nomes citados na Dinâmica dos fatos, com aviso explícito de que são citações em relato, não identificações formais.

**Exportação:**
- "⬇ Baixar PDF" → gera documento via `window.print()` (evolução futura: PDF no servidor via Apps Script)
- "💬 Copiar WhatsApp" → copia texto formatado para colar no grupo

**Arquivo de referência:** `mockup_relatorio_semanal.html`

**Checklist para o Claude Code:**
- [ ] Criar aba "📋 Relatório Semanal" em Gestão e Planejamento
- [ ] Seletor de período + checkboxes de seções
- [ ] Função `gerarContextoSemanal(dataInicio, dataFim)` — agrega dados do período
- [ ] Chamada à API Claude com context dos dados + instrução de formato
- [ ] Preview PDF renderizado no painel direito
- [ ] Preview WhatsApp com formatação de negrito `*texto*`
- [ ] Botão "Baixar PDF" → `window.print()` com CSS de impressão
- [ ] Botão "Copiar WhatsApp" → `navigator.clipboard.writeText()`
- [ ] Nota de rodapé automática: "Gerado automaticamente pelo IARA · [data/hora]"

---

## 32. Painel do Comandante — estrutura completa com quatro abas

### As quatro abas

| Aba | Ícone | Função |
|---|---|---|
| Visão Geral | 📊 | Dashboard com três faixas (seção 29) |
| Projetos | 📁 | Lista compacta de Gestão e Planejamento |
| Relatório Semanal | 📋 | Atalho para o gerador (seção 31) |
| IARA | ✦ | Assistente conversacional com dados reais |

### Aba IARA — Assistente Inteligente

**Conceito:** IA que conhece todos os dados da base e conversa de forma fluente. Não é um chatbot genérico — é uma analista que sabe que hoje há 765 ocorrências, 8 FRIDAs nível E e 2 projetos críticos.

**Layout:** duas colunas — sidebar com contexto e perguntas rápidas (260px) + área de chat.

**Sidebar da IARA:**
- Avatar + nome "IARA" + status "Dados atualizados às HH:MM"
- Contexto atual: os 7 indicadores-chave da base em tempo real
- 8 perguntas rápidas — atalhos para as análises mais comuns

**Comportamento:**
- Ao abrir, a IARA já saúda com dados do dia: *"Bom dia, Comandante. Tenho 18 ocorrências aguardando triagem…"*
- Conversa fluente — responde sobre qualquer ocorrência, estatística, projeto ou tendência
- Formata respostas com seções, rankings e destaques — não responde em texto corrido
- Identifica lacunas e faz recomendações concretas
- Perguntas de follow-up funcionam — ela mantém o contexto da conversa

**O segredo técnico — o system prompt com dados reais:**

```javascript
function gerarSystemPromptIARA() {
  const d = state.db;
  const ocs = d.ocorrencias;
  const vd = ocs.filter(o => o.violencia_domestica).length;
  const semTriagem = ocs.filter(o => o.situacao === 'nova').length;
  const fridaE = (state.db.fridas || []).filter(f => f.nivel === 'E').length;

  return `Você é a IARA, assistente inteligente da 77ª CIPM BCS,
Vitória da Conquista-BA. Conheço todos os dados da base.

DADOS ATUAIS (${new Date().toLocaleDateString('pt-BR')}):
- Total ocorrências: ${ocs.length}
- Sem triagem: ${semTriagem}
- Casos VD: ${vd}
- FRIDA nível E: ${fridaE}
- Cobertura FRIDA: ${Math.round(state.db.fridas?.length / vd * 100) || 0}%
- Tipos principais: ${_topTipos(ocs, 5).join(', ')}
- Projetos críticos: ${(state.projetos||[]).filter(p=>p.status==='Crítico').length}

Converse de forma fluente e direta. Use os dados reais.
Quando identificar lacunas, aponte com clareza.
Formate respostas com seções e destaques — não em texto corrido.
Ao fazer recomendações, seja concreto e operacional.`;
}
```

**Perguntas rápidas pré-configuradas:**
1. Quais bairros estão mais críticos esta semana?
2. Como evoluiu a VCM nos últimos 3 meses?
3. Qual o horário de pico das ocorrências?
4. Quais suspeitos foram mais citados nos relatos?
5. Qual o status das vítimas nível E?
6. Gere o relatório semanal para a guarnição
7. Como estão os projetos em andamento?
8. O que devo priorizar hoje?

**Arquivo de referência:** `mockup_iara_assistente.html`

**Checklist para o Claude Code:**
- [ ] Criar aba "✦ IARA" no Painel do Comandante
- [ ] Sidebar com contexto em tempo real (7 indicadores)
- [ ] 8 botões de perguntas rápidas
- [ ] Função `gerarSystemPromptIARA()` que injeta dados reais antes de cada mensagem
- [ ] Saudação inicial contextualizada ao abrir a aba
- [ ] Formatação de respostas com seções, rankings e destaque roxo para recomendações
- [ ] Manter histórico da conversa durante a sessão (`state.iaChat`)
- [ ] Botão "↺ Nova conversa" limpa o histórico
- [ ] Usar `claude-sonnet-4-6` (já usado em partes do código) — não Haiku para esta função
- [ ] Atualizar contexto a cada abertura da aba (dados sempre frescos)


---

## 33. Dashboard VCM — especificação completa

### Conceito

Limpo e prático. Quatro blocos — nada além do necessário. A auxiliar abre e sabe o que é urgente em 5 segundos.

### Quatro blocos

**Bloco 1 — Números do mês**
Cinco métricas com seta de tendência vs mês anterior:
- Casos VD ativos
- FRIDA nível E
- Cobertura FRIDA (com meta 80% visível)
- Medidas protetivas ativas
- Visitas realizadas

**Bloco 2 — Fila de urgência**
Casos ordenados por criticidade — vencidos primeiro, em vermelho.
Cada linha: nível (E/M/B) · nome · bairro · tipo · MP ativa · prazo · botão "Contatar" ou "Ver ficha".
Botão "Contatar" em vermelho para casos vencidos — impossível ignorar.

**Bloco 3 — Tendências (três gráficos compactos)**
- Casos VD por mês: 2026 vs 2025 (barras comparativas)
- Medidas protetivas: evolução mensal (linha)
- Cobertura FRIDA: % aplicado com linha tracejada da meta 80%

**Bloco 4 — Resultado das visitas**
Três barras: realizadas/aceitas · não encontrada · recusou atendimento.
Nota: campo "resultado" só capturado a partir do novo fluxo (abril/2026 em diante).
Dado anterior é estimado — exibir aviso discreto.

### Observação sobre dados reais

- **Medidas protetivas:** 165/165 marcadas como "Sim" na importação — provavelmente padrão. Novo fluxo corrige progressivamente.
- **Resultado de visitas:** aba "Visitas Realizadas" tem 193 linhas com dados vazios. O campo `resultado` passa a ser capturado pelo novo módulo de Atendimento (seção 4.3).
- **Cobertura FRIDA:** 21% real — 35 FRIDAs para 165 casos VD. 19 sem nível registrado.

### Arquivo de referência

`mockup_dashboard_vcm.html`

### Checklist para o Claude Code

- [ ] Criar tela `state.tela = 'dashVCM'` dentro da Central de Atendimento
- [ ] Bloco 1: cinco métricas com delta vs mês anterior
- [ ] Bloco 2: fila ordenada por urgência — vencidos primeiro, botão "Contatar" em vermelho
- [ ] Bloco 3: três gráficos Chart.js com dados reais
- [ ] Bloco 4: barras de resultado de visitas com nota de dados estimados
- [ ] Seletor de período: Este mês / Últimos 90 dias / Este ano
- [ ] Aplicar paleta pergaminho (seção 24)

---

## 34. Central de Atendimento — área de trabalho da auxiliar

### Decisão arquitetural

Dashboard VCM, Devolutivas, Fila do dia, Triagem e Atendimentos ficam todos dentro de uma única área chamada **Central de Atendimento**. A auxiliar não precisa navegar para outros módulos — tudo o que faz está em um só lugar.

### Conceito

A triagem não é só "classificar uma ocorrência" — é o ciclo completo de acompanhamento de um caso. A Central cobre esse ciclo inteiro:

```
Fila do dia → Triagem → VCM → Atendimentos → Devolutivas
  (o que        (analisar   (acompanhar   (registrar    (fechar
  chegou)       e rotear)   urgentes)     o que fez)    o ciclo)
```

Cada aba alimenta a próxima. É um único fluxo de trabalho.

### Cinco abas

| Aba | Ícone | Função |
|---|---|---|
| Fila do dia | 📥 | Entrada — o que chegou e precisa de ação hoje |
| Triagem | 🔍 | Analisar e rotear cada ocorrência nova |
| VCM | 🛡️ | Acompanhar casos urgentes e tendências |
| Atendimentos | 📞 | Registrar o que a guarnição fez |
| Devolutivas | 📤 | Fechar o ciclo com os órgãos parceiros |

### Posição no menu lateral

```
OPERACIONAL
  📋 Ocorrências
  🗓 Calendário

CENTRAL DE ATENDIMENTO
  📥 Fila do dia
  🔍 Triagem          (badge: N para triar)
  🛡️ VCM              (badge: N urgentes)
  📞 Atendimentos
  📤 Devolutivas      (badge: N novas)

GESTÃO
  📁 Gestão e Planejamento
  🤝 Projetos Sociais

COMANDO
  🎖 Painel do Comandante
```

### Badges no menu

- **Triagem:** número de ocorrências com `situacao = nova`
- **VCM:** número de FRIDAs nível E com prazo vencido ou vencendo hoje
- **Devolutivas:** número de devolutivas recebidas não registradas na ficha

### Perfil de acesso

A Central de Atendimento é a área principal do perfil **operador/gestor** (auxiliar).
O Comandante também acessa, mas sua entrada padrão é o Painel do Comandante.

### Checklist para o Claude Code

- [ ] Criar grupo "CENTRAL DE ATENDIMENTO" no menu lateral
- [ ] Mover `dashVCM` para dentro da Central (aba VCM)
- [ ] Mover `devolutivas` para dentro da Central (aba Devolutivas)
- [ ] Mover `fila_auxiliar` para dentro da Central (aba Fila do dia)
- [ ] Mover triagem para dentro da Central (aba Triagem)
- [ ] Criar aba Atendimentos dentro da Central
- [ ] Badges automáticos no menu para Triagem, VCM e Devolutivas
- [ ] Perfil `operador/gestor` → entrada padrão na aba Fila do dia
- [ ] Perfil `comandante` → entrada padrão no Painel do Comandante
- [ ] Navegação entre abas sem recarregar — `state.centralAba`


---

## 35. Projetos Sociais — especificação completa

### Conceito

Gestão dos programas oferecidos à comunidade: Robótica, Luta Cidadã, Adote um Leitor, Comida no Prato, etc. Foco em **pessoas e presença** — não em tarefas e prazos (isso é Gestão e Planejamento).

### Distinção importante

| Projetos Sociais | Gestão e Planejamento |
|---|---|
| Programas para a comunidade | Ações internas da base |
| Inscritos, chamadas, frequência | Entregas, tarefas, prazos |
| Instrutor, vagas, QR code | Responsável, progresso, meta |
| Produto: participante atendido | Produto: entrega institucional |

### Cinco abas

| Aba | Função |
|---|---|
| ⊞ Portfólio | Grade dos projetos com vagas, inscritos e frequência |
| 👥 Candidaturas | Fila de inscrições para aprovar ou recusar |
| 📋 Chamadas | Registrar presença por aula/atividade |
| 🏫 Instrutores | Cadastro dos professores/responsáveis |
| 📊 Relatório | Frequência, evolução e resultados |

### Diagnóstico dos problemas atuais

**1. Sincronização frágil**
`_sincronizarProjetosSociais()` envia projetos em loop com `setTimeout(200ms)` sem confirmação de chegada. Se a conexão cair, alguns projetos vão e outros não — sem aviso. Resolver com as três camadas da seção 30.

**2. Assinatura digital não registra**
O canvas salva a assinatura em base64 (~50-80KB), mas o Google Sheets trunca células acima de 50.000 caracteres. A assinatura fica como `[assin_local]` na planilha — nunca chegou de fato.

**Solução:** salvar a imagem da assinatura no Google Drive via `Drive.Files.create()` no Apps Script e guardar apenas o link na planilha. O código de aprovação de candidatura já tem o canvas — só muda o destino.

**3. Termo de uso de imagem inexistente**
O formulário de inscrição não tem nenhum aviso sobre fotografias. Obrigação legal especialmente para menores.

### Ficha de inscrição — três blocos novos

**Bloco 1 — Termo de uso de imagem (todos os participantes)**
```
A 77ª CIPM poderá realizar fotografias e filmagens durante as
atividades para fins de divulgação institucional em redes sociais,
materiais de comunicação e relatórios oficiais. As imagens serão
utilizadas exclusivamente para fins institucionais, sem fins comerciais.

☑ Autorizo o uso de imagem do participante para fins institucionais.
```
Campo obrigatório. Registra: quem autorizou + data + hora + IP.

**Bloco 2 — Termo reforçado para menores (automático quando idade < 18)**
```
Por ser o participante menor de idade, esta autorização deve ser
concedida pelo responsável legal.

☑ Declaro ser responsável legal e autorizo o uso de imagem.
```
Aparece automaticamente quando o sistema detecta idade < 18. O checkbox é do responsável, não da criança.

**Bloco 3 — Assinatura digital**
- Canvas HTML para coleta da assinatura (já existe)
- Ao submeter: `Drive.Files.create()` salva imagem PNG no Google Drive
- Planilha recebe apenas o link (não o base64)
- Rodapé da ficha: "Assinaturas salvas no Google Drive · [data/hora]"

### Portfólio — card de projeto

Cada card mostra:
- Tipo (ícone + categoria)
- Nome do projeto
- Descrição curta
- Três métricas: Vagas · Inscritos · Chamadas do mês
- Barra de ocupação (só quando vagas preenchidas)
- Dias/horário/local
- Três botões: Abrir · QR Code · Editar

Alerta visual quando `chamadas_mes = 0` — sinaliza projeto sem atividade registrada.

### Badge de sincronização

No resumo do portfólio: "✓ Sinc. HH:MM" quando tudo está atualizado. "⟳ Sincronizando..." durante o processo. "⚠ Dados locais" quando offline.

### Arquivo de referência

`mockup_projetos_sociais_completo.html`

### Checklist para o Claude Code

**Backend (Apps Script):**
- [ ] Criar função `salvarAssinaturaNosDrive(base64, nome)` → retorna link
- [ ] Modificar `_confirmarDecisaoCandidatura` para chamar `salvarAssinaturaNosDrive` antes de gravar na planilha
- [ ] Adicionar campo `termo_imagem` e `termo_imagem_responsavel` nas candidaturas
- [ ] Adicionar campo `assinatura_drive_link` e `assinatura_resp_drive_link` (substituindo base64)
- [ ] Corrigir `_sincronizarProjetosSociais` para usar as três camadas da seção 30

**Frontend:**
- [ ] Adicionar bloco "Termo de uso de imagem" no formulário de inscrição (inscricao.html)
- [ ] Lógica automática: se idade < 18 → mostrar bloco reforçado para responsável
- [ ] Checkboxes obrigatórios — formulário não submete sem ambas as autorizações
- [ ] Gravar `termo_imagem: true/false`, `termo_imagem_data`, `termo_imagem_resp` na candidatura
- [ ] Badge de sincronização no portfólio
- [ ] Alerta visual nos cards sem chamadas registradas

---

## 36. Reorganização do menu lateral e perfis de acesso

### Estrutura final do menu

```
OPERACIONAL
  📋 Ocorrências
  🗓 Calendário

CENTRAL DE ATENDIMENTO          [perfil: auxiliar]
  📥 Fila do dia
  🔍 Triagem
  🛡️ VCM
  📞 Atendimentos
  📤 Devolutivas

GESTÃO COMUNITÁRIA
  🤝 Projetos Sociais
  🏫 Escolar
  👥 Conselho Comunitário

MÓDULOS
  🔫 Armamento
  📦 Inventário

COMANDO                         [perfil: comandante]
  🎖 Painel do Comandante
```

### Painel do Comandante — quatro abas (revisado)

| Aba | Conteúdo |
|---|---|
| 📊 Visão Geral | Dashboard com três faixas (seção 29) |
| 📁 Gestão e Planejamento | Cinco abas: Projetos · Kanban · Lista · Chuva de Ideias · Relatório Semanal |
| 📋 Relatório Semanal | Gerador de inteligência com IA (seção 31) |
| ✦ IARA | Assistente conversacional com dados reais (seção 32) |

### Justificativa

Gestão e Planejamento é de uso exclusivo do Comandante — operações, capacitações, metas institucionais. Não faz sentido estar no menu lateral acessível a todos. Entra como aba dentro do Painel do Comandante, onde o perfil já controla o acesso.

### Perfis de entrada padrão

| Perfil | Tela de entrada |
|---|---|
| Comandante | Painel do Comandante → aba Visão Geral |
| Auxiliar/Gestor | Central de Atendimento → aba Fila do dia |
| Operador | Calendário → visão do dia |
| Conselho | Módulo Conselho Comunitário |

### Checklist para o Claude Code

- [ ] Remover "Gestão e Planejamento" do menu lateral
- [ ] Criar aba "📁 Gestão e Planejamento" dentro do Painel do Comandante
- [ ] Adicionar grupo "GESTÃO COMUNITÁRIA" no menu com Projetos Sociais, Escolar e Conselho
- [ ] Adicionar grupo "MÓDULOS" com Armamento e Inventário
- [ ] Implementar `state.perfil` como controlador de tela de entrada
- [ ] Redirecionar automaticamente conforme perfil ao fazer login


---

## 37. Módulo Escolar — decisão arquitetural

### Decisão

Rondas e visitas escolares **não terão módulo próprio**. Serão tratadas como visitas dentro do fluxo já existente:

| Situação | Tipo de visita | Âncora |
|---|---|---|
| Aluno em situação de risco, menor envolvido em ocorrência, encaminhamento do Conselho Tutelar | **Solidária** | Pessoa (aluno) |
| Presença preventiva, palestra, articulação com direção, ação de cidadania | **Comunitária** | Local (escola) |

### O que muda no modelo existente

- Adicionar subtipo `ronda_escolar` no campo de visita comunitária
- Adicionar "Escola" como categoria de local nos agendamentos
- Ícone 🏫 no calendário para visitas com subtipo `ronda_escolar`
- Filtro "Rondas Escolares" nos relatórios do calendário

### Justificativa

A ronda escolar é uma visita com destino específico — a escola é só mais um território. Sem módulo próprio: calendário mais limpo, fluxo único para a auxiliar, sem fragmentação de dados. Relatórios específicos de rondas escolares são gerados por filtro de subtipo — sem precisar de módulo separado.

### Checklist para o Claude Code

- [ ] Adicionar `ronda_escolar` como subtipo de visita comunitária
- [ ] Adicionar "Escola" como opção de local no formulário de agendamento
- [ ] Ícone 🏫 no calendário quando `subtipo = ronda_escolar`
- [ ] Filtro "Rondas Escolares" no relatório do calendário e no relatório semanal


---

## 38. Relatório Mensal — Departamento de Crises Comunitárias

### Conceito

Relatório gerado automaticamente no final de cada mês com todos os indicadores que a 77ª CIPM envia ao Departamento de Crises Comunitárias. A auxiliar abre, confere os números e exporta — sem calcular nada manualmente.

### Fontes dos indicadores

| Indicador | Fonte no IARA | Automático? |
|---|---|---|
| Visitas comunitárias realizadas | Agendamentos tipo=comunitária status=realizada | ✅ Sim |
| Visitas solidárias realizadas | Agendamentos tipo=solidaria status=realizada | ✅ Sim |
| Rondas escolares | Agendamentos subtipo=ronda_escolar | ✅ Sim |
| Projetos sociais ativos | Projetos Sociais status=ativo | ✅ Sim |
| Alunos matriculados em projetos | Candidaturas aprovadas | ✅ Sim |
| Palestras realizadas | Relatório diário da Patrulha (IA extrai) | ⚡ Semi |
| Alimentos doados | Relatório diário da Patrulha (IA extrai) | ⚡ Semi |
| Pessoas atendidas em ações | Relatório diário da Patrulha (IA extrai) | ⚡ Semi |

### Relatório diário da Patrulha Comunitária

A Patrulha lança um único relatório narrativo ao final do dia (texto livre). A IA extrai os números estruturados automaticamente. A auxiliar confirma ou corrige antes de salvar.

**Fluxo:**
```
Patrulha lança relato narrativo do dia
       ↓
IA lê o texto e extrai:
  - Qtd palestras + pessoas
  - Qtd alimentos doados
  - Qtd pessoas atendidas
  - Locais visitados
       ↓
Auxiliar confirma ou corrige os números
       ↓
Dados entram no consolidado mensal automaticamente
```

**Tela de lançamento:**
- Campo 1: texto livre (relato do dia — a patrulha digita ou dita)
- Campo 2: extração automática pela IA (aparece ao salvar o relato)
- Campo 3: confirmação/ajuste pela auxiliar

**Exemplo de extração:**
```
Relato: "Realizamos palestra sobre segurança na E.E. Dom Pedro
com 45 alunos. Distribuímos 30 cestas básicas no Panorama.
Atendemos 12 famílias em situação de vulnerabilidade."

IA extrai:
  Palestras: 1
  Pessoas em palestras: 45
  Cestas distribuídas: 30
  Famílias atendidas: 12
  Locais: E.E. Dom Pedro · Panorama
```

### Onde fica no sistema

Aba **"Ações"** dentro de Projetos Sociais — além do Portfólio, Candidaturas, Chamadas, Instrutores e Relatório. A auxiliar acessa pelo menu Gestão Comunitária → Projetos Sociais → aba Ações.

### Gerador do relatório mensal

Botão "Gerar relatório mensal" na aba Relatório dos Projetos Sociais. Consolida automaticamente todos os indicadores do mês selecionado. Exporta em PDF e/ou texto para envio ao departamento.

### Checklist para o Claude Code

- [ ] Criar aba "Ações" em Projetos Sociais
- [ ] Tela de lançamento: campo de texto livre + extração IA + confirmação
- [ ] Chamada à API Claude para extrair indicadores do relato narrativo
- [ ] Salvar indicadores extraídos em aba `acoes_patrulha` na planilha
- [ ] Criar função `consolidarRelatorioMensal(mes, ano)` que agrega todas as fontes
- [ ] Botão "Gerar relatório mensal" na aba Relatório dos Projetos Sociais
- [ ] Exportar em PDF + texto formatado para envio

---

## 39. Conselho Comunitário

### O que existe hoje

O IARA já tem um módulo de Conselho Comunitário com cadastro de membros e registro de reuniões. Sem dados na planilha — módulo nunca usado.

### Fluxo básico

```
Cadastrar membros do conselho
       ↓
Agendar reunião → aparece no Calendário
       ↓
Registrar pauta e ata da reunião
       ↓
Gerar PDF da ata para arquivo
```

### Integração com outros módulos

- Reuniões do conselho aparecem no **Calendário** como evento institucional
- Encaminhamentos de casos VCM para o conselho passam pelo módulo de **Devolutivas**
- Projetos Sociais podem ser apresentados nas reuniões do conselho

### Decisão

Manter o módulo existente sem grandes mudanças. Aplicar:
- Design pergaminho (seção 24)
- Sincronização (seção 30)
- Reuniões integradas ao Calendário

### Posição no menu

Gestão Comunitária → 👥 Conselho Comunitário

---

## 40. Armamento e Inventário

### O que existe hoje

Dois módulos separados com registro de carga/descarga de armamento e controle de patrimônio com upload de foto para o Drive. Funcionam de forma relativamente independente.

### Problemas identificados

- Mesma causa de sincronização do restante do sistema
- Upload de foto para o Drive já funciona — manter essa lógica (igual à solução da assinatura digital)
- Design desalinhado do restante

### Decisão

Manter os módulos existentes sem redesenho funcional. Aplicar:
- Design pergaminho (seção 24)
- Sincronização (seção 30)
- Badge de sincronização nos dois módulos

### Posição no menu

Módulos → 🔫 Armamento · 📦 Inventário

### Checklist para o Claude Code

- [ ] Aplicar paleta pergaminho em Armamento e Inventário
- [ ] Aplicar as três camadas de sincronização (seção 30)
- [ ] Badge "✓ Atualizado às HH:MM" nos dois módulos

---

## 41. Segurança — token e PINs

### Problemas atuais

- **TOKEN_FIXO** hardcoded no `index.html` — qualquer pessoa com acesso ao arquivo tem o token de acesso ao backend
- **Hashes de PIN** hardcoded — credenciais visíveis no código-fonte
- Não há rotação de token — o mesmo token vale para sempre

### Risco real

O repositório é público no GitHub (`oseiasvarges-lgtm/bcs-vigilia`). Qualquer pessoa pode ver o `index.html`, extrair o TOKEN_FIXO e fazer chamadas diretas à API do Apps Script — lendo ou gravando dados na planilha sem autenticação.

### Solução recomendada — curto prazo

Mover o TOKEN_FIXO para uma variável de ambiente do Apps Script (PropertiesService) — ele não aparece mais no código-fonte:

```javascript
// No Apps Script — substitui TOKEN_FIXO hardcoded
const TOKEN = PropertiesService.getScriptProperties().getProperty('TOKEN_ACESSO');
```

O token é configurado uma vez no painel do Apps Script e nunca aparece no código. O repositório pode continuar público sem expor credenciais.

### Solução recomendada — médio prazo

Substituir o sistema de PIN por autenticação via Google (OAuth) — cada usuário faz login com a conta Google da PM. Isso elimina PINs, é gratuito e é a forma correta de autenticação para sistemas que usam o ecossistema Google.

### Checklist para o Claude Code

- [ ] Mover TOKEN_FIXO para `PropertiesService.getScriptProperties()`
- [ ] Remover o token hardcoded do `index.html`
- [ ] Documentar como configurar o token no painel do Apps Script (para o administrador)
- [ ] **Não implementar OAuth agora** — deixar para versão futura após estabilização dos módulos


---

## 42. Perfis de acesso — simplificação

### Decisão

O perfil **operador** foi extinto. O IARA passa a ter dois perfis:

| Perfil | Tela de entrada | Acesso |
|---|---|---|
| **Auxiliar / Gestor** | Central de Atendimento → Fila do dia | Operacional completo |
| **Comandante** | Painel do Comandante → Visão Geral | Monitoramento + Gestão |

### O que é extinto

- Perfil `operador` e sua tela de entrada
- Tela de filtro/busca genérica (`state.tela = 'filtro'`) — substituída pela busca integrada dentro de Ocorrências e da Central de Atendimento
- Lógica de roteamento por perfil operador no `renderTela()`

### Checklist para o Claude Code

- [ ] Remover perfil `operador` do sistema de login
- [ ] Remover `case 'filtro'` do `renderTela()`
- [ ] Remover botão de acesso à tela de filtro do menu
- [ ] Garantir que login com PIN redireciona apenas para dois destinos: auxiliar → Fila do dia · comandante → Painel do Comandante


---

## 43. Painel do Comandante — Visão Geral como briefing de decisão

### Decisão

Extinguir o dashboard genérico (`state.tela = 'dashboard'`). A aba Visão Geral do Painel do Comandante substitui com um formato de **briefing de decisão** — cada bloco responde uma pergunta de comando e já vem com a ação sugerida.

### Diferença conceitual

| Dashboard tradicional | Briefing de decisão |
|---|---|
| Mostra números e gráficos | Responde perguntas de comando |
| Você interpreta o que fazer | Estatística + interpretação + ação juntas |
| Você procura o problema | O problema vem até você |

### Quatro cards de decisão

Cada card tem: semáforo (vermelho/âmbar/verde) + pergunta + dados + ação sugerida pela IA + badge de status + link para o módulo correspondente.

| Card | Semáforo | Pergunta | Ação |
|---|---|---|---|
| 1 | 🔴 | Onde concentrar o patrulhamento? | Bairro + horário + suspeito → ronda sugerida |
| 2 | 🔴 | O que está em risco imediato nas vítimas VCM? | Vítimas nível E vencidas → contato hoje |
| 3 | 🟡 | O que está fora da meta? | Projetos atrasados → cobranças específicas |
| 4 | 🟢 | O que está evoluindo bem? | Conquistas da semana → sem ação necessária |

### Geração automática

Os cards são gerados pela mesma IA da aba IARA — rodando uma vez por dia ao abrir o painel. O system prompt injeta os dados reais e pede análise estruturada em quatro perguntas fixas. O resultado é cacheado até a próxima atualização (sincronização ou recarregamento).

### Gráficos de apoio

Ficam abaixo dos cards — separados por divisor tracejado. Três gráficos compactos: ocorrências por semana (linha), VCM comparativo anual (barras), cobertura FRIDA com meta (linha + tracejado). Apoio à decisão, não destaque principal.

### Arquivo de referência

`mockup_painel_comandante.html` (versão atualizada)

### Checklist para o Claude Code

- [ ] Remover `case 'dashboard'` do `renderTela()` — módulo extinto
- [ ] Criar função `gerarBriefingDiario()` — chama API Claude com dados reais e retorna 4 cards estruturados
- [ ] Cachear o briefing em `state.briefingHoje` — não regerar a cada clique
- [ ] Semáforo automático por card baseado nos dados (vermelho se ação urgente, âmbar se monitorar, verde se ok)
- [ ] Cada card tem link `→` que navega para o módulo correspondente
- [ ] Gráficos Chart.js abaixo dos cards com dados reais da planilha
- [ ] Aplicar paleta pergaminho (seção 24)


---

## 44. Telas extintas — mapa completo

### Decisão final sobre todas as telas existentes

| Tela | Decisão | Motivo |
|---|---|---|
| `dashboard` | **Extinta** | Substituída pelo briefing de decisão (seção 43) |
| `filtro` | **Extinta** | Extinção do perfil operador (seção 42) |
| `escolas` | **Extinta** | Rondas viram subtipo de visita (seção 37) |
| `agendamentos` | **Extinta** | Absorvida pela Central de Atendimento |
| `cadastrosvcm` | **Extinta** | Dados nascem da triagem → ficha da vítima (seção 4.4) |
| `importar_zap` | **Extinta** | Não é mais usado — lançamento manual substitui |
| `pendencias` | **Extinta** | Era a fila de triagem — unificada na Central de Atendimento |
| `transparent` | **Extinta** | Tela de loading — substituída pelo badge de sincronização |
| `alertas` | **Unificar com avisos** | Mesmo conceito com dois nomes — manter só `avisos` |
| `associados` | **Sub-tela do Conselho** | Manter como aba dentro do módulo Conselho (seção 39) |
| `atas` | **Sub-tela do Conselho** | Manter como aba dentro do módulo Conselho (seção 39) |
| `diretoria` | **Sub-tela do Conselho** | Manter como aba dentro do módulo Conselho (seção 39) |
| `config` | **Manter simplificada** | Tela de configurações — PINs + token (seção 41) |

### Telas que permanecem (inventário final)

| Tela | Destino no novo sistema |
|---|---|
| `ocorrencias` | Operacional → Ocorrências |
| `lancar` | Dentro de Ocorrências |
| `calendario` | Operacional → Calendário |
| `dashvcm` | Central de Atendimento → aba VCM |
| `encaminhamentos` | Central de Atendimento → aba Devolutivas |
| `avisos` | Sistema de cobrança (seção 17) |
| `projetossociais` | Gestão Comunitária → Projetos Sociais |
| `conselho` | Gestão Comunitária → Conselho Comunitário |
| `associados` | Dentro do Conselho — aba Membros |
| `atas` | Dentro do Conselho — aba Atas |
| `diretoria` | Dentro do Conselho — aba Diretoria |
| `armamento` | Módulos → Armamento |
| `inventario` | Módulos → Inventário |
| `solicitacoes` | Módulos → Solicitações (funcionando bem) |
| `assistente` | Painel do Comandante → aba IARA |
| `dashcomandante` | Painel do Comandante → aba Visão Geral |
| `config` | Configurações (simplificada) |

### Checklist para o Claude Code

- [ ] Remover `case 'agendamentos'` do `renderTela()`
- [ ] Remover `case 'cadastrosvcm'` do `renderTela()`
- [ ] Remover `case 'importar_zap'` do `renderTela()`
- [ ] Remover `case 'pendencias'` do `renderTela()`
- [ ] Remover `case 'transparent'` do `renderTela()`
- [ ] Remover `case 'escolas'` do `renderTela()`
- [ ] Remover `case 'filtro'` do `renderTela()`
- [ ] Remover `case 'dashboard'` do `renderTela()`
- [ ] Unificar `alertas` com `avisos` — remover `case 'alertas'`
- [ ] Mover `associados`, `atas`, `diretoria` para dentro do módulo Conselho
- [ ] Remover todos os botões de navegação para telas extintas


---

## 45. Inventário — diagnóstico e melhorias

### O que existe (e é bom)

O `renderInventario` é um dos módulos mais bem construídos do IARA atual. Já tem:
- Categorias com ícones e cores (INV_CATS)
- KPIs no topo: total, por categoria, conferências
- **Alerta de validade** — itens vencidos ou vencendo em 90 dias
- **Alerta de itens sem conferência há mais de 30 dias**
- Movimentações (entrada/saída) e conferências de patrimônio
- Importação de lista, exportação PDF, upload de foto para o Drive
- Vínculo com Armamento (`_armMigrarParaInventario`, `_armAtualizarInventarioAposCarga`)

### Problema grave — colunas trocadas na importação

Os 8 itens em `materiais_patrimonio` foram importados com os campos embaralhados:

| Coluna | Deveria conter | Contém de fato |
|---|---|---|
| `tipo` | Arma / Colete / etc | "SEY77939" (número de série) |
| `descricao` | PT 100 Taurus | "Arma" (que é o tipo) |
| `numero_serie` | SEY77939 | "PT 100 TAURUS" (descrição) |
| `status` | Em uso / Disponível | repete o número de série |

O dado existe, mas está nas colunas erradas. São apenas 8 registros — revisar um a um.

### Sugestões de melhoria

**1. Corrigir o mapeamento dos 8 itens (prioridade)**
Script de limpeza que reorganiza os campos nas colunas certas. Por serem poucos, revisar manualmente após o script.

**2. Aplicar design pergaminho**
Hoje está no tema escuro verde (#10b981) — destoa do restante. Migrar para a paleta pergaminho (seção 24), mantendo toda a lógica funcional intacta.

**3. Migrar sincronização**
Hoje usa sync de 5 minutos (`_invLastSync`). Migrar para as três camadas da seção 30.

**4. Manter e reforçar vínculo com Armamento**
A carga/descarga de arma já reflete no inventário. Garantir que continue funcionando após o redesign.

**5. Levar o alerta de validade ao Painel do Comandante**
O alerta de coletes balísticos vencendo é valioso. Adicionar como card de decisão no briefing ("2 coletes vencem em 90 dias → providenciar substituição").

### O que NÃO mudar

- Toda a lógica de movimentações, conferências e categorias — está bem construída
- O alerta de validade e de itens sem conferência — funcionalidades valiosas
- O vínculo com Armamento

### Checklist para o Claude Code

- [ ] Script de correção: remapear os 8 itens de `materiais_patrimonio` (tipo/descricao/numero_serie trocados)
- [ ] Aplicar paleta pergaminho (seção 24) preservando toda a lógica
- [ ] Migrar sync de 5min para as três camadas (seção 30)
- [ ] Garantir vínculo Armamento → Inventário após redesign
- [ ] Adicionar card de validade vencendo no briefing do Comandante (seção 43)
- [ ] Manter movimentações, conferências, categorias, importação e PDF


---

## 46. Identidade visual — Logo da BCS

### O logo

Logo oficial da Base Comunitária de Segurança Nova Cidade: duas mãos se cumprimentando dentro de círculo azul — simboliza a parceria entre polícia e comunidade. Texto "Base Comunitária de Segurança · Nova Cidade".

### Tratamento técnico

- Original: 500x500, fundo preto, sem transparência
- **Versão tratada:** recortada em círculo com fundo transparente (`logo_bcs_circulo.png`) — assenta sobre o pergaminho sem o quadrado preto destoar
- A borda azul-escura do logo serve de moldura natural

### Onde o logo aparece

| Local | Tamanho | Observação |
|---|---|---|
| Tela de login | Grande (140px) | Centralizado sobre o pergaminho |
| Sidebar (topo) | Pequeno (42px) | Ao lado do nome "IARA" |
| Cabeçalho de PDFs | Médio (60px) | Faixa azul ao lado do título |
| Marca d'água | Grande, 6% opacidade | Fundo dos relatórios institucionais |
| Formulários públicos | Médio | Devolutiva e inscrição — dá credibilidade |

### PDFs que levam o logo

- Dossiê da vítima
- Relatório semanal
- Relatório mensal (Dep. Crises Comunitárias)
- Ata do conselho comunitário
- Termo de inscrição em projetos sociais
- Relatório de inventário

### Nota sobre nomenclatura

O logo identifica "Nova Cidade" (bairro/distrito onde fica a base). As referências de cidade no sistema usam "Vitória da Conquista". Confirmar uso correto: BCS Nova Cidade, 77ª CIPM, Vitória da Conquista-BA.

### Arquivos de referência

- `logo_bcs_circulo.png` — versão tratada (circular, transparente) para uso no sistema
- `logo_bcs_original.png` — original
- `mockup_logo_integrado.html` — demonstração dos usos

### Checklist para o Claude Code

- [ ] Adicionar `logo_bcs_circulo.png` aos assets do projeto
- [ ] Logo na tela de login (grande, centralizado)
- [ ] Logo pequeno no topo da sidebar ao lado de "IARA"
- [ ] Logo no cabeçalho de todos os PDFs gerados (faixa azul --azul-bcs: #1B3A6B)
- [ ] Marca d'água sutil (6% opacidade) ao fundo dos relatórios
- [ ] Logo nos formulários públicos (devolutiva e inscrição)
- [ ] Embutir como base64 ou referência local — não depender de URL externa


---

## 47. Calendário mobile — perfil guarnição

### Decisão

Os policiais acessam o IARA pelo celular com três funções:
1. Ver a agenda completa (mês/semana/dia)
2. Confirmar ou não a visita (dois toques)
3. Criar eventos avulsos de campo

O relatório detalhado continua indo por WhatsApp → auxiliar lança no IARA. A confirmação no celular é leve — só "Realizei" ou "Não fui" — para manter o calendário atualizado em tempo real sem depender do lançamento da auxiliar.

### Interface mobile

- **Mini calendário mensal** no topo — pontinhos nos dias com eventos, navegação por mês
- **Três visões:** Mês / Semana (padrão) / Dia
- **Cards grandes e tocáveis** — tipo, hora, nome, local. Fácil ao sol, fácil com o polegar
- **Dois botões por visita:** ✓ Realizei (verde) · ✗ Não fui (terracota)
- **Visita realizada** — card esmaecido com ✓ verde e "relatório enviado via WhatsApp"
- **Botão "+ Novo evento" fixo no rodapé** — sempre visível
- **Badge de sincronização** — "✓ Atualizado às HH:MM"

### Perfil de acesso

- Login pelo celular → cai direto no calendário
- Vê todos os eventos (das 6 fontes — seção 28)
- Confirma visitas da própria guarnição
- Cria eventos avulsos (aparecem para todos)
- **Não acessa:** Ocorrências, VCM, Central de Atendimento, projetos, nada mais

### Arquivo de referência

`mockup_calendario_mobile_guarnicao.html`

### Checklist para o Claude Code

- [ ] Criar visão mobile responsiva do calendário (viewport 390px)
- [ ] Mini calendário mensal com pontinhos por dia
- [ ] Cards de evento com botões de confirmação
- [ ] `confirmarVisita(id, resultado)` → grava em Sheets + atualiza `state`
- [ ] Botão "+ Novo evento" flutuante → modal simples (título, data, hora, tipo)
- [ ] Perfil `guarnicao` → login redireciona para calendário mobile
- [ ] Sincronização das três camadas (seção 30) — especialmente crítico com múltiplos celulares

---

## 48. Eventos recuperáveis da planilha — mapa completo

### Diagnóstico

| Fonte | Total | Futuros | Passados | Observação |
|---|---|---|---|---|
| `eventos_avulsos` | 70 | **11** | 59 | Dados reais — migrar diretamente |
| `Agendamentos` | 2.530 | **2** | 2.528 | Só 2 com data futura |
| **Total recuperável** | — | **13** | — | Prontos para o novo calendário |

### Os 11 eventos avulsos futuros (dados reais)

- SENASP Capacitação — 23, 24 e 25/06
- [CONSEG] Chapas — 20/06
- [CONSEG] Apresentação de Chapas — 15/06 às 19h
- Campanha do Agasalho — 15/06
- São João — 13/06
- Organização do Evento Projeto — 16/06 às 08h30
- Evento Adote um Pequeno Leitor — 18/06 às 14h
- Visita a Idosos — 24/06 às 08h30
- BURITI - fixo no Fisco — 15/09

### Estrutura dos eventos avulsos — já está ótima

```
id, data, hora, tipo, titulo, descricao, cor, status, resultado, criadoEm
```

O novo calendário lê direto dessa estrutura — sem conversão.

### O que fazer com os passados

- **Eventos avulsos passados (59):** ficam como histórico consultável. Não aparecem no calendário futuro.
- **Agendamentos passados (2.528):** filtrar por `status = Agendado` (390 registros) e exibir numa tela de "agendamentos não confirmados" — a auxiliar revisa e marca o que foi realizado progressivamente.

### Checklist para o Claude Code

- [ ] Ao carregar o calendário: filtrar `eventos_avulsos` por `data >= hoje`
- [ ] Ao carregar o calendário: filtrar `Agendamentos` por `data >= hoje`
- [ ] Histórico de passados: acessível por filtro, não carregado por padrão
- [ ] Tela de revisão de agendamentos vencidos para a auxiliar

---

## 49. Logo da BCS — integração no sistema

### Logo

Logo oficial da BCS Nova Cidade — duas mãos se cumprimentando em círculo azul-marinho. Texto "Base Comunitária de Segurança · Nova Cidade".

### Tratamento

- Original: 500×500, fundo preto
- Versão tratada: `logo_bcs_circulo.png` — recortada em círculo, fundo transparente (RGBA)
- Assenta sobre o pergaminho sem o quadrado preto destoar

### Onde aparece

| Local | Tamanho | Detalhe |
|---|---|---|
| Tela de login | 140px | Centralizado, destaque principal |
| Topo da sidebar | 42px | Ao lado do nome "IARA" |
| Cabeçalho PDFs | 60px | Faixa azul (#1B3A6B) ao lado do título |
| Marca d'água | Grande, 6% opacidade | Fundo dos relatórios |
| Formulários públicos | Médio | Devolutiva e inscrição |

### Documentos que levam o logo

Dossiê da vítima · Relatório semanal · Relatório mensal · Ata do conselho · Termo de inscrição · Relatório de inventário

### Nomenclatura correta

BCS Nova Cidade · 77ª CIPM · Vitória da Conquista-BA

### Checklist para o Claude Code

- [ ] Adicionar `logo_bcs_circulo.png` aos assets
- [ ] Logo na tela de login (140px, centralizado)
- [ ] Logo no topo da sidebar ao lado de "IARA" (42px)
- [ ] Logo em todos os cabeçalhos de PDF (faixa azul #1B3A6B)
- [ ] Marca d'água 6% opacidade nos relatórios
- [ ] Logo nos formulários públicos (devolutiva + inscrição)
- [ ] Embutir como base64 no HTML para não depender de URL externa


---

## 50. Armamento (Livro de Parte) × Inventário Patrimonial — separação arquitetural

### O problema atual

Hoje os dois estão grudados no mesmo módulo. A carga de armamento (`_armAtualizarInventarioAposCarga`) altera o inventário a cada operação. Isso embaralha duas naturezas diferentes e é parte do motivo dos dados patrimoniais virem trocados.

### Duas naturezas distintas

| | Livro de Parte (Armamento) | Inventário Patrimonial |
|---|---|---|
| Natureza | Dinâmico, operacional | Estático, contábil |
| Frequência | Muda todo dia | Muda raramente |
| Pergunta que responde | "Quem está com a arma agora?" | "O que a base possui?" |
| Registra | Arma, policial, carga/descarga, hora | Patrimônio fixo da base |

### Arquitetura decidida

Ambos **dentro do IARA**, mas em abas/planilhas separadas:

```
IARA
 ├── Módulo Armamento (Livro de Parte)
 │     aba: carga_armamento — dinâmica
 │     LÊ do inventário, NÃO altera
 │
 └── Módulo Inventário (Patrimonial)
       aba: inventario_patrimonio — estável
       fonte da verdade sobre o que existe
```

### Regra de ouro

O livro de parte **consulta** o inventário (para listar armas disponíveis na carga) mas **nunca escreve** nele. Isso quebra o acoplamento que embaralha os dados hoje.

### Por que dentro do IARA e não planilha externa

- Uma interface só — uma aprendizagem só para a auxiliar
- Sincronização unificada (as três camadas da seção 30 valem para os dois)
- Vínculo de leitura confiável (sem ponto de falha de sincronização externa)
- O inventário fica limpo — a carga diária não mexe nele

### Migração

- O usuário já tem as listas de itens patrimoniais → importar direto para `inventario_patrimonio`
- Os 8 itens atuais de `materiais_patrimonio` (com campos trocados) → remapear e migrar para a nova aba limpa
- Remover a função `_armAtualizarInventarioAposCarga` que escreve no inventário
- Substituir por `_armConsultarInventario` que apenas lê

### Checklist para o Claude Code

- [ ] Criar aba `inventario_patrimonio` separada (estável, contábil)
- [ ] Manter aba `carga_armamento` para o livro de parte (dinâmica)
- [ ] Remover `_armAtualizarInventarioAposCarga` (acoplamento que altera inventário)
- [ ] Criar `_armConsultarInventario` — leitura apenas, lista armas para a carga
- [ ] Importar as listas patrimoniais do usuário para `inventario_patrimonio`
- [ ] Migrar e remapear os 8 itens de `materiais_patrimonio`
- [ ] Livro de parte e inventário compartilham a sincronização (seção 30)
- [ ] Aplicar design pergaminho nos dois módulos

### ⚠️ Nota de reconciliação com o código real (app_script.txt + index.html)

Confronto da seção 50 com o código vigente. O verdadeiro problema é **maior e diferente** do que a seção previa — não é "acoplamento a desfazer", são **dois sistemas de inventário paralelos coexistindo**. Corrigir antes de levar ao Claude Code.

**Achado central: existem DOIS inventários no app, e eles não se encontram.**

```
TRILHO A — materiais_patrimonio (legado)     TRILHO B — inv_itens (atual, da tela)
────────────────────────────────────────     ──────────────────────────────────────
salvarCargaArmamento → carga_armamento ✅      renderInventario (seção 45) ✅
   ↓                                              ↓
_armAtualizarInventarioAposCarga               _invSalvarItem / _invAbrirMovimentacao
(index.html ~13757, chamada ~14469)            / _invSalvarConferencia
   ↓ escreve em                                   ↓ _invEnviarSheets / _invSincronizarDoSheets
state.materiaisPatrimonio                      state.invItens / invMovimentacoes / invConferencias
   ↓ _sincSheets (~901)                           ↓
aba materiais_patrimonio ✅                     abas inv_itens / inv_movimentacoes / inv_conferencias ✅
(campos: codigo, serie)                        (campos: numero_serie, tombamento, localizacao)

            ╳  OS DOIS TRILHOS NÃO SE ENCONTRAM  ╳
```

**1. Ambos os trilhos estão completos front↔back — o problema não é técnico de sincronização.**
- Trilho B (`inv_*`) tem handlers no backend (app_script.txt linhas ~1225-1697, via `_salvarJson`/`_listarJson`). É o `renderInventario` "bem construído" da seção 45. Funciona inteiro.
- Trilho A (`materiais_patrimonio`) também sincroniza (backend ~514-585, frontend ~901). Funciona, mas é legado.

**2. A ruptura real:** quando uma arma recebe carga, `_armAtualizarInventarioAposCarga` (~14469) escreve no **Trilho A** (`materiaisPatrimonio`). Mas a tela de inventário que o usuário abre renderiza o **Trilho B** (`invItens`). **A arma carregada nunca aparece no inventário que o comandante vê.** O vínculo Armamento→Inventário da seção 45/50 está ligado ao trilho errado (morto).

**3. Os "8 itens com colunas trocadas" (seção 45) estão no Trilho A.** Por isso ninguém os corrigiu — ficam numa aba que a interface principal não exibe. Corrigir colunas lá não resolve nada enquanto o trilho não for reconectado ou aposentado.

**4. Premissas desatualizadas da seção 50:**
- A aba `inventario_patrimonio` que a seção manda "criar" não existe e não precisa: o inventário real já é `inv_itens`.
- `_armConsultarInventario` não existe (nem precisa criar com esse nome).
- Não há nada a "remover do backend" — o acoplamento é só no frontend (~14469).

**✅ DECISÃO TOMADA — Opção 1: unificar no Trilho B.**
A carga de armamento passa a refletir em `state.invItens` (Trilho B). O Trilho A (`materiais_patrimonio`) é aposentado e os 8 itens migram para `inv_itens`.
Justificativa: o Trilho B é o inventário que o usuário já usa, está completo (itens, movimentação, conferência, validade, foto) e tem backend pronto. O reflexo automático da carga no inventário é útil ao comandante (ver a arma em uso sem cadastro duplicado). Respeita a decisão original da seção 50 de manter armamento e inventário dentro do IARA. Custo baixo: reescrever uma função + migrar 8 itens.
Opção 2 (desligar o vínculo) foi descartada — devolveria o controle ao manual e separaria o que a seção 50 quis manter junto.

**Checklist corrigido (substitui o da seção 50):**
- [x] DECIDIDO: Opção 1 — unificar no Trilho B (ver decisão acima)
- [ ] Reescrever `_armAtualizarInventarioAposCarga` (~14469) para gravar em `invItens` + `_invEnviarSheets`, não em `materiaisPatrimonio`
- [ ] Migrar os 8 itens de `materiais_patrimonio` (remapeados, seção 45) para `inv_itens`
- [ ] Aposentar Trilho A: `state.materiaisPatrimonio`, `_armMigrarParaInventario`, `_sincSheets("materiais_patrimonio")`, aba `materiais_patrimonio`
- [ ] NÃO criar `inventario_patrimonio` (inexistente e desnecessária — o alvo é `inv_itens`)
- [ ] Backend: nada a remover; abas `inv_*` já existem (~1225-1697)
- [ ] Revalidar alerta de validade/conferência (Trilho B) após a unificação

### Verificação das funções essenciais do inventário (confronto com index.html)

| Função pedida | Estado | Onde |
|---|---|---|
| Registro de item completo | ✅ Completo | `_invSalvarItem` (~18436) — tombamento, descrição, categoria, marca/modelo, nº série, estado, localização, validade, foto (Drive), tamanho/gênero, carga fixa com responsável+liberador+assinatura |
| Movimentação — registro | ✅ Completo | `_invConfirmarMovimentacao` (~18624) — origem→destino, motivo, autorizador+receptor com matrícula e assinatura; atualiza localização |
| Movimentação — histórico por item | ✅ Completo | `_invVerHistorico` (~18662) — movimentações + cargas/descargas do Livro de Parte cruzadas por tombamento |
| Movimentação — visão/busca por policial | ✅ Completo | `_invRenderPoliciais` (~19125) + busca `_invFiltrarPoliciais` + `_invTermoResponsabilidade` + `_invDevolverItem` |
| **Movimentação — RELATÓRIO PDF de carga/descarga** | ❌ **Não existe** | `_invGerarPDF` (~19446) lista o inventário com responsável atual, NÃO o movimento. Não há PDF de carga/descarga por policial nem por item — só consulta em tela |
| Conferência — fluxo completo | ✅ Completo | `_invAbrirConferencia` (~18743) → conferir item a item → 2 responsáveis com assinatura → conclui |
| Conferência — relatório com base na fonte | ✅ Completo | `_invSalvarConferencia` (~18831) gera `_invGerarPDFConferencia` ao concluir. Confere contra `invItens` (Trilho B) — coerente com a decisão Opção 1 |

**Pendência única — relatório de movimentação (carga/descarga):**
- [ ] Criar PDF de relatório de movimentação, com dois recortes: **por policial** (todas as cargas/descargas de um policial no período) e **por item** (todo o trânsito de um item). Hoje esses dados existem em `state.invMovimentacoes` + `state.cargasArmamento`, mas só são exibidos em tela (`_invVerHistorico`, `_invRenderPoliciais`) — falta a saída em PDF.
- [ ] Reaproveitar o cruzamento por tombamento já feito em `_invVerHistorico` (movimentações + Livro de Parte) para o recorte por item.
- [ ] Filtro de período (data inicial/final) no relatório.

### Cadastro de itens e de policiais (confirmação)

| Função | Estado | Onde |
|---|---|---|
| Lançar novo item (manual, sem importação) | ✅ Existe | Botão "+ Novo Item" (~18901) → `_invAbrirItem(null)` → formulário completo `_invSalvarItem`. Também "+ Adicionar" na lista vazia (~18983) e "✏️ Editar" por item (~19045) |
| Cadastro de policiais | ✅ Existe | Módulo "➕ Cadastrar Policial" `_polSalvar` (~14048-14137) — validação de matrícula duplicada, contagem de ativos, editar/excluir; sincroniza com aba `policiais` (`salvarPolicial`) |

**Melhoria recomendada — vincular responsável do item ao cadastro de policiais:**
No formulário de item, a carga fixa pede nome e matrícula do responsável como **texto livre** (`inv-carga-nome`, `inv-carga-mat`, ~18356-18357) — não puxa do cadastro de policiais. Risco: nome digitado divergente do policial cadastrado quebra a visão por policial (`_invRenderPoliciais`) e o termo de responsabilidade (`_invTermoResponsabilidade`), que agrupam por nome/matrícula.
- [ ] Trocar os campos de texto livre do responsável (e do liberador) por um seletor que busca em `state.policiais`, preenchendo nome + matrícula automaticamente. Manter opção de texto livre só como fallback.

### ⚠️ Adequação às listas oficiais da fonte (RELATORIO_ARMA / COLETE / MUNIÇÃO / SIAP)

Os "PDFs" da fonte são, na verdade, pacotes ZIP com imagens escaneadas + OCR das listas oficiais do CMB/SISBM (consulta de Débora Batista, 11/06/2026). Confronto com o esquema de `inv_itens` (Trilho B):

**1. A migração Trilho A→B JÁ ocorreu nos dados.** `inv_itens` contém itens com prefixo `inv_arm_MAT-...` e campo `_matId` (arma SEY77939, colete, carregadores, munição). No `materiais_patrimonio` (Trilho A) os itens estão `status: excluido`, exceto um resíduo (FTG48). A decisão Opção 1 está praticamente executada nos dados — falta só limpar o código (remover `_armAtualizarInventarioAposCarga`/`materiaisPatrimonio` e o resíduo).

**2. Descompasso de esquema entre as listas oficiais e `inv_itens`:**

| Lista (código) | Colunas da fonte | Cobertura no nosso fluxo |
|---|---|---|
| ARMA (Rel 01) | ID, SÉRIE, MODELO, CALIBRE, UNIDADE, CIDADE, SITUAÇÃO | ❌ falta `calibre`; ❌ `situação` oficial não mapeia em `INV_ESTADOS` |
| COLETE (Rel 08) | ID, Nº SÉRIE, VALIDADE, MARCA, UNIDADE, CIDADE, SITUAÇÃO | ✅ `data_validade` existe; ❌ `situação` oficial (ver item 3) |
| MUNIÇÃO (IM-01) | UNIDADE/CIDADE, GUIA, CALIBRE/MODELO, QTD, BAX, EST | ❌ modelo inexistente — ver item 4 |
| SIAP | Patrimônio, Patr.Antigo, Descrição, Dt.Aquisição, Sit.Física, Valor, Conta Contábil | ❌ falta `valor`, `conta_contabil`, `patr_antigo` — ver item 4b |

**3. Valores de SITUAÇÃO da fonte não batem com `INV_ESTADOS`.**
Fonte usa: `EM CONDIÇÕES DE USO`, `INSERVÍVEL`, `CARGA PESSOAL`. Enum atual: `otimo, bom, com_defeito, inservivel`.
- `INSERVÍVEL` → mapeia em `inservivel` ✅
- `EM CONDIÇÕES DE USO` → aproxima de `bom` (perda de fidelidade)
- `CARGA PESSOAL` → NÃO é estado de conservação, é situação de posse → deveria virar `tipo_carga: "pessoal"` + responsável, não um estado.
- [ ] Separar "estado de conservação" (INV_ESTADOS) de "situação/posse" (disponível / carga pessoal / carga fixa / inservível). Dois eixos distintos.

**4. Munição não é suportada pelo fluxo atual (gap mais grave).**
`inv_itens` é um-item-por-linha com nº de série. Munição na fonte é granel por quantidade: guia + calibre/modelo + QTD + BAX (baixa) + EST (saldo). Não há série; controle é de saldo com baixas. Cadastrar 5000 munições como 5000 linhas é inviável.
- [ ] Criar tratamento de munição como categoria de saldo/lote: `guia`, `calibre_modelo`, `qtd`, `baixa`, `saldo`, `data_guia`. Movimentação de munição = baixa de quantidade, não troca de localização.
- [ ] "Munição" já é subcategoria de material_belico, mas precisa de formulário e relatório próprios (granel), distintos do item serial.

**4b. SIAP — inventário patrimonial contábil (4º layout, o maior: 16 páginas).**
`Inventário Geral agrupado por Conta Contábil` (PMBA/SIAP, ref. 09/06/2026). É o patrimônio geral da base (TVs, computadores, scanners, projetores…), não bélico. Campos: `Patrimônio`, `Patr. Antigo`, `Descrição` (concatena marca/série/specs no texto), `Dt. Aquisição`, `Sit. Física`, `Valor Aquisição`, agrupado por `Conta Contábil` (1.1, 2.1…). Encaixa bem no Trilho B (é o "Inventário Patrimonial" da seção 50), mas faltam:
- [ ] Campo `valor_aquisicao` (R$) — relevante para inventário contábil/auditoria
- [ ] Campo `conta_contabil` + agrupamento por conta no relatório PDF
- [ ] Campo `patrimonio_antigo` (tombamento secundário)
- [ ] Parser para descrição concatenada da fonte (extrair marca/série/specs do texto livre "DESCRICAO: … MARCA: … SERIE: …")
- [ ] Mapear `Sit. Física` (BOM…) para `INV_ESTADOS` (mesmo problema do item 3)

**São 4 layouts de fonte, não 3:** ARMA (serial), COLETE (serial+validade), MUNIÇÃO (granel/saldo), SIAP (contábil com valor/conta). A importação precisa de 4 perfis.

**5. Importação precisa reconhecer 3 layouts distintos.**
`_invAutoMapCols`/`_invParseLinhas` (~19581) fazem auto-map genérico. As listas oficiais têm cabeçalhos fixos e diferentes por tipo.
- [ ] Adicionar perfis de importação por tipo (Rel 01 arma, Rel 08 colete, IM-01 munição, SIAP contábil), com mapeamento fixo e detecção pelo cabeçalho/código do relatório.

**6. Campos a acrescentar em `inv_itens`:** `calibre` (arma/munição), `guia`+saldo (munição), `situacao_posse` (separada do estado). Acrescentar sem quebrar os itens já migrados.

**Resumo:** o Trilho B é sólido para patrimônio genérico, mas NÃO está adaptado às listas oficiais — perde calibre e situação de arma/colete e não comporta munição (granel). Antes de importar a fonte de verdade, o modelo precisa desses ajustes.


---

## 51. Inventário — modelo de conferência completo

### Conceito

O inventário trabalha em ciclos de conferência. O fluxo separa quem importa (comandante, com a lista pronta) de quem confere (policial, no campo, enriquecendo item por item).

### Fluxo em três etapas

```
1. IMPORTAR LISTA
   Upload da lista de itens (já pronta)
   → itens entram no sistema sem cadastro manual
        ↓
2. CONFERÊNCIA FÍSICA
   Policial confere item por item:
   → foto (Drive) + localização + estado + observações
        ↓
3. RELATÓRIO FINAL
   PDF com tudo conferido + assinatura digital do responsável
   → documento oficial para anexo
```

### Etapa 1 — Importar lista

- Upload de lista (CSV, XLSX ou colar texto)
- Cada item entra com: nome, categoria, número de série
- Não precisa de cadastro manual — a lista já vem pronta
- O comandante já tem as listas dos itens

### Etapa 2 — Conferência física

Para cada item, o policial registra:
- **Foto** — mostrando número de série e estado (salva no Drive, link na planilha — lógica `_invUploadFoto` já existe)
- **Localização** — onde está guardado (ex.: "Armário 2, Prateleira B")
- **Estado de conservação** — bom / regular / danificado
- **Observações** — texto livre (ex.: "bateria com desgaste")
- Botão "Confirmar conferência deste item" → marca como conferido

**Busca na lista (essencial):**
- Campo de busca no topo da lista de itens
- Filtra por nome, número de série ou categoria
- Com 47+ itens, busca é indispensável

**Indicadores visuais:**
- Item conferido: check verde + borda verde
- Item pendente: borda âmbar
- Barra de progresso: "28/47 itens conferidos · 60%"

### Etapa 3 — Relatório final com assinatura

- Quando todos os itens estão conferidos, gera o relatório
- **Assinatura digital no final** — o responsável assina o relatório completo de uma vez (não item por item)
- Assinatura salva no Drive, link registrado no ciclo de conferência
- Relatório PDF: lista completa com fotos, localizações, estados, observações + assinatura
- Documento oficial para anexo

### Conferências avulsas

- Não amarradas a calendário fixo — abrir quando necessário (semestral, troca de comando, auditoria)
- Cada conferência é um ciclo independente: data de abertura, responsável, data de fechamento, relatório assinado
- Histórico guarda todos os ciclos — permite comparar conferências (o que mudou, sumiu, se desgastou)

### Modelo de dados

```javascript
conferencia {
  id            string
  titulo        string    // "Conferência de Junho/2026"
  responsavel   string
  dataAbertura  date
  dataFechamento date
  status        string    // aberta | fechada
  assinatura_drive_link string  // assinatura do relatório final
  itens_conferidos int
  itens_total      int
}

item_conferido {
  conferencia_id string
  item_id        string
  foto_drive_link string
  localizacao    string
  estado         string    // bom | regular | danificado
  observacoes    string
  conferido_em   datetime
}
```

### Arquivo de referência

`mockup_inventario_conferencia.html`

### Checklist para o Claude Code

- [ ] Tela de conferência em 3 etapas (importar → conferir → relatório)
- [ ] Importação de lista (CSV/XLSX/colar) para `inventario_patrimonio`
- [ ] Campo de busca na lista (filtra nome, série, categoria)
- [ ] Conferência item por item: foto + localização + estado + observações
- [ ] Reaproveitar `_invUploadFoto` e `_invComprimirFoto` (já existem) para a foto no Drive
- [ ] Barra de progresso da conferência
- [ ] Assinatura digital ao fechar a conferência (relatório completo) → Drive
- [ ] Conferências avulsas — cada uma um ciclo independente
- [ ] Histórico de conferências para comparação
- [ ] Relatório PDF final com fotos, dados e assinatura
- [ ] Miniatura da foto na lista de itens
- [ ] Aplicar design pergaminho (seção 24)


---

## 52. Inventário — sistema de cargas com rastreabilidade

### Origem e destino dos itens

Todo item nasce no **almoxarifado** e pode seguir três caminhos:

| Situação | Descrição | Quem assina |
|---|---|---|
| **Em estoque** | Guardado no almoxarifado, sem responsável individual | Almoxarife/base |
| **Carga individual (fixa)** | Entregue a um policial específico, responsabilidade pessoal permanente | O próprio policial |
| **Carga de seção** | Entregue a uma seção/setor | O chefe da seção |

### Ciclo de carga

```
ALMOXARIFADO (em estoque)
      ↓ entrega (assinatura)
      ├──→ CARGA INDIVIDUAL → policial assina
      └──→ CARGA DE SEÇÃO → chefe da seção assina
      ↓ devolução (assinatura)
ALMOXARIFADO
```

### Regra de assinatura

**Cada movimentação gera uma assinatura** — tanto a entrega quanto a devolução. Isso cria uma cadeia de custódia completa. A assinatura vai para o Drive, o link fica registrado na movimentação.

### Histórico por item (rastreabilidade)

Cada item tem uma linha do tempo de cargas. Exemplo:

```
Pistola SEY77939
├── 10/01/2026 · Carga individual → Cb. Santos (assinou) ✓
├── 15/03/2026 · Devolução → almoxarifado (Cb. Santos assinou) ✓
├── 20/03/2026 · Carga de seção → Seção Operacional (Sgt. Lima assinou) ✓
└── 11/06/2026 · em carga · Seção Operacional
```

Em qualquer momento o sistema mostra a **carga atual** (de quem é agora) e o **histórico completo** (por onde passou). Se um item some, há registro do último responsável assinado.

### Modelo de dados

```javascript
item_patrimonio {
  id, nome, categoria, numero_serie
  situacao_carga    // em_estoque | carga_individual | carga_secao
  responsavel_atual // policial ou seção (null se em estoque)
  foto_drive_link
  localizacao
  estado
}

movimentacao_carga {   // uma linha por movimento — é o histórico
  id
  item_id
  tipo              // entrega | devolucao
  modalidade        // individual | secao
  responsavel       // quem recebe/devolve a carga
  assinante         // quem assina (policial ou chefe da seção)
  assinatura_drive_link
  data_hora
  observacao
}
```

### Relação com o Livro de Parte (armamento)

São duas camadas distintas:
- **Carga patrimonial (este módulo)** — a posse: de quem é o item, fixo. Muda raramente.
- **Livro de parte (armamento)** — o uso diário: o policial pega e devolve a arma a cada turno. Muda todo dia.

Uma arma pode ter carga individual fixa (é do policial) e ainda assim aparecer no livro de parte diário (pega/devolve). As duas camadas coexistem sem conflito.

### Integração com a conferência

Na conferência (seção 51), o item já mostra de quem é a carga atual. Isso ajuda a auditar: um item em carga individual deveria estar com o responsável, não no armário. A conferência verifica se a carga registrada bate com a realidade física.

### Checklist para o Claude Code

- [ ] Adicionar `situacao_carga` e `responsavel_atual` em `inventario_patrimonio`
- [ ] Criar aba `movimentacao_carga` (histórico de cargas)
- [ ] Tela de entrega de carga: escolher modalidade (individual/seção) + responsável + assinatura
- [ ] Tela de devolução: registrar + assinatura
- [ ] Assinatura de cada movimentação salva no Drive
- [ ] Linha do tempo de cargas na ficha de cada item
- [ ] Carga atual sempre visível no item (badge: em estoque / com [nome] / seção [nome])
- [ ] Integração com a conferência — mostrar carga atual ao conferir
- [ ] Manter separação: carga patrimonial ≠ livro de parte diário


---

## 53. Separação Armamento × Inventário — cirurgia no código

### O problema em detalhe

Existem três pontos no código que criam o acoplamento errado:

**Ponto 1 — linha 14469** (o mais crítico)
Toda vez que uma carga nova é sincronizada, chama `_armAtualizarInventarioAposCarga(r)`:
```javascript
if(!ex){ state.cargasArmamento.push(r); novas++; _armAtualizarInventarioAposCarga(r); }
```
Isso faz a carga de armamento **escrever** no inventário a cada sync.

**Ponto 2 — função `_armAtualizarInventarioAposCarga` (linha 13757)**
Recebe uma carga e altera diretamente os campos de `state.invItens`:
- `item.tipo_carga`, `item.localizacao`, `item.carga_responsavel_nome`, etc.
- Chama `_invEnviarSheets("inv_item", item)` → grava no Sheets
Esta função faz a carga **sobrescrever dados do inventário patrimonial**.

**Ponto 3 — função `_armMigrarParaInventario` (linha 13692)**
Copia itens de `materiaisPatrimonio` para `invItens` mesclando as duas coisas.
Tem lógica útil (o mapeamento de tipos) mas o conceito é errado — mistura as origens.

### O que o Claude Code deve fazer

**REMOVER da linha 14469:**
```javascript
// ANTES (remover esta chamada):
if(!ex){ state.cargasArmamento.push(r); novas++; _armAtualizarInventarioAposCarga(r); }

// DEPOIS (sem a chamada):
if(!ex){ state.cargasArmamento.push(r); novas++; }
```

**REMOVER a função inteira `_armAtualizarInventarioAposCarga` (linhas 13757–13795)**
```javascript
// REMOVER TODO ESTE BLOCO:
function _armAtualizarInventarioAposCarga(carga){ ... }
```

**REMOVER ou desativar `_armMigrarParaInventario` (linhas 13692–13755)**
O botão "Migrar para Inventário" some do UI. A importação passa a ser feita
pelo novo fluxo de upload de lista (seção 51).

**CRIAR `_armConsultarInventario(codigo)` — só leitura:**
```javascript
// Substitui _armStatusInventario — lê o inventario_patrimonio, nunca escreve
function _armConsultarInventario(codigo){
  if(!codigo) return null;
  var cod = codigo.toUpperCase();
  return (state.inventarioPatrimonio || []).find(function(x){
    return x.numero_serie && x.numero_serie.toUpperCase() === cod;
  });
}
```

**CRIAR aba `inventario_patrimonio` no Sheets** (separada de `inv_itens`):
- É a fonte da verdade do patrimônio
- O livro de parte lê dela via `_armConsultarInventario`
- A conferência (seção 51) e as cargas (seção 52) também operam sobre ela
- Nunca é alterada pelo livro de parte

### Resultado após a cirurgia

```
LIVRO DE PARTE (carga_armamento)
  _armConsultarInventario() ──lê──→ inventario_patrimonio
  NUNCA escreve no inventário

INVENTÁRIO (inventario_patrimonio)
  Alterado apenas por:
    - Upload de lista (seção 51)
    - Conferência física (seção 51)
    - Movimentação de carga patrimonial (seção 52)
```

### Checklist cirúrgico para o Claude Code

- [ ] Linha 14469: remover `_armAtualizarInventarioAposCarga(r)` da chamada de sync
- [ ] Linhas 13757–13795: remover função `_armAtualizarInventarioAposCarga` inteira
- [ ] Linhas 13692–13755: remover função `_armMigrarParaInventario` e seu botão no UI
- [ ] Criar função `_armConsultarInventario(codigo)` — leitura apenas de `inventario_patrimonio`
- [ ] Criar aba `inventario_patrimonio` no Sheets (separada de `inv_itens` e `materiais_patrimonio`)
- [ ] Importar lista patrimonial do usuário para `inventario_patrimonio`
- [ ] Verificar e remover outras referências a `_armAtualizarInventarioAposCarga` no código


---

## 54. Armamento × Inventário — correção cirúrgica (linhas exatas)
> Nota: complementa a seção 53 (não a substitui). Sujeita ao Aviso de Precedência item 1 — alvo é `inv_itens`, não `inventario_patrimonio`.

### O problema no código atual

Hoje o livro de parte (carga de armamento) **escreve** no inventário a cada operação. São três pontos de acoplamento incorreto:

**Ponto 1 — Linha 14469 (a chamada que dispara o problema)**
```javascript
// ATUAL — errado
if(!ex){ state.cargasArmamento.push(r); novas++; _armAtualizarInventarioAposCarga(r); }

// CORRETO — remover a chamada
if(!ex){ state.cargasArmamento.push(r); novas++; }
```

**Ponto 2 — Linhas 13757–13830 (`_armAtualizarInventarioAposCarga`)**
Função que altera `state.invItens` e chama `_invEnviarSheets("inv_item", item)` — ou seja, grava no Sheets do inventário a cada carga/descarga de arma.
```
→ REMOVER a função inteira (linhas 13757–13830)
```

**Ponto 3 — Linhas 13692–13756 (`_armMigrarParaInventario`)**
Função que copia itens do patrimônio para o inventário e cria vínculos `_matId`. Mistura as duas naturezas.
```
→ REMOVER a função inteira (linhas 13692–13756)
→ REMOVER o botão que a chama (buscar por '_armMigrarParaInventario()' na renderização)
```

### O que criar no lugar

**`_armConsultarInventario(codigo)`** — substitui `_armStatusInventario` mas deixa claro que é só leitura:
```javascript
// NOVA FUNÇÃO — só leitura, nunca escreve
function _armConsultarInventario(codigo) {
  if (!codigo) return null;
  var cod = codigo.toUpperCase();
  // Lê do inventario_patrimonio — nunca de invItens misturados
  return (state.inventarioPatrimonio || []).find(function(x) {
    return x.numero_serie && x.numero_serie.toUpperCase() === cod;
  });
}
```

**Nota:** `_armStatusInventario` (linha imediatamente após `_armMigrarParaInventario`) pode ser mantida mas deve ler de `state.inventarioPatrimonio` em vez de `state.invItens`.

### Resumo das mudanças

| Ação | O que | Linha(s) |
|---|---|---|
| REMOVER chamada | `_armAtualizarInventarioAposCarga(r)` | 14469 |
| REMOVER função | `_armAtualizarInventarioAposCarga` | 13757–13830 |
| REMOVER função | `_armMigrarParaInventario` | 13692–13756 |
| REMOVER botão | que chama `_armMigrarParaInventario()` | buscar na renderização |
| CRIAR função | `_armConsultarInventario` | nova |
| AJUSTAR | `_armStatusInventario` para ler `inventarioPatrimonio` | após 13756 |

### Checklist para o Claude Code

- [ ] Linha 14469: remover `_armAtualizarInventarioAposCarga(r)` da cadeia de sync
- [ ] Linhas 13757–13830: remover função `_armAtualizarInventarioAposCarga` inteira
- [ ] Linhas 13692–13756: remover função `_armMigrarParaInventario` inteira
- [ ] Buscar e remover botão "Migrar para Inventário" / "Atualizar Inventário" na renderização
- [ ] Criar `_armConsultarInventario(codigo)` — lê de `state.inventarioPatrimonio`, nunca escreve
- [ ] Ajustar `_armStatusInventario` para ler de `state.inventarioPatrimonio`
- [ ] Criar aba `inventario_patrimonio` separada de `materiais_patrimonio` e `inv_itens`
- [ ] Verificar que após as remoções o livro de parte ainda funciona (listar cargas, registrar carga/descarga)
- [ ] Testar: registrar uma carga e confirmar que `inventario_patrimonio` NÃO foi alterado


### ⚠️ Parecer da Comissão de Inventário — saída final ausente (RELATORIO PARECER_DA_COMISSAO_ROTATIVO_2025)

A fonte tem o documento oficial que deve coroar a conferência: **"Relatório Analítico de Inventário nº XXX/ANO — Parecer da Comissão"** (PMBA, exercício 2025, tipo Rotativo, 77ª CIPM). Hoje o `_invGerarPDFConferencia` (~19733) gera apenas uma checklist técnica (KPIs ok/divergência/ausente + tabela de itens + 2 assinaturas genéricas). **NÃO gera o parecer.** O parecer é o documento que vai para a árvore SEI / DAL — é o entregável real da conferência.

**Estrutura do parecer oficial (modelo a reproduzir):**

1. **Cabeçalho institucional:** PMBA → COPPM → CPRC-Central → 77ª CIPM + título "Relatório Analítico de Inventário nº ___/ANO ___ — Parecer da Comissão".
2. **Bloco de identificação:** Data de Conclusão, Tipo (Rotativo/…), Sigla da OPM, Código de Gestora, Área, Objeto, Exercício, Gestor da OPM, Chefe da SSO, Responsável pelo Almoxarifado.
3. **1. Considerações Iniciais:** texto citando a portaria de nomeação da comissão (nº, BIO), presidente e membros com nome + matrícula; objetivo dos trabalhos; rotina DAL-DAF de referência.
4. **2. Desenvolvimento:**
   - 2.1 Bens Permanentes — **10 categorias normativas fixas (a–j):** a) sem tombamento; b) plaqueta extraviada; c) não localizado/extraviado; d) obsoleto para desativação; e) descrição incorreta; f) recebido de outro órgão (carente de transferência); g) cedido a outro órgão; h) de terceiro (empréstimo/cessão); i) oriundo de convênio; j) inservível vinculado a convênio. Cada uma com texto ("Sem alterações" ou descrição).
   - "Outras dignas de registro" (ex.: permutas de viaturas).
   - 2.2 **Tabela de Quantificação (Bens Permanentes)** — categorias a–j + "Outras" + TOTAL, com quantidade.
   - 2.3 Bens de Consumo (apenas unidades gestoras) — subitens 2.3.1 a 2.3.5.
   - 2.4 Tabela de Quantificação (Bens de Consumo).
   - 2.5 Utilização do SIMPAS.
   - 2.6 Arrolamento e Vistoria de Bens Imóveis.
5. **3. Conclusão:** texto-síntese (não-conformidades encontradas, providências, encaminhamento ao DAL via SEI) + local e data.
6. **Assinaturas:** Presidente da Comissão + todos os membros, cada um com nome, posto e matrícula (não dois responsáveis genéricos como hoje).

**Relação com o fluxo atual:**
- As categorias do app (ok / divergência / ausente) NÃO mapeiam nas 10 categorias normativas. A conferência precisa permitir classificar cada divergência numa das categorias a–j (a mais comum aqui é "b) plaqueta extraviada").
- A comissão (presidente + membros) não existe como entidade no app. Precisa de cadastro de comissão por inventário (reaproveitar `state.policiais` para nome/matrícula/posto).
- O documento é por **exercício/ano** e numerado — precisa de numerador e campo de exercício.

**Checklist para o Claude Code:**
- [ ] Criar gerador de **Parecer da Comissão** como saída final da conferência (separado do relatório técnico atual, que pode permanecer como anexo de trabalho)
- [ ] Cadastro de Comissão de Inventário por exercício: presidente + membros (nome/posto/matrícula, via `state.policiais`), portaria de nomeação (nº + BIO)
- [ ] Bloco de identificação (gestor da OPM, chefe da SSO, responsável pelo almoxarifado, tipo, área, objeto, exercício, código de gestora)
- [ ] Classificar divergências da conferência nas 10 categorias normativas a–j (substituir/estender o ok/divergência/ausente)
- [ ] Tabela de quantificação automática por categoria (a–j + Outras + TOTAL) a partir das classificações
- [ ] Seções de Bens de Consumo (2.3/2.4), SIMPAS (2.5) e Bens Imóveis (2.6) — com fallback "A OPM não é Unidade Gestora" quando aplicável
- [ ] Texto de Conclusão editável + local/data automáticos
- [ ] Bloco de assinaturas de todos os membros da comissão (não 2 fixas)
- [ ] Numeração do parecer (nº/ano) e referência à rotina DAL-DAF
- [ ] Exportar em formato adequado para anexo na árvore SEI (PDF)

### ✅ Projetos Sociais — fluxo verificado e fechado

Confronto dos requisitos (cadastro de professores, cursos, candidatura de aluno com despacho → aluno) com o código (index.html + app_script.txt). **Diferente do inventário, não há gaps estruturais — o módulo está completo nas duas pontas.**

| Requisito | Estado | Onde |
|---|---|---|
| Cadastro de instrutores/professores | ✅ Completo | `abrirCadastroInstrutor` (~8620): tipo PM/voluntário, graduação, nome, telefone, área, qualificação, PIN pessoal, assinatura digital, obs. Portal próprio (`renderPortalInstrutor`, login `fazerLoginInstrutor`), termo de voluntário |
| Cadastro de cursos | ✅ Completo | `abrirModalNovoCurso` (~7756), `renderCursosComunitarios`, `gerarCardCurso`, `excluirCurso`. Seed com 10 projetos reais |
| Candidatura de aluno | ✅ Completo | Inscrição via QR (`_qrCandidatura`), PDF (`_pdfCandidatura`), aba backend `candidaturas` (`salvarCandidatura`, ~1151-1613) |
| Despacho da candidatura (aprovar/recusar) | ✅ Completo | `_decidirCandidatura` (~8199) — aprovação EXIGE assinatura do gestor (modal canvas) → `_confirmarDecisaoCandidatura` grava status + assinatura. Recusa direta |
| Candidatura aprovada → aluno do curso | ✅ Completo (modelagem elegante) | `_getAlunosProjeto` (~6453) deriva alunos das candidaturas com `status==="aprovado"` por projeto. Não duplica cadastro — o aluno É a candidatura aprovada. Mantém compat. com inscrições legadas |
| Chamada / presença | ✅ Bônus | Portal do instrutor + modal-chamada; aba backend `chamadas_projetos` |
| Monitoramento / relatórios | ✅ Bônus | Filtros por período/bairro, monitoramento, KPIs |

**Sincronização front↔back confirmada:**
- Candidaturas: aba dedicada `candidaturas` (JSON), handler `salvarCandidatura`/`listar candidaturas`. ✅
- Chamadas: aba `chamadas_projetos` com handler próprio. ✅
- Instrutores: via `salvarDadoAppSheets("bcs_instrutores_cad")` (armazenamento de app genérico, merge por id ~812) — não tem aba dedicada como candidatura, mas sincroniza e funciona. ✅

**Observações menores (não bloqueiam):**
- O instrutor sincroniza por mecanismo diferente (app-data genérico) do resto (abas dedicadas). Funciona, mas é inconsistência arquitetural — se algum dia quiser relatório SQL/planilha de instrutores, considerar migrar para aba própria.
- O vínculo curso↔instrutor é por nome (`c.instrutor` comparado por `.toLowerCase()`, ~12892/13160), não por id do instrutor cadastrado. Mesmo risco de divergência por digitação visto no inventário (responsável). Melhoria opcional: vincular por `INSTR_id`.

**Conclusão:** Projetos Sociais está fechado. Cobre professores, cursos, candidatura com despacho assinado e a virada candidato→aluno, além de chamada e monitoramento. As duas observações são refinamentos, não pendências.

### ⚠️ Projetos Sociais — identidade visual da jornada pública (pendência destacada)

Correção importante ao fechamento anterior: o fluxo *interno* de Projetos Sociais está completo, mas a **face pública** — que é divulgada na comunidade para o morador escolher um curso — ficou de fora da identidade visual "Pergaminho e Madeira" (seção 24) E está espalhada por páginas externas ao app. Como é material visto por cidadãos (o cartão de visitas do projeto), o peso é alto.

**A jornada pública do morador passa por TRÊS superfícies, nenhuma no pergaminho, duas fora do index.html:**

| Superfície | O que é | Onde mora | Visual atual |
|---|---|---|---|
| 🌐 Portfólio | Vitrine de cursos divulgada na comunidade | **Site externo** `bcs-iara.github.io/projetos` | Próprio (fora do controle do app) |
| 📝 Inscrição | Formulário onde o morador se candidata (destino do QR/card) | **Página externa** `inscricao.html` (NÃO está no pacote) | Roxo escuro (`#130d24`, `#c89ae8`) |
| 📋 Candidatura | Onde a inscrição entra no app para despacho | `index.html` aba Projetos Sociais | Roxo/escuro antigo |

**Problemas:**
1. **Nenhuma das três** usa o pergaminho/madeira. O módulo Projetos Sociais inteiro (no index.html) ainda está na paleta roxa antiga — a seção 35 esqueceu de marcar "aplicar design pergaminho", marcação que armamento (40), conselho (39) e inventário (45/50) receberam.
2. **Duas superfícies são externas** (`bcs-iara.github.io/projetos` e `inscricao.html`) e não estão no pacote enviado ao Code. O Claude Code não as alcança — precisam de tratamento à parte.
3. **Inconsistência de marca para o cidadão:** vitrine (site A) → inscrição (página B) → app (visual C). Três caras diferentes para a mesma iniciativa, vista pela comunidade.

**Checklist para o Claude Code (o que está dentro do app):**
- [ ] Aplicar design "Pergaminho e Madeira" (seção 24) em TODO o módulo Projetos Sociais (monitoramento, cursos, candidaturas, instrutores, relatório) — substituir a paleta roxa
- [ ] Aplicar pergaminho no card/QR do curso (`gerarCardCurso`) — é peça impressa/distribuída na comunidade
- [ ] Garantir que o QR continue funcional após a mudança visual (cor do QR sobre fundo claro)

**Pendências FORA do app (decisão + trabalho à parte, não vão pro Code com o index.html):**
- [ ] Portfólio externo (`bcs-iara.github.io/projetos`): decidir — alinhar o visual do site GitHub Pages ao pergaminho OU trazer a vitrine para dentro do app
- [ ] `inscricao.html`: localizar a fonte desta página (não está no pacote), aplicar pergaminho, manter sincronização das candidaturas
- [ ] Definir uma identidade visual única para as três superfícies públicas, já que o morador as vê em sequência

**Observação:** estas páginas externas precisam ser adicionadas ao pacote do projeto para que possam ser auditadas e ajustadas. Sem elas, a jornada pública fica sem cobertura.

### ✅ Portfólio público — direção visual aprovada (protótipo)

Definida e aprovada a nova identidade visual do portfólio de cursos (a vitrine divulgada na comunidade para o morador escolher um projeto). Entregue como protótipo navegável: **PORTFOLIO_PROTOTIPO.html**.

**Decisões de design aprovadas:**
- Padrão "Pergaminho e Madeira" (seção 24) — fundo creme, moldura madeira escura, destaques âmbar dourado, tipografia serifada (Fraunces). Resolve a divergência visual apontada na pendência anterior.
- Público-alvo: **morador da comunidade** escolhendo curso. Tom: equilíbrio entre acolhedor e institucional.
- **Logo oficial da BCS** (`logo_bcs_circulo.png` — as duas mãos, "Nova Cidade") no brasão do topo e no rodapé, com moldura dourada.
- Cada card de curso destaca: **ilustração temática** (placeholder para foto real), **vagas/horário** (badge verde com nº de vagas ou "vagas abertas") e **botão de inscrição** em evidência.
- Filtros por área (Educação, Esporte, Música & Arte, Tecnologia, Saúde & Bem-estar).
- Seção "Como participar em 3 passos" (escolher → inscrever → aguardar contato) para reduzir a barreira de inscrição.
- Os 10 cursos reais do seed do sistema (Pequeno Leitor, Informática, Acordes Mágicos, Luta Cidadã/Judô, Gravidez com Amparo, Empoderamento Feminino, Universidade para Todos/UESB, Robótica, Esporte por Toda Parte, Gibi Turma da BCS).

**Checklist para implementação:**
- [ ] Aplicar o layout do protótipo ao portfólio real (hoje em `bcs-iara.github.io/projetos`, site externo)
- [ ] Conectar os cards aos dados reais dos cursos via Sheets (como o portfólio atual já carrega), em vez de cursos fixos no HTML
- [ ] Ligar o botão "Quero me inscrever" de cada card ao formulário de inscrição (`inscricao.html`), passando o ID do curso
- [ ] Aplicar a mesma identidade pergaminho ao `inscricao.html` para a jornada pública ficar coesa (vitrine → inscrição → app)
- [ ] Substituir as ilustrações temáticas por **fotos reais** dos cursos quando a base disponibilizar
- [ ] Badge de vagas dinâmico: mostrar nº real de vagas restantes (vagas totais − candidaturas aprovadas) ou "vagas abertas" quando for fluxo contínuo

**Observação:** o protótipo é autocontido (logo embutido em base64) e serve como referência visual. As páginas externas (portfólio e `inscricao.html`) ainda precisam ser adicionadas ao pacote do projeto para serem efetivamente reconstruídas — ver pendência "identidade visual da jornada pública".

### 📋 Parecer — Projetos Sociais: fluxo aprovado, aparência a repaginar

Distinção entre as duas camadas, com base na verificação contra o código:

**Fluxo (lógica) — APROVADO, sem retrabalho.** A cadeia completa funciona front+back: instrutor → curso → candidatura (QR) → despacho com assinatura do gestor → vira aluno → chamada/presença → monitoramento. Modelagem boa (aluno = candidatura aprovada, sem duplicação). É o módulo mais maduro auditado. Sem buraco estrutural.

**Aparência — A REPAGINAR.** Todo o módulo está na paleta roxa antiga; a face pública (portfólio + inscrição) está em páginas externas com visual divergente. Já há protótipo novo do portfólio aprovado (ver seção correspondente).

**Refinamentos menores de lógica (não bloqueiam):** instrutor sincroniza por mecanismo diferente do resto; vínculo curso↔instrutor por nome em vez de id (risco de divergência por digitação).

**Veredito:** não refazer o fluxo — está bom. Investir na pele (pergaminho) e na jornada pública. Ver pendência transversal abaixo.

---

### 🎨 PENDÊNCIA TRANSVERSAL — Migração de identidade visual de TODO o sistema

**Diagnóstico do código real (junho/2026):** o padrão "Pergaminho e Madeira" (seção 24) está **0% implementado**. Medição no `index.html`:
- Cores da paleta nova (`#F2E4C8`, `#3E2A1A`, `#D9A53C`…): **0 ocorrências**
- Variáveis `--papel / --madeira / --ambar`: **não definidas**
- Paleta antiga (roxo/escuro `#1a0a28`, `#130d24`, `#a78bfa`…): **230+ ocorrências**

Ou seja, a identidade visual definida na seção 24 existe só na especificação. **Todo o sistema ainda usa a paleta antiga.** Isto não é ajuste pontual de um módulo — é um redesign transversal, de peso significativo, que toca todas as telas.

**Decisão do responsável:** *todo o sistema deve se adequar à nova identidade visual* (Pergaminho e Madeira, seção 24). Aplica-se a todos os módulos, não apenas aos que já tinham a marcação.

**Abordagem recomendada para o Claude Code:**
- [ ] **Passo 1 — fundação:** definir as variáveis CSS da seção 24 (`--papel`, `--papel-2/3`, `--madeira`, `--madeira-2/3`, `--tinta`, `--tinta-2`, `--ambar`, `--ambar-2`, `--verde`, `--verm`) em `:root`, uma única vez.
- [ ] **Passo 2 — estrutura:** aplicar nos elementos globais (sidebar madeira 230px, titlebar com borda âmbar 3px, fundo `--papel`, tipografia serifada nos títulos).
- [ ] **Passo 3 — por módulo, substituir a paleta antiga.** Ordem sugerida por visibilidade: (1) telas mais usadas — Central de Atendimento, Calendário, Ocorrências; (2) Projetos Sociais + jornada pública (portfólio/inscrição); (3) Painel do Comandante; (4) Módulos administrativos (Armamento, Inventário, Solicitações, Conselho).
- [ ] **Passo 4 — varredura final:** garantir 0 ocorrências das cores antigas (`#1a0a28`, `#130d24`, `#2a1040`, `#a78bfa`, `#c89ae8`, `#0e0820`) no `index.html`.
- [ ] Páginas externas (`inscricao.html`, portfólio): aplicar a mesma paleta — exigem ser adicionadas ao pacote primeiro.

**Atenção:** este é provavelmente o item de maior esforço de toda a auditoria (toca ~230+ pontos de cor + estrutura de layout). Recomenda-se tratá-lo como uma fase própria do trabalho do Code (Fase de Design), separada das correções funcionais, para não misturar mudança de comportamento com mudança de aparência num mesmo passo.
