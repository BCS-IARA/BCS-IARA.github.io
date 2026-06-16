import sys, re
sys.stdout.reconfigure(encoding='utf-8')
with open('index.html','r',encoding='utf-8') as f:
    content = f.read()
sc = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)[0]
lines = sc.split('\n')
balance = 0
suspect = 0
for i, line in enumerate(lines):
    prev = balance
    for ch in line:
        if ch == '{': balance += 1
        elif ch == '}': balance -= 1
    if balance == 1 and prev == 0:
        suspect = i
print("Ultimo aberto sem fechar em script linha", suspect+1)
for j in range(max(0,suspect-2), suspect+4):
    print(" ", j+1, repr(lines[j][:140]))
