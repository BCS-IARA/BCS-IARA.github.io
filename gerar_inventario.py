import json

now = '2026-06-16T09:00:00.000Z'
itens = []

def dt(s):
    p = s.split('/')
    return p[2]+'-'+p[1]+'-'+p[0] if len(p)==3 else s

def add(tomb, desc, cat, sub, marca, estado, dtaq, valor, obs='', patr_ant=''):
    itens.append({
        'id': 'inv_siap_'+tomb.replace(' ','_').replace('/','_'),
        'tombamento': tomb,
        'descricao': desc,
        'categoria': cat,
        'subcategoria': sub,
        'marca': marca,
        'modelo': '',
        'numero_serie': '',
        'estado': estado,
        'localizacao': '77a CIPM',
        'data_aquisicao': dt(dtaq),
        'valor_aquisicao': valor,
        'observacoes': ('Patr.Ant: '+patr_ant+' | ' if patr_ant else '')+'SIAP 09/06/2026',
        'tipo_carga': 'interna',
        'criadoEm': now
    })

# ===== CONTA 1.1 - EQUIPAMENTOS COMUNICACAO =====
add('00116001','Televisor LCD 42 pol','material_permanente','equipamento_comunicacao','LG','bom','26/11/2013',1585.67,'','00142367')
add('00116002','Televisor LCD 42 pol','material_permanente','equipamento_comunicacao','LG','bom','26/11/2013',1585.67,'','00142368')
add('00116003','Televisor LCD 42 pol','material_permanente','equipamento_comunicacao','LG','bom','26/11/2013',1585.67,'','00142369')
add('00131193','Console Veicular MVC 6000 Terminal Trunking Movel Digital TETRA KIT Bluetooth','material_permanente','equipamento_comunicacao','TELTRONIC','bom','19/02/2015',17895.15,'','00148202')
add('00135572','Televisor LED 32 pol','material_permanente','equipamento_comunicacao','AOC','bom','25/02/2015',900.00)
add('00152437','Caixa Amplificada de Som 80NW','material_permanente','equipamento_comunicacao','FRAHM','bom','28/11/2017',649.90)
add('00164632','Projetor de Multimidia','material_permanente','equipamento_comunicacao','BENQ','bom','11/02/2019',2799.00)
add('00164691','Microfone Sem Fio Duplo de Mao','material_permanente','equipamento_comunicacao','QUANTA','bom','08/02/2019',736.10)
add('00178359','Televisor Smart TV LED 55pol UHD 4K','material_permanente','equipamento_comunicacao','PHILIPS','bom','18/04/2022',3173.00)
add('00178414','Televisor Smart TV LED 43pol Full HD Wifi USB HDMI','material_permanente','equipamento_comunicacao','AOC','bom','01/06/2022',1748.99)
add('00232671','Televisor Smart TV LED 43pol LCD/LED Bivolt - Serie A2','material_permanente','equipamento_comunicacao','SEMP TOSHIBA','bom','16/10/2024',1391.16)

# ===== CONTA 2.1 - EQUIPAMENTOS PROCESSAMENTO DADOS =====
add('00111701','Impressora Laser LED A4 Duplex Preta M16MB','material_permanente','informatica','HP','bom','31/08/2013',1640.00)
add('00121121','Microcomputador Core i5 UDP Intel 3470 8GB 500GB Monitor LED 20pol','material_permanente','informatica','DATEN','bom','08/07/2014',2453.30)
add('00121122','Microcomputador Core i5 UDP Intel 3470 8GB 500GB Monitor LED 20pol','material_permanente','informatica','DATEN','bom','08/07/2014',2453.30)
add('00122642','Microcomputador Core i5 Monitor LED 20pol 500GB 8GB','material_permanente','informatica','','bom','29/08/2014',2453.30)
add('00122643','Microcomputador Core i5 Monitor LED 20pol 500GB 8GB','material_permanente','informatica','','bom','29/08/2014',2453.30)
add('00126574','Scanner de Mesa A4 e Oficio','material_permanente','informatica','AVISION','bom','18/11/2014',1259.66)
add('00127438','Microcomputador Portatil Notebook Modelo 80AU','material_permanente','informatica','LENOVO','bom','19/12/2014',3066.66)
add('00129053','Microcomputador Core i5 LI PLUS com Teclado e Mouse','material_permanente','informatica','LI PLUS','bom','19/12/2014',2789.47)
add('00129252','Microcomputador Core i5 LI PLUS com Teclado e Mouse','material_permanente','informatica','LI PLUS','bom','19/12/2014',2789.47)
add('00133248','Microcomputador Portatil Notebook ProBook 6455B Core i5 com Maleta','material_permanente','informatica','HP','bom','17/12/2014',2937.35)
add('00146628','Microcomputador Desktop 3.5GHz 16GB 500GB Win8.1 Monitor LED 20pol','material_permanente','informatica','LI PLUS','bom','17/06/2016',3862.81)
add('00146629','Microcomputador Desktop 3.5GHz 16GB 500GB Win8.1 Monitor LED 20pol','material_permanente','informatica','LI PLUS','bom','17/06/2016',3862.81)
add('00146630','Microcomputador Desktop 3.5GHz 16GB 500GB Win8.1 Monitor LED 20pol','material_permanente','informatica','LI PLUS','bom','17/06/2016',3862.81)
add('00146631','Microcomputador Desktop 3.5GHz 16GB 500GB Win8.1 Monitor LED 20pol','material_permanente','informatica','LI PLUS','bom','17/06/2016',3862.81)
add('00157828','Disco Rigido HD Portatil 1TB','material_permanente','informatica','SEAGATE','bom','09/01/2018',251.00)
add('00166908','Microcomputador Processador com Monitor Teclado Mouse','material_permanente','informatica','','bom','28/11/2019',2970.00)
add('00175408','Monitor de Video Colorido LED 20pol E2050SDA','material_permanente','informatica','AOC','regular','31/03/2022',292.16,'','00064183')
add('00175410','Monitor de Video Colorido LED 20pol E2050SDA','material_permanente','informatica','AOC','regular','31/03/2022',292.16,'','00064502')
add('00175414','Microcomputador Core i5 500GB 8GB 3.30GHz Serie 138879','material_permanente','informatica','LOGIN','regular','31/03/2022',1548.78,'','00065158')
add('00175888','Microcomputador Processador Master D48 com Monitor LED','material_permanente','informatica','POSITIVO','bom','15/09/2022',473.07,'','00187674')
add('00175889','Microcomputador Processador Master D48 com Monitor LED','material_permanente','informatica','POSITIVO','bom','15/09/2022',473.07,'','00186881')
add('00175890','Microcomputador Processador Master D48 com Monitor LED','material_permanente','informatica','POSITIVO','bom','15/09/2022',473.07,'','00186928')
add('00175891','Microcomputador Processador Master D48 com Monitor LED','material_permanente','informatica','POSITIVO','bom','15/09/2022',473.07,'','00186929')
add('00175892','Microcomputador Processador Master D48 com Monitor LED','material_permanente','informatica','POSITIVO','bom','15/09/2022',473.07,'','00186961')
add('00175893','Microcomputador Processador Master D48 com Monitor LED','material_permanente','informatica','POSITIVO','bom','15/09/2022',473.10,'','00187132')
add('00185087','Microcomputador Netbook Processador 10a Geracao Quad Core','material_permanente','informatica','DELL','bom','06/01/2023',6490.00,'','00230075')
add('00187893','Microcomputador Processador SFF com Monitor Teclado Mouse','material_permanente','informatica','','bom','19/12/2022',3683.99)
add('00190024','CPU Microcomputador Compaq 8200 Elite - Serie BRG221FKQ0','material_permanente','informatica','HP','bom','09/02/2023',159.91)
add('00190028','CPU Microcomputador Compaq 8200 Elite - Serie BRG221FKMT','material_permanente','informatica','HP','bom','09/02/2023',159.91)
for n in range(196141, 196151):
    add(str(n).zfill(8),'Microcomputador Core i5 4GB','material_permanente','informatica','','bom','11/08/2023',1152.00)
