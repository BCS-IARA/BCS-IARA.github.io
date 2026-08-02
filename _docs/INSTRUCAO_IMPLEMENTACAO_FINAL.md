# INSTRUÇÃO EXECUTÁVEL: Implementar Sincronização Encaminhamentos + Fila

## 🎯 OBJETIVO
Implementar 5 mudanças no `index.html` para sincronizar encaminhamentos e fila de triagem entre aparelhos via Google Sheets.

---

## 📁 ARQUIVO A MODIFICAR
**Arquivo:** `/mnt/user-data/uploads/index.html`  
**Tamanho:** 2.2 MB (25.399 linhas)  
**Cópia de trabalho:** Copiar para `/home/claude/index_sync.html` para trabalhar

---

## ✅ PASSO 0: PREPARAÇÃO

```bash
# Copiar arquivo para trabalho
cp /mnt/user-data/uploads/index.html /home/claude/index_sync.html

# Verificar que foi copiado
ls -lh /home/claude/index_sync.html
```

---

## ✅ MUDANÇA 1️⃣: ADICIONAR CARREGAMENTO DO SHEETS (linha 808)

### Localizar:
```bash
grep -n "var devolutivasSheets.*await lerDadoAppSheets.*bcs_devolutivas_crav_blob" /home/claude/index_sync.html
```

**Esperado encontrar:** Linha 808

### Contexto (ANTES):
```javascript
    var devolutivasSheets    = await lerDadoAppSheets("bcs_devolutivas_crav_blob");
    var conselhoAtasSheets   = await lerDadoAppSheets("bcs_conselho_atas");
```

### Contexto (DEPOIS):
```javascript
    var devolutivasSheets    = await lerDadoAppSheets("bcs_devolutivas_crav_blob");
    var encaminhamientosSheets = await lerDadoAppSheets("bcs_encaminhamentos");
    var filaPendenteSheets   = await lerDadoAppSheets("bcs_fila_pendente");
    var conselhoAtasSheets   = await lerDadoAppSheets("bcs_conselho_atas");
```

### EXECUTAR (usar str_replace):
- **old_str:**
```javascript
    var devolutivasSheets    = await lerDadoAppSheets("bcs_devolutivas_crav_blob");
    var conselhoAtasSheets   = await lerDadoAppSheets("bcs_conselho_atas");
```

- **new_str:**
```javascript
    var devolutivasSheets    = await lerDadoAppSheets("bcs_devolutivas_crav_blob");
    var encaminhamientosSheets = await lerDadoAppSheets("bcs_encaminhamentos");
    var filaPendenteSheets   = await lerDadoAppSheets("bcs_fila_pendente");
    var conselhoAtasSheets   = await lerDadoAppSheets("bcs_conselho_atas");
```

### Verificar:
```bash
grep -n "var encaminhamientosSheets.*await lerDadoAppSheets" /home/claude/index_sync.html
grep -n "var filaPendenteSheets.*await lerDadoAppSheets" /home/claude/index_sync.html
```

**Status:** ✅ Deve encontrar ambas

---

## ✅ MUDANÇA 2️⃣: ADICIONAR MERGE INTELIGENTE (linha ~905+)

### Localizar:
```bash
grep -n "state.devolutivasCrav.*=.*_mergeById.*state.devolutivasCrav" /home/claude/index_sync.html | head -1
```

**Esperado encontrar:** Linha ~905

### Contexto (ANTES):
```javascript
    state.devolutivasCrav     = _mergeById(state.devolutivasCrav||[],     devolutivasSheets);
    // Cruzar devolutivasCrav com encaminhamentos — atualiza relato_devolutiva localmente
```

