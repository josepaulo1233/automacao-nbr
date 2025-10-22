#### FUNÇÕES PARA GERAR O TXT (.IDF) ARRUMANDO  #### 
#### CADA FUNÇÃO IRÁ GERAR UMA CLASSE ESPECIFICADA ####

import pandas as pd

######################################################################## OUTPUTVARIABLE #########################################################################

def gera_txt_OUTPUTVARIABLE(file, output_conditition=True):
    
    print('TXT: OUTPUTVARIABLE ...')

    '''
    Não há necessidade de usar objetos do txt aqui ... 
    '''
    
    qtdade_de_objetos = 2 # qtdade_de_objetos

    zero_linha = ['Output:Variable,']*len(range(qtdade_de_objetos))
    primeira_linha = ['     *,                  !- Key Value']*len(range(qtdade_de_objetos))
    segunda_linha = ['     '+x+',                  !- Variable Name' for x in ['Zone Operative Temperature', 'Site Outdoor Air Drybulb Temperature']]
    terceira_linha = ['     Hourly;                  !- Reporting Frequency']*len(range(qtdade_de_objetos))

    if output_conditition:

        for i in range(qtdade_de_objetos):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: OUTPUT:VARIABLE ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n\n"

            file.write(linha)

    return 

######################################################################## SCHEDULETYPELIMITS #########################################################################  

def gera_txt_SCHEDULETYPELIMITS(file, output_conditition=True):

    print('TXT: SCHEDULETYPELIMITS ...')

    '''
    Não há necessidade de utilizar objetos do txt de input
    '''
    
    qtdade_de_objetos = 4 # qtdade_de_objetos

    zero_linha = ['ScheduleTypeLimits,']*len(range(qtdade_de_objetos))
    primeira_linha = ['     '+x+',                  !- Name' for x in ['on_off', 'ocupacao', 'atividade', 'faixa_temp']]
    segunda_linha = ['     '+x+',                  !- Lower Limit Value' for x in ['0', '0', '0', '-100']]
    terceira_linha = ['     '+x+',                  !- Upper Limit Value' for x in ['1', '1', '1000', '100']]
    quarta_linha = ['     '+x+',                  !- Numeric Type' for x in ['Discrete', 'Continuous', 'Continuous', 'Continuous']]
    quinta_linha = ['     '+x+';                  !- Unit Type' for x in ['Control', 'Percent', 'ActivityLevel', 'Temperature']]

    if output_conditition:

        for i in range(qtdade_de_objetos):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: SCHEDULETYPELIMITS ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n\n"

            file.write(linha)

    return 

######################################################################## SCHEDULE_COMPACT #########################################################################      

