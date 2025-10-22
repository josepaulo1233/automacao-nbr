from db.db_local import get_cores
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, MATCH
from utils.utilidades import abs_mais_prox
from utils.styles import select_classnames, number_input_classnames
import feffery_antd_components as fac
import pandas as pd
import dash

####################################################################################################################################################################

def cores_form(cores: dict):

    CORES = get_cores()
    CORES = pd.DataFrame(CORES)
    # CORES = pd.read_csv('./arquivos/cores.csv')
    
    CORES = CORES.to_dict(orient='list')
    opcoes_cores_dropdown = CORES.get('Nomes')
    opcoes_cores_dropdown.append('Outro')

    # Ordemando as chaves para que fiquem na ordem correta
    ordem_chaves = ['numero_pavimentos',
    'pe_direito',
    'Fachada 1',
    'Fachada 2',
    'Fachada 3',
    'Parede interna',
    'Parede externa',
    'Piso',
    'Teto ou forro',
    'Cobertura',
    'Piso da varanda',
    'Piso externo',
    'Elemento de sombreamento',
    'Muro/fechamento']
    cores = {chave: cores[chave] for chave in ordem_chaves if chave in cores}

    # 
    cores_layouts = []

    for index, key in enumerate(cores.keys()):

        if key == 'numero_pavimentos':
            cores_layout = dmc.NumberInput(label='Numero de pavimentos', value=cores.get('numero_pavimentos'), classNames=number_input_classnames, id='numero_pavimentos')

        elif key == 'pe_direito':
            cores_layout = dmc.NumberInput(label='Pé direito', value=cores.get('pe_direito'), classNames=number_input_classnames, id='pe_direito')

        else:
            cores_layout = html.Div([

                dbc.Row([

                    dbc.Col(dmc.Select(label=f"{key}", id={'type': 'cores-nome', 'index': index}, value=cores.get(key).get('nome'), data=opcoes_cores_dropdown, classNames=select_classnames, searchable=True), width=3),
                    dbc.Col(dmc.NumberInput(label='R', classNames=number_input_classnames, id={'type': 'cores-R', 'index': index}, value=cores.get(key).get('r'), min=0, max=255), width=3),
                    dbc.Col(dmc.NumberInput(label='G', classNames=number_input_classnames, id={'type': 'cores-G', 'index': index}, value=cores.get(key).get('g'), min=0, max=255), width=3),
                    dbc.Col(dmc.NumberInput(label='B', classNames=number_input_classnames, id={'type': 'cores-B', 'index': index}, value=cores.get(key).get('b'), min=0, max=255), width=3),
                    
                ]),

                dbc.Row([

                    dbc.Col(dmc.TextInput(label='Cor mais próxima', classNames=number_input_classnames, id={'type': 'cores-mais-proxima', 'index': index}, disabled=True, value=cores.get(key).get('cor_prox')), width=6),
                    dbc.Col(dmc.NumberInput(label='Absortancia mais próxima', classNames=number_input_classnames, id={'type': 'absortancia-mais-proxima', 'index': index}, disabled=True, value=cores.get(key).get('abs_prox')), width=6),
                    
                ]),

                fac.AntdDivider()

            ])

        cores_layouts.append(cores_layout)

        if index == 1:
            cores_layouts.append(fac.AntdDivider())

    return cores_layouts

####################################################################################################################################################################

@callback(
    Output({'type': 'cores-R', 'index': MATCH}, 'value'),
    Output({'type': 'cores-G', 'index': MATCH}, 'value'),
    Output({'type': 'cores-B', 'index': MATCH}, 'value'),
    Output({'type': 'cores-R', 'index': MATCH}, 'disabled'),
    Output({'type': 'cores-G', 'index': MATCH}, 'disabled'),
    Output({'type': 'cores-B', 'index': MATCH}, 'disabled'),
    Output({'type': 'cores-mais-proxima', 'index': MATCH}, 'value'),
    Output({'type': 'absortancia-mais-proxima', 'index': MATCH}, 'value'),
    Input({'type': 'cores-nome', 'index': MATCH}, 'value')
)
def cor_prox(cor):

    CORES = get_cores()
    CORES = pd.DataFrame(CORES)

    if cor != 'Outro':

        cols_abs = [x for x in CORES.columns if 'Nomes' not in x if 'Rs' not in x if 'Gs' not in x if 'Bs' not in x]
        absortancias = CORES[CORES['Nomes'] == cor][cols_abs]

        r_prox = CORES[CORES['Nomes'] == cor]['Rs'].values[0]
        g_prox = CORES[CORES['Nomes'] == cor]['Gs'].values[0]
        b_prox = CORES[CORES['Nomes'] == cor]['Bs'].values[0]

        return r_prox, g_prox, b_prox, True, True, True, cor, absortancias.mean(axis=1).item()
    
    else:

        return 0, 1, 1, False, False, False, '', 1
    
##########################################################################################################

@callback(
    Output({'type': 'cores-mais-proxima', 'index': MATCH}, 'value', allow_duplicate=True),
    Output({'type': 'absortancia-mais-proxima', 'index': MATCH}, 'value', allow_duplicate=True),
    Input({'type': 'cores-nome', 'index': MATCH}, 'value'),
    Input({'type': 'cores-R', 'index': MATCH}, 'value'),
    Input({'type': 'cores-G', 'index': MATCH}, 'value'),
    Input({'type': 'cores-B', 'index': MATCH}, 'value'),
    prevent_initial_call='initial_duplicate'
)
def cor_abs_prox(nome, r, g, b):

    if nome == 'Outro':

        CORES = get_cores()
        cor, abst = abs_mais_prox(r, g, b, **CORES)
        return cor, abst
    
    return dash.no_update

##########################################################################################################