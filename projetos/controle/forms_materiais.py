import pandas as pd
import dash
from dash import html, dash_table, callback, Input, Output, State, MATCH
from dash_iconify import DashIconify
import dash_mantine_components as dmc
# from utils.informacoes import opcoes_materiais, lista_materiais
from utils.styles import number_input_classnames, input_classnames
from db.db_local import get_db_colection

##########################################################################################################

def materiais_form(materiais: dict):

    lista_materiais = get_db_colection('materiais', 'materiais')
    opcoes_materiais = lista_materiais['TIPO MATERIAL'].unique()
    dropdown_opcoes_tipo_material = [{"label": opcao, "value": opcao} for opcao in opcoes_materiais]

    tipos_materiais = [
        'Parede interna',
        'Parede externa',
        'Cobertura edifício',
        'Piso (laje)'
    ]

    conteudos = []

    for tipo_material in tipos_materiais:

        # Seleciona os dados do tipo
        dados_materiais = materiais.get(tipo_material, {})

        # Converte para DataFrame
        material = pd.DataFrame(dados_materiais)
        material = material.rename(index={
            'tipo_material': 'Tipo do material',
            'espessura': 'Espessura [m]',
            'resistencia': 'Resistência [m²K/W]',
            'calor_especifico': 'Calor específico [kJ/KgK]',
            'densidade': 'Densidade [kg/m³]',
            'condutividade': 'Condutividade [W/mK]'
        })

        colunas = [x for x in material.columns if x not in ['R total', 'CT', 'U', 'Criterio']]
        material = material[colunas].transpose()
        
        if 'Calor específico [kJ/KgK]' in material.columns:
            material = material[['Tipo do material', 'Espessura [m]', 'Densidade [kg/m³]', 'Condutividade [W/mK]', 'Calor específico [kJ/KgK]', 'Resistência [m²K/W]']]
     
        conteudo = html.Div([
                
                html.H5(tipo_material, className='mt-4'),

                dmc.Button(f"Adicionar {tipo_material.lower()}", leftSection=DashIconify(icon="ic:baseline-plus"),
                    style={'margin-bottom': '10px'}, radius="xl", n_clicks=0,
                    id={'type': 'adiciona-material', 'index': tipo_material.lower()}),

                dash_table.DataTable(
                    id={'type': 'materiais-table', 'index': tipo_material.lower()},
                    columns=[
                        {"name": col, "id": col, "editable": True, "presentation": "dropdown"}
                        if col == "Tipo do material" else
                        {"name": col, "id": col, "editable": True}
                        for col in material.columns
                    ],
                    data=material.to_dict('records'),
                    dropdown={
                        "Tipo do material": {
                            "options": dropdown_opcoes_tipo_material,
                        },
                    },
                    style_cell={
                        'textAlign': 'center',
                        'padding': '10px',
                        'fontSize': '16px',
                        'fontFamily': 'Arial, sans-serif',
                    },
                    style_header={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                    },
                    style_data={
                        'backgroundColor': '#f9f9f9',
                        'color': '#333',
                        'border': '1px solid #ddd'
                    },
                    style_data_conditional=[
                        {
                            'if': {'state': 'active'},
                            'backgroundColor': 'transparent'
                        }
                    ],
                    style_table={'overflowX': 'auto', 'height': '250px'},
                    row_deletable=True,
                ),

                html.Div(id={'type': 'campos-materiais-resultados-totais', 'index': tipo_material.lower()}, style={'margin-top': '10px'}),

            ])

        conteudos.append(conteudo)

    return conteudos

##########################################################################################################

def calcular_resistencia_termica(row):

    lista_materiais = get_db_colection('materiais', 'materiais')

    lista_materiais_copy = lista_materiais.copy()
    lista_materiais_copy = lista_materiais_copy.rename(columns={'TIPO MATERIAL': 'Tipo do material'})
    material_info = lista_materiais_copy[lista_materiais_copy['Tipo do material'] == row['Tipo do material']]
    if pd.isna(material_info['RESISTENCIA TERMICA'].iat[0]) == False:
        return material_info['RESISTENCIA TERMICA'].iat[0]
    else:
        return (row['Espessura [m]'] / 100) / row['Condutividade [W/mK]']
    
##########################################################################################################

def calcular_capacidade_termica(row):
    lista_materiais = get_db_colection('materiais', 'materiais')
    lista_materiais_copy = lista_materiais.copy()
    lista_materiais_copy = lista_materiais_copy.rename(columns={'TIPO MATERIAL': 'Tipo do material'})
    material_info = lista_materiais_copy[lista_materiais_copy['Tipo do material'] == row['Tipo do material']]
    if pd.isna(material_info['CAPACIDADE TERMICA'].iat[0]) == False:
        return material_info['CAPACIDADE TERMICA'].iat[0]
    else:
        return row['Espessura [m]'] * 0.01 * row['Resistência [m²K/W]'] * row['Calor específico [kJ/KgK]'] * row['Densidade [kg/m³]']

##########################################################################################################

@callback(
    Output({'type': 'materiais-table', 'index': MATCH}, 'data'),
    Input({'type': 'adiciona-material', 'index': MATCH}, 'n_clicks'),
    State({'type': 'materiais-table', 'index': MATCH}, 'data'),
)
def adiciona_novo_material(n_clicks, rows):

    if n_clicks > 0 and rows:
        last_row = rows[-1].copy()  # Copia a última linha
        rows.append(last_row)    # Insere a nova linha no final da lista

    return rows

##########################################################################################################