for n in range(220480, 220494):
    add(str(n).zfill(8),'Microcomputador Desktop Basico R5 4600G 8GB SSD Monitor 21.5pol Full HD','material_permanente','informatica','GIGAPC','bom','06/12/2023',3227.32)

# ===== CONTA 3.2 - VEICULOS =====
def addv(tomb, desc, placa, marca, modelo, ano_fab, ano_mod, comb, cor, chassi, renavam, motor, estado, dtaq, valor, patr_ant=''):
    obs = f'Placa:{placa} | Chassi:{chassi} | RENAVAM:{renavam} | Motor:{motor} | AnoFab:{ano_fab} | AnoMod:{ano_mod} | Cor:{cor} | Combustivel:{comb} | SIAP 09/06/2026'
    itens.append({
        'id': 'inv_vtr_'+tomb.replace(' ','_'),
        'tombamento': tomb,
        'descricao': desc,
        'categoria': 'veiculo',
        'subcategoria': 'viatura',
        'marca': marca,
        'modelo': modelo,
        'numero_serie': placa,
        'estado': estado,
        'localizacao': '77a CIPM',
        'data_aquisicao': dt(dtaq),
        'valor_aquisicao': valor,
        'observacoes': ('Patr.Ant: '+patr_ant+' | ' if patr_ant else '')+obs,
        'tipo_carga': 'interna',
        'criadoEm': now
    })