def gera_txt_SCHEDULE_COMPACT(file, output_conditition=True):
    
    print('TXT: SCHEDULE_COMPACT ...')

    '''
    Não há necessidade de utilizar objetos do txt de input.
    Não muda ... sempre o mesmo. 
    '''

    string = ('''
!-   ===========  ALL OBJECTS IN CLASS: SCHEDULE:COMPACT ===========

Schedule:Compact,
    sch_ilum_sala,           !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 16:00,            !- Field 3
    0,                       !- Field 4
    Until: 22:00,            !- Field 5
    1,                       !- Field 6
    Until: 24:00,            !- Field 7
    0;                       !- Field 8

Schedule:Compact,
    sch_ilum_dorm,           !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 06:00,            !- Field 3
    0,                       !- Field 4
    Until: 08:00,            !- Field 5
    1,                       !- Field 6
    Until: 22:00,            !- Field 7
    0,                       !- Field 8
    Until: 24:00,            !- Field 9
    1;                       !- Field 10

Schedule:Compact,
    sch_ativ_sala,           !- Name
    atividade,               !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 24:00,            !- Field 3
    108;                     !- Field 4

Schedule:Compact,
    sch_ativ_dorm,           !- Name
    atividade,               !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 24:00,            !- Field 3
    81;                      !- Field 4

Schedule:Compact,
    sch_ocup_sala,           !- Name
    ocupacao,                !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 14:00,            !- Field 3
    0,                       !- Field 4
    Until: 18:00,            !- Field 5
    0.5,                     !- Field 6
    Until: 22:00,            !- Field 7
    1,                       !- Field 8
    Until: 24:00,            !- Field 9
    0;                       !- Field 10

Schedule:Compact,
    sch_ocup_dorm,           !- Name
    ocupacao,                !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 08:00,            !- Field 3
    1,                       !- Field 4
    Until: 22:00,            !- Field 5
    0,                       !- Field 6
    Until: 24:00,            !- Field 7
    1;                       !- Field 8

Schedule:Compact,
    sch_equip_sala,          !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 14:00,            !- Field 3
    0,                       !- Field 4
    Until: 22:00,            !- Field 5
    1,                       !- Field 6
    Until: 24:00,            !- Field 7
    0;                       !- Field 8

Schedule:Compact,
    Sch_tempVN,              !- Name
    faixa_temp,              !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 24:00,            !- Field 3
    19;                      !- Field 4

Schedule:Compact,
    ON,                      !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 24:00,            !- Field 3
    1;                       !- Field 4

Schedule:Compact,
    OFF,                     !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 24:00,            !- Field 3
    0;                       !- Field 4

Schedule:Compact,
    sch_hvac_sala,           !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 14:00,            !- Field 3
    0,                       !- Field 4
    Until: 22:00,            !- Field 5
    1,                       !- Field 6
    Until: 24:00,            !- Field 7
    0;                       !- Field 8

Schedule:Compact,
    sch_hvac_dorm,           !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 08:00,            !- Field 3
    1,                       !- Field 4
    Until: 22:00,            !- Field 5
    0,                       !- Field 6
    Until: 24:00,            !- Field 7
    1;                       !- Field 8

Schedule:Compact,
    sch_ocup_studio,         !- Name
    ocupacao,                !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 08:00,            !- Field 3
    1,                       !- Field 4
    Until: 14:00,            !- Field 5
    0,                       !- Field 6
    Until: 18:00,            !- Field 7
    0.5,                     !- Field 8
    Until: 24:00,            !- Field 9
    1;                       !- Field 10

Schedule:Compact,
    sch_ativ_studio,         !- Name
    atividade,               !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 08:00,            !- Field 3
    81,                      !- Field 4
    Until: 14:00,            !- Field 5
    0,                       !- Field 6
    Until: 22:00,            !- Field 7
    108,                     !- Field 8
    Until: 24:00,            !- Field 9
    81;                      !- Field 10

Schedule:Compact,
    sch_ilum_studio,         !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 06:00,            !- Field 3
    0,                       !- Field 4
    Until: 08:00,            !- Field 5
    1,                       !- Field 6
    Until: 16:00,            !- Field 7
    0,                       !- Field 8
    Until: 24:00,            !- Field 9
    1;                       !- Field 10

Schedule:Compact,
    sch_equip_studio,        !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 14:00,            !- Field 3
    0,                       !- Field 4
    Until: 22:00,            !- Field 5
    1,                       !- Field 6
    Until: 24:00,            !- Field 7
    0;                       !- Field 8
                    
Schedule:Compact,
    sch_hvac_studio,           !- Name
    on_off,                  !- Schedule Type Limits Name
    Through: 12/31,          !- Field 1
    For: AllDays,            !- Field 2
    Until: 08:00,            !- Field 3
    1,                       !- Field 4
    Until: 14:00,            !- Field 5
    0,                       !- Field 6
    Until: 18:00,            !- Field 7
    1,                     !- Field 8
    Until: 24:00,            !- Field 9
    1;              
''')

    if output_conditition:

        file.write(string)

    return     

######################################################################## AIRFLOWMULTIZONE_SURFACE COMPLETA #########################################################################

def get_surfaces_names(df):

    '''
    Função para pegar o nome das superficies da classe AIRFLOWMULTIZONE_SURFACE
    '''
    
    surface_names = []
    
    for i in df.values:
        
        if '!- SURFACE NAME' in i[0].upper() and 'CRACK' not in i[0].upper():
            
            name = i[0].split('!')[0].replace(' ', '')
            
            surface_names.append(name)

    return surface_names

