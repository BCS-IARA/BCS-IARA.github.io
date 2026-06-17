import json, csv, io

with open('BCS_inventario_importacao.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

itens = d['invItens']

# Colunas que o _invAutoMapCols reconhece automaticamente
cols = [
    'Nro Patrimônio',
    'Patr Antigo',
    'Descrição Bem',
    'Conta Contábil',
    'Marca',
    'Modelo',
    'Nr Serie',
    'Sit Física',
    'Localização',
    'Data Aquisição',
    'Valor',
    'Observações',
]

# Mapeamento conta contábil reverso para exibição
cat_map = {
    'material_belico/arma': '45200000 - Material Bélico / Arma',
    'material_belico/municao': '45200000 - Material Bélico / Munição',
    'material_permanente/colete': '44900000 - Equipamento Prot. Individual / Colete',
    'material_permanente/equipamento_comunicacao': '44600000 - Equip. Comunicação',
    'material_permanente/informatica': '44500000 - Equip. Processamento de Dados',
    'material_permanente/maquina': '44300000 - Máquinas e Equipamentos',
    'material_permanente/mobiliario': '44100000 - Móveis e Utensílios',
    'material_permanente/monitoramento': '44600000 - Equip. Monitoramento',
    'material_permanente/seguranca': '44900000 - Equip. Segurança',
    'veiculo/viatura': '44200000 - Veículos',
}

estado_map = {
    'bom': 'BOM',
    'regular': 'REGULAR',
    'inservivel': 'INSERVIVEL',
    'otimo': 'ÓTIMO',
}

output = io.StringIO()
writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
writer.writerow(cols)

for item in itens:
    cat_key = item.get('categoria','') + '/' + item.get('subcategoria','')
    conta = cat_map.get(cat_key, item.get('categoria',''))
    est = estado_map.get(item.get('estado',''), item.get('estado',''))
    writer.writerow([
        item.get('tombamento',''),
        '',  # patr_antigo — não temos
        item.get('descricao',''),
        conta,
        item.get('marca',''),
        item.get('modelo',''),
        item.get('numero_serie','') or item.get('tombamento',''),
        est,
        item.get('localizacao','77a CIPM/BCS'),
        item.get('data_aquisicao',''),
        item.get('valor_aquisicao','') or '',
        item.get('observacoes',''),
    ])

with open('BCS_inventario.csv', 'w', encoding='utf-8-sig', newline='') as f:
    f.write(output.getvalue())

print(f'{len(itens)} itens exportados para BCS_inventario.csv')
