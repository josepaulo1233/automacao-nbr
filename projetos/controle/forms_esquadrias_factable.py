import pandas as pd
from dash import html, callback, Input, Output, State, callback_context
import dash
import feffery_antd_components as fac
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from utils.utilidades import calc_largura_folhas_de_vidro, calc_altura_folhas_de_vidro, calc_area_total_vidro
from utils.informacoes import opcoes_esquadrias, opcoes_vidros, coeficientes_janela, vidros

##########################################################################################################

def esquadrias_form(esquadrias: dict):

    #  Ordem das esquadrias
    ordem_colunas = [
        'indicador',
        'divisores_verticais',
        'largura',
        'altura',
        'parapeito',
        'numero_molduras',
        'espessura_moldura',
        'tipo_vidro',
        'divisores_horizontais',
        'espessura_divisores',
        'folhas_vidro_horizontal',
        'folhas_vidro_vertical',
        'tipo_janela',
        'coef_abertura',
        'coef_vidro',
        'cor_caixilho'
    ]

    # df = pd.DataFrame(esquadrias)
    df = pd.DataFrame.from_dict(esquadrias, orient='index')[ordem_colunas]
    df['transmitancia_luminosa'] = None
    df['transmitancia_termica'] = None
    df['fator_solar'] = None
    df['area'] = None
    df['largura_folhas_vidro'] = None
    df['altura_folhas_vidro'] = None
    df['area_total_vidro'] = None

    dropdown_options_esquadrias = [{"label": opcao, "value": opcao} for opcao in opcoes_esquadrias]
    dropdown_options_vidro = [{"label": opcao, "value": opcao} for opcao in opcoes_vidros]
    colunas_editaveis = ['largura', 'altura', 'parapeito', 'numero_molduras','espessura_moldura', 'divisores_verticais', 'espessura_divisores', 'folhas_vidro_horizontal', 'folhas_vidro_vertical', 'coef_abertura', 'coef_vidro']
    colunas_fixas = ['indicador']

    conteudo = html.Div([
        dmc.Button(
            "Adicionar esquadria",
            leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'},
            radius="xl",
            n_clicks=0,
            id='add-row-btn'
        ),
        dmc.Button(
            "Remove esquadria",
            leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'},
            radius="xl",
            n_clicks=0,
            id='remove-row-btn'
        ),
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
                } if col in ['tipo_janela', 'tipo_vidro'] else 
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
                    } if col == 'tipo_janela' else
                    {
                        'options': dropdown_options_vidro,
                        'value': row[col],
                        'allowClear': True,
                        'placeholder': 'Selecione...'
                    } if col == 'tipo_vidro' else row[col]
                    for col in df.columns
                }
                for _, row in df.iterrows()
            ],
            bordered=True,
            rowSelectionType='checkbox',
            pagination=False,
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

def extrair_valor_janela(x):
    if isinstance(x, dict):
        val = x.get('value')
        if isinstance(val, list):
            return ', '.join(val)  # ou apenas `val` se quiser a lista
        return val if isinstance(val, str) else None
    return x