addv('00131107','Bicicleta para Policiamento Ostensivo Aro 26 Aco Carbono','','','','','','','','','','','bom','14/01/2015',600.00)
addv('00131108','Bicicleta para Policiamento Ostensivo Aro 26 Aco Carbono','','','','','','','','','','','bom','14/01/2015',600.00)
addv('00133063','Viatura Policial Tipo Furgao Base Movel','OZU8617','MERCEDES BENZ','515CDISPRINTERF','2014','2014','Diesel','Azul','8AC906655EE097887','1035807456','651955W0035962','bom','11/12/2014',190650.00)
addv('00144165','Veiculo Viatura Policial City','PJQ9827','VOLKSWAGEM','VOYAGE TL MB S','2014','2015','Alcool/Gasolina','Branca','9BWDB45U5FT069925','1069044870','CCRT48184','bom','21/07/2016',41960.00)
addv('00148353','Veiculo Viatura Policial','PKF7775','FORD','KA SE 1.5 HA B','2016','2017','Alcool/Gasolina','Prata','9BFZH55J6H8396615','01103940250','U2KAH8396615','bom','02/01/2017',46700.00)
addv('00148386','Veiculo Viatura Policial','PKE1688','FIAT','WEEKEND ADVENTURE','2016','2016','Alcool/Gasolina','Prata','9BD37417SG5093074','01103392856','370A00113025273','bom','05/01/2017',66400.00)
addv('00148392','Veiculo Viatura Policial','PKE9700','FIAT','WEEKEND ADVENTURE','2016','2016','Alcool/Gasolina','Prata','9BD37417SG5093133','01103397734','370A00113037273','regular','05/01/2017',66400.00)
addv('00151119','Veiculo Viatura Policial','PKE0195','FORD','KA SE 1.5 HA B','2016','2017','Alcool/Gasolina','Prata','9BFZH54J3H8391051','01101874497','U2KAH8391051','bom','13/09/2016',51556.10)
addv('00159626','Motocicleta Viatura Policial','PKW3443','HONDA','XRE 300','2017','2017','Alcool/Gasolina','Branca','9C2ND1120HR001701','1143094422','ND11E2H001705','bom','13/12/2017',24388.28)
addv('00160449','Veiculo Viatura Policial','PKY8406','FIAT','WEEKEND ADVENTURE','2017','2018','Alcool/Gasolina','Prata','9BD37417DJ5100341','1147518910','370A00113194669','bom','21/12/2017',72270.00)
addv('00160760','Veiculo Viatura Policial','PKZ9505','FORD','RANGER XL CD4 22C','2017','2018','Diesel','Branca','A8FAR23N2JJ057348','1150007777','QJ2UJJ057348','bom','27/12/2017',131900.00)
addv('00164148','Motocicleta Viatura Policial','PLJ6440','HONDA','XRE 300','2018','2018','Alcool/Gasolina','Branca','9C2ND1120JR002506','1175333376','ND11E2J002511','bom','05/12/2018',24388.28)
addv('00164149','Motocicleta Viatura Policial','PLJ2345','HONDA','XRE 300','2018','2018','Alcool/Gasolina','Branca','9C2ND1120JR002528','1175329816','ND11E2J002537','bom','05/12/2018',24388.28)
addv('00169725','Veiculo Viatura Policial','RCX8D52','FORD','ECOSPORT SE AT 1.5','2020','2021','Alcool/Gasolina','Branca','9BFZB55S2M8846491','1248677614','Y2JCM8846491','bom','02/12/2020',65400.00)
addv('00169748','Motocicleta Viatura Policial','RCX0C51','HONDA','XRE 300','2020','2020','Alcool/Gasolina','Cinza','9C2ND1120LR006368','1248438709','ND11E2L006379','bom','02/12/2020',25312.00)
addv('00169767','Motocicleta Viatura Policial','RCX0J29','HONDA','XRE 300','2020','2020','Alcool/Gasolina','Cinza','9C2ND1120LR006333','1248435955','ND11E2L006344','bom','02/12/2020',25312.00)
addv('00169821','Motocicleta Viatura Policial','RCX2G63','HONDA','XRE 300','2020','2020','Alcool/Gasolina','Cinza','9C2ND1120LR006087','1248421350','ND11E2L006022','bom','02/12/2020',25312.00)
addv('00226207','Motocicleta Viatura Policial','SJX9F85','YAMAHA','LANDER XTZ 250','2024','2024','Alcool/Gasolina','Branca','9C6DG3320R0132962','01389856159','G3C4E-157885','bom','29/02/2024',34200.00)
addv('00230629','Veiculo Viatura Policial','SSM7B76','CHEVROLET','TRAILBLAZER LT D4A','2023','2024','Diesel','Bege','9BG156FK0RC419736','1403793929','FK0RC419736','bom','01/11/2024',348600.00,'00239722')
addv('00235268','Viatura Policial Tipo Furgao Base Movel','TGR6B76','FORD','TRANSIT 350 F','2025','2025','Diesel','Branca','WF0BTTVD2SU017369','1433673298','SU017369','bom','14/03/2025',274000.00)
addv('00241884','Veiculo Viatura Policial','THH6J35','RENAULT','DUSTER INTP MT','2025','2025','Alcool/Gasolina','Preta','93YHJD20XTJ356720','1466908138','H4MK745Q015282','bom','12/01/2026',201636.43,'00242996')
addv('00241892','Veiculo Viatura Policial','THH5F88','RENAULT','DUSTER INTP MT','2025','2025','Alcool/Gasolina','Preta','93YHJD208TJ356733','1466908472','H4MK745Q015955','bom','13/01/2026',201636.43,'00243005')
addv('Y00003720','Veiculo Viatura Policial','DYC8440','FORD','FIESTA','2008','2008','Alcool/Gasolina','Prata','9BFZF20A288231883','954713281','SMJA822319936','bom','29/01/2013',24000.00)
addv('Y00003846','Veiculo Viatura Policial','NFN7725','GM','CORSA SEDAN PREMIUM','2005','2005','Alcool/Gasolina','Prata','9BGXM19005B276583','862611717','A20036410','regular','30/04/2013',11592.00)
addv('Y00003847','Veiculo Viatura Policial','AMS1564','VOLKSWAGEM','GOL 1.6 POWER','2005','2005','Alcool/Gasolina','Prata','9BWCB05X35P120571','853795894','','regular','10/10/2013',10389.60)
addv('Y00004319','Veiculo Viatura Policial Maxx','KHH1676','GM','MERIVA','2008','2008','Alcool/Gasolina','Cinza','9BGXH75G08C735009','973553782','N20052101','regular','26/01/2015',26121.96)
addv('Y00005870','Veiculo Viatura Policial','NZH4413','VOLKSWAGEM','JETTA','2011','2012','Alcool/Gasolina','Branca','3VWBJ2168CM009161','372661726','CKJ006214','bom','04/05/2017',30000.00)
addv('Y00008656','Veiculo Viatura Policial','RPV7I81','GM','S10 LS DD4','2022','2023','Diesel','Branca','9BG148DK0PC424206','1346913681','LWNF222571023','bom','15/07/2023',252759.00)
addv('Y00008735','Veiculo Viatura Policial','FND1J21','NISSAN','VERSA SENSE CVT','2017','2017','Alcool/Gasolina','Branca','94DBCAN17HB119140','1124752959','HR16104322T','bom','24/01/2024',32816.00)
addv('Y00009227','Veiculo Viatura Policial','TGV7D66','CHEVROLET','S10 WT DD4','2025','2025','Diesel','Branca','9BG1481K0TC405743','1442477056','LWNF251351154','bom','17/07/2025',303586.20)
addv('Y00009292','Veiculo Viatura Policial','TGW5C79','RENAULT','DUSTER 1.6L','2025','2025','Alcool/Gasolina','Branca','93YHJD205TJ263359','1445601483','H4MK745Q007798','bom','18/07/2025',197345.10)
addv('Y00009293','Veiculo Viatura Policial','TGW0B22','RENAULT','DUSTER 1.6L','2025','2025','Alcool/Gasolina','Branca','93YHJD206TJ263354','1445601807','H4MK745Q007270','bom','18/07/2025',197345.10)
addv('Y00009295','Veiculo Viatura Policial','TGW0H54','RENAULT','DUSTER 1.6L','2025','2025','Alcool/Gasolina','Branca','93YHJD200TJ307235','1445614542','H4MK745Q009824','bom','18/07/2025',197345.10)
addv('Y00009314','Veiculo Viatura Policial','TGW0B90','RENAULT','DUSTER 1.6L','2025','2025','Alcool/Gasolina','Branca','93YHJD205TJ263314','1445577329','H4MK745Q007198','bom','18/07/2025',197345.10)

