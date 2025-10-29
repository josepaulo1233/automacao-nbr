import pandas as pd
from dash import html, callback, Input, Output, State
import dash
from dash_iconify import DashIconify
import feffery_antd_components as fac
import dash_mantine_components as dmc
import copy
from db.db_local import get_projetos, get_cores
from utils.utilidades import calc_largura_folhas_de_vidro, calc_altura_folhas_de_vidro, calc_area_total_vidro
from utils.informacoes import opcoes_esquadrias, coeficientes_janela
from db.db_local import get_db_colection

##########################################################################################################

def extrair_values_esquadrias(esquadrias_dict):

    import numpy as np

    """
    Extrai o 'value' de campos que contêm estrutura com 'options'
    e converte valores None para np.nan
    """
    resultado = {}
    
    for idx, dados in esquadrias_dict.items():
        novo_dados = {}
        
        for chave, valor in dados.items():
            # Se o valor é um dicionário e contém 'value' e 'options'
            if isinstance(valor, dict) and 'value' in valor and 'options' in valor:
                # Extrai apenas o value, convertendo None para np.nan
                novo_dados[chave] = valor['value'] if valor['value'] is not None else np.nan
            else:
                # Mantém o valor original
                novo_dados[chave] = valor
        
        resultado[idx] = novo_dados
    
    return resultado