@callback(
    Output("editable-table", "data", allow_duplicate=True),
    Input("editable-table", "data"),
    prevent_initial_call='initial_duplicate',
)
def caracteristicas_das_esquadrias(data):

    # print(data)

    if not data:
        return data

    df = pd.DataFrame(data)
    dropdown_options_esquadrias = [{"label": opcao, "value": opcao} for opcao in opcoes_esquadrias]
    dropdown_options_vidro = [{"label": opcao, "value": opcao} for opcao in opcoes_vidros]

    # Extrair valores reais de tipo_janela e tipo_vidro
    print(df['tipo_janela'].values[0], type(df['tipo_janela'].values[0]), df['tipo_janela'].values[0].get('value'))
    df['tipo_janela_valor'] = df['tipo_janela'].values[0].get('value')
    df['tipo_vidro_valor'] = df['tipo_vidro'].values[0].get('value')

    # df['tipo_janela_valor'] = df['tipo_janela'].apply(lambda x: x.get('value') if isinstance(x, dict) else x)
    # df['tipo_vidro_valor'] = df['tipo_vidro'].apply(lambda x: x.get('value') if isinstance(x, dict) else x)


    # Atualizando coeficientes baseados em tipo_janela (exceto "Outro")
    df.loc[(df['tipo_janela_valor'].isin(coeficientes_janela.keys())) & 
           (df['tipo_janela_valor'] != 'Outro'), 'coef_abertura'] = df['tipo_janela_valor'].map(
        lambda x: coeficientes_janela.get(x, {}).get("Coef de abertura", None))
    
    df.loc[(df['tipo_janela_valor'].isin(coeficientes_janela.keys())) & 
           (df['tipo_janela_valor'] != 'Outro'), 'coef_vidro'] = df['tipo_janela_valor'].map(
        lambda x: coeficientes_janela.get(x, {}).get("Coef. De vidro", None))

    # Atualizando dados baseados em tipo_vidro
    df['fator_solar'] = df['tipo_vidro_valor'].map(
        lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'FATOR SOLAR'].iat[0]
        if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'FATOR SOLAR'].empty else None)
    
    df['transmitancia_luminosa'] = df['tipo_vidro_valor'].map(
        lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS LUMINOSA'].iat[0]
        if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS LUMINOSA'].empty else None)
    
    df['transmitancia_termica'] = df['tipo_vidro_valor'].map(
        lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS TERMICA'].iat[0]
        if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS TERMICA'].empty else None)
    
    df['cor_caixilho'] = df['tipo_vidro_valor'].map(
        lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'COR CAIXILHO'].iat[0]
        if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'COR CAIXILHO'].empty else None)

    # Calculando área da esquadria
    df['area'] = df['altura'] * df['largura']

    # Calculando folhas de vidro
    df['largura_folhas_vidro'] = df.apply(
        lambda row: calc_largura_folhas_de_vidro(
            row['largura'],
            row['numero_molduras'],
            row['espessura_moldura'],
            row['divisores_verticais'],
            row['espessura_divisores'],
            row['folhas_vidro_horizontal']
        ), axis=1
    ).round(2)

    df['altura_folhas_vidro'] = df.apply(
        lambda row: calc_altura_folhas_de_vidro(
            row['altura'],
            row['numero_molduras'],
            row['espessura_moldura'],
            row['divisores_horizontais'],
            row['espessura_divisores'],
            row['folhas_vidro_vertical']
        ), axis=1
    ).round(2)

    df['area_total_vidro'] = df.apply(
        lambda row: calc_area_total_vidro(
            row['largura_folhas_vidro'],
            row['altura_folhas_vidro'],
            row['folhas_vidro_vertical'],
            row['folhas_vidro_horizontal'],
        ), axis=1
    ).round(2)

    # Reconstituindo os campos dropdown com opções e valores
    df['tipo_janela'] = df['tipo_janela_valor'].apply(lambda x: {
        'value': x,
        'options': dropdown_options_esquadrias,
        'allowClear': True,
        'placeholder': 'Selecione...'
    })

    df['tipo_vidro'] = df['tipo_vidro_valor'].apply(lambda x: {
        'value': x,
        'options': dropdown_options_vidro,
        'allowClear': True,
        'placeholder': 'Selecione...'
    })

    # Remover colunas auxiliares
    df.drop(columns=['tipo_janela_valor', 'tipo_vidro_valor'], inplace=True)

    return df.to_dict('records')

##########################################################################################################

@callback(
    Output('editable-table', 'data'),
    Input('add-row-btn', 'n_clicks'),
    State('editable-table', 'data'),
    prevent_initial_call=True
)
def adiciona_nova_esquadria(n_clicks, rows):
    if n_clicks and rows:
        # Faz uma cópia profunda da última linha para preservar a estrutura
        last_row = rows[-1].copy() #.deepcopy(rows[-1])
        
        # Remove valores selecionados dos campos tipo_janela e tipo_vidro (mantém apenas as opções)
        if 'tipo_janela' in last_row:
            last_row['tipo_janela']['value'] = None
        if 'tipo_vidro' in last_row:
            last_row['tipo_vidro']['value'] = None

        rows.append(last_row)
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