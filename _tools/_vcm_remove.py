import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('index.html','r',encoding='utf-8') as f:
    lines = f.readlines()

changes = 0

# Linha 12878 — botao 'Dashboard VCM' dentro do detail de OC
if 'dashvcm' in lines[12877]:
    lines[12877] = ''
    changes += 1
else:
    print('NAO ACHOU: botao dashvcm linha 12878')

# Linha 19324 — botao que chama setTela('dashvcm')
if 'dashvcm' in lines[19323]:
    lines[19323] = ''
    changes += 1
else:
    print('NAO ACHOU: botao 19324')

# Linha 19784 — if(state.tela===dashvcm) renderDashboardVCM
if 'dashvcm' in lines[19783] and 'renderDashboardVCM' in lines[19783]:
    lines[19783] = ''
    changes += 1
else:
    print('NAO ACHOU: renderDashboardVCM listener 19784')

# Bloco if(tela==="dashvcm") no renderTela — linha 14936
if 'dashvcm' in lines[14935]:
    for i in range(14935, 14945):
        if lines[i].strip():
            lines[i] = ''
            changes += 1
            if '}' in lines[i] and i > 14936:
                break
else:
    print('NAO ACHOU: bloco dashvcm renderTela')

# Bloco if(tela==="cadastrosvcm") no renderTela — linha 14942
for i in range(14935, 14950):
    if 'cadastrosvcm' in lines[i]:
        for j in range(i, i+6):
            if lines[j].strip():
                lines[j] = ''
                changes += 1
        break

# Linha 1214 — sync listener que inclui dashvcm
if 'dashvcm' in lines[1213]:
    lines[1213] = lines[1213].replace('||state.tela==="dashvcm"', '')
    changes += 1
else:
    print('NAO ACHOU: sync listener dashvcm')

with open('index.html','w',encoding='utf-8') as f:
    f.writelines(lines)

print(f'Feito — {changes} alteracoes')