def define_controle_vento(nome_do_ambiente, bib_ambiente):

    '''
    Função para definir o controle de vento do ambiente
    Utiliza a biblioteca de ambientes definada anteriormente
    A definição do controle de vento é feito pela intersecção dos valores de AMBIENTE, TIPO DE SUPERFICIE e ABERTURA
    '''
    
    nome_do_ambiente = nome_do_ambiente.upper()

    index_ambiente = []
    for index,x in enumerate(bib_ambiente['AMBIENTE'].values):
        x = x.upper()
        if x in nome_do_ambiente:
            index_ambiente.append(index)

    index_sup = []
    for index,x in enumerate(bib_ambiente['SUPERFICIE'].values):
        x = x.upper()
        if x in nome_do_ambiente or x.upper() in nome_do_ambiente:
            index_sup.append(index)

    index_abertura = []
    for index,x in enumerate(bib_ambiente['ABERTURA'].values):
        x = x.upper()
        if x in nome_do_ambiente or x.upper() in nome_do_ambiente:
            index_abertura.append(index)

    if len(index_abertura) == 0:
        index_abertura = []
        for index,x in enumerate(bib_ambiente['ABERTURA'].values):
            x = x.upper()
            if x == 'SEM ABERTURA':
                index_abertura.append(index)

    intersection = set(index_sup).intersection(index_ambiente, index_abertura)

    try:
        return bib_ambiente['CONTROLE DE VENTO'].loc[intersection.pop()]
    except:
        return intersection
    
def get_external_node_name(df):

    '''
    Função para pegar o nome do EXTERNAL NODE da classe AIRFLOWMULTIZONE_SURFACE
    '''
    
    external_names = []
    
    for i in df.values:
        
        if '!- EXTERNAL NODE NAME' in i[0].upper():
            
            external_names_sem_desc = i[0].split(',')[0].replace(' ', '')
            
            external_names.append(external_names_sem_desc)
            
    return external_names

def get_leake_component_name(df):

    '''
    Função para pegar o nome do LEAKAGE COMPONENT da classe AIRFLOWMULTIZONE_SURFACE
    '''
    
    leake_names = []
    
    for i in df.values:
        
        if '!- LEAKAGE COMPONENT NAME' in i[0].upper():
            
            leake_names_sem_desc = i[0].split(',')[0].replace(' ', '')
            
            leake_names.append(leake_names_sem_desc)
            
    return leake_names

            
def gera_txt_AIRFLOWNETWORKMULTIZONE_SURFACE(file, surface_names_whitout_desc, bib_ambiente, ambientes, leake_name, external_node_name, output_conditition=True):
    
    print('TXT: AIRFLOWNETWORKMULTIZONE_SURFACE ...')

    '''
    Necessita do nome das superficies dentro da clase (surface_names_whitout_desc)
    Necessita da biblioteca de ambiente (bib_ambiente)
    Necessita dos nomes do leakeage name (leake_name)
    Necessita dos nomes do external node name (external_node_name)
    '''

    ctl_vento = [] # Lista que vai armazenar o controle de vento 
    for x in surface_names_whitout_desc:
        if define_controle_vento(x, bib_ambiente) == set():
            nome = x.split(':')[1].split(',')[0]
            print(f'{nome} está com nome diferente da biblioteca de ambiente. Esperado um dos ambientes: {ambientes}')
        else:
            ctl_vento.append(define_controle_vento(x, bib_ambiente))

    if len(ctl_vento) == len(surface_names_whitout_desc):

        zero_linha = ['AirflowNetwork:MultiZone:Surface,']*len(surface_names_whitout_desc)
        primeira_linha = ['    '+ x +'           !- Surface Name' for x in surface_names_whitout_desc]
        segunda_linha = ['    '+ x +',            !- Leakage Component Name' for x in leake_name]
        terceira_linha = ['    '+ x +',             !- External Node Name' for x in external_node_name]
        quarta_linha = ['    1,                        !- Window/Door Opening Factor, or Crack Factor {dimensionless}']*len(surface_names_whitout_desc)
        quinta_linha = ['    '+ x +',              !- Ventilation Control Mode' for x in ctl_vento]
        sexta_linha = ['    ,                        !- Ventilation Control Zone Temperature Setpoint Schedule Name']*len(surface_names_whitout_desc)
        setima_linha = ['    ,                        !- Minimum Venting Open Factor {dimensionless}']*len(surface_names_whitout_desc)
        oitava_linha = ['    ,                        !- Indoor and Outdoor Temperature Difference Lower Limit For Maximum Venting Open Factor {deltaC}']*len(surface_names_whitout_desc)
        nona_linha = ['    ,                        !- Indoor and Outdoor Temperature Difference Upper Limit for Minimum Venting Open Factor {deltaC}']*len(surface_names_whitout_desc)
        decima_linha = ['    ,                        !- Indoor and Outdoor Enthalpy Difference Lower Limit For Maximum Venting Open Factor {deltaJ/kg}']*len(surface_names_whitout_desc)
        decimaprimeira_linha = ['    ,                        !- Indoor and Outdoor Enthalpy Difference Upper Limit for Minimum Venting Open Factor {deltaJ/kg}']*len(surface_names_whitout_desc)
        decimasegunda_linha = ['    ;                        !- Venting Availability Schedule Name']*len(surface_names_whitout_desc)

        if output_conditition:

            for i in range(len(surface_names_whitout_desc)):

                if i == 0:

                    cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: AIRFLOWNETWORK:MULTIZONE:SURFACE ==========='

                    linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimaprimeira_linha[i]}\n{decimasegunda_linha[i]}\n\n"

                else:

                    linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimaprimeira_linha[i]}\n{decimasegunda_linha[i]}\n\n"

                file.write(linha)

    else:

        print('AIRFLOWNETWORK:MULTIZONE:SURFACE não foi gerada')

        return 

