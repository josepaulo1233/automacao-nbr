import pandas as pd
import dash
from dash import html, dash_table, callback, Input, Output, State, dcc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from db.db_local import get_projetos
from utils.utilidades import calc_largura_folhas_de_vidro, calc_altura_folhas_de_vidro, calc_area_total_vidro
from utils.informacoes import opcoes_esquadrias, coeficientes_janela
from db.db_local import get_db_colection

##########################################################################################################

def esquadrias_form(esquadrias: dict):

    #  Ordem das esquadrias
    ordem_colunas = [
        'Indicador',
        'Largura [m]',
        'Altura [m]',
        'Área [m²]',
        'Parapeito [m]',
        'Número de molduras',
        'Espessura da moldura [m]',
        'Tipo de vidro',
        'Divisores horizontais',
        'Divisores verticais',
        'Espessura dos divisores [m]',
        'Folhas de vidro na horizontal',
        'Folhas de vidro na vertical',
        'Tipo de janela',
        'Coeficiente de abertura',
        'Coeficiente de vidro',
        'Cor do caixilho',
        'Trânsmitancia luminosa',
        'Trânsmitancia térmica [W/(m²K)]',
        'Fator solar',
        'Largura das folhas de vidro [m]',
        'Altura das folhas de vidro [m]',
        'Área total do vidro [m²]',
    ]

    # df = pd.DataFrame(esquadrias)
    df = pd.DataFrame.from_dict(esquadrias, orient='index')

    # Renomeando colunas para manter consistência
    df.rename(columns={
        'indicador': 'Indicador',
        'tipo_janela': 'Tipo de janela',
        'tipo_vidro': 'Tipo de vidro',
        'transmitancia_luminosa': 'Trânsmitancia luminosa',
        'largura_folhas_vidro': 'Largura das folhas de vidro [m]',
        'altura_folhas_vidro': 'Altura das folhas de vidro [m]',
        'area_total_vidro': 'Área total do vidro [m²]',
        'transmitancia_termica': 'Trânsmitancia térmica [W/(m²K)]',
        'fator_solar': 'Fator solar',
        'cor_caixilho': 'Cor do caixilho',
        'area': 'Área [m²]',
        'largura': 'Largura [m]',
        'altura': 'Altura [m]',
        'espessura_moldura': 'Espessura da moldura [m]',
        'espessura_divisores': 'Espessura dos divisores [m]',
        'folhas_vidro_horizontal': 'Folhas de vidro na horizontal',
        'folhas_vidro_vertical': 'Folhas de vidro na vertical',
        'coef_abertura': 'Coeficiente de abertura',
        'coef_vidro': 'Coeficiente de vidro',
        'transmitancia_luminosa': 'Trânsmitancia luminosa',
        'divisores_verticais': 'Divisores verticais',
        'divisores_horizontais': 'Divisores horizontais',
        'numero_molduras': 'Número de molduras',
        'parapeito': 'Parapeito [m]',
    }, inplace=True)

    # df['Trânsmitancia luminosa'] = None
    # df['Trânsmitancia térmica [W/(m²K)]'] = None
    # df['Fator solar'] = None
    # df['Área [m²]'] = None
    # df['Largura das folhas de vidro [m]'] = None
    # df['Altura das folhas de vidro [m]'] = None
    # df['Área total do vidro [m²]'] = None

    # Garantindo que as colunas estejam na ordem correta
    df = df[ordem_colunas]

    vidros = get_db_colection('materiais', 'vidros')
    opcoes_vidros = vidros['TIPO DE VIDRO'].unique()

    dropdown_options_esquadrias = [{"label": opcao, "value": opcao} for opcao in opcoes_esquadrias]
    dropdown_options_vidro = [{"label": opcao, "value": opcao} for opcao in opcoes_vidros]

    conteudo = html.Div([

        dmc.Text('Use "." como separador decimal', fw=700, style={'margin-bottom': '10px'}, c='green'),

        dmc.Button("Adicionar esquadria", leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'}, radius="xl", n_clicks=0,
            id='add-row-btn'),

        dmc.Button("Importar esquadria", leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'}, radius="xl", n_clicks=0, color='red', ml=2,
            id='import-row-btn'),

        html.Div(id='esquadrias-importadas'),
        html.Div(id='esquadrias-importadas-alert', style={'margin': '10px'}),
        
        dash_table.DataTable(
            id='editable-table',
            columns=[
                {"name": col, "id": col, "editable": True, "presentation": "dropdown"}
                if col == "Tipo de janela" else
                {"name": col, "id": col, "editable": True, "presentation": "dropdown"}
                if col == "Tipo de vidro" else
                {"name": col, "id": col, "editable": True}
                for col in df.columns
            ],
            data=df.to_dict('records'),
            dropdown={
                "Tipo de janela": {
                    "options": dropdown_options_esquadrias,
                },
                "Tipo de vidro": {
                    "options": dropdown_options_vidro,
                }
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
                'backgroundColor': 'transparent',
                'textAlign': 'center',
            }
        ],
        row_deletable=True,
        style_table={'overflowX': 'auto', 'height': '250px'},
        ),
    ])

    return conteudo