### Contexto (DEPOIS):
```javascript
    state.devolutivasCrav     = _mergeById(state.devolutivasCrav||[],     devolutivasSheets);
    state.encaminhamentos     = _mergeById(state.encaminhamentos||[],     encaminhamientosSheets);
    // Fila de triagem: sobrescrever (ordem-dependente, sem merge)
    if(filaPendenteSheets && Array.isArray(filaPendenteSheets)){
      state.filaPendente = filaPendenteSheets;
    } else if(filaPendenteSheets === null && (state.filaPendente||[]).length > 0){
      // Sheets vazio mas locale tem dados → faz push imediato (bootstrap cross-device)
      await salvarDadoAppSheets("bcs_fila_pendente", state.filaPendente||[]);
    }
    // Cruzar devolutivasCrav com encaminhamentos — atualiza relato_devolutiva localmente
```

### EXECUTAR (usar str_replace):
- **old_str:**
```javascript
    state.devolutivasCrav     = _mergeById(state.devolutivasCrav||[],     devolutivasSheets);
    // Cruzar devolutivasCrav com encaminhamentos — atualiza relato_devolutiva localmente
```

- **new_str:**
```javascript
    state.devolutivasCrav     = _mergeById(state.devolutivasCrav||[],     devolutivasSheets);
    state.encaminhamentos     = _mergeById(state.encaminhamentos||[],     encaminhamientosSheets);
    // Fila de triagem: sobrescrever (ordem-dependente, sem merge)
    if(filaPendenteSheets && Array.isArray(filaPendenteSheets)){
      state.filaPendente = filaPendenteSheets;
    } else if(filaPendenteSheets === null && (state.filaPendente||[]).length > 0){
      // Sheets vazio mas locale tem dados → faz push imediato (bootstrap cross-device)
      await salvarDadoAppSheets("bcs_fila_pendente", state.filaPendente||[]);
    }
    // Cruzar devolutivasCrav com encaminhamentos — atualiza relato_devolutiva localmente
```

### Verificar:
```bash
grep -n "state.encaminhamentos.*=.*_mergeById" /home/claude/index_sync.html
grep -n "if(filaPendenteSheets && Array.isArray" /home/claude/index_sync.html
```

**Status:** ✅ Deve encontrar ambas

---

## ✅ MUDANÇA 3️⃣: ADICIONAR LOCALSTORAGE EM carregarDadosAppDoSheets (linha ~942+)

### Localizar:
```bash
grep -n 'localStorage.setItem("bcs_devolutivas_crav"' /home/claude/index_sync.html | grep -v "if(state"
```

**Esperado encontrar:** Linha ~942 (dentro de carregarDadosAppDoSheets, após comentário "Reflete tudo")

### Contexto (ANTES):
```javascript
    localStorage.setItem("bcs_devolutivas_crav",   JSON.stringify(state.devolutivasCrav||[]));
    localStorage.setItem("bcs_conselho_atas",      JSON.stringify(state.conselho_atas||[]));
```

### Contexto (DEPOIS):
```javascript
    localStorage.setItem("bcs_devolutivas_crav",   JSON.stringify(state.devolutivasCrav||[]));
    localStorage.setItem("bcs_encaminhamentos",    JSON.stringify(state.encaminhamentos||[]));
    localStorage.setItem("bcs_fila_pendente",      JSON.stringify(state.filaPendente||[]));
    localStorage.setItem("bcs_conselho_atas",      JSON.stringify(state.conselho_atas||[]));
```

### EXECUTAR (usar str_replace):
- **old_str:**
```javascript
    localStorage.setItem("bcs_devolutivas_crav",   JSON.stringify(state.devolutivasCrav||[]));
    localStorage.setItem("bcs_conselho_atas",      JSON.stringify(state.conselho_atas||[]));
```

- **new_str:**
```javascript
    localStorage.setItem("bcs_devolutivas_crav",   JSON.stringify(state.devolutivasCrav||[]));
    localStorage.setItem("bcs_encaminhamentos",    JSON.stringify(state.encaminhamentos||[]));
    localStorage.setItem("bcs_fila_pendente",      JSON.stringify(state.filaPendente||[]));
    localStorage.setItem("bcs_conselho_atas",      JSON.stringify(state.conselho_atas||[]));
```

