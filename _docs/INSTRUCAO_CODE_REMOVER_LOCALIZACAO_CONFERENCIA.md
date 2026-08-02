# Remover campo "Localização" do painel de detalhe do item (conferência)

## Onde

`index.html`, dentro de `function _invRenderConferencia(conf){`, no loop
`catItens.forEach(function(item){...})`, no painel expandido pelo botão "+"
(`id='inv-ci-det-'+iid`).

## Por quê

O campo "Localização" desse painel é só do registro da conferência (não é a
localização cadastral do item). Estava confundindo o conferente — em vez de
preencher, as pessoas colam a localização dentro de "Observações" (como no
print: "Sala do comandante" foi parar em Observações). Solução: remover o
campo daqui. "Estado de conservação" continua, só deixa de dividir a linha
com Localização e passa a ocupar a linha sozinho, como "Observações" já faz.

## Alteração

Localizar:

```js
      html+="<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px'>";
      html+="<div><label style='color:#6B5236;font-size:10px'>Localização</label><input id='inv-ci-loc-"+iid+"' value='"+esc(det.localizacao||"")+"' placeholder='Ex.: Armário 2, Prateleira B' oninput='_invConfDetalhe(\""+iid+"\",\"localizacao\",this.value)' style='"+ISci+"'></div>";
      html+="<div><label style='color:#6B5236;font-size:10px'>Estado de conservação</label><select id='inv-ci-est-"+iid+"' onchange='_invConfDetalhe(\""+iid+"\",\"estado\",this.value)' style='"+ISci+"'>";
      ["","bom","regular","danificado"].forEach(function(v){html+="<option value='"+v+"'"+(det.estado===v?" selected":"")+">"+(v||"— selecione —")+"</option>";});
      html+="</select></div></div>";
```

Substituir por:

```js
      html+="<div><label style='color:#6B5236;font-size:10px'>Estado de conservação</label><select id='inv-ci-est-"+iid+"' onchange='_invConfDetalhe(\""+iid+"\",\"estado\",this.value)' style='"+ISci+"'>";
      ["","bom","regular","danificado"].forEach(function(v){html+="<option value='"+v+"'"+(det.estado===v?" selected":"")+">"+(v||"— selecione —")+"</option>";});
      html+="</select></div>";
```

(removeu a `<div>` grid de 2 colunas e o campo Localização; "Estado de
conservação" vira uma linha própria, com o mesmo `<select>`, mesma lógica.)

## Fora de escopo

- Não mexer em `_invConfDetalhe`, nem no campo `localizacao` do registro do
  item em si (`item.localizacao`, usado em Itens/Localizações) — só o campo
  de digitação dentro do painel de conferência some.
- Não mexer em Observações nem no botão "Anexar foto de divergência".
- Se sobrar algum dado antigo salvo em `conf.itens[id].localizacao` de
  conferências anteriores, não precisa limpar — só não vai mais aparecer
  campo para editar isso; não quebra nada (a propagação em
  `_invSalvarConferencia` já é condicional a `det.localizacao` existir).

## Teste

Abrir uma conferência, expandir o "+" de um item e confirmar que aparecem
só "Estado de conservação" e "Observações" — sem o campo Localização.
