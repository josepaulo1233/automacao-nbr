import os
import pandas as pd
import warnings
import numpy as np
warnings.simplefilter(action='ignore', category=UserWarning)

def find_section_index_by_name(name, sections, sections_names):
    
    '''
    Função para determinar o indice da lista de determinado name
    Retorna um dataframe com a parte desejada se houver a seção. Se não houver retorna um python string
    '''
    
    frase_no_txt = f'!-   ===========  ALL OBJECTS IN CLASS: {name.upper()} ==========='

    if frase_no_txt in sections_names:
    
        for index, valor in enumerate(sections):
            
            if frase_no_txt == valor[0].values[0].upper():
                
                index_name = index  

        return sections[index_name]
    
    else:

        return frase_no_txt + 'Nao existe'

def delete_sections_from_original_file(df, all_sections):
    
    '''
    Função que exclui as seções que vamos reescrever no txt ...
    '''
    
    for classes in all_sections:

        if type(classes) != str:

            indexes = classes.index.tolist()
            df.loc[indexes] = np.nan # colocando uma mascara para dar drop depois ...

    return df.dropna(inplace=True)

def remove_cracks(df_section):
    
    condicao = False
    for index_val, valor in enumerate(df_section.values):
        valor = str(valor[0]).upper()
        if '!- NAME' in valor and 'EXTRA CRACK' in valor:
            while condicao == False:
                index_val2 = index_val - 1
                if ';' in df_section[index_val2:index_val].values[0][0]:
                    condicao = True
                    df_section[index_val:] = np.nan
                else:
                    index_val = index_val - 1

    return df_section.dropna(inplace=True)

def replace_to_blank(df_section, line_to_blank_value):
    
    if type(df_section) != str:

        for valor, index_df in zip(df_section.values, df_section.index):
            if line_to_blank_value.upper() in valor[0].upper():
                df_section.loc[index_df, 0] = f'    ,                        {line_to_blank_value}'

    return

def fix_airflow_detailedopening(df_section, fenestration, esquadrias):
    
    if type(df_section) != str: 
    
        names = []
        
        for valor in df_section.values:
            
            valor = valor[0].upper()
            
            if '!- NAME' in valor:
                
                names.append(valor.split(',')[0])
                
    ########################################################################################################################################
                
        names_val = []
        
        for name in names:
            
            if 'WIN' in name:
                
                val = '0.00063'
            
            else:
                
                val = '0.0024'
                
            names_val.append(val)        
        
        air_mass_flow_coef = ['    '+ x +',                    !- Air Mass Flow Coefficient When Opening is Closed {kg/s-m}' for x in names_val]

    ########################################################################################################################################
                
        names_val2 = []
        
        for name in names:
            
            if 'WIN' in name:
                
                val = '0.63'
            
            else:
                
                val = '0.59'
                
            names_val2.append(val)        
        
        air_mass_flow_expo = ['    '+ x +',                    !- Air Mass Flow Exponent When Opening is Closed {dimensionless}' for x in names_val2]

    ########################################################################################################################################

        wins_area = []

        for valor in fenestration.values:

            valor = valor[0].upper()

            if 'WIN' in valor and 'M2' in valor and '!- NAME' not in valor:

                valor_area = valor.split(',')
                primeiro_dig = valor_area[1]
                segundo_dig = valor_area[2]
                valor_area = primeiro_dig + '.' + segundo_dig
                valor_area = valor_area.split('M')[0].replace(' ', '')
                valor_area = float(valor_area)

                wins_area.append(valor_area)

    ########################################################################################################################################
    
        coef_abertura = []
        
        for valor in wins_area:
        
            menor_erro = (np.abs(esquadrias['Área total do vidro [m²]'].values.astype(float) - valor)).argmin()
            coef_abertura.append(esquadrias['Coeficiente de abertura'].loc[menor_erro])

    ########################################################################################################################################
                
        names_val3 = []
        index = 0

        for name in names:

            if 'WIN' not in name:
                
                val = '1'

            else:
                val = str(coef_abertura[index])
                index += 1      

            names_val3.append(val)

        factor_opening = ['    '+ str(x) +',                    !- Width Factor for Opening Factor 2' for x in names_val3]

    ########################################################################################################################################
            
        i = 0
        j = 0
        k = 0
        
        for index_df, valor in zip(df_section.index, df_section.values):
            
            valor = valor[0].upper()
            
            if '!- AIR MASS FLOW COEFFICIENT WHEN OPENING IS CLOSED {KG/S-M}' in valor:
                
                df_section.loc[index_df, 0] = air_mass_flow_coef[i]
                i += 1
                
            if '!- AIR MASS FLOW EXPONENT WHEN OPENING IS CLOSED {DIMENSIONLESS}' in valor:
                
                df_section.loc[index_df, 0] = air_mass_flow_expo[j]
                j += 1

            if '!- WIDTH FACTOR FOR OPENING FACTOR 2 {DIMENSIONLESS}' in valor:
        
                df_section.loc[index_df, 0] = factor_opening[k]
                k += 1
                
            if '!- DISCHARGE COEFFICIENT FOR OPENING FACTOR 1 {DIMENSIONLESS}' in valor:
                
                df_section.loc[index_df, 0] = '    0.001,                   !- Discharge Coefficient for Opening Factor 1 {dimensionless}'
                
            if '!- DISCHARGE COEFFICIENT FOR OPENING FACTOR 2 {DIMENSIONLESS}' in valor:
                
                df_section.loc[index_df, 0] = '    0.6,                     !- Discharge Coefficient for Opening Factor 2 {dimensionless}'  

    return