### Verificar:
```bash
grep -n 'localStorage.setItem("bcs_encaminhamentos"' /home/claude/index_sync.html | head -1
grep -n 'localStorage.setItem("bcs_fila_pendente"' /home/claude/index_sync.html | head -1
```

**Status:** ✅ Deve encontrar ambas (linhas diferentes de _salvarLocalSemSync)

---

## ✅ MUDANÇA 4️⃣: ADICIONAR ENVIO PARA SHEETS EM sincronizarSheets (linha ~688+)

### Localizar:
```bash
grep -n 'await salvarDadoAppSheets("bcs_devolutivas_crav_blob"' /home/claude/index_sync.html
```

**Esperado encontrar:** Linha ~688

### Contexto (ANTES):
```javascript
    await salvarDadoAppSheets("bcs_devolutivas_crav_blob", state.devolutivasCrav||[]);
    await salvarDadoAppSheets("bcs_conselho_atas",     state.conselho_atas||[]);
```

### Contexto (DEPOIS):
```javascript
    await salvarDadoAppSheets("bcs_devolutivas_crav_blob", state.devolutivasCrav||[]);
    await salvarDadoAppSheets("bcs_encaminhamentos",   state.encaminhamentos||[]);
    await salvarDadoAppSheets("bcs_fila_pendente",     state.filaPendente||[]);
    await salvarDadoAppSheets("bcs_conselho_atas",     state.conselho_atas||[]);
```

### EXECUTAR (usar str_replace):
- **old_str:**
```javascript
    await salvarDadoAppSheets("bcs_devolutivas_crav_blob", state.devolutivasCrav||[]);
    await salvarDadoAppSheets("bcs_conselho_atas",     state.conselho_atas||[]);
```

- **new_str:**
```javascript
    await salvarDadoAppSheets("bcs_devolutivas_crav_blob", state.devolutivasCrav||[]);
    await salvarDadoAppSheets("bcs_encaminhamentos",   state.encaminhamentos||[]);
    await salvarDadoAppSheets("bcs_fila_pendente",     state.filaPendente||[]);
    await salvarDadoAppSheets("bcs_conselho_atas",     state.conselho_atas||[]);
```

### Verificar:
```bash
grep -n 'await salvarDadoAppSheets("bcs_encaminhamentos"' /home/claude/index_sync.html
grep -n 'await salvarDadoAppSheets("bcs_fila_pendente"' /home/claude/index_sync.html
```

**Status:** ✅ Deve encontrar ambas

---

## ✅ MUDANÇA 5️⃣: ADICIONAR BOOTSTRAP EM _salvarLocalSemSync (linha ~761+)

### Localizar:
```bash
grep -n 'if(state.devolutivasCrav).*localStorage.setItem' /home/claude/index_sync.html
```

**Esperado encontrar:** Linha ~761 (com `if(state.devolutivasCrav)`)

### Contexto (ANTES):
```javascript
    if(state.devolutivasCrav)     localStorage.setItem("bcs_devolutivas_crav",    JSON.stringify(state.devolutivasCrav));
    if(state.conselho_atas)       localStorage.setItem("bcs_conselho_atas",       JSON.stringify(state.conselho_atas));
```

### Contexto (DEPOIS):
```javascript
    if(state.devolutivasCrav)     localStorage.setItem("bcs_devolutivas_crav",    JSON.stringify(state.devolutivasCrav));
    if(state.encaminhamentos)     localStorage.setItem("bcs_encaminhamentos",     JSON.stringify(state.encaminhamentos));
    if(state.filaPendente)        localStorage.setItem("bcs_fila_pendente",       JSON.stringify(state.filaPendente));
    if(state.conselho_atas)       localStorage.setItem("bcs_conselho_atas",       JSON.stringify(state.conselho_atas));
```

### EXECUTAR (usar str_replace):
- **old_str:**
```javascript
    if(state.devolutivasCrav)     localStorage.setItem("bcs_devolutivas_crav",    JSON.stringify(state.devolutivasCrav));
    if(state.conselho_atas)       localStorage.setItem("bcs_conselho_atas",       JSON.stringify(state.conselho_atas));
```