######################################################################## AIRFLOWMULTIZONE_SURFACE SIMPLIFICADA #########################################################################

def get_surfaces_names_simplificada(df):

    '''
    Função para pegar o nome das superficies da classe AIRFLOWMULTIZONE_SURFACE
    '''
    
    surface_names = []
    
    for i in df.values:
        
        if '!- SURFACE NAME' in i[0].upper() and 'CRACK' not in i[0].upper():

            if 'WIN' in i[0].upper() or 'DOOR' in i[0].upper() or 'VENT' in i[0].upper():
            
                name = i[0].split('!')[0].replace(' ', '')
                
                surface_names.append(name)

    return surface_names

def get_leake_component_name_simplificada(surfaces):

    '''
    Função para pegar o nome do EXTERNAL NODE da classe AIRFLOWMULTIZONE_SURFACE
    '''
    
    external_names = []
    
    for i in surfaces:

        if 'DOOR' in i.upper():

            external_names_sem_desc = 'PORTA'
        
        elif 'WIN' in i.upper():

            external_names_sem_desc = 'JANELA'

        elif 'VENT' in i.upper():

            external_names_sem_desc = 'VENT'

        external_names.append(external_names_sem_desc)
            
    return external_names

# def get_external_node_name_simplificada(df): 

#     '''
#     Função para pegar o nome do LEAKAGE COMPONENT da classe AIRFLOWMULTIZONE_SURFACE
#     '''
    
#     leake_names = []
    
#     for i in df.values:
        
#         if '!- LEAKAGE COMPONENT NAME' in i[0].upper():
            
#             leake_names_sem_desc = i[0].split(',')[0].replace(' ', '')
            
#             leake_names.append(leake_names_sem_desc)
            