# ===== CONTA 5.1 - MOVEIS E UTENSILIOS =====
moveis = [
    ('00013456','Gaveteiro em Madeira com 03 Gavetas','material_permanente','mobiliario','','bom','02/01/1997',168.80,'01345600'),
    ('00031848','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','02/01/1997',117.80,'03184800'),
    ('00031995','Mesa para Telefone em Metal','material_permanente','mobiliario','','bom','02/01/1997',58.08,'03199500'),
    ('00071791','Mesa Estacao de Trabalho em L 1200x600x740mm','material_permanente','mobiliario','','bom','09/10/2010',490.00,''),
    ('00071792','Mesa Estacao de Trabalho em L 1200x600x740mm','material_permanente','mobiliario','','bom','09/10/2010',490.00,''),
    ('00071793','Mesa Estacao de Trabalho em L 1200x600x740mm','material_permanente','mobiliario','','bom','09/10/2010',490.00,''),
    ('00071794','Poltrona Fixa em Courvim Espaldar Medio com Bracos','material_permanente','mobiliario','','bom','09/10/2010',365.00,''),
    ('00071795','Poltrona Fixa em Courvim Espaldar Medio com Bracos','material_permanente','mobiliario','','bom','09/10/2010',365.00,''),
    ('00071811','Armario Baixo em Madeira','material_permanente','mobiliario','','bom','20/12/2007',460.00,''),
    ('00071812','Armario Baixo em Madeira','material_permanente','mobiliario','','bom','20/12/2007',460.00,''),
    ('00071813','Armario Baixo em Madeira','material_permanente','mobiliario','','bom','20/12/2007',460.00,''),
    ('00071814','Suporte para CPU','material_permanente','mobiliario','','bom','20/12/2007',85.00,''),
    ('00071815','Suporte para CPU','material_permanente','mobiliario','','bom','20/12/2007',85.00,''),
    ('00071816','Suporte para CPU','material_permanente','mobiliario','','bom','20/12/2007',85.00,''),
    ('00071817','Suporte para CPU','material_permanente','mobiliario','','bom','20/12/2007',85.00,''),
    ('00071819','Mesa Estacao de Trabalho em L 1200x1200x600x740mm','material_permanente','mobiliario','','bom','20/12/2007',510.00,''),
    ('00071820','Mesa Estacao de Trabalho em L 1200x1200x600x740mm','material_permanente','mobiliario','','bom','20/12/2007',510.00,''),
    ('00071821','Armario Alto em Aco','material_permanente','mobiliario','','bom','20/12/2007',295.00,''),
    ('00071822','Armario Alto em Aco','material_permanente','mobiliario','','bom','20/12/2007',295.00,''),
    ('00071823','Armario Alto em Aco','material_permanente','mobiliario','','bom','20/12/2007',295.00,''),
    ('00071824','Armario Alto em Madeira 02 Portas 02 Prateleiras','material_permanente','mobiliario','','bom','20/12/2007',522.00,''),
    ('00071825','Armario Alto em Madeira 02 Portas 02 Prateleiras','material_permanente','mobiliario','','bom','20/12/2007',522.00,''),
    ('00071829','Suporte para CPU e Estabilizador em Madeira','material_permanente','mobiliario','','bom','20/12/2007',99.00,''),
    ('00071830','Suporte para CPU e Estabilizador em Madeira','material_permanente','mobiliario','','bom','20/12/2007',99.00,''),
    ('00071832','Gaveteiro Volante em Madeira','material_permanente','mobiliario','','bom','20/12/2007',82.00,''),
    ('00071833','Gaveteiro Volante em Madeira','material_permanente','mobiliario','','bom','20/12/2007',82.00,''),
    ('00071834','Gaveteiro Volante em Madeira','material_permanente','mobiliario','','bom','20/12/2007',82.00,''),
    ('00071835','Gaveteiro Volante em Madeira','material_permanente','mobiliario','','bom','20/12/2007',82.00,''),
    ('00071848','Refrigerador Tipo Residencial 420L','material_permanente','mobiliario','CONSUL','bom','22/12/2009',1542.50,''),
    ('00071849','Refrigerador Tipo Residencial 420L','material_permanente','mobiliario','CONSUL','bom','22/12/2009',1542.50,''),
    ('00071942','Cama Tipo Beliche em Aco 2000x840mm Aco Nobre','material_permanente','mobiliario','ACO NOBRE','bom','22/12/2009',460.00,''),
    ('00071961','Cama Tipo Beliche em Aco 2000x840mm Aco Nobre','material_permanente','mobiliario','ACO NOBRE','bom','22/12/2009',460.00,''),
    ('00071962','Cama Tipo Beliche em Aco 2000x840mm Aco Nobre','material_permanente','mobiliario','ACO NOBRE','bom','22/12/2009',460.00,''),
    ('00071963','Cama Tipo Beliche em Aco 2000x840mm Aco Nobre','material_permanente','mobiliario','ACO NOBRE','bom','22/12/2009',460.00,''),
    ('00071964','Cama Tipo Beliche em Aco 2000x840mm Aco Nobre','material_permanente','mobiliario','ACO NOBRE','bom','22/12/2009',460.00,''),
    ('00071965','Cama Tipo Beliche em Aco 2000x840mm Aco Nobre','material_permanente','mobiliario','ACO NOBRE','bom','22/12/2009',460.00,''),
    ('00071990','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071991','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071992','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071993','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071994','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071995','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071996','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071997','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071998','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00071999','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00072000','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00072001','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',527.00,''),
    ('00072050','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072051','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072052','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072053','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072054','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072055','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072056','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','inservivel','22/12/2009',410.00,''),
    ('00072057','Mesa para Escritorio em Madeira 1200x700x740mm 03 Gavetas','material_permanente','mobiliario','','bom','22/12/2009',410.00,''),
    ('00072078','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072079','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072080','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072081','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072082','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072083','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072084','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072085','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072086','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072087','Armario Alto em Aco 02 Portas','material_permanente','mobiliario','','bom','22/12/2009',409.00,''),
    ('00072172','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00072174','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00072176','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00072180','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00072181','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00072182','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00072188','Cadeira Fixa em Tecido Espaldar Baixo Sem Bracos','material_permanente','mobiliario','','bom','22/12/2009',105.00,''),
    ('00074290','Bebedouro de Agua Tipo Garrafao Latina Acquatronic','material_permanente','mobiliario','LATINA','bom','23/12/2009',489.00,''),
    ('00074315','Sofa em Courvim 03 Lugares','material_permanente','mobiliario','IMPERIAL','bom','23/12/2009',837.50,''),
    ('00074316','Sofa em Courvim 03 Lugares','material_permanente','mobiliario','IMPERIAL','bom','23/12/2009',837.50,''),
    ('00074323','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074324','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074325','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074326','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074327','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074328','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074329','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074330','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074331','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00074332','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','','bom','23/12/2009',336.25,''),
    ('00100946','Mesa de Trabalho em Madeira 780x600x740mm','material_permanente','mobiliario','','bom','19/09/2012',275.00,''),
    ('00100947','Cadeira Fixa em Vinil Espaldar Medio Sem Braco','material_permanente','mobiliario','','bom','19/09/2012',236.67,''),
    ('00115843','Cadeira Fixa em Tecido Sem Bracos','material_permanente','mobiliario','','bom','26/11/2013',66.77,'00129319'),
    ('00115844','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',402.50,'00137020'),
    ('00115845','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',402.50,'00137033'),
    ('00115846','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',402.50,'00137036'),
    ('00115847','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',185.74,'00137039'),
    ('00115848','Armario em Aco com 02 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',383.35,'00137041'),
    ('00115849','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',185.74,'00137063'),
    ('00115850','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',185.74,'00137062'),
    ('00115851','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',185.74,'00137067'),
    ('00115852','Mesa para Refeitorio com 04 Cadeiras','material_permanente','mobiliario','','bom','26/11/2013',585.00,'00138671'),
    ('00115853','Mesa para Refeitorio com 04 Cadeiras','material_permanente','mobiliario','','bom','26/11/2013',585.00,'00138672'),
    ('00115856','Cadeira Giratoria em Vinil com Bracos','material_permanente','mobiliario','','bom','26/11/2013',343.42,'00138692'),
    ('00115857','Cadeira Giratoria em Vinil com Bracos','material_permanente','mobiliario','CAVALETTI','bom','26/11/2013',343.42,'00138693'),
    ('00115860','Poltrona Fixa em Vinil','material_permanente','mobiliario','','bom','26/11/2013',255.64,'00138700'),
    ('00115861','Poltrona Fixa em Vinil','material_permanente','mobiliario','','bom','26/11/2013',255.64,'00138701'),
    ('00115864','Cadeira Giratoria em Vinil Espaldar Medio com Bracos','material_permanente','mobiliario','','bom','26/11/2013',676.86,'00138851'),
    ('00115866','Cadeira Giratoria em Vinil Espaldar Medio com Bracos','material_permanente','mobiliario','','bom','26/11/2013',676.86,'00138853'),
    ('00115868','Cadeira Giratoria em Vinil Espaldar Medio com Bracos','material_permanente','mobiliario','','bom','26/11/2013',676.86,'00138855'),
    ('00115869','Cadeira Giratoria em Vinil Espaldar Medio com Bracos','material_permanente','mobiliario','','bom','26/11/2013',676.86,'00138856'),
    ('00115870','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',409.50,'00138965'),
    ('00115871','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','','bom','26/11/2013',409.50,'00138966'),
    ('00115872','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',409.50,'00138967'),
    ('00115873','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','','bom','26/11/2013',409.50,'00138968'),
    ('00115875','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',409.50,'00138970'),
    ('00115876','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',409.50,'00138971'),
    ('00115877','Armario Guarda-Roupa em Aco com 08 Portas','material_permanente','mobiliario','ITALBRAS','bom','26/11/2013',409.50,'00138972'),
    ('00115878','Armario Alto em Aco','material_permanente','mobiliario','','bom','26/11/2013',390.01,'00142268'),
    ('00115879','Armario Alto em Aco','material_permanente','mobiliario','','bom','26/11/2013',390.01,'00142269'),
    ('00115880','Poltrona Giratoria Espaldar Alto em Courvim','material_permanente','mobiliario','','bom','26/11/2013',513.57,'00142309'),
    ('00115881','Poltrona Giratoria Espaldar Alto em Courvim','material_permanente','mobiliario','','bom','26/11/2013',513.57,'00142310'),
    ('00115882','Poltrona Giratoria Espaldar Alto em Courvim','material_permanente','mobiliario','','bom','26/11/2013',513.57,'00142311'),
    ('00116004','Refrigerador Tipo Frigobar','material_permanente','mobiliario','CONSUL','bom','26/11/2013',729.37,'00142370'),
    ('00116005','Mesa para Reuniao em Madeira Retangular','material_permanente','mobiliario','','bom','26/11/2013',388.84,'00142371'),
    ('00116007','Refrigerador Tipo Residencial','material_permanente','mobiliario','','bom','26/11/2013',1700.00,'00143191'),
    ('00116009','Mesa para Escritorio em Madeira','material_permanente','mobiliario','','bom','26/11/2013',185.42,'00119074'),
    ('00116010','Cadeira Fixa em Tecido Sem Bracos','material_permanente','mobiliario','','bom','26/11/2013',66.77,'00129306'),
    ('00116011','Mesa para Micro/Terminal de Computador com Teclado Retratil e Suporte CPU','material_permanente','mobiliario','MF','bom','26/11/2013',149.44,'00129399'),
    ('00116012','Mesa para Micro/Terminal de Computador com Teclado Retratil e Suporte CPU','material_permanente','mobiliario','MF','bom','26/11/2013',149.44,'00129400'),
    ('00116013','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','MF','bom','26/11/2013',149.44,'00129407'),
    ('00116014','Mesa para Micro/Terminal de Computador','material_permanente','mobiliario','MF','bom','26/11/2013',149.44,'00129412'),
    ('00116015','Gaveteiro em Madeira com 02 Gavetas e um Gavetao','material_permanente','mobiliario','','bom','26/11/2013',438.75,'00138666'),
    ('00116016','Gaveteiro em Madeira com 02 Gavetas e um Gavetao','material_permanente','mobiliario','','bom','26/11/2013',438.75,'00138667'),
    ('00116017','Mesa de Trabalho em Madeira','material_permanente','mobiliario','','bom','26/11/2013',390.01,'00138674'),
    ('00116018','Mesa de Trabalho em Madeira','material_permanente','mobiliario','','bom','26/11/2013',390.01,'00138675'),
    ('00116019','Mesa de Trabalho em Madeira','material_permanente','mobiliario','','bom','26/11/2013',390.01,'00138857'),
    ('00116020','Gaveteiro em Madeira com 02 Gavetas e um Gavetao','material_permanente','mobiliario','','bom','26/11/2013',438.75,'00138858'),
    ('00116021','Gaveteiro em Madeira com 02 Gavetas e um Gavetao','material_permanente','mobiliario','','bom','26/11/2013',438.75,'00138859'),
    ('00116022','Armario Baixo em Madeira','material_permanente','mobiliario','','bom','26/11/2013',487.49,'00138860'),
    ('00116023','Armario Baixo em Madeira','material_permanente','mobiliario','','bom','26/11/2013',487.49,'00138861'),
    ('00116024','Mesa de Trabalho em Madeira em L','material_permanente','mobiliario','','bom','26/11/2013',828.76,'00138862'),
    ('00135092','Bebedouro de Agua Eletrico Suspenso','material_permanente','mobiliario','ELBER','bom','25/02/2015',300.00,''),
    ('00135193','Binoculo Prismatico Zoom 10 a 30x60 04 Prismas','material_permanente','mobiliario','BARSKA','bom','03/09/2014',490.00,''),
    ('00141438','Beliche em Metal MFS 2000x1500mm Desmontavel','material_permanente','mobiliario','MFS BELICHE','bom','16/12/2015',400.00,''),
    ('00141567','Sofa em Couro 03 Lugares com Bracos','material_permanente','mobiliario','IDEALIZE','bom','17/12/2015',975.00,''),
    ('00143524','Estante em Aco 05 Prateleiras 1980x930mm','material_permanente','mobiliario','PANDIN','bom','21/07/2015',300.00,''),
    ('00145496','Estante em Aco Bibliografica','material_permanente','mobiliario','','bom','19/05/2016',150.00,''),
    ('00145497','Estante em Aco Bibliografica','material_permanente','mobiliario','','bom','19/05/2016',150.00,''),
    ('00145498','Estante em Aco Bibliografica','material_permanente','mobiliario','','bom','19/05/2016',150.00,''),
    ('00145499','Estante em Aco Bibliografica','material_permanente','mobiliario','','bom','19/05/2016',150.00,''),
    ('00152131','Armario Alto em Aco 02 Portas 04 Prateleiras 800x400x1900mm','material_permanente','mobiliario','','bom','15/09/2017',709.98,''),
    ('00152132','Armario Alto em Aco 02 Portas 04 Prateleiras 800x400x1900mm','material_permanente','mobiliario','','bom','15/09/2017',709.98,''),
    ('00152133','Armario Alto em Aco 02 Portas 04 Prateleiras 800x400x1900mm','material_permanente','mobiliario','','bom','15/09/2017',709.98,''),
    ('00152140','Arquivo em Aco com 04 Gavetas','material_permanente','mobiliario','','bom','15/09/2017',492.02,''),
    ('00152153','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','','bom','15/09/2017',242.89,''),
    ('00153226','Armario Alto em Madeira 02 Portas 03 Prateleiras 800x500x1600mm','material_permanente','mobiliario','','bom','12/09/2017',531.13,''),
    ('00153227','Armario Alto em Madeira 02 Portas 03 Prateleiras 800x500x1600mm','material_permanente','mobiliario','','bom','12/09/2017',531.13,''),
    ('00153228','Armario Alto em Madeira 02 Portas 03 Prateleiras 800x500x1600mm','material_permanente','mobiliario','','bom','12/09/2017',531.13,''),
    ('00153229','Armario Alto em Madeira 02 Portas 03 Prateleiras 800x500x1600mm','material_permanente','mobiliario','','bom','12/09/2017',531.13,''),
    ('00153560','Cadeira Fixa em Vinil Espaldar Medio Bracos Fixos','material_permanente','mobiliario','','bom','14/09/2017',304.00,''),
    ('00153561','Cadeira Fixa em Vinil Espaldar Medio Bracos Fixos','material_permanente','mobiliario','','bom','14/09/2017',304.00,''),
    ('00153562','Cadeira Fixa em Vinil Espaldar Medio Bracos Fixos','material_permanente','mobiliario','','bom','14/09/2017',304.00,''),
    ('00153563','Cadeira Fixa em Vinil Espaldar Medio Bracos Fixos','material_permanente','mobiliario','','bom','14/09/2017',304.00,''),
    ('00153564','Cadeira Fixa em Vinil Espaldar Medio Bracos Fixos','material_permanente','mobiliario','','bom','14/09/2017',304.00,''),
    ('00153576','Cadeira Fixa em Vinil Espaldar Medio Sem Bracos','material_permanente','mobiliario','','bom','14/09/2017',141.00,''),
    ('00153577','Cadeira Fixa em Vinil Espaldar Medio Sem Bracos','material_permanente','mobiliario','','bom','14/09/2017',141.00,''),
    ('00153578','Cadeira Fixa em Vinil Espaldar Medio Sem Bracos','material_permanente','mobiliario','','bom','14/09/2017',141.00,''),
    ('00154674','Mesa de Trabalho Formato em L 1350/600x1350/600x740mm','material_permanente','mobiliario','','bom','31/05/2017',589.95,''),
    ('00154682','Mesa de Trabalho em Madeira 1200x730x740mm','material_permanente','mobiliario','','bom','31/05/2017',294.78,''),
    ('00154683','Mesa de Trabalho em Madeira 1200x730x740mm','material_permanente','mobiliario','','bom','31/05/2017',294.78,''),
    ('00154684','Mesa de Trabalho em Madeira 1200x730x740mm','material_permanente','mobiliario','','bom','31/05/2017',294.78,''),
    ('00154690','Gaveteiro Volante em Madeira 02 Gavetas 01 Gavetao','material_permanente','mobiliario','','bom','31/05/2017',370.00,''),
    ('00154691','Gaveteiro Volante em Madeira 02 Gavetas 01 Gavetao','material_permanente','mobiliario','','bom','31/05/2017',370.00,''),
    ('00154692','Gaveteiro Volante em Madeira 02 Gavetas 01 Gavetao','material_permanente','mobiliario','','bom','31/05/2017',370.00,''),
    ('00156203','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156204','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156205','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156206','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156207','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156209','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156210','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156211','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00156212','Cadeira Giratoria em Vinil Espaldar Medio Bracos Regulaveis','material_permanente','mobiliario','','bom','14/09/2017',342.15,''),
    ('00164688','Tela para Projecao 4x3m PVC Frontal com Ilhoses','material_permanente','mobiliario','NARDELLI','bom','11/02/2019',1293.00,''),
    ('00165529','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165530','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165533','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165534','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165535','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165536','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165537','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165538','Extintor de Incendio PQS 6kg ABC','material_permanente','seguranca','','bom','11/06/2019',134.26,''),
    ('00165539','Extintor de Incendio CO2 6kg','material_permanente','seguranca','','bom','11/06/2019',292.71,''),
    ('00168000','Forno Combinado a Gas Turbo Eletrico Fast Oven Gastronomico PRP-004','material_permanente','mobiliario','PROGAS','bom','16/10/2019',1615.00,''),
    ('00168910','Cadeira Fixa em Tecido Secretaria Ergonomica de Trapezio','material_permanente','mobiliario','','regular','03/07/2020',82.33,'00006218'),
    ('00168926','Estacao de Trabalho em Madeira 1600x1600mm','material_permanente','mobiliario','','regular','03/07/2020',188.26,'00006179'),
    ('00168944','Longarina com 03 Lugares Braco Corsa Tecido 302-B','material_permanente','mobiliario','','regular','03/07/2020',214.99,'00006199'),
    ('00168945','Longarina com 04 Lugares Braco Corsa Tecido 302-B','material_permanente','mobiliario','','regular','03/07/2020',178.36,'00006192'),
    ('00172549','Poltrona Giratoria em Vinil Espaldar Medio com Braco','material_permanente','mobiliario','FRISOKAR','bom','07/01/2021',852.83,''),
    ('00177549','Gaveteiro em Madeira','material_permanente','mobiliario','MIRANTI','bom','18/05/2022',503.99,''),
    ('00177584','Estante em Aco','material_permanente','mobiliario','ITALBRAS','bom','26/04/2022',550.00,''),
    ('00177585','Estante em Aco','material_permanente','mobiliario','ITALBRAS','bom','26/04/2022',550.00,''),
    ('00177586','Estante em Aco','material_permanente','mobiliario','ITALBRAS','bom','26/04/2022',550.00,''),
    ('00177587','Estante em Aco','material_permanente','mobiliario','ITALBRAS','bom','26/04/2022',550.00,''),
    ('00177588','Estante em Aco','material_permanente','mobiliario','ITALBRAS','bom','26/04/2022',550.00,''),
    ('00177589','Estante em Aco','material_permanente','mobiliario','ITALBRAS','bom','26/04/2022',550.00,''),
    ('00178366','Bebedouro Eletrico em Inox 220V','material_permanente','mobiliario','LIBEL-PRESS','bom','13/04/2022',740.00,''),
    ('00227288','Refrigerador Tipo Frigobar 90-124L 220V','material_permanente','mobiliario','EOS','bom','15/08/2024',1194.99,''),
    ('00233223','Refrigerador Tipo Frigobar 93L 220V Branco','material_permanente','mobiliario','MIDEA','bom','10/10/2024',1081.00,''),
    ('00234467','Ventilador de Parede','material_permanente','mobiliario','VENTISOL','bom','30/04/2025',294.66,''),
    ('00234468','Ventilador de Parede','material_permanente','mobiliario','VENTISOL','bom','30/04/2025',294.66,''),
    ('00234469','Ventilador de Parede','material_permanente','mobiliario','VENTISOL','bom','30/04/2025',294.66,''),
    ('Y00004530','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','','bom','27/08/2015',48.00,''),
    ('Y00004531','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','','bom','27/08/2015',48.00,''),
    ('Y00004540','Estante Bibliotecaria','material_permanente','mobiliario','','bom','27/08/2015',405.00,''),
    ('Y00004541','Estante Bibliotecaria','material_permanente','mobiliario','','bom','27/08/2015',405.00,''),
    ('Y00004542','Estante Bibliotecaria','material_permanente','mobiliario','','bom','27/08/2015',405.00,''),
    ('Y00004543','Estante Bibliotecaria','material_permanente','mobiliario','','bom','27/08/2015',405.00,''),
    ('Y00004544','Estante Bibliotecaria','material_permanente','mobiliario','','bom','27/08/2015',405.00,''),
    ('Y00004545','Estante Bibliotecaria','material_permanente','mobiliario','','bom','27/08/2015',405.00,''),
    ('Y00004760','Estante em Aco com 06 Prateleiras','material_permanente','mobiliario','','bom','26/11/2015',80.00,''),
    ('Y00006866','Forno de Microondas 34L 220V Branco MEO44','material_permanente','mobiliario','ELETROLUX','bom','13/06/2019',499.90,''),
]
for m in moveis:
    add(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],'' ,m[8] if len(m)>8 else '')