def esquadrias_form(esquadrias: dict):

    # Continua aplicando extração enquanto houver campos aninhados
    while True:
        tem_aninhamento = False
        if esquadrias:
            primeira_esquadria = next(iter(esquadrias.values()))
            for valor in primeira_esquadria.values():
                if isinstance(valor, dict) and 'value' in valor and 'options' in valor:
                    tem_aninhamento = True
                    break
        
        if not tem_aninhamento:
            break
            
        esquadrias = extrair_values_esquadrias(esquadrias)
    
    # Ordem das esquadrias
    ordem_colunas = [
        'index',
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

    # Garantindo que as colunas estejam na ordem correta
    df = df[ordem_colunas]

    # Ordenando pelo index
    df = df.sort_values(by='index')

    vidros = get_db_colection('materiais', 'vidros')
    opcoes_vidros = vidros['TIPO DE VIDRO'].unique()

    CORES = get_cores()
    CORES = pd.DataFrame(CORES)
    CORES = CORES.to_dict(orient='list')
    opcoes_cores_dropdown = CORES.get('Nomes')

    dropdown_options_esquadrias = [{"label": opcao, "value": opcao} for opcao in opcoes_esquadrias]
    dropdown_options_vidro = [{"label": opcao, "value": opcao} for opcao in opcoes_vidros]
    dropdown_options_cores = [{"label": opcao, "value": opcao} for opcao in opcoes_cores_dropdown]

    colunas_editaveis = ['Largura [m]', 
                         'Altura [m]', 
                         'Parapeito [m]', 
                         'Número de molduras', 
                         'Espessura da moldura [m]', 
                         'Divisores verticais', 
                         'Divisores horizontais', 
                         'Espessura dos divisores [m]', 
                         'Folhas de vidro na horizontal', 
                         'Folhas de vidro na vertical', 
                         'Coeficiente de abertura', 
                         'Coeficiente de vidro',
                         'index']
    
    colunas_fixas = ['Indicador']

    conteudo = html.Div([

        dmc.Text('Use "." como separador decimal', fw=700, style={'margin-bottom': '10px'}, c='green'),

        dmc.Button("Adicionar esquadria", leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'}, radius="md", n_clicks=0, mr=2,
            id='add-row-btn'),

        dmc.Button("Remover esquadria", leftSection=DashIconify(icon="ic:baseline-minus"),
            style={'margin-bottom': '10px'}, radius="md", n_clicks=0, mr=2,
            id='remove-row-btn', color='red'),

        dmc.Button("Importar esquadria", leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'}, radius="md", n_clicks=0, color='green',
            id='import-row-btn'),

        html.Div(id='esquadrias-importadas'),
        
        html.Div(id='esquadrias-importadas-alert', style={'margin': '10px'}),
        
        fac.AntdTable(
            id='editable-table',
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
                } if col in ['Tipo de janela', 'Tipo de vidro', 'Cor do caixilho'] else 
                {
                    'title': col,
                    'dataIndex': col,
                    'name': col,
                    'id': col,
                    'editable': True,
                    'width': 150
                } if col in colunas_editaveis else
                {
                    'title': col,
                    'dataIndex': col,
                    'name': col,
                    'id': col,
                    'editable': True,
                    'width': 150,
                    'fixed': 'left',
                } if col in colunas_fixas else
                {
                    'title': col,
                    'dataIndex': col,
                    'name': col,
                    'id': col,
                    'editable': False,
                    'width': 150
                }
                for col in df.columns
            ],
            data=[
                {
                    col: {
                        'options': dropdown_options_esquadrias,
                        'value': row[col],
                        'allowClear': True,
                        'placeholder': 'Selecione...'
                    } if col == 'Tipo de janela' else
                    {
                        'options': dropdown_options_cores,
                        'value': row[col],
                        'allowClear': True,
                        'placeholder': 'Selecione...'
                    } if col == 'Cor do caixilho' else
                    {
                        'options': dropdown_options_vidro,
                        'value': row[col],
                        'allowClear': True,
                        'placeholder': 'Selecione...'
                    } if col == 'Tipo de vidro' else row[col]
                    for col in df.columns
                }
                for _, row in df.iterrows()
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
        )
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

@callback(
    Output("editable-table", "data", allow_duplicate=True),
    Input("editable-table", "data"),
    prevent_initial_call='initial_duplicate',
)
def caracteristicas_das_esquadrias(data):

    if not data:
        return dash.no_update
    
    # Deep copy dos dados para evitar mutação de objetos compartilhados
    data = copy.deepcopy(data)

    # Pegando os vidros cadastrados
    vidros = get_db_colection('materiais', 'vidros', return_type='dict')

    # Atualizar a área calculada para cada linha
    for row in data:
        # Extrair valores de Largura e Altura
        largura = row.get('Largura [m]')
        altura = row.get('Altura [m]')
        
        tipo_janela_obj = row.get('Tipo de janela')

        # Verificar se é um dicionário (dropdown) ou valor direto
        if isinstance(tipo_janela_obj, dict):
            tipo_de_janela = tipo_janela_obj.get('value')
        else:
            tipo_de_janela = tipo_janela_obj


        coef_abertura = coeficientes_janela.get(tipo_de_janela, {}).get('Coef de abertura')
        coef_vidro = coeficientes_janela.get(tipo_de_janela, {}).get('Coef. De vidro')

        print(f"Tipo de janela: {tipo_de_janela}, Coeficiente de abertura: {coef_abertura}, Coeficiente de vidro: {coef_vidro}")
        
        # Verificar se ambos os valores existem e são numéricos
        if largura is not None and altura is not None:
            largura_float = float(largura)
            altura_float = float(altura)
            
            # Calcular a área
            area = largura_float * altura_float
            
            # Atualizar a coluna de área
            row['Área [m²]'] = round(area, 2)

        # Atualizar coeficientes
        if tipo_de_janela is not None:
            # Se o tipo de janela for "Outro", preservar valores existentes dos coeficientes
            if tipo_de_janela == "Outro":
                # Não atualizar os coeficientes para "Outro" - deixar que o usuário os edite manualmente
                # Só inicializar se não existirem ainda
                if 'Coeficiente de abertura' not in row:
                    row['Coeficiente de abertura'] = None
                if 'Coeficiente de vidro' not in row:
                    row['Coeficiente de vidro'] = None
            else:
                # Para outros tipos de janela, atualizar normalmente
                row['Coeficiente de abertura'] = coef_abertura
                row['Coeficiente de vidro'] = coef_vidro

        # Calcular largura das folhas de vidro com a função calc_largura_folhas_de_vidro
        largura_folhas_vidro = calc_largura_folhas_de_vidro(
            largura=largura,
            numero_molduras=row.get('Número de molduras'),
            divisores_verticais=row.get('Divisores verticais'),
            espessura_molduras=row.get('Espessura da moldura [m]'),
            espessura_divisores=row.get('Espessura dos divisores [m]'),
            folhas_vidro_horizontais=row.get('Folhas de vidro na horizontal'),
        )

        # Calcular altura das folhas de vidro com a função calc_altura_folhas_de_vidro
        altura_folhas_vidro = calc_altura_folhas_de_vidro(
            altura=altura,
            numero_molduras=row.get('Número de molduras'),
            divisores_horizontais=row.get('Divisores horizontais'),
            espessura_molduras=row.get('Espessura da moldura [m]'),
            espessura_divisores=row.get('Espessura dos divisores [m]'),
            folhas_vidro_verticais=row.get('Folhas de vidro na vertical'),
        )

        # Calcula área total de vidro com a função calc_area_total_vidro
        area_total_vidro = calc_area_total_vidro(
            folhas_vidro_vertical=largura_folhas_vidro,
            folhas_vidro_horizontal=altura_folhas_vidro,
            qtade_folha_vertical=row.get('Folhas de vidro na horizontal'),
            qtade_folha_horizontal=row.get('Folhas de vidro na vertical'),
        )

        row['Largura das folhas de vidro [m]'] = round(largura_folhas_vidro, 3)
        row['Altura das folhas de vidro [m]'] = round(altura_folhas_vidro, 3)
        row['Área total do vidro [m²]'] = round(area_total_vidro, 3)

        # Adicionando características do vidro
        tipo_vidro_obj = row.get('Tipo de vidro')
        if isinstance(tipo_vidro_obj, dict):
            tipo_vidro_value = tipo_vidro_obj.get('value')
        else:
            tipo_vidro_value = tipo_vidro_obj
        
        if tipo_vidro_value and 'vidros' in vidros:
            vidros_list = vidros['vidros']
            row['Fator solar'] = next((item['FATOR SOLAR'] for item in vidros_list if item['TIPO DE VIDRO'] == tipo_vidro_value), None)
            row['Trânsmitancia luminosa'] = next((item['TRANS LUMINOSA'] for item in vidros_list if item['TIPO DE VIDRO'] == tipo_vidro_value), None)
            row['Trânsmitancia térmica [W/(m²K)]'] = next((item['TRANS TERMICA'] for item in vidros_list if item['TIPO DE VIDRO'] == tipo_vidro_value), None)

    return data

##########################################################################################################

@callback(
    Output('editable-table', 'data'),
    Input('add-row-btn', 'n_clicks'),
    State('editable-table', 'data'),
)
def adiciona_nova_esquadria(n_clicks, rows):
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
    Output("editable-table", "data", allow_duplicate=True),
    Output('editable-table', 'selectedRowKeys'),
    Input("remove-row-btn", "n_clicks"),
    Input("editable-table", "data"),
    Input('editable-table', 'selectedRows'),
    Input('editable-table', 'selectedRowKeys'),
    prevent_initial_call=True
)
def remover_linha_selecionada(n_clicks, data, selectedRows, selectedRowKeys):
    
    ctx = dash.callback_context

    if ctx.triggered_id == "remove-row-btn" and selectedRows:

        keys = selectedRowKeys
        indices_para_remover = [int(key) for key in keys]

        data_df = pd.DataFrame(data)
        data_df = data_df.drop(indices_para_remover)
        data = data_df.to_dict('records')

        return data, []

    return dash.no_update, selectedRowKeys

##########################################################################################################