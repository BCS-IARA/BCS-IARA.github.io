import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('index.html','r',encoding='utf-8') as f:
    lines = f.readlines()

changes = 0

# 1. Linha 19718: else if → if (orphan else after dashvcm removal)
if 'else if' in lines[19717] and 'ocorrencias' in lines[19717]:
    lines[19717] = lines[19717].replace('    else if(', '    if(')
    changes += 1
else:
    print(f'NAO ACHOU: else if orfao 19718, linha contem: {repr(lines[19717][:80])}')

# 2. Remover bloco else if(tabAtiva==="vcm") linhas 5687-5759
# Inclui comentário + else if block + fim aba vcm
for i in range(5686, 5760):
    lines[i] = ''
    changes += 1

with open('index.html','w',encoding='utf-8') as f:
    f.writelines(lines)

print(f'Feito — {changes} alteracoes')