# ===== CONTA 5.3 - MAQUINAS E EQUIPAMENTOS =====
maqeq = [
    ('00032291','Conversor AC/DC para VHF CV 06','material_permanente','maquina','INTRACO','bom','02/01/1997',192.00,'','03229100'),
    ('00130759','Sinalizador Acustico para Veiculo 15 Modulos - Viatura OZI1276','material_permanente','maquina','AMELFIS','bom','16/12/2014',7475.00,'',''),
    ('00135512','DVR Video Monitoramento Digital 4 Camaras Monitor 19pol','material_permanente','monitoramento','AOC','bom','25/02/2015',3700.00,'',''),
    ('00135532','Gerador de Energia Portatil 10 KVA','material_permanente','maquina','','bom','25/02/2015',2000.00,'',''),
    ('00135542','GPS','material_permanente','maquina','DOTOM','bom','25/02/2015',400.00,'',''),
    ('00140255','Microcamera para Sistema de Seguranca Day Night 3.60mm CCD 1/3','material_permanente','monitoramento','VOXI','bom','14/08/2015',95.88,'','00136847'),
    ('00157577','Nobreak 700VA Bivolt','material_permanente','maquina','BMI','bom','09/01/2018',299.14,'',''),
    ('00178383','Condicionador de Ar Tipo Split 18000BTU 220V','material_permanente','maquina','AGRATTO','bom','18/04/2022',2529.05,'',''),
    ('00178384','Condicionador de Ar Tipo Split 18000BTU 220V','material_permanente','maquina','AGRATTO','bom','18/04/2022',2529.05,'',''),
    ('00178391','Purificador de Agua Acquaflex Hermetico Branco Cinza 220V','material_permanente','maquina','LIBELL','bom','30/05/2022',651.11,'',''),
    ('00178405','Purificador de Agua Acquaflex Hermetico Branco Fume 220V','material_permanente','maquina','LIBELL','bom','30/05/2022',651.11,'',''),
    ('00178406','Purificador de Agua Acquaflex Hermetico Branco Fume 220V','material_permanente','maquina','LIBELL','bom','30/05/2022',651.11,'',''),
    ('00178407','Purificador de Agua Acquaflex Hermetico Branco Fume 220V','material_permanente','maquina','LIBELL','bom','30/05/2022',651.11,'',''),
    ('00234845','Purificador de Agua Branco 127V','material_permanente','maquina','LIBELL','bom','09/10/2024',871.00,'',''),
]
for m in maqeq:
    add(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],'',m[9] if len(m)>9 else '')