#     return leake_names

            
def gera_txt_AIRFLOWNETWORKMULTIZONE_SURFACE_SIMPLIFICADA(file, surface_names_whitout_desc, bib_ambiente, ambientes, leake_name, output_conditition=True):

    print(leake_name)
    
    print('TXT: AIRFLOWNETWORKMULTIZONE_SURFACE ...')

    '''
    Necessita do nome das superficies dentro da clase (surface_names_whitout_desc)
    Necessita da biblioteca de ambiente (bib_ambiente)
    Necessita dos nomes do leakeage name (leake_name)
    Necessita dos nomes do external node name (external_node_name)
    '''

    ctl_vento = [] # Lista que vai armazenar o controle de vento 
    for x in surface_names_whitout_desc:
        if define_controle_vento(x, bib_ambiente) == set():
            nome = x.split(':')[1].split(',')[0]
            print(f'{nome} está com nome diferente da biblioteca de ambiente. Esperado um dos ambientes: {ambientes}')
        else:
            ctl_vento.append(define_controle_vento(x, bib_ambiente))

    if len(ctl_vento) == len(surface_names_whitout_desc):

        zero_linha = ['AirflowNetwork:MultiZone:Surface,']*len(surface_names_whitout_desc)
        primeira_linha = ['    '+ x +'           !- Surface Name' for x in surface_names_whitout_desc]
        segunda_linha = ['    '+ x +',            !- Leakage Component Name' for x in leake_name]
        terceira_linha = ['    ,             !- External Node Name']*len(surface_names_whitout_desc)
        quarta_linha = ['    1,                        !- Window/Door Opening Factor, or Crack Factor {dimensionless}']*len(surface_names_whitout_desc)
        quinta_linha = ['    '+ x +',              !- Ventilation Control Mode' for x in ctl_vento]
        sexta_linha = ['    ,                        !- Ventilation Control Zone Temperature Setpoint Schedule Name']*len(surface_names_whitout_desc)
        setima_linha = ['    ,                        !- Minimum Venting Open Factor {dimensionless}']*len(surface_names_whitout_desc)
        oitava_linha = ['    ,                        !- Indoor and Outdoor Temperature Difference Lower Limit For Maximum Venting Open Factor {deltaC}']*len(surface_names_whitout_desc)
        nona_linha = ['    ,                        !- Indoor and Outdoor Temperature Difference Upper Limit for Minimum Venting Open Factor {deltaC}']*len(surface_names_whitout_desc)
        decima_linha = ['    ,                        !- Indoor and Outdoor Enthalpy Difference Lower Limit For Maximum Venting Open Factor {deltaJ/kg}']*len(surface_names_whitout_desc)
        decimaprimeira_linha = ['    ,                        !- Indoor and Outdoor Enthalpy Difference Upper Limit for Minimum Venting Open Factor {deltaJ/kg}']*len(surface_names_whitout_desc)
        decimasegunda_linha = ['    ;                        !- Venting Availability Schedule Name']*len(surface_names_whitout_desc)

        if output_conditition:

            for i in range(len(surface_names_whitout_desc)):

                if i == 0:

                    cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: AIRFLOWNETWORK:MULTIZONE:SURFACE ==========='

                    linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimaprimeira_linha[i]}\n{decimasegunda_linha[i]}\n\n"

                else:

                    linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimaprimeira_linha[i]}\n{decimasegunda_linha[i]}\n\n"

                file.write(linha)

    else:

        print('AIRFLOWNETWORK:MULTIZONE:SURFACE não foi gerada')

        return 


######################################################################## OTHEREQUIPAMENT #########################################################################

def sch_equip(zone_names_sala_studio):
    sch_equips = []
    for valor in zone_names_sala_studio:
        if 'STUDIO' in valor.upper():
            sch = 'sch_equip_studio,'
        if 'SALADEESTAR' in valor.upper():
            sch = 'sch_equip_sala,'
        sch_equips.append(sch)
    return sch_equips

def gera_txt_OTHEREQUIPAMENT(file, zone_names_sala_studio, output_conditition=True):

    print('TXT: OTHEREQUIPAMENT ...')

    '''
    Necessita dos nomes de ambiente com sala e studio -> zone_names_sala_studio
    '''

    zero_linha = ['OtherEquipment,']*len(zone_names_sala_studio)
    primeira_linha = ['    '+ x + ' Miscellaneous gain,' +'    !- Name' for x in zone_names_sala_studio]
    segunda_linha = ['    Electricity,             !- Fuel Type']*len(zone_names_sala_studio)
    terceira_linha = ['    '+ x +','+'    !- Zone or ZoneList Name' for x in zone_names_sala_studio]
    quarta_linha = ['    ' + x + '          !- Schedule Name' for x in sch_equip(zone_names_sala_studio)]
    quinta_linha = ['    EquipmentLevel,          !- Design Level Calculation Method']*len(zone_names_sala_studio)
    sexta_linha = ['    120,                     !- Design Level {W}']*len(zone_names_sala_studio)
    setima_linha = ['    ,                        !- Power per Zone Floor Area {W/m2}']*len(zone_names_sala_studio)
    oitava_linha = ['    ,                        !- Power per Person {W/person}']*len(zone_names_sala_studio)
    nona_linha = ['    0,                       !- Fraction Latent']*len(zone_names_sala_studio)
    decima_linha = ['    0.3,                     !- Fraction Radiant']*len(zone_names_sala_studio)
    decimop_linha = ['    0,                       !- Fraction Lost']*len(zone_names_sala_studio)
    decimos_linha = ['    0,                       !- Carbon Dioxide Generation Rate {m3/s-W}']*len(zone_names_sala_studio)
    decimot_linha = ['    General;                 !- End-Use Subcategory']*len(zone_names_sala_studio)

    if output_conditition:

        for i in range(len(zone_names_sala_studio)):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: OTHEREQUIPMENT   ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimop_linha[i]}\n{decimos_linha[i]}\n{decimot_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimop_linha[i]}\n{decimos_linha[i]}\n{decimot_linha[i]}\n\n"

            file.write(linha)

    return 

