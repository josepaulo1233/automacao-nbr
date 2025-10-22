from dash import html, dcc, callback, Input, Output, MATCH, dash_table
import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
from utils.styles import input_classnames, number_input_classnames
import feffery_antd_components as fac
from collections import Counter

##########################################################################################################

def ambientes_form(ambientes: dict):

    ambientes = dict(list(ambientes.items()))

    conteudo = html.Div([
        
        dmc.Button("Adicionar ambiente", 
                   leftSection=DashIconify(icon="ic:baseline-plus"), 
                   style={'margin-bottom': '10px'}, 
                   radius="xl",
                   n_clicks=0,
                   id="add-btn-ambiente",
                   ),
        
        dcc.Store(id="ambientes", data=ambientes),
        html.Div(id="campos-ambientes", children=[]),
    
    ])

    return conteudo

##########################################################################################################

def create_ambientes_field(newindex, esquadrias, ambiente):

    esquadrias = pd.DataFrame(esquadrias)

    children = html.Div(

        [
            dmc.CheckboxGroup(
                id={'type': 'ambiente-esquadria-checkbox', 'index': newindex},
                label="Selecione os indicadores dentro do ambiente",
                withAsterisk=True,
                mt=10,
                children=dmc.Group(
                    [dmc.Checkbox(label=x, value=x) for x in esquadrias['Indicador']],
                    mt=10,
                ),
                value=ambiente.get('esquadrias', []),
            ),

            html.Div([
                
                dash_table.DataTable(
                id={'type': 'quantidade-ambiente-esquadria', 'index': newindex},
                columns=[{"name": col, "id": col, "editable": True} for col in ['esquadrias', 'quantidade']],
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'fontSize': '16px',
                    'fontFamily': 'Arial, sans-serif',
                },
                style_data_conditional=[
                    {
                        'if': {'state': 'active'},
                        'backgroundColor': 'transparent',
                        'textAlign': 'center',
                    }
                ],
                style_header={
                    'backgroundColor': '#4CAF50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',}
                )

            ], className='mt-3'),

            dbc.Row([

                dbc.Col([
                    
                    dmc.NumberInput(label="Área do ambiente (m²)", id={'type': 'area_ambiente', 'index': newindex}, min=1, step=0.01, value=ambiente.get('area_ambiente', 1), className='mb-2 mt-2', classNames=number_input_classnames, required=True),

                ], width=4),

                dbc.Col([
                    
                    dmc.TextInput(label="Ambiente", id={'type': 'ambiente', 'index': newindex}, value=ambiente.get('ambiente', 1), className='mb-2 mt-2', classNames=input_classnames, required=True),

                ], width=4),

                dbc.Col([
                    
                    dmc.TextInput(label="Torre/Casa", id={'type': 'torre_casa', 'index': newindex}, value=ambiente.get('torre_casa', 1), className='mb-2 mt-2', classNames=input_classnames, required=True),

                ], width=4),

                dbc.Col([
                    
                    dmc.TextInput(label="Pavimento", id={'type': 'pavimento', 'index': newindex}, value=ambiente.get('pavimento', 1), className='mb-2 mt-2', classNames=input_classnames, required=True),

                ], width=4),

                dbc.Col([
                    
                    dmc.TextInput(label="Unidade", id={'type': 'unidade', 'index': newindex}, value=ambiente.get('unidade', 1), className='mb-2 mt-2', classNames=input_classnames, required=True),

                ], width=4),


            ]),
            
            html.Div(id={'type': 'ambiente-esquadria-campos-caculados', 'index': newindex},),
            fac.AntdDivider(),
        ]
    )

    return children

##########################################################################################################

@callback(
    Output({'type': 'quantidade-ambiente-esquadria', 'index': MATCH}, 'data'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'value'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'id'),
    Input('ambientes', 'data'),
)
def update_quantidade_esquadrias(indicadores, id, ambientes):

    ambiente = ambientes.get(id.get('index'), {'esquadrias': 'indicador1', 'quantidade': 1})  # Dicionário {'esquadrias': 'indicador1', 'quantidade': 1}
    qtdade_esquadrias = ambiente.get('qtdade_esquadrias', [])
    data = []
    
    for indicador in indicadores:
        # Busca se já existe quantidade registrada para esse indicador
        quantidade = next(
            (item['quantidade'] for item in qtdade_esquadrias if item['esquadrias'] == indicador),
            1  # Valor padrão se não encontrar
        )

        data.append({'esquadrias': indicador, 'quantidade': quantidade})

    return data

