import pandas as pd
import dash
from dash import html, dash_table, callback, Input, Output, State, MATCH
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import feffery_antd_components as fac
import copy
import numpy as np
from utils.styles import number_input_classnames, input_classnames
from db.db_local import get_db_colection, get_materiais

##########################################################################################################

def materiais_form(materiais: dict):

    lista_materiais = get_materiais()
    opcoes_materiais = lista_materiais['TIPO MATERIAL'].unique()
    dropdown_opcoes_tipo_material = [{"label": opcao, "value": opcao} for opcao in opcoes_materiais]

    tipos_materiais = [
        'Parede externa',
        'Parede interna',
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

        # cria a nova coluna só se for dicionário
        if isinstance(material['Tipo do material'].iloc[0], dict):
            tipo_material_coluna = material['Tipo do material'].apply(lambda x: x.get('value') if isinstance(x, dict) else x)
            material_coluna = [tipo_material_coluna.values[i].get('value') for i in range(len(tipo_material_coluna))]
            material['Tipo do material'] = material_coluna

        # tipo_material_coluna = material['Tipo do material'].apply(lambda x: x.get('value') if isinstance(x, dict) else x)
        # material_coluna = [tipo_material_coluna.values[i].get('value') for i in range(len(tipo_material_coluna))]
        # material['Tipo do material'] = material_coluna

        if 'Calor específico [kJ/KgK]' in material.columns:
            material = material[['Tipo do material', 'Espessura [m]', 'Densidade [kg/m³]', 'Condutividade [W/mK]', 'Calor específico [kJ/KgK]', 'Resistência [m²K/W]']]
     
        material = material.reset_index()
        material = material.sort_values(by='index')

        # Trocar , por . quando for float
        for col in material.columns:
            if col not in ['Tipo do material']:
                material[col] = material[col].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
                material[col] = pd.to_numeric(material[col], errors='coerce')

        conteudo = html.Div([

                fac.AntdCollapse(
                    title=f"{tipo_material}",
                    isOpen=False,
                    style={'margin-bottom': '20px'},
                    children=[
                        
                        # html.H5(tipo_material, className='mt-4'),

                        html.H5('Quanto menor o index mais externo é o material na construção.', className='mb-2'),

                        dmc.Button(f"Adicionar {tipo_material.lower()}", leftSection=DashIconify(icon="ic:baseline-plus"),
                            style={'margin-bottom': '10px'}, radius="xl", n_clicks=0,
                            id={'type': 'adiciona-material', 'index': tipo_material.lower()}),

                        dmc.Button(f"Remover {tipo_material.lower()} selecionado", leftSection=DashIconify(icon="ic:baseline-minus"),
                            style={'margin-bottom': '10px', 'margin-left': '10px'}, radius="xl", n_clicks=0, color='red',
                            id={'type': 'remove-material', 'index': tipo_material.lower()}),

                        fac.AntdTable(
                            id={'type': 'materiais-table', 'index': tipo_material.lower()},
                            locale="en-us",
                            columns=[
                                {
                                    'title': col,
                                    'dataIndex': col,
                                    'name': col,
                                    'id': col,
                                    'renderOptions': {
                                        'renderType': 'select'
                                    },
                                    'width': 150
                                } if col in ['Tipo do material'] else 
                                {
                                    'title': col,
                                    'dataIndex': col,
                                    'name': col,
                                    'id': col,
                                    'editable': True,
                                    'width': 150
                                } if col in ['Espessura [m]', 'index'] else
                                {
                                    'title': col,
                                    'dataIndex': col,
                                    'name': col,
                                    'id': col,
                                    'editable': False,
                                    'width': 150
                                }
                                for col in material.columns
                            ],
                            data=[
                                {
                                    col: {
                                        'options': dropdown_opcoes_tipo_material,
                                        'value': row[col],
                                        'allowClear': True,
                                        'placeholder': 'Selecione...'
                                    } if col == 'Tipo do material' else row[col]

                                    for col in material.columns
                                }
                                for _, row in material.iterrows()
                            ],
                            bordered=True,
                            rowSelectionType='checkbox',
                            pagination=False,
                            sortOptions={'sortDataIndexes': ['index']},
                            selectedRowKeys=[],
                            selectedRows=[],
                            style={
                                'width': '100%',
                                'fontSize': '16px',
                                'fontFamily': 'Arial, sans-serif',
                                'overflowX': 'auto',
                                'overflowY': 'auto'
                            }
                        ),

                        html.Div(id={'type': 'campos-materiais-resultados-totais', 'index': tipo_material.lower()}, style={'margin-top': '10px'}),

                    ]

                ),
                
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
    lista_materiais = get_materiais()
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
        last_row = copy.deepcopy(rows[-1])  # Deep copy da última linha
        
        # se index estiver na ultima linha, somar index +1
        if 'index' in last_row:
            last_row['index'] += 1

        # Atribuir uma nova key única baseada no número de linhas
        if 'key' in last_row:
            last_row['key'] = str(len(rows))
        
        rows.append(last_row)    # Insere a nova linha no final da lista

    return rows

##########################################################################################################

@callback(
    Output({'type': 'materiais-table', 'index': MATCH}, 'data', allow_duplicate=True),
    Output({'type': 'materiais-table', 'index': MATCH}, 'selectedRowKeys'),
    Input({'type': 'remove-material', 'index': MATCH}, "n_clicks"),
    Input({'type': 'materiais-table', 'index': MATCH}, "data"),
    Input({'type': 'materiais-table', 'index': MATCH}, 'selectedRows'),
    Input({'type': 'materiais-table', 'index': MATCH}, 'selectedRowKeys'),
    prevent_initial_call=True
)
def remover_linha_selecionada(n_clicks, data, selectedRows, selectedRowKeys):
    
    ctx = dash.callback_context

    if ctx.triggered and selectedRows:
        # Para pattern-matching callbacks, verificar se o trigger foi o botão de remover
        trigger_id = ctx.triggered[0]['prop_id']
        if 'remove-material' in trigger_id and n_clicks > 0:

            keys = selectedRowKeys
            indices_para_remover = [int(key) for key in keys]

            data_df = pd.DataFrame(data)
            data_df = data_df.drop(indices_para_remover)
            data = data_df.to_dict('records')

            return data, []

    return dash.no_update, selectedRowKeys

##########################################################################################################

@callback(
    Output({'type': 'materiais-table', 'index': MATCH}, 'data', allow_duplicate=True),
    Output({'type': 'campos-materiais-resultados-totais', 'index': MATCH}, 'children'),
    Input({'type': 'materiais-table', 'index': MATCH}, 'data'),
    Input('zona_bioclimatica', 'value'),
    Input({'type': 'absortancia-mais-proxima', 'index': 2}, 'value'),
    Input({'type': 'absortancia-mais-proxima', 'index': 8}, 'value'),
    Input({'type': 'materiais-table', 'index': MATCH}, 'id'),
    prevent_initial_call='initial_duplicate',
)
def caracteristicas_materiais(data, zona_bioclimatica, absortancia_mais_proxima_fachada, absortancia_mais_proxima_cobertura, materiais_table_id):

    if not data:
        return dash.no_update, dash.no_update

    # Deep copy dos dados para evitar mutação de objetos compartilhados
    data = copy.deepcopy(data)
    
    # Processar cada linha dos dados
    for row in data:
        
        # Extrair tipo do material
        tipo_material_obj = row.get('Tipo do material')

        # Verificar se é um dicionário (dropdown) ou valor direto
        if isinstance(tipo_material_obj, dict):
            tipo_material = tipo_material_obj.get('value')
        else:
            tipo_material = tipo_material_obj

        if isinstance(tipo_material, dict):
            tipo_material = tipo_material.get('value')

        if isinstance(tipo_material, dict):
            tipo_material = tipo_material.get('value')

        if tipo_material:
            # Obter dados do material da base de dados
            lista_materiais = get_materiais()
            material_info = lista_materiais[lista_materiais['TIPO MATERIAL'] == tipo_material]

            if not material_info.empty:
                # Atualizar propriedades baseadas no tipo de material selecionado
                row['Densidade [kg/m³]'] = material_info['DENSIDADE'].iloc[0]
                row['Condutividade [W/mK]'] = material_info['CONDUTIVIDADE'].iloc[0]
                row['Calor específico [kJ/KgK]'] = material_info['CALOR ESPECIFICO'].iloc[0]
                
                # Calcular resistência térmica
                if not pd.isna(material_info['RESISTENCIA TERMICA'].iloc[0]):
                    row['Resistência [m²K/W]'] = material_info['RESISTENCIA TERMICA'].iloc[0]
                else:
                    espessura = row.get('Espessura [m]', 0)
                    condutividade = row.get('Condutividade [W/mK]', 1)
                    if espessura and condutividade:
                        row['Resistência [m²K/W]'] = np.round((float(espessura) / 100) / float(condutividade), 4)
                
                # Calcular capacidade térmica
                if not pd.isna(material_info['CAPACIDADE TERMICA'].iloc[0]):
                    row['Capacidade termica [kJ/(m²K)]'] = material_info['CAPACIDADE TERMICA'].iloc[0]
                else:
                    espessura = row.get('Espessura [m]', 0)
                    calor_especifico = row.get('Calor específico [kJ/KgK]', 0)
                    densidade = row.get('Densidade [kg/m³]', 0)
                    if all([espessura, calor_especifico, densidade]):
                        row['Capacidade termica [kJ/(m²K)]'] = float(espessura) * float(calor_especifico) * float(densidade)
    
    # Cálculos dos resultados totais
    df = pd.DataFrame(data)
    # df['Tipo do material'] = df['Tipo do material'].apply(lambda x: x['value'] if isinstance(x, dict) else x)

    # Converter colunas numéricas
    for col in df.columns:
        if col not in ['Tipo do material', 'key']:
            try:
                # Se for um dicionário, pegar apenas o valor
                if isinstance(df[col].iloc[0], dict):
                    continue
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

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
        if zona_bioclimatica and zona_bioclimatica <= 2:
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
    resultados_totais = dmc.Grid([
        dmc.GridCol(dmc.NumberInput(label="R total", classNames=number_input_classnames, disabled=True, value=round(r_total, 4), id={'type': 'Rtotal', 'index': id_material.lower()}), span=1),
        dmc.GridCol(dmc.NumberInput(label="CT", classNames=number_input_classnames, disabled=True, value=round(ct, 2), id={'type': 'CT', 'index': id_material.lower()}), span=1),
        dmc.GridCol(dmc.NumberInput(label="U", classNames=number_input_classnames, disabled=True, value=round(u, 4), id={'type': 'U', 'index': id_material.lower()}), span=1),        
        dmc.GridCol(dmc.TextInput(label="Critério", classNames=input_classnames, disabled=True, value=criterio, id={'type': 'criterio', 'index': id_material.lower()}), span=1),                     
    ])
        
    return data, resultados_totais

##########################################################################################################