def get_zone_with_people_names(df, zones):
    
    if type(df) != str: 

        '''
        Função para selecionar o nome dos ambientes com pessoas (ZONES_WHIT_PEOPLE)
        '''
        
        names = []
        
        for i in df.values:
            
            for j in zones:
                
                if j.upper() in i[0].upper() and '!- NAME' in i[0].upper():
                    
                    names.append(i[0])

        return names
    
def get_zone_with_all(df):
    
    if type(df) != str:
    
        names = []
        
        for i in df.values:
                
            if '!- NAME' in i[0].upper():
                
                names.append(i[0])
                    
        return names
    
def nome_secoes(df, frase):

    '''
    Retorna o nome das seções presentes no txt
    '''
    
    sections_names = []
    
    for valor in df.values:
        
        if frase in valor[0]:
            
            sections_names.append(valor[0])
            
    return sections_names

def separada_por_secao(df, frase):
            
    '''
    Função para achar as classes separadas

    todos_elementos_da_classe = df[lista[i]:lista[i+1]]

    retorna uma lista de dataframes correpondentes as classes encontradas no txt 

    '''

    lista = []
    for index, valor in enumerate(df.values):

        if frase in valor[0]:
            lista.append(index)
            
    dff = []
    for x in range(len(lista)):
        if x+1 < len(lista):
            dff.append(df[lista[x]:lista[x+1]])

    # Dando append na ultima classe        
    dff.append(df[lista[-1]:len(df)])

    return dff

def fix_airflor_surface(df_section):
    
    names = []

    for valor in df_section.values:

        valor = valor[0].upper()

        if '!- SURFACE NAME' in valor:

            names.append(valor)

    ventilation_control = []

    for name in names:

        if 'WIN' not in name:
            ventilation_control.append('NoVent')

        if 'WIN' in name:
            if 'BANH' in name or 'LAV' in name:
                ventilation_control.append('Constant')
            else:
                ventilation_control.append('NoVent')

    i = 0

    for index_df, valor_df in zip(df_section.index, df_section.values):

        #print (ventilation)

        valor_df = valor_df[0].upper()

        if '!- VENTILATION CONTROL MODE' in valor_df:

            df_section.loc[index_df, 0] = f'    {ventilation_control[i]},              !- Ventilation Control Mode'
            i += 1

    return
        
######################################################################## Testador #########################################################################

def limpar_celula(celula):
    if isinstance(celula, list):
        return [item.replace('\r', '').replace('\n', '') for item in celula]
    elif isinstance(celula, str):
        return celula.replace('\r', '').replace('\n', '')
    return celula

def check_mandatory_sections(sections_to_check, sections_names):

    '''
    Retorna uma lista com as seções faltantes
    '''

    sections_less = []
    
    for sessions in sections_to_check:

        sessions = sessions.upper()
        frase_no_txt = f'!-   ===========  ALL OBJECTS IN CLASS: {sessions.upper()} ==========='

        if frase_no_txt not in sections_names:

            sections_less.append(sessions)

    return sections_less

    