# ===== SICOMB - MUNICAO (com estoque > 0) =====
municoes = [
    ('mun_40_etpp_180gr',  '.40 - ETPP 180GR - Expansivo de Alta Pressao',         'material_belico','municao','','bom','09/06/2026',0, 'Calibre .40 | Qtd confirmada no SICOMB - verificar saldo exato'),
    ('mun_556_ss109',      '5,56x45mm - Comum SS109 A',                            'material_belico','municao','','bom','09/06/2026',0, 'Calibre 5,56x45mm | Qtd: 645 (500+145) | SICOMB 09/06/2026'),
    ('mun_762_nato',       '7,62x51mm - NATO Ball A',                              'material_belico','municao','','bom','09/06/2026',0, 'Calibre 7,62x51mm | Qtd: ~500 (200+100+200 instrucao) | SICOMB 09/06/2026'),
    ('mun_40_eopp_nta',    '.40 - EOPP 180GR NTA A - Expansivo de Baixa Pressao', 'material_belico','municao','','bom','09/06/2026',0, 'Calibre .40 | Qtd: 600 (500+100) | SICOMB 09/06/2026'),
    ('mun_30_etog_110gr',  '.30 - ETOG 110GR A',                                  'material_belico','municao','','bom','09/06/2026',0, 'Calibre .30 | Qtd: 218 (100+79+39) | SICOMB 09/06/2026'),
    ('mun_556_m193',       '5,56x45mm - Comum M193',                              'material_belico','municao','','bom','09/06/2026',0, 'Calibre 5,56x45mm M193 | Verificar saldo SICOMB'),
    ('mun_12_proj_sing',   '12 - Projetil Simples Hi-Impact A',                   'material_belico','municao','','bom','09/06/2026',0, 'Calibre 12 | Qtd: 25 | SICOMB 09/06/2026'),
    ('mun_12_chsg_plast',  '12 - CH-SG Hi-Impact Plastico A',                     'material_belico','municao','','bom','09/06/2026',0, 'Calibre 12 | Qtd: 15 | SICOMB 09/06/2026'),
    ('mun_38_p_expo',      '.38 - +P Expansivo',                                  'material_belico','municao','','bom','09/06/2026',0, 'Calibre .38 | Qtd: 100 | SICOMB 09/06/2026'),
]
for m in municoes:
    itens.append({
        'id': 'inv_'+m[0],
        'tombamento': '',
        'descricao': m[1],
        'categoria': m[2],
        'subcategoria': m[3],
        'marca': m[4],
        'modelo': '',
        'numero_serie': '',
        'estado': m[5],
        'localizacao': '77a CIPM - Arsenal',
        'data_aquisicao': dt(m[6]),
        'valor_aquisicao': m[7],
        'observacoes': m[8],
        'tipo_carga': 'interna',
        'criadoEm': now
    })

