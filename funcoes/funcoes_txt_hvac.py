## HVACTEMPLATE

def gera_txt_HVACTEMPLATETHERMOSTAT(file, output_conditition=True):
    
    print('TXT: HVACTEMPLATETHERMOSTAT ...')

    '''
    Não há necessidade de utilizar objetos do txt de input

    '''
    
    qtdade_de_objetos = 1 # qtdade_de_objetos

    zero_linha = ['HVACTemplate:Thermostat,']*len(range(qtdade_de_objetos))
    primeira_linha = ['     termostato,                  !- Name']
    segunda_linha = ['     ,                  !- Heating Setpoint Schedule Name']
    terceira_linha = ['     21,                   !- Constant Heating Setpoint {C}']
    quarta_linha = ['     ,                  !- Cooling Setpoint Schedule Name']
    quinta_linha = ['     23;                  !- Constant Cooling Setpoint {C}']

    if output_conditition:

        for i in range(qtdade_de_objetos):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: HVACTEMPLATE:THERMOSTAT ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n\n"

            file.write(linha)

    return 

####################################################################################################################################

def sch_hvac(zone_names_only_sala_dorm):
    sch_equips = []
    for valor in zone_names_only_sala_dorm:
        if 'DORM' in valor.upper():
            sch = 'sch_hvac_dorm'
        if 'SUITE' in valor.upper():
            sch = 'sch_hvac_dorm'
        if 'SALADEESTAR' in valor.upper():
            sch = 'sch_hvac_sala'
        if 'STUDIO' in valor.upper():
            sch = 'sch_hvac_studio'
        sch_equips.append(sch)
    return sch_equips

