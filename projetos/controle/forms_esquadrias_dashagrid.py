import pandas as pd
from dash import html, dash_table, callback, Input, Output, State
import dash_ag_grid as dag
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

    column_defs = []
    for col in df.columns:
        if col == 'tipo_janela':
            column_defs.append({
                "field": col,
                "headerName": col,
                "editable": True,
                "cellEditor": "agSelectCellEditor",
                "cellEditorParams": {
                    "values": [op["value"] for op in dropdown_options_esquadrias]
                }
            })
        elif col == 'tipo_vidro':
            column_defs.append({
                "field": col,
                "headerName": col,
                "editable": True,
                "cellEditor": "agSelectCellEditor",
                "cellEditorParams": {
                    "values": [op["value"] for op in dropdown_options_vidro]
                }
            })
        else:
            column_defs.append({
                "field": col,
                "headerName": col,
                "editable": True,
            })

    conteudo = html.Div([
        dmc.Button("Adicionar esquadria", leftSection=DashIconify(icon="ic:baseline-plus"),
            style={'margin-bottom': '10px'}, radius="xl", n_clicks=0,
            id='add-row-btn'),
        dag.AgGrid(
            id='editable-table',
            columnDefs=column_defs,
            rowData=df.to_dict("records"),
            defaultColDef={
                "resizable": True,
                "sortable": True,
                "filter": True,
                "minWidth": 120,
                "editable": True,
            },
            dashGridOptions={
                "rowSelection": "multiple",
                "animateRows": True,
                "pagination": True,
                "paginationAutoPageSize": True
            },
            style={"height": "600px", "width": "100%"},
            className="ag-theme-alpine",
        )
    ])

    return conteudo

##########################################################################################################

@callback(
    Output("editable-table", "data", allow_duplicate=True),
    Input("editable-table", "data"),
    prevent_initial_call='initial_duplicate',
)
def caracteristicas_das_esquadrias(data):
    if not data:
        return data
    
    df = pd.DataFrame(data)
    
    # Atualizando coeficientes baseados em 'tipo_janela', exceto quando for 'Outro'
    df.loc[(df['tipo_janela'].isin(coeficientes_janela.keys())) & (df['tipo_janela'] != 'Outro'), 'coef_abertura'] = df['tipo_janela'].map(lambda x: coeficientes_janela.get(x, {}).get("Coef de abertura", None))
    df.loc[(df['tipo_janela'].isin(coeficientes_janela.keys())) & (df['tipo_janela'] != 'Outro'), 'coef_vidro'] = df['tipo_janela'].map(lambda x: coeficientes_janela.get(x, {}).get("Coef. De vidro", None))
    
    # Atualizando valores baseados em 'tipo_vidro'
    df['fator_solar'] = df['tipo_vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'FATOR SOLAR'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'FATOR SOLAR'].empty else None)
    df['transmitancia_luminosa'] = df['tipo_vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS LUMINOSA'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS LUMINOSA'].empty else None)
    df['transmitancia_termica'] = df['tipo_vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS TERMICA'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'TRANS TERMICA'].empty else None)
    df['cor_caixilho'] = df['tipo_vidro'].map(lambda x: vidros.loc[vidros['TIPO DE VIDRO'] == x, 'COR CAIXILHO'].iat[0] if not vidros.loc[vidros['TIPO DE VIDRO'] == x, 'COR CAIXILHO'].empty else None)
    
    # Calculando area
    df['area'] = df['altura'] * df['largura']

    # Calculando largura das folhas de vidro
    df['largura_folhas_vidro'] = df.apply(
        lambda row: calc_largura_folhas_de_vidro(
            row['largura'],
            row['numero_molduras'],
            row['espessura_moldura'],
            row['divisores_verticais'],
            row['espessura_divisores'],
            row['folhas_vidro_horizontal']
        ),
        axis=1
    ).round(2)

    # Calculando altura das folhas de vidro
    df['altura_folhas_vidro'] = df.apply(
        lambda row: calc_altura_folhas_de_vidro(
            row['altura'],
            row['numero_molduras'],
            row['espessura_moldura'],
            row['divisores_horizontais'],
            row['espessura_divisores'],
            row['folhas_vidro_vertical']
        ),
        axis=1
    ).round(2)

    # Calculando area total de vidro
    df['area_total_vidro'] = df.apply(
        lambda row: calc_area_total_vidro(
            row['largura_folhas_vidro'],
            row['altura_folhas_vidro'],
            row['folhas_vidro_vertical'],
            row['folhas_vidro_horizontal'],
        ),
        axis=1
    ).round(2)


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
        # tamanho = last_row.get('indicador').split('indicador')[1] if 'indicador' in last_row else 0
        # tamanho = int(tamanho) + 1 if tamanho.isdigit() else 1
        # last_row['indicador'] = f'indicador{tamanho}'
        rows.append(last_row)    # Insere a nova linha no final da lista
        # rows.insert(0, last_row) # Insere a nova linha no início (posição 0)
    return rows

##########################################################################################################