######################################################################## LIGHT #########################################################################

def sch_ilum(zone_names):
    sch_ilums = []
    for valor in zone_names:
        if 'DORM' in valor.upper() or 'SUITE' in valor.upper():
            sch = 'sch_ilum_dorm,'
        if 'STUDIO' in valor.upper():
            sch = 'sch_ilum_studio,'
        if 'SALADEESTAR' in valor.upper():
            sch = 'sch_ilum_sala,'

        sch_ilums.append(sch)
    return sch_ilums

def gera_txt_LIGHT(file, zone_names, output_conditition=True):

    zone_names_whitout_desc = [zone_names[name].split('!')[0].replace(' ', '') for name in range(len(zone_names))]
    zone_names_whitout_desc = [zone_names_whitout_desc[name].split(',')[0] for name in range(len(zone_names_whitout_desc))]

    print('TXT: LIGHT ...')

    '''
    Necessita do nome das zonas com dorms, suite, studio e sala -> zone_names
    '''

    zero_linha = ['Lights,']*len(zone_names)
    primeira_linha = ['    '+ x + ' General lighting,' +'    !- Name' for x in zone_names_whitout_desc]
    segunda_linha = ['    ' + x + ',' + '          !- Zone or ZoneList Name' for x in zone_names_whitout_desc]
    terceira_linha = ['    ' + x + '          !- Schedule Name' for x in sch_ilum(zone_names)]
    quarta_linha = ['    Watts/Area,              !- Design Level Calculation Method']*len(zone_names)
    quinta_linha = ['    ,                        !- Lighting Level {W}']*len(zone_names)
    sexta_linha = ['    5,                       !- Watts per Zone Floor Area {W/m2}']*len(zone_names)
    setima_linha = ['    ,                        !- Watts per Person {W/person}']*len(zone_names)
    oitava_linha = ['    0,                       !- Return Air Fraction']*len(zone_names)
    nona_linha = ['    0.32,                    !- Fraction Radiant']*len(zone_names)
    decima_linha = ['    0.23,                    !- Fraction Visible']*len(zone_names)
    decimop_linha = ['    1,                       !- Fraction Replaceable']*len(zone_names)
    decimos_linha = ['    GeneralLights;  !- End-Use Subcategory']*len(zone_names)

    if output_conditition:

        for i in range(len(zone_names)):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: LIGHTS  ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimop_linha[i]}\n{decimos_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decimop_linha[i]}\n{decimos_linha[i]}\n\n"

            file.write(linha)

    return 
 
######################################################################## PEOPLE #########################################################################

def sch_ocup(zone_names):
    sch_ocups = []
    for valor in zone_names:
        if 'DORM' in valor.upper() or 'SUITE' in valor.upper():
            sch = 'sch_ocup_dorm,'
        if 'STUDIO' in valor.upper():
            sch = 'sch_ocup_studio,'
        if 'SALADEESTAR' in valor.upper():
            sch = 'sch_ocup_sala,'

        sch_ocups.append(sch)
    return sch_ocups

########################################################################################################

