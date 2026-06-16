import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\oseia\Downloads\BCS\index.html', encoding='utf-8') as f:
    content = f.read()

# Find the editar ocorrencia button in triagem (it has the title with formulário)
anchor = "formulário completo de edição da ocorrência"
idx = content.find(anchor)
if idx < 0:
    print("NOT FOUND")
    sys.exit(1)

# Find start of that h.push line
line_start = content.rfind('\n', 0, idx) + 1
line_end = content.find('\n', idx)
line = content[line_start:line_end]
print("FOUND LINE:", repr(line[:120]))

# The line has: onclick='state.popEditarOc=\""+esc(o.id)+"\"
# We want to prepend: state._triagemRetornoId=\""+esc(o.id)+"\";
OLD_ONCLICK = "onclick='state.popEditarOc=\\\""
NEW_ONCLICK = "onclick='state._triagemRetornoId=\\\"" + '"+esc(o.id)+"\\";state.popEditarOc=\\"'

new_line = line.replace(OLD_ONCLICK, NEW_ONCLICK, 1)
print("NEW LINE:", repr(new_line[:160]))

count = content.count(line)
print("line count:", count)

if count == 1:
    content = content.replace(line, new_line, 1)
    with open(r'C:\Users\oseia\Downloads\BCS\index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("DONE")
else:
    print("ERROR: not unique")