@callback(
    Output({'type': 'materiais-table', 'index': MATCH}, 'data', allow_duplicate=True),
    Output({'type': 'materiais-table', 'index': MATCH}, 'columns', allow_duplicate=True),
    Output({'type': 'campos-materiais-resultados-totais', 'index': MATCH}, 'children'),
    Input({'type': 'materiais-table', 'index': MATCH}, 'data'),
    Input('zona_bioclimatica', 'value'),
    Input({'type': 'absortancia-mais-proxima', 'index': 2}, 'value'),
    Input({'type': 'absortancia-mais-proxima', 'index': 8}, 'value'),
    Input({'type': 'materiais-table', 'index': MATCH}, 'id'),
    prevent_initial_call='initial_duplicate',
)
def caracteristicas_materiais(data, zona_bioclimatica, absortancia_mais_proxima_fachada, absortancia_mais_proxima_cobertura, materiais_table_id):

    # Calcula das tabelas
    if not data:
        return data, dash.no_update

    df = pd.DataFrame(data)
    for colunas in df.columns:
        if colunas != 'Tipo do material':
            df[colunas] = df[colunas].astype(float)

    lista_materiais = get_db_colection('materiais', 'materiais')
    lista_materiais_copy = lista_materiais.copy()
    lista_materiais_copy = lista_materiais_copy.rename(columns={'TIPO MATERIAL': 'Tipo do material'})
    df['Densidade [kg/m³]'] = df['Tipo do material'].map(lambda x: lista_materiais_copy.loc[lista_materiais_copy['Tipo do material'] == x, 'DENSIDADE'].iat[0] if not lista_materiais_copy.loc[lista_materiais_copy['Tipo do material'] == x, 'DENSIDADE'].empty else None)
    df['Condutividade [W/mK]'] = df['Tipo do material'].map(lambda x: lista_materiais_copy.loc[lista_materiais_copy['Tipo do material'] == x, 'CONDUTIVIDADE'].iat[0] if not lista_materiais_copy.loc[lista_materiais_copy['Tipo do material'] == x, 'CONDUTIVIDADE'].empty else None)
    df['Calor específico [kJ/KgK]'] = df['Tipo do material'].map(lambda x: lista_materiais_copy.loc[lista_materiais_copy['Tipo do material'] == x, 'CALOR ESPECIFICO'].iat[0] if not lista_materiais_copy.loc[lista_materiais_copy['Tipo do material'] == x, 'CALOR ESPECIFICO'].empty else None)  
    df['Resistência [m²K/W]'] = df.apply(calcular_resistencia_termica, axis=1)
    df['Capacidade termica [kJ/(m²K)]'] = df.apply(calcular_capacidade_termica, axis=1)

    # Colunas nao editaveis
    colunas_calculadas = [
        "Densidade [kg/m³]",
        "Condutividade [W/mK]",
        "Calor específico [kJ/KgK]",
        "Resistência [m²K/W]",
        'Capacidade termica [kJ/(m²K)]'
    ]
    
    # Criação das colunas dinamicamente
    columns = [
        {
            "name": col,
            "id": col,
            "editable": False if col in colunas_calculadas else True,
            "presentation": "dropdown" if col == "Tipo do material" else "input"
        }
        for col in df.columns
    ]

    # Resultados totais
    id_material = materiais_table_id['index']

    if 'parede' in id_material.lower():
        rsi = 0.13
        rse = 0.054

    elif 'cobertura' in id_material.lower():
        rsi = 0.17
        rse = 0.04

    else:
        rsi = 0.10
        rse = 0.04

    r_total = df['Resistência [m²K/W]'].sum() + rsi + rse
    ct = df['Capacidade termica [kJ/(m²K)]'].sum()
    u = 1/r_total

    # Critérios
    if 'interna' in id_material.lower() or 'piso' in id_material.lower():

        criterio = 'Não aplicado' 

    else:

        if zona_bioclimatica <= 2:

            if 1/r_total <= 2.7:
                criterio = 'Atendido'
            else:
                criterio = 'Não atendido'

        else:

            if 'externa' in id_material.lower():
                absortancia_mais_proxima = absortancia_mais_proxima_fachada
            else:
                absortancia_mais_proxima = absortancia_mais_proxima_cobertura

            if absortancia_mais_proxima is not None:

                if absortancia_mais_proxima <= 0.6:

                    if 1/r_total <= 3.7:
                        criterio = 'Atendido'
                    else:
                        criterio = 'Não atendido'
                else:

                    if 1/r_total <= 2.5:
                        criterio = 'Atendido'
                    else:
                        criterio = 'Não atendido'   

            else:

                criterio = 'Não aplicado'          

    # Montando o children
    resultados_totais =  dmc.Grid([

        dmc.GridCol(dmc.NumberInput(label="R total", classNames=number_input_classnames, disabled=True, value=r_total, id={'type': 'Rtotal', 'index': id_material.lower()}), span=1),
        dmc.GridCol(dmc.NumberInput(label="CT", classNames=number_input_classnames, disabled=True, value=ct, id={'type': 'CT', 'index': id_material.lower()}), span=1),
        dmc.GridCol(dmc.NumberInput(label="U", classNames=number_input_classnames, disabled=True, value=u, id={'type': 'U', 'index': id_material.lower()}), span=1),        
        dmc.GridCol(dmc.TextInput(label="Critério", classNames=input_classnames, disabled=True, value=criterio, id={'type': 'criterio', 'index': id_material.lower()}), span=1),                     
                                    
    ])
        
    return df.to_dict('records'), columns, resultados_totais

##########################################################################################################