def sch_ativ(zone_names):
    sch_ativs = []
    for valor in zone_names:
        valor = valor.upper()
        if 'DORM' in valor or 'SUITE' in valor:
            sch = 'sch_ativ_dorm;'
        if 'STUDIO' in valor:
            sch = 'sch_ativ_studio;'
        if 'SALADEESTAR' in valor:
            sch = 'sch_ativ_sala;'

        sch_ativs.append(sch)
        
    return sch_ativs

########################################################################################################

def numero_pessoas_na_sala(zone_names):
    
    seperador = []

    for valor in zone_names:

        valor = valor.upper()

        if 'DORM' in valor:
            index = valor.index('DORM')
            tipologia = valor[:index]
            ambiente = valor[index:]            
        if 'SUIT' in valor:
            index = valor.index('SUIT')
            tipologia = valor[:index]
            ambiente = valor[index:]     
        if 'SALA' in valor:
            index = valor.index('SALA')
            tipologia = valor[:index]
            ambiente = valor[index:]     
        if 'STUDIO' in valor:
            index = valor.index('STUDIO')
            tipologia = valor[:index]
            ambiente = valor[index:]  

        seperador.append([tipologia, ambiente])

    seperador = pd.DataFrame(seperador)
    seperador.columns = ['TIPOLOGIA', 'AMBIENTE']

    #######################################################################

    # Coloca 2 pessoas se for suite, dorm ou studio
    for index_separador, valor_separador in enumerate(seperador['AMBIENTE']):

        valor_separador = valor_separador.upper()

        if 'SUITE' in valor_separador or 'DORM' in valor_separador or 'STUDIO' in valor_separador:

            seperador.loc[index_separador, 'NUMERO_PESSOAS'] = 2

    #######################################################################

    # Agrupa os ambientes por tipologia e somando para o caso da SALA
    seperador_agrupado = pd.DataFrame(seperador.groupby('TIPOLOGIA')['AMBIENTE'].sum())
    seperador_agrupado.reset_index(inplace=True)

    # Seleciona apenas as salas dos ambientes separados
    seperador_sala = seperador[seperador['AMBIENTE'].str.contains('SALA')]

    # Coloca o número de pessoas nas salas (2*numero de dorms/suite se num_dorms/suite <= 2, ou 4 se num_dorms/suite > 2)
    for tipologia_agrupada, ambiente_agrupado in zip(seperador_agrupado['TIPOLOGIA'], seperador_agrupado['AMBIENTE']):
        
        for tipologia_original_sala, index_original_sala in zip(seperador_sala['TIPOLOGIA'], seperador_sala.index):
            
            if tipologia_agrupada == tipologia_original_sala:
                
                if 'DORM' in ambiente_agrupado:
                    num_p = ambiente_agrupado.count('DORM')
                elif 'SUIT' in ambiente_agrupado:
                    num_p = ambiente_agrupado.count('SUIT')
                else:
                    num_p = 10 # Um valor arbritario só para atribuir 4 na condicao abaixo. Nesse caso não há suits/dorms no mesmo ambiente da sala..
                
                if num_p <= 2:
                    num_p = 2*num_p
                else:
                    num_p = 4
                    
                seperador.loc[index_original_sala, 'NUMERO_PESSOAS'] = num_p      

    return seperador   
    
########################################################################################################

def gera_txt_PEOPLE(file, zone_names, output_conditition=True):

    
    # CONSTANTES para o PEOPLE

    SEPARADOR_PAVIMENTADO = 'X' # 8PAV:R02DXF04XBANHO1 -> X é o separador das topologias
    SEPARADOR_ZONAS = ':' # # 8PAV:R02DXF04XBANHO1 -> : é o sepador dos pavimentos   

    '''
    Necessita do nome das zones -> zone_names
    '''

    print('TXT: PEOPLE ...')
    
    zero_linha = ['People,']*len(zone_names)
    primeira_linha = ['    People'+ x + ',' +'    !- Name' for x in zone_names]
    segunda_linha = ['    ' + x + ',' + '          !- Zone or ZoneList Name' for x in zone_names]
    terceira_linha = ['    ' + x + '          !- Number of People Schedule Name' for x in sch_ocup(zone_names)]
    quarta_linha = ['    ' + 'People,                 !- Number of People Calculation Method']*len(zone_names)
    num_p = numero_pessoas_na_sala(zone_names)['NUMERO_PESSOAS'].values
    num_p = [int(x) for x in num_p]
    quinta_linha = ['    ' + str(x) +',' + '                      !- Number of People' for x in num_p]
    sexta_linha = ['    ' + '0,                      !- People per Zone Floor Area {person/m2}']*len(zone_names)
    setima_linha = ['    ' + ',                       !- Zone Floor Area per Person {m2/person}']*len(zone_names)
    oitava_linha = ['    ' + '0.3,                    !- Fraction Radiant']*len(zone_names)
    nona_linha = ['    ' + ',                       !- Sensible Heat Fraction']*len(zone_names)
    decima_linha = ['    ' + x + '          !- Activity Level Schedule Name' for x in sch_ativ(zone_names)]
    
    if output_conditition:

        for i in range(len(zone_names)):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: PEOPLE ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n\n"

            file.write(linha)
            
    return 

