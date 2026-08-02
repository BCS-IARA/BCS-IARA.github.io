# Fix — Botão de sync visível, bug do polling, e ligação Conferência ↔ Itens

Três mudanças independentes, todas em `index.html`. Pode aplicar juntas, são isoladas entre si.

## 1. Bug: polling reabre o seletor "Quem está conferindo?" a cada 30s

**Causa:** o polling automático (linha 23330-23335) chama `_invAbrirConferencia(idAtual)` pra atualizar a conferência aberta com dado novo do sync. Só que `_invAbrirConferencia` sempre passa por `_invAbrirConferencia2`, que **sempre** mostra o modal "Quem está conferindo?" (é proposital pra abertura normal — linha 22611: "Sempre pede quem está conferindo... sempre pergunta ao abrir"). Resultado: enquanto uma conferência está aberta, a cada 30 segundos o auxiliar leva esse popup de novo, no meio do trabalho. Isso provavelmente conta bastante pra sensação de "trava"/demora.

**Correção:** trocar pra chamar `_invRenderConferencia` diretamente — é a função que de fato desenha o modal com a lista de itens, sem passar pelo seletor de conferente (que só precisa ser perguntado uma vez, na abertura original).

Localizar (linha 23330-23335):
```javascript
      var modalAberto=document.getElementById("modal-inv-conf");
      if(modalAberto&&window._invConfAtual){
        var idAtual=window._invConfAtual.id;
        modalAberto.remove();
        _invAbrirConferencia(idAtual);
      }
```

Substituir por:
```javascript
      var modalAberto=document.getElementById("modal-inv-conf");
      if(modalAberto&&window._invConfAtual){
        modalAberto.remove();
        _invRenderConferencia(window._invConfAtual);
      }
```

## 2. Botão "Sincronizar" pouco visível no celular

O botão já existe (linha 23358), só está disputando espaço com 4-5 outros botões (Importar Lista, Limpar Tudo, Exportar PDF, PDF da Seção, + Novo Item) numa linha `flex-wrap`. Em tela de celular essa fileira empilha e o Sincronizar pode acabar não sendo o primeiro a aparecer.

**Correção:** mover o bloco do badge de status + botão Sincronizar (linhas 23355-23358) pra **antes** de `<div style='display:flex;gap:8px;...'>` abrir os outros botões — ou seja, ser sempre o primeiro item da fileira, garantindo que apareça primeiro tanto no desktop quanto quando a fileira empilha no celular. A ordem dos outros botões não muda.

(Se preferir, também dá pra fixar esse badge+botão fora da fileira que quebra, tipo um cabeçalho fixo no topo — mas a troca de ordem já resolve o "não achei" sem mexer em mais nada.)

## 3. Conferência: editar item completo + ligação com o cadastro geral

### 3a. Botão "Editar item completo" dentro do "+"

No painel expansível de cada item (`_invRenderConferencia`, mesmo bloco onde fica "📷 Anexar foto"), adicionar um botão que abre a ficha completa do item.

Logo após a linha do bloco de foto (a que tem `📷 Anexar foto de divergência` — se você já aplicou o `FIX_POLICIAIS_E_FOTO_CONFERENCIA.md`; se não aplicou ainda, é a linha com `📷 Anexar foto` original), adicionar:

```javascript
html+="<button type='button' onclick='_invConfEditarItem(\""+iid+"\")' style='align-self:flex-start;background:transparent;border:1px solid #A87B22;color:#6B5236;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer'>✏️ Editar item completo</button>";
```

E criar a função (perto de `_invConfExpandir`, linha ~22943):
```javascript
function _invConfEditarItem(itemId){
  _invAbrirItem(itemId);
}
```

### 3b. Salvar item: se a conferência estiver aberta atrás, atualizar ela também

`_invAbrirItem`/`_invSalvarItem` não sabem que podem estar sendo chamados de dentro de uma conferência. Sem isso, editar o item pelo botão acima fecha a ficha mas a conferência atrás continua com o dado antigo na tela (mesmo problema do item 1, versão "ao salvar" em vez de "ao sincronizar").

Em `_invSalvarItem` (linha ~22239, logo depois de `if(main) renderInventario(main);`), adicionar:
```javascript
  var modalConfAberto=document.getElementById("modal-inv-conf");
  if(modalConfAberto&&window._invConfAtual){
    modalConfAberto.remove();
    _invRenderConferencia(window._invConfAtual);
  }
```

### 3c. Localização/Estado/Observações da conferência atualizam o cadastro do item

Hoje esses três campos (preenchidos no "+") ficam isolados dentro de `conf.itens[id]`, nunca tocam o item de verdade — por isso não aparecem na aba Itens depois. Em `_invSalvarConferencia` (linha 23057), logo antes de `if(!state.invConferencias) state.invConferencias=[];` (linha 23076), adicionar:

```javascript
  // Propaga Localização/Estado/Observações marcados na conferência pro cadastro geral do item
  var _itensAtualizadosConf=[];
  Object.keys(conf.itens||{}).forEach(function(iid){
    var det=conf.itens[iid];
    if(!det||typeof det!=="object") return;
    var idxIt=(state.invItens||[]).findIndex(function(x){return x.id===iid;});
    if(idxIt<0) return;
    var it=state.invItens[idxIt];
    var mudou=false;
    if(det.localizacao && det.localizacao!==it.localizacao){ it.localizacao=det.localizacao; mudou=true; }
    if(det.estado && det.estado!==it.estado){ it.estado=det.estado; mudou=true; }
    if(det.observacoes && det.observacoes!==it.observacoes){ it.observacoes=det.observacoes; mudou=true; }
    if(mudou){ it.atualizadoEm=new Date().toISOString(); _itensAtualizadosConf.push(it); }
  });
  _itensAtualizadosConf.forEach(function(it){ _invEnviarSheets("inv_item", it); });
```

Importante: isso só propaga quando o auxiliar de fato preencheu algo no "+" — se ele só marcar OK/DIV/AUS sem expandir e editar nada, o item não é tocado. E só dispara no save (Salvar Progresso/Concluir), não a cada tecla digitada — evita ficar martelando o Sheets a cada caractere.

## Pendente — preciso do `app_script.txt` atual

Pra fechar de vez "ainda muita demora pra sincronizar entre os aparelhos", preciso confirmar se o lado do servidor (Apps Script) já tem o merge seguro de conferência com `LockService` que passei no `FIX_SYNC_INVENTARIO.md`. Você só me mandou o `index.html` atualizado — sem ver o `app_script.txt` atual não dá pra saber se essa parte já foi aplicada ou se ainda está sobrescrevendo conferências inteiras na gravação (o que causaria perda silenciosa mesmo com o cliente rápido). Pode subir o `app_script.txt` que está publicado?

## Teste

- Abrir uma conferência, deixar parado 35-40s (mais que o intervalo de polling) — confirmar que **não** aparece o popup "Quem está conferindo?" de novo.
- No "+", clicar "Editar item completo", mudar a descrição, salvar — confirmar que a conferência por trás atualiza com a nova descrição sem fechar.
- Preencher Localização num item dentro do "+", salvar progresso da conferência, depois abrir a aba Itens — confirmar que a localização nova aparece lá.