##########################################################################################################

@callback(
    Output('esquadrias-importadas', 'children'),
    Input('import-row-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def importa_esquadria(n_clicks):

    ctx = dash.callback_context

    if ctx.triggered_id == "import-row-btn":
        # Pegando os projetos no DB
        projetos_cadastrados = get_projetos()
        projetos_cadastrados_ids = [x.id for x in projetos_cadastrados]
        projetos_cadastrados = [{'label': str(id), 'value': str(id)} for id in projetos_cadastrados_ids]

        children = html.Div([

            dmc.Group(
                children=[
                    dmc.Select(
                        id='dropdown-esquadrias',
                        label="Selecione a esquadria do NÚMERO do projeto cadastrado:",
                        data=projetos_cadastrados,
                        placeholder="Selecione uma esquadria",
                        style={"margin-bottom": "1rem", "minWidth": "300px"},
                        searchable=True,
                    ),
                    dmc.Button(
                        'Importar esquadria',
                        id='importar-esquadria-btn',
                        color='green',
                        radius='md',
                        variant='light',
                        style={'margin-bottom': '1rem'}
                    ),
                ],
                align="end",   # Alinha verticalmente à base
            ),
        ])

        return children

##########################################################################################################

@callback(
    Output('editable-table', 'data', allow_duplicate=True),
    Output('esquadrias-importadas-alert', 'children'),
    Input('importar-esquadria-btn', 'n_clicks'),
    State('dropdown-esquadrias', 'value'),
    prevent_initial_call=True,
)
def atualiza_esquadrias(n_clicks, id_projeto):

    ctx = dash.callback_context

    if ctx.triggered_id == "importar-esquadria-btn" and id_projeto:

        # Pegando os projetos no DB
        esquadrias_projeto = get_projetos(id_projeto)
        esquadrias_projeto = esquadrias_projeto['esquadrias']
        esquadrias_projeto = pd.DataFrame.from_dict(esquadrias_projeto, orient='index').reset_index(drop=True)

        esquadrias_projeto.rename(columns={
            'indicador': 'Indicador',
            'tipo_janela': 'Tipo de janela',
            'tipo_vidro': 'Tipo de vidro',
            'transmitancia_luminosa': 'Trânsmitancia luminosa',
            'largura_folhas_vidro': 'Largura das folhas de vidro [m]',
            'altura_folhas_vidro': 'Altura das folhas de vidro [m]',
            'area_total_vidro': 'Área total do vidro [m²]',
            'transmitancia_termica': 'Trânsmitancia térmica [W/(m²K)]',
            'fator_solar': 'Fator solar',
            'cor_caixilho': 'Cor do caixilho',
            'area': 'Área [m²]',
            'largura': 'Largura [m]',
            'altura': 'Altura [m]',
            'espessura_moldura': 'Espessura da moldura [m]',
            'espessura_divisores': 'Espessura dos divisores [m]',
            'folhas_vidro_horizontal': 'Folhas de vidro na horizontal',
            'folhas_vidro_vertical': 'Folhas de vidro na vertical',
            'coef_abertura': 'Coeficiente de abertura',
            'coef_vidro': 'Coeficiente de vidro',
            'transmitancia_luminosa': 'Trânsmitancia luminosa',
            'divisores_verticais': 'Divisores verticais',
            'divisores_horizontais': 'Divisores horizontais',
            'numero_molduras': 'Número de molduras',
            'parapeito': 'Parapeito [m]',
        }, inplace=True)

        return esquadrias_projeto.to_dict('records'), dmc.Alert(
            f"Esquadrias do projeto {id_projeto} importadas com sucesso!",
            title="Sucesso!",
            color="green",
            withCloseButton=True,
            )
    
    else:

        return dash.no_update, dash.no_update

##########################################################################################################

def convert_mixed_dataframe(df):
    def convert_value(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return str(val)
    
    return df.applymap(convert_value)

@callback(
    Output("editable-table", "data", allow_duplicate=True),
    Input("editable-table", "data"),
    prevent_initial_call='initial_duplicate',
)
def caracteristicas_das_esquadrias(data):
    if not data:
        return data
    
    df = pd.DataFrame(data)
    df = convert_mixed_dataframe(df)
    
    vidros = get_db_colection('materiais', 'vidros')

    # Atualizando coeficientes baseados em 'tipo_janela', exceto quando for 'Outro'
    df.loc[(df['Tipo de janela'].isin(coeficientes_janela.keys())) & (df['Tipo de janela'] != 'Outro'), 'Coeficiente de abertura'] = df['Tipo de janela'].map(lambda x: coeficientes_janela.get(x, {}).get("Coef de abertura", None))
    df.loc[(df['Tipo de janela'].isin(coeficientes_janela.keys())) & (df['Tipo de janela'] != 'Outro'), 'Coeficiente de vidro'] = df['Tipo de janela'].map(lambda x: coeficientes_janela.get(x, {}).get("Coef. De vidro", None))
    
    # Atualizando valores baseados em 'tipo_vidro'
    df['Fator solar'] = df['Tipo de vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'FATOR SOLAR'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'FATOR SOLAR'].empty else None)
    df['Trânsmitancia luminosa'] = df['Tipo de vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS LUMINOSA'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS LUMINOSA'].empty else None)
    df['Trânsmitancia térmica [W/(m²K)]'] = df['Tipo de vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS TERMICA'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS TERMICA'].empty else None)
    df['Cor do caixilho'] = df['Tipo de vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'COR CAIXILHO'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'COR CAIXILHO'].empty else None)
    
    # Calculando area
    df['Área [m²]'] = df['Altura [m]'] * df['Largura [m]']

    # Calculando largura das folhas de vidro
    df['Largura das folhas de vidro [m]'] = df.apply(
        lambda row: calc_largura_folhas_de_vidro(
            row['Largura [m]'],
            row['Número de molduras'],
            row['Espessura da moldura [m]'],
            row['Divisores verticais'],
            row['Espessura dos divisores [m]'],
            row['Folhas de vidro na horizontal']
        ),
        axis=1
    )

    # Calculando altura das folhas de vidro
    df['Altura das folhas de vidro [m]'] = df.apply(
        lambda row: calc_altura_folhas_de_vidro(
            row['Altura [m]'],
            row['Número de molduras'],
            row['Espessura da moldura [m]'],
            row['Divisores horizontais'],
            row['Espessura dos divisores [m]'],
            row['Folhas de vidro na vertical']
        ),
        axis=1
    )

    # Calculando area total de vidro
    df['Área total do vidro [m²]'] = df.apply(
        lambda row: calc_area_total_vidro(
            row['Largura das folhas de vidro [m]'],
            row['Altura das folhas de vidro [m]'],
            row['Folhas de vidro na vertical'],
            row['Folhas de vidro na horizontal'],
        ),
        axis=1
    )

    return df.to_dict('records')

##########################################################################################################

@callback(
    Output('editable-table', 'data'),
    Input('add-row-btn', 'n_clicks'),
    State('editable-table', 'data'),
)
def adiciona_nova_esquadria(n_clicks, rows):
    if n_clicks > 0 and rows:
        last_row = rows[-1].copy()  # Copia a última linha
        # tamanho = last_row.get('Indicador').split('Indicador')[1] if 'Indicador' in last_row else 0
        # tamanho = int(tamanho) + 1 if tamanho.isdigit() else 1
        # last_row['Indicador'] = f'Indicador{tamanho}'
        rows.append(last_row)    # Insere a nova linha no final da lista
        # rows.insert(0, last_row) # Insere a nova linha no início (posição 0)
    return rows

##########################################################################################################