def gera_txt_HVACTEMPLATEZONEIDEALLOADSAIRSYSTEM(file, zone_names_only_sala_dorm, output_conditition=True):
    
    print('TXT: HVACTEMPLATEZONEIDEALLOADSAIRSYSTEM ...')

    '''
    Necessita dessa informação zone_names_only_sala_dorm

    '''

    zero_linha = ['HVACTemplate:Zone:IdealLoadsAirSystem,']*len(zone_names_only_sala_dorm)
    primeira_linha = ['    '+ x +',    !- Zone Name' for x in zone_names_only_sala_dorm]
    segunda_linha = ['    termostato,              !- Template Thermostat Name']*len(zone_names_only_sala_dorm)
    terceira_linha = ['    '+ x +',              !- System Availability Schedule Name' for x in sch_hvac(zone_names_only_sala_dorm)]
    quarta_linha = ['    50,               !- Maximum Heating Supply Air Temperature {C}']*len(zone_names_only_sala_dorm)
    quinta_linha = ['    13,               !- Minimum Cooling Supply Air Temperature {C}']*len(zone_names_only_sala_dorm)
    sexta_linha = ['    0.0156,                 !- Maximum Heating Supply Air Humidity Ratio {kgWater/kgDryAir}']*len(zone_names_only_sala_dorm)
    setima_linha = ['    0.0077,                 !- Minimum Cooling Supply Air Humidity Ratio {kgWater/kgDryAir}']*len(zone_names_only_sala_dorm)
    oitava_linha = ['    NoLimit,                  !- Heating Limit']*len(zone_names_only_sala_dorm)
    nona_linha = ['    ,                  !- Maximum Heating Air Flow Rate {m3/s}']*len(zone_names_only_sala_dorm)
    decima_linha = ['    ,                  !- Maximum Sensible Heating Capacity {W}']*len(zone_names_only_sala_dorm)
    decima1_linha = ['    NoLimit,                    !- Cooling Limit']*len(zone_names_only_sala_dorm)
    decima2_linha = ['    ,                    !- Maximum Cooling Air Flow Rate {m3/s}']*len(zone_names_only_sala_dorm)
    decima3_linha = ['    ,                     !- Maximum Total Cooling Capacity {W}']*len(zone_names_only_sala_dorm)
    decima4_linha = ['    ,                     !- Heating Availability Schedule Name']*len(zone_names_only_sala_dorm)
    decima5_linha = ['    ,                     !- Cooling Availability Schedule Name']*len(zone_names_only_sala_dorm)
    decima6_linha = ['    None,                     !- Dehumidification Control Type']*len(zone_names_only_sala_dorm)
    decima7_linha = ['    0.7,                     !- Cooling Sensible Heat Ratio {dimensionless}']*len(zone_names_only_sala_dorm)
    decima8_linha = ['    ,                     !- Dehumidification Setpoint {percent}']*len(zone_names_only_sala_dorm)
    decima9_linha = ['    None,                      !- Humidification Control Type']*len(zone_names_only_sala_dorm)
    decima10_linha = ['    ,                       !- Humidification Setpoint {percent}']*len(zone_names_only_sala_dorm)
    decima11_linha = ['    None,                       !- Outdoor Air Method']*len(zone_names_only_sala_dorm)
    decima12_linha = ['    ,                       !- Outdoor Air Flow Rate per Person {m3/s}']*len(zone_names_only_sala_dorm)
    decima13_linha = ['    ,                        !- Outdoor Air Flow Rate per Zone Floor Area {m3/s-m2}']*len(zone_names_only_sala_dorm)
    decima14_linha = ['    ,                         !- Outdoor Air Flow Rate per Zone {m3/s}']*len(zone_names_only_sala_dorm)
    decima15_linha = ['    ,                          !- Design Specification Outdoor Air Object Name']*len(zone_names_only_sala_dorm)
    decima16_linha = ['    None,                          !- Demand Controlled Ventilation Type']*len(zone_names_only_sala_dorm)
    decima17_linha = ['    NoEconomizer,                           !- Outdoor Air Economizer Type']*len(zone_names_only_sala_dorm)
    decima18_linha = ['    None,                           !- Heat Recovery Type']*len(zone_names_only_sala_dorm)
    decima19_linha = ['    0.7,                            !- Sensible Heat Recovery Effectiveness {dimensionless}']*len(zone_names_only_sala_dorm)
    decima20_linha = ['    0.65;                            !- Latent Heat Recovery Effectiveness {dimensionless}']*len(zone_names_only_sala_dorm)

    if output_conditition:

        for i in range(len(zone_names_only_sala_dorm)):

            if i == 0:

                cabecalho = '!-   ===========  ALL OBJECTS IN CLASS: HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM ==========='

                linha = f"{cabecalho}\n\n{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decima1_linha[i]}\n{decima2_linha[i]}\n{decima3_linha[i]}\n{decima4_linha[i]}\n{decima5_linha[i]}\n{decima6_linha[i]}\n{decima7_linha[i]}\n{decima8_linha[i]}\n{decima9_linha[i]}\n{decima10_linha[i]}\n{decima11_linha[i]}\n{decima12_linha[i]}\n{decima13_linha[i]}\n{decima14_linha[i]}\n{decima15_linha[i]}\n{decima16_linha[i]}\n{decima17_linha[i]}\n{decima18_linha[i]}\n{decima19_linha[i]}\n{decima20_linha[i]}\n\n"

            else:

                linha = f"{zero_linha[i]}\n{primeira_linha[i]}\n{segunda_linha[i]}\n{terceira_linha[i]}\n{quarta_linha[i]}\n{quinta_linha[i]}\n{sexta_linha[i]}\n{setima_linha[i]}\n{oitava_linha[i]}\n{nona_linha[i]}\n{decima_linha[i]}\n{decima1_linha[i]}\n{decima2_linha[i]}\n{decima3_linha[i]}\n{decima4_linha[i]}\n{decima5_linha[i]}\n{decima6_linha[i]}\n{decima7_linha[i]}\n{decima8_linha[i]}\n{decima9_linha[i]}\n{decima10_linha[i]}\n{decima11_linha[i]}\n{decima12_linha[i]}\n{decima13_linha[i]}\n{decima14_linha[i]}\n{decima15_linha[i]}\n{decima16_linha[i]}\n{decima17_linha[i]}\n{decima18_linha[i]}\n{decima19_linha[i]}\n{decima20_linha[i]}\n\n"

            file.write(linha)

    return 

######################################################################## OUTPUTVARIABLE #########################################################################

def gera_txt_OUTPUTVARIABLEHVAC(file, output_conditition=True):
    
    print('TXT: OUTPUTVARIABLE ...')

    '''
    Não há necessidade de usar objetos do txt aqui ... 

    '''
    
    qtdade_de_objetos = 2 # qtdade_de_objetos

    zero_linha = ['Output:Variable,']*len(range(qtdade_de_objetos))
    primeira_linha = ['     *,                  !- Key Value']*len(range(qtdade_de_objetos))
    segunda_linha = ['     '+x+',                  !- Variable Name' for x in ['Zone Ideal Loads Zone Total Heating Energy', 'Zone Ideal Loads Zone Total Cooling Energy']]
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