- **new_str:**
```javascript
    if(state.devolutivasCrav)     localStorage.setItem("bcs_devolutivas_crav",    JSON.stringify(state.devolutivasCrav));
    if(state.encaminhamentos)     localStorage.setItem("bcs_encaminhamentos",     JSON.stringify(state.encaminhamentos));
    if(state.filaPendente)        localStorage.setItem("bcs_fila_pendente",       JSON.stringify(state.filaPendente));
    if(state.conselho_atas)       localStorage.setItem("bcs_conselho_atas",       JSON.stringify(state.conselho_atas));
```

### Verificar:
```bash
grep -n "if(state.encaminhamentos).*localStorage.setItem" /home/claude/index_sync.html
grep -n "if(state.filaPendente).*localStorage.setItem" /home/claude/index_sync.html
```

**Status:** ✅ Deve encontrar ambas

---

## ✅ PASSO FINAL: VALIDAÇÃO COMPLETA

Após fazer as 5 mudanças, executar:

```bash
echo "=== VALIDAÇÃO FINAL ===" && \
echo -e "\n1. lerDadoAppSheets:" && \
grep -c "var encaminhamientosSheets.*await lerDadoAppSheets" /home/claude/index_sync.html && \
grep -c "var filaPendenteSheets.*await lerDadoAppSheets" /home/claude/index_sync.html && \
echo -e "\n2. Merge:" && \
grep -c "state.encaminhamentos.*=.*_mergeById" /home/claude/index_sync.html && \
grep -c "if(filaPendenteSheets && Array.isArray" /home/claude/index_sync.html && \
echo -e "\n3. localStorage (carregarDadosAppDoSheets):" && \
grep -c 'localStorage.setItem("bcs_encaminhamentos"' /home/claude/index_sync.html | head -1 && \
echo -e "\n4. salvarDadoAppSheets:" && \
grep -c 'await salvarDadoAppSheets("bcs_encaminhamentos"' /home/claude/index_sync.html && \
echo -e "\n5. Bootstrap (_salvarLocalSemSync):" && \
grep -c "if(state.encaminhamentos).*localStorage.setItem" /home/claude/index_sync.html && \
echo -e "\n✅ TUDO OK! Todas as 5 mudanças implementadas"
```

---

## 📁 ENTREGA FINAL

Após concluir, executar:

```bash
# Copiar para outputs
cp /home/claude/index_sync.html /mnt/user-data/outputs/index.html

# Verificar tamanho
ls -lh /mnt/user-data/outputs/index.html

# Confirmar
echo "✅ Arquivo pronto em: /mnt/user-data/outputs/index.html"
```

---

## 📋 CHECKLIST

- [ ] MUDANÇA 1️⃣: lerDadoAppSheets implementada
- [ ] MUDANÇA 2️⃣: Merge implementado
- [ ] MUDANÇA 3️⃣: localStorage em carregarDadosAppDoSheets implementado
- [ ] MUDANÇA 4️⃣: salvarDadoAppSheets implementado
- [ ] MUDANÇA 5️⃣: Bootstrap implementado
- [ ] VALIDAÇÃO COMPLETA executada (5 buscas retornam OK)
- [ ] Arquivo copiado para `/mnt/user-data/outputs/index.html`

---

## ⚠️ IMPORTANTE

- Não remover nada existente
- Apenas adicionar as 5 mudanças nos pontos indicados
- Se encontrar erro em alguma mudança, reportar qual mudança
- Usar exatamente os `old_str` e `new_str` fornecidos

---

## 🚀 RESULTADO ESPERADO

Após implementar todas as 5 mudanças:
- ✅ Encaminhamentos sincronizam entre aparelhos
- ✅ Fila de triagem sincroniza
- ✅ Devolutivas CRAV ligam corretamente
- ✅ Arquivo pronto para deploy em GitHub