# ===== SICOMB - COLETES =====
# IDs 1-3: INSERVIVEL (marcas antigas), IDs 4-220: PROTECTA
colete_validades = {
    # tombamento: validade
    1: '2018-04-30', 2: '2018-04-30', 3: '2018-04-30',  # vencidos INSERVIVEL
}
# Grupos de validade para os PROTECTA (baseado no relatorio SICOMB)
grupos_protecta = [
    (range(4,   10),  '2025-02-27', 'regular'),   # vencidos em 2025
    (range(10,  30),  '2027-06-21', 'bom'),
    (range(30,  60),  '2028-07-11', 'bom'),
    (range(60,  90),  '2028-07-18', 'bom'),
    (range(90, 110),  '2028-07-27', 'bom'),
    (range(110,130),  '2028-09-04', 'bom'),
    (range(130,150),  '2028-12-14', 'bom'),
    (range(150,165),  '2028-11-30', 'bom'),
    (range(165,180),  '2029-01-22', 'bom'),
    (range(180,200),  '2030-06-29', 'bom'),
    (range(200,210),  '2030-10-31', 'bom'),
    (range(210,221),  '2025-02-27', 'regular'),   # carga pessoal, alguns vencidos
]
for i in range(1,4):
    itens.append({
        'id': f'inv_col_{i:03d}',
        'tombamento': str(i),
        'descricao': 'Colete a Prova de Balas',
        'categoria': 'material_permanente',
        'subcategoria': 'colete',
        'marca': 'INBRATERRESTRE' if i<=2 else 'TAURUS',
        'modelo': '',
        'numero_serie': str(i),
        'estado': 'inservivel',
        'localizacao': '77a CIPM',
        'data_aquisicao': '',
        'valor_aquisicao': 0,
        'observacoes': 'SICOMB ID '+str(i)+' | Situacao: INSERVIVEL | SICOMB 09/06/2026',
        'tipo_carga': 'interna',
        'criadoEm': now
    })
