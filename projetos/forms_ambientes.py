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
import json

##########################################################################################################

def ambientes_form(ambientes: dict):

    # Manter a ordem original dos ambientes
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
        dcc.Store(id="ambiente-counter", data=len(ambientes)),
        html.Div(id="campos-ambientes", children=[]),
    
    ])

    return conteudo

##########################################################################################################

def create_ambientes_field(newindex, esquadrias, ambiente):

    esquadrias = pd.DataFrame(esquadrias)

    if 'ambiente' not in str(newindex):
        newindex_checkbox = f'ambiente{newindex}'
    else:
        newindex_checkbox = newindex

    children = html.Div([

        # Cabeçalho do ambiente com botão de deletar
        dbc.Row([
            dbc.Col([
                html.H5(f"Ambiente {newindex_checkbox}", className="fw-bold mb-3")
            ], width=10),
            dbc.Col([
                dmc.Button(
                    f"Deletar {newindex_checkbox}",
                    leftSection=DashIconify(icon="ic:baseline-delete"),
                    size="sm",
                    color="red",
                    variant="outline",
                    id={'type': 'delete-ambiente-btn', 'index': newindex_checkbox},
                    n_clicks=0,
                )
            ], width=2, className="text-end"),
        ], className="mb-3"),

        dmc.CheckboxGroup(
            id={'type': 'ambiente-esquadria-checkbox', 'index': newindex_checkbox},
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
                        # 'if': {'Input': 'active'},
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
            
            html.Div(id={'type': 'ambiente-esquadria-campos-calculados', 'index': newindex},),
            fac.AntdDivider(),
        ],
        id={'type': 'ambiente-container', 'index': newindex_checkbox}  # Container para facilitar remoção
    )

    return children

##########################################################################################################

@callback(
    Output({'type': 'quantidade-ambiente-esquadria', 'index': MATCH}, 'data'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'value'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'children'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'id'),
    Input('ambientes', 'data'),
)
def update_quantidade_esquadrias(inds, children, id, ambientes):

    valores = [child['props']['value'] for child in children['props']['children']]
    ambiente = ambientes.get(id.get('index')) 
    qtdade_esquadrias = ambiente.get('qtdade_esquadrias', [])

    # Adiciona um item {'esquadrias': 'indicador1', 'quantidade': 1} para cada indicador selecionado que não esteja na lista
    for indicador in inds:
        if indicador not in [item['esquadrias'] for item in qtdade_esquadrias]:
            qtdade_esquadrias.append({'esquadrias': indicador, 'quantidade': 1})

    qtdade_esquadrias = [item for item in qtdade_esquadrias if item['esquadrias'] in inds]
    indicadores_temp = [qtdade_esquadrias[i]['esquadrias'] for i in range(len(qtdade_esquadrias))]
    indicadores = [x for x in indicadores_temp if x in valores]

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
    [Output("campos-ambientes", "children", allow_duplicate=True),
     Output("ambiente-counter", "data", allow_duplicate=True),
     Output("ambientes", "data", allow_duplicate=True)],
    [Input("add-btn-ambiente", "n_clicks"),
     Input({'type': 'delete-ambiente-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [dash.dependencies.State("campos-ambientes", "children"),
     dash.dependencies.State('editable-table', 'data'),
     dash.dependencies.State('ambientes', 'data'),
     dash.dependencies.State("ambiente-counter", "data")],
    prevent_initial_call=True,
)
def manage_ambientes(add_clicks, delete_clicks, children, esquadrias, ambientes, counter):
    
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    triggered_prop = ctx.triggered[0]['prop_id']
    
    # Adicionar novo ambiente
    if 'add-btn-ambiente' in triggered_prop:
        if add_clicks and add_clicks > 0 and esquadrias:
            new_counter = (counter or 0) + 1
            new_index = f'ambiente{new_counter}'
            
            # Criar novo ambiente vazio
            novo_ambiente = {
                'esquadrias': [],
                'area_ambiente': 1,
                'ambiente': '',
                'torre_casa': '',
                'pavimento': '',
                'unidade': '',
                'qtdade_esquadrias': []
            }
            
            # Adicionar ao dicionário de ambientes
            if not ambientes:
                ambientes = {}
            ambientes[new_index] = novo_ambiente
            
            # Criar novo campo
            new_field = create_ambientes_field(new_index, esquadrias, novo_ambiente)
            if not children:
                children = []
            children.append(new_field)
            
            return children, new_counter, ambientes
    
    # Deletar ambiente específico
    elif 'delete-ambiente-btn' in triggered_prop and delete_clicks:
        # Extrair o índice do ambiente a ser deletado do prop_id
        try:
            # Parse do JSON do ID do botão clicado
            start_idx = triggered_prop.find('{')
            end_idx = triggered_prop.find('}') + 1
            button_id_str = triggered_prop[start_idx:end_idx]
            button_id = json.loads(button_id_str)
            ambiente_to_delete = button_id['index']
            
            # Verificar se algum botão de deletar foi clicado
            if any(clicks and clicks > 0 for clicks in delete_clicks if clicks is not None):
                # Remover do dicionário de ambientes
                if ambiente_to_delete in ambientes:
                    del ambientes[ambiente_to_delete]
                
                # Recriar todos os campos sem o deletado
                new_children = []
                for ambiente_key, ambiente_data in ambientes.items():
                    field = create_ambientes_field(ambiente_key, esquadrias, ambiente_data)
                    new_children.append(field)
                
                return new_children, counter, ambientes
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    
    return dash.no_update, dash.no_update, dash.no_update

##########################################################################################################

@callback(
    [Output('campos-ambientes', 'children'),
     Output("ambiente-counter", "data")],
    [Input('editable-table', 'data'),
     Input('ambientes', 'data')],
)
def campos_ambiente_inicial(esquadrias, ambientes):
    
    if not esquadrias or not ambientes:
        return [], len(ambientes) if ambientes else 0

    esquadrias = pd.DataFrame(esquadrias)
    childrens = []
    max_counter = 0

    for ambiente_key, ambiente_data in ambientes.items():
        # Extrair número do ambiente para manter controle do counter
        if 'ambiente' in str(ambiente_key):
            try:
                num = int(str(ambiente_key).replace('ambiente', ''))
                max_counter = max(max_counter, num)
            except:
                max_counter = max(max_counter, len(ambientes))
        else:
            max_counter = max(max_counter, len(ambientes))
        
        children = create_ambientes_field(ambiente_key, esquadrias, ambiente_data)
        childrens.append(children)

    return childrens, max_counter
    
##########################################################################################################

@callback(
    Output({'type': 'ambiente-esquadria-campos-calculados', 'index': MATCH}, 'children'),
    # Output({'type': 'quantidade-ambiente-esquadria', 'index': MATCH}, 'data'),
    Input({'type': 'area_ambiente', 'index': MATCH}, 'value'),
    Input({'type': 'quantidade-ambiente-esquadria', 'index': MATCH}, 'data'),
    Input('editable-table', 'data'),
    Input('zona_bioclimatica', 'value'),
    Input('regiao', 'value'),
    # Input({'type': 'quantidade-ambiente-esquadria', 'index': MATCH}, 'data'),
    Input({'type': 'ambiente-esquadria-checkbox', 'index': MATCH}, 'value'),
)
def campos_ambientes_calculados_esquadrias(area_ambiente, indicadores, esquadrias, zona_bioclimatica, regiao, esquadrias_selecionadas):

    indicadores = pd.DataFrame(indicadores)
    indicadores = indicadores.rename(columns={'esquadrias': 'Indicador'})

    if len(indicadores) > 0:

        # Motando as esquadrias em um dataframe
        esquadrias = pd.DataFrame(esquadrias)

        # Transforma coeficientes de abertura e de vidro em numéricos
        esquadrias['Coeficiente de abertura'] = pd.to_numeric(esquadrias['Coeficiente de abertura'], errors='coerce').fillna(0)
        esquadrias['Coeficiente de vidro'] = pd.to_numeric(esquadrias['Coeficiente de vidro'], errors='coerce').fillna(0)

        # Filtra apenas os indicadores presentes em indicadores_original
        esquadrias_filtradas = esquadrias.copy()

        # Adiciona a quantidade conforme contagem
        esquadrias_filtradas = esquadrias_filtradas.merge(indicadores, on='Indicador', how='left')

        # Transforma a quntidade em numérico
        esquadrias_filtradas['quantidade'] = pd.to_numeric(esquadrias_filtradas['quantidade'], errors='coerce').fillna(0)

        # Soma ponderada pela quantidade
        soma_area_janelas = (esquadrias_filtradas['Área [m²]'] * esquadrias_filtradas['quantidade']).sum()

        childrens = []

        for index, indicador_ambiente in enumerate(esquadrias_filtradas[esquadrias_filtradas['Indicador'].isin(esquadrias_selecionadas)]['Indicador'].unique()):

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

# Callback removido para evitar conflitos com MATCH pattern
# Os dados serão gerenciados através dos outros callbacks existentes

##########################################################################################################

