import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('index.html','r',encoding='utf-8') as f:
    lines = f.readlines()

changes = 0

def rm(i, label=""):
    global changes
    if lines[i].strip():
        lines[i] = ''
        changes += 1
    else:
        if label: print(f'JA VAZIA: {label} linha {i+1}')

# 4353 — _renderCentralBar(main,"dashvcm") — mudar para tela generica
if 'dashvcm' in lines[4352]:
    lines[4352] = lines[4352].replace('"dashvcm"', '"vcm"')
    changes += 1

# 5107 — badge FRIDA no dashboard do comandante
rm(5106, 'badge FRIDA dashvcm')

# 5260 — card clicável que vai para dashvcm
if 'dashvcm' in lines[5259]:
    lines[5259] = lines[5259].replace("state.tela='dashvcm';render()", "")
    # Tornar não clicável (remover onclick)
    lines[5259] = lines[5259].replace(
        "onclick=\\\"state.tela='dashvcm';render()\\\" ",
        ""
    )
    changes += 1

# 5269 — link "+ mais" que vai para dashvcm
if 'dashvcm' in lines[5268]:
    lines[5268] = ''
    changes += 1

# 12875 — botão "Dashboard VCM" dentro de OC (índice 12874)
if 'dashvcm' in lines[12874]:
    lines[12874] = ''
    changes += 1

# 14931 — bloco if(tela==="dashvcm") no renderTela
if 'dashvcm' in lines[14930]:
    for i in range(14930, 14940):
        if lines[i].strip():
            lines[i] = ''
            changes += 1
        # parar após fechar o bloco
        if i > 14930 and lines[i].strip() == '}':
            break

# 15167 — bloco VCM dentro do comandante (card pink)
if 'ff69b4' in lines[15166] and '1a0810' in lines[15166]:
    # Encontrar extensão do bloco
    for i in range(15166, 15200):
        if lines[i].strip():
            lines[i] = ''
            changes += 1
        if i > 15170 and '</div>' in lines[i]:
            break

# 19314 — botão "encaminhar ao CRAV/VCM" que chama setTela('dashvcm')
if 'dashvcm' in lines[19313]:
    lines[19313] = ''
    changes += 1

# 19774 — if(state.tela==="dashvcm") renderDashboardVCM no sync callback
if 'dashvcm' in lines[19773]:
    lines[19773] = ''
    changes += 1

with open('index.html','w',encoding='utf-8') as f:
    f.writelines(lines)

print(f'Feito — {changes} alteracoes')