##########################################################################################################

@callback(
    Output("campos-ambientes", "children", allow_duplicate=True),
    Input("add-btn-ambiente", "n_clicks"),
    Input("campos-ambientes", "children"),
    Input('editable-table', 'data'),
    Input('ambientes', 'data'),
    prevent_initial_call='initial_duplicate',
)
def add_field_ambiente(n_clicks, children, esquadrias, ambientes):

    ctx=dash.callback_context
    x = ctx.triggered_id

    if x == 'add-btn-ambiente':

        new_index = len(children)
        new_field = create_ambientes_field(new_index, esquadrias, ambientes)
        children.append(new_field) 

        return children    

    return dash.no_update

##########################################################################################################

@callback(
    Output('campos-ambientes', 'children'),
    Input('editable-table', 'data'),
    Input('ambientes', 'data'),
)
def campos_ambiente(esquadrias, ambientes):

    esquadrias = pd.DataFrame(esquadrias)

    childrens = []

    for ambiente in ambientes.keys():

        children = create_ambientes_field(ambiente, esquadrias, ambientes[ambiente])
        childrens.append(children)

    return childrens
    
##########################################################################################################

@callback(
    Output({'type': 'ambiente-esquadria-campos-caculados', 'index': MATCH}, 'children'),
    Input({'type': 'area_ambiente', 'index': MATCH}, 'value'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'value'),
    Input('editable-table', 'data'),
    Input('zona_bioclimatica', 'value'),
    Input('regiao', 'value'),
    Input({'type': 'quantidade-ambiente-esquadria', 'index': MATCH}, 'data'),
)
def campos_ambientes_calculados_esquadrias(area_ambiente, indicadores, esquadrias, zona_bioclimatica, regiao, qtdade):

    indicadores_original = indicadores

    if len(indicadores) > 0:

        indicadores = [
            item['esquadrias'] 
            for item in qtdade 
            for _ in range(int(item['quantidade']))
        ]
        # Conta quantas vezes cada indicador aparece
        contagens = Counter(indicadores)

        # Motando as esquadrias em um dataframe
        esquadrias = pd.DataFrame(esquadrias)

        # Filtra apenas os indicadores presentes em indicadores_original
        esquadrias_filtradas = esquadrias[esquadrias['Indicador'].isin(indicadores_original)].copy()

        # Adiciona a quantidade conforme contagem
        esquadrias_filtradas['quantidade'] = esquadrias_filtradas['Indicador'].map(contagens).fillna(0)

        # Soma ponderada pela quantidade
        soma_area_janelas = (esquadrias_filtradas['Área [m²]'] * esquadrias_filtradas['quantidade']).sum()

        childrens = []

        for index, indicador_ambiente in enumerate(indicadores):

            # Coeficiente de vidro
            coef_vidro = esquadrias[esquadrias['Indicador'] == indicador_ambiente]['Coeficiente de vidro'].values[0]

            # Area vidro referencia
            area_vidro_referencia = area_ambiente*0.17

            # Area janela referencia
            area_janela_referencia = area_vidro_referencia/coef_vidro
            
            # Area de influencia
            area_vidro = esquadrias[esquadrias['Indicador'] == indicador_ambiente]['Área [m²]'].values[0]
            area_influencia = (area_ambiente/soma_area_janelas)*area_vidro

            # proporção
            altura = esquadrias[esquadrias['Indicador'] == indicador_ambiente]['Altura [m]'].values[0]
            largura = esquadrias[esquadrias['Indicador'] == indicador_ambiente]['Largura [m]'].values[0]
            proporcao = min(float(altura), float(largura))/max(float(altura), float(largura))

            # Lados
            lado_maior2 = (area_janela_referencia/proporcao)**0.5
            lado_menor2 = lado_maior2*proporcao

            # Variação maior
            variacao_maior = (lado_maior2-max(float(altura), float(largura)))/2

            if variacao_maior < 0:
                situacao = html.H6(f'A janela do indicador {indicador_ambiente} diminuiu')
            else:
                situacao = html.H6(f'A janela do indicador {indicador_ambiente} aumentou')

            # Montando o children
            children = html.Div([

                html.H6(f'{indicador_ambiente.title()}', className='fw-bold'),

                dmc.Grid([
                    dmc.GridCol(dmc.TextInput(label=f"Area de influência", classNames=input_classnames, disabled=True, value=np.round(area_influencia, 2), id={'type': 'area_de_influencia', 'index': f'{index}{indicador_ambiente}'}), span=1),
                    dmc.GridCol(dmc.TextInput(label=f"Coeficiente de vidro", classNames=input_classnames, disabled=True, value=coef_vidro, id={'type': 'area_janela', 'index': f'{index}{indicador_ambiente}'}), span=1),
                    dmc.GridCol(dmc.TextInput(label="Lado maior 2", classNames=input_classnames, disabled=True, value=np.round(lado_maior2, 2), id={'type': 'lado_maior2_ambiente', 'index': f'{index}{indicador_ambiente}'}), span=1),
                    dmc.GridCol(dmc.TextInput(label="Lado menor 2", classNames=input_classnames, disabled=True, value=np.round(lado_menor2, 2), id={'type': 'lado_menor2_ambiente', 'index': f'{index}{indicador_ambiente}'}), span=1),
                    dmc.GridCol(dmc.TextInput(label="Variação maior", classNames=input_classnames, disabled=True, value=np.round(variacao_maior, 2), id={'type': 'variacao_maior_ambiente', 'index': f'{index}{indicador_ambiente}'}), span=1),
                    dmc.GridCol(html.Div(children=situacao, className='fw-bold mt-2', id={'type': 'situacao_ambiente', 'index': f'{index}{indicador_ambiente}'}), span=1),
                ]),

            ], className='mt-3')

            childrens.append(children)

        # Resultados gerais
        # Calculando a soma das areas ponderadas
        esquadrias['Area*coef abertura'] = esquadrias['Área [m²]']*esquadrias['Coeficiente de abertura']
        soma_areas_ponderadas_abertura =  esquadrias['Area*coef abertura'].sum()

        # Coeficiente de acordo com regiao e zona bioclimatica
        if zona_bioclimatica <= 7:
            coeficiente = 0.07

        else:
            if regiao == 'Norte':
                coeficiente = 0.12
            elif regiao == 'Nordeste' or regiao == 'Sudeste':
                coeficiente = 0.8
            else:
                coeficiente = 0.7

        # Situação se a abertura de ventilação passou
        if soma_areas_ponderadas_abertura >= coeficiente*area_ambiente:
            situacao_abertura_ventilacao = 'Não passou'
        else:
            situacao_abertura_ventilacao = 'Passou'  

        children_areas_ponderadas_abertura = html.H6(f'Soma das areas ponderadas pelo coeficiente de abertura: {soma_areas_ponderadas_abertura: .2f}m². Situação: {situacao_abertura_ventilacao}', className='mt-4', id={'type': 'situacao_abertura_ventilacao', 'index': f'{indicador_ambiente}'}) 

        # Areas ponderadas pelos coefs de vidro
        esquadrias['Area*coef vidro'] = esquadrias['Área [m²]']*esquadrias['Coeficiente de vidro']
        soma_areas_ponderadas_vidro = esquadrias['Area*coef vidro'].sum()

        if area_ambiente <= 20:
            if soma_areas_ponderadas_vidro <= 0.2*area_ambiente:
                situacao_elementos_transparentes = 'Passou'
            else:
                situacao_elementos_transparentes = 'Não passou'
        
        else:
            if soma_areas_ponderadas_vidro <= 4:
                situacao_elementos_transparentes = 'Passou'
            else:
                situacao_elementos_transparentes = 'Não passou'

        children_areas_ponderadas_vidro = html.H6(f'Soma das areas ponderadas pelo coeficiente de vidro: {soma_areas_ponderadas_vidro: .2f}m². Situação: {situacao_elementos_transparentes}', id={'type': 'situacao_elementos_transparentes', 'index': f'{indicador_ambiente}'}) 

        childrens.append(children_areas_ponderadas_abertura)
        childrens.append(children_areas_ponderadas_vidro)
    
        return childrens

##########################################################################################################