for rng, validade, estado in grupos_protecta:
    for i in rng:
        itens.append({
            'id': f'inv_col_{i:03d}',
            'tombamento': str(i),
            'descricao': 'Colete a Prova de Balas',
            'categoria': 'material_permanente',
            'subcategoria': 'colete',
            'marca': 'PROTECTA',
            'modelo': '',
            'numero_serie': str(i),
            'estado': estado,
            'localizacao': '77a CIPM',
            'data_aquisicao': '',
            'valor_aquisicao': 0,
            'data_validade': validade,
            'observacoes': f'SICOMB ID {i} | Validade: {validade} | SICOMB 09/06/2026',
            'tipo_carga': 'interna',
            'criadoEm': now
        })

# Gerar JSON final
resultado = {
    'versao': '1.0',
    'exportadoEm': '2026-06-16',
    'fonte': 'SIAP/SICOMB - 77a CIPM BCS',
    'totalItens': len(itens),
    'invItens': itens
}

with open('BCS_inventario_importacao.json','w',encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f'TOTAL DE ITENS: {len(itens)}')
# Contagem por categoria
from collections import Counter
cats = Counter(x['categoria']+'/'+x['subcategoria'] for x in itens)
for k,v in sorted(cats.items()):
    print(f'  {k}: {v}')