######################################################################## AIRFLOW_ZONE #########################################################################

def vent_control_mode(zone_names_all):
    vent_control_modes = []
    for valor in zone_names_all:
        if 'BANH' in valor.upper() or 'LAVABO' in valor.upper():
            vent = 'Constant,'
        else:
            vent = 'Temperature,'
        vent_control_modes.append(vent)
    return vent_control_modes

def sch_temp(zone_names_all):
    sch_temps = []
    for valor in zone_names_all:
        if 'BANH' in valor.upper() or 'LAVABO' in valor.upper():
            sch = ',          '
        else:
            sch = 'Sch_tempVN,'
        sch_temps.append(sch)
    return sch_temps

def vent_sch(zone_names_all):
    vent_schs = []
    for valor in zone_names_all:
        if 'BANH' in valor.upper() or 'LAVABO' in valor.upper():
            vent_sch_name = 'ON;            '
        elif 'DORM' in valor.upper() or 'SUITE' in valor.upper():
            vent_sch_name = 'sch_ocup_dorm; '
        elif 'SALADEESTAR' in valor.upper():
            vent_sch_name = 'sch_equip_sala;'        
        elif 'STUDIO' in valor.upper():
            vent_sch_name = 'sch_equip_studio;' 
        else:
            vent_sch_name = 'OFF;'
        vent_schs.append(vent_sch_name)
    return vent_schs

def gera_txt_AIRFLOWNETWORKMULTIZONE_ZONE(file, zone_names_all, output_conditition=True):

    print('TXT: AIRFLOWNETWORKMULTIZONE_ZONE ..')

    '''
    Necessita do nome de todas as zonas -> zone_names_all
    '''

    zero_linha = ['AirflowNetwork:MultiZone:Zone,']*len(zone_names_all)
    primeira_linha = ['    '+ x +',           !- Zone Name' for x in zone_names_all]
    segunda_linha = ['    '+ x +'             !- Ventilation Control Mode' for x in vent_control_mode(zone_names_all)]
    terceira_linha = ['    '+ x +'              !- Ventilation Control Zone Temperature Setpoint Schedule Name' for x in sch_temp(zone_names_all)]
    quarta_linha = ['    ,                        !- Minimum Venting Open Factor {dimensionless}']*len(zone_names_all)
    quinta_linha = ['    ,                        !- Indoor and Outdoor Temperature Difference Lower Limit For Maximum Venting Open Factor {deltaC}']*len(zone_names_all)
    sexta_linha = ['    ,                        !- Indoor and Outdoor Temperature Difference Upper Limit for Minimum Venting Open Factor {deltaC}']*len(zone_names_all)
    setima_linha = ['    ,                        !- Indoor and Outdoor Enthalpy Difference Lower Limit For Maximum Venting Open Factor {deltaJ/kg}']*len(zone_names_all)
    oitava_linha = ['    ,                        !- Indoor and Outdoor Enthalpy Difference Upper Limit for Minimum Venting Open Factor {deltaJ/kg}']*len(zone_names_all)
    nona_linha = ['    '+ x +'              !- Venting Availability Schedule Name' for x in vent_sch(zone_names_all)]

    if output_conditition:

        for i in range(len(zone_names_all)):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: AIRFLOWNETWORK:MULTIZONE:ZONE ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n\n"

            file.write(linha)

    return






