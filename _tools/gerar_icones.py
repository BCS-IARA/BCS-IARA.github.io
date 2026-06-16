"""
Gera os ícones PNG do PWA (icon-192.png e icon-512.png)
usando apenas a biblioteca padrão do Python.
Execute: python gerar_icones.py
"""
import struct, zlib, math

def png(w, h, pixels):
    """Gera bytes de um PNG RGB a partir de uma lista de tuplas (r,g,b)."""
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)

    raw = b''
    for y in range(h):
        raw += b'\x00'  # filter type none
        for x in range(w):
            r, g, b = pixels[y * w + x]
            raw += bytes([r, g, b])

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw, 9)

    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', idat)
        + chunk(b'IEND', b'')
    )

def draw_icon(size):
    pixels = []
    cx = cy = size / 2
    r = size / 2

    # Cores
    bg1      = (26, 16, 0)      # fundo escuro
    bg2      = (42, 28, 16)     # fundo gradiente
    gold     = (212, 168, 122)  # dourado
    gold_dim = (140, 106, 58)   # dourado escuro
    white    = (245, 237, 224)  # texto

    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)

            # Fora do círculo → transparente (branco puro para PNG sem alpha)
            if dist > r - 1:
                pixels.append((15, 10, 6))
                continue

            # Gradiente de fundo
            t = (y / size)
            bg = tuple(int(bg1[i] + (bg2[i]-bg1[i])*t) for i in range(3))

            # Borda dourada (anel)
            border_w = max(2, size // 48)
            if dist > r - border_w - 2:
                t2 = (dist - (r - border_w - 2)) / (border_w + 2)
                col = tuple(int(bg[i] + (gold[i]-bg[i])*min(t2,1)) for i in range(3))
                pixels.append(col)
                continue

            # Espada (linha vertical + horizontal = cruz)
            sw = max(2, size // 32)   # largura do traço
            sh = int(size * 0.55)     # altura da lâmina
            gw = int(size * 0.30)     # largura da guarda
            gh = max(2, size // 20)   # altura da guarda

            # Lâmina vertical
            lx1 = int(cx - sw//2)
            lx2 = int(cx + sw//2)
            ly1 = int(cy - sh//2)
            ly2 = int(cy + sh//2)

            # Guarda horizontal
            gx1 = int(cx - gw//2)
            gx2 = int(cx + gw//2)
            gy1 = int(cy - gh//2)
            gy2 = int(cy + gh//2)

            on_blade  = (lx1 <= x <= lx2 and ly1 <= y <= ly2)
            on_guard  = (gx1 <= x <= gx2 and gy1 <= y <= gy2)

            if on_blade or on_guard:
                # Brilho leve no centro da lâmina
                if on_blade and abs(x - cx) <= sw // 4:
                    pixels.append(white)
                else:
                    pixels.append(gold)
            else:
                pixels.append(bg)

    return png(size, size, pixels)

for size, name in [(192, 'icon-192.png'), (512, 'icon-512.png')]:
    data = draw_icon(size)
    with open(name, 'wb') as f:
        f.write(data)
    print(f'✅ {name} gerado ({size}x{size})')

print('Pronto! Copie os arquivos para a pasta BCS.')
