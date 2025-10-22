import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)

#######################################################################################

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

#######################################################################################    

def nome_secoes(df, frase):

    '''
    Retorna o nome das seções presentes no txt
    '''
    
    sections_names = []
    
    for valor in df.values:
        
        if frase in valor[0]:
            
            sections_names.append(valor[0])
            
    return sections_names

#######################################################################################

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

#######################################################################################

def get_zone_area_value(df_section, pavimentacao):
   
    names = []
    areas = []
    
    condicao = False
    for valor in df_section.values:
        
        valor = valor[0].upper()

        if pavimentacao == 'unifamiliar':

            if '!- NAME' in valor:
                names.append(valor.split(',')[0].replace(' ', ''))
                condicao = True
        
            if '!- FLOOR AREA' in valor and condicao == True:
                areas.append(float(valor.split(',')[0].replace(' ', '')))  
                condicao = False

        if pavimentacao == 'multifamiliar':
        
            # if '!- NAME' in valor and 'X' in valor and 'CIRCULACAO' not in valor and 'VAZIO' not in valor:
            if '!- NAME' in valor and 'X' in valor and valor.count('X') > 1:
                names.append(valor.split(',')[0].replace(' ', ''))
                condicao = True
            
            
            if '!- FLOOR AREA' in valor and condicao == True:
                areas.append(float(valor.split(',')[0].replace(' ', '')))  
                condicao = False

        # if pavimentacao == 'ambas':

        #     st.warning('Ainda implementando essa parte ....')
        #     return
     
    # Separando em ambientes e unidades

    if pavimentacao == 'unifamiliar':
            
        ambientes = [x.split(':')[1] for x in names]
        unidades = [x.split('X')[0] if 'X' in x.upper() else x.split(':')[0] for x in names]

    if pavimentacao == 'multifamiliar':

        unidades = [x.split(':')[0] + x.split(':')[1].split('X')[0] + x.split(':')[1].split('X')[1] for x in names]
        ambientes = [x.split(':')[1].split('X')[-1] for x in names]

    
    # if pavimentacao == 'ambas':            
    #     st.warning('Ainda implementando essa parte ....')
        
    df = pd.DataFrame()
    df['AREA'] = areas
    df['Unidades'] = unidades
    df['ambientes'] = ambientes
    df_final = pd.DataFrame(df.groupby(['Unidades'])['AREA'].sum())
        
    return df_final

#######################################################################################