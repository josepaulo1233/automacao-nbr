import pandas as pd
import dash_mantine_components as dmc
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import feffery_antd_components as fac
import dash
from dash_iconify import DashIconify
from dash import html, callback, Input, Output, MATCH, State
from funcoes.funcoes_analises import *
from funcoes.funcoes_app_analise import *
from funcoes.funcoes_graficos import *
from funcoes.funcoes_app_txt import limpar_celula, check_mandatory_sections
import base64
import io

####################################################################################################################################################################

def forms_analise():

    conteudo_analise = html.Div([

        html.H5('Tipologia', className='fw-bold'),
        dmc.RadioGroup(
            label="Selecione a tipologia:",
            id='tipologia',
            children=[ dmc.Radio("unifamiliar", value="unifamiliar", my=10), dmc.Radio("multifamiliar", value="multifamiliar", my=10)],
            value="unifamiliar",
            my=10,
        ),

        fac.AntdDivider(),

        html.H5('Arquivos de entrada', className='fw-bold'),
        fac.AntdUpload(
            id='arquivo-vn-para-as-areas',
            apiUrl='/upload/',
            uploadId='areas-vn',
            locale='en-us',
            fileMaxSize=500,
            fileTypes=['txt'],
            buttonContent='Arquivo de ventilação natural (.txt)',
        ),
        html.Div(id='filename-data-area', className='mt-2'),
        html.Div(id='output-data-area', className='mt-2'),

        fac.AntdDivider(),

        html.Div(id='tipologia-e-pavimentacao', className='mt-2'),

        html.H6('Arquivos CSV de termperatura e carga térmica', className='fw-bold'),

        dbc.Row([

            # Arquivo VN
            dbc.Col(
                children=[
                    html.H5('CSV REAL', className='fw-bold'),
                    fac.AntdUpload(
                        id='upload-csv_temp-real',
                        apiUrl='/upload/',
                        uploadId='csv-temp',
                        locale='en-us',
                        fileMaxSize=500,
                        fileTypes=['csv'],
                        buttonContent="Carregue o resultado da simulação de ventilação natural (VN) do EDIFÍCIO REAL no formato csv",
                    ),
                    html.Div(id='filename_csv_temp_real', className='mt-2'),
                    html.Div(id='resultados_csv_temp_real', className='mt-2'),
                ],
                width=6,
                style={"textAlign": "center", "marginTop": "10px"}
            ),

            # Arquivo HVAC
            dbc.Col(
                children=[
                    html.H5('CSV REFERÊNCIA', className='fw-bold'),
                    fac.AntdUpload(
                        id='upload-csv_temp-referencia',
                        apiUrl='/upload/',
                        uploadId='csv-temp',
                        locale='en-us',
                        fileMaxSize=500,
                        fileTypes=['csv'],
                        buttonContent="Carregue o resultado da simulação de ventilação natural (VN) do EDIFÍCIO REFERÊNCIA no formato csv",
                    ),
                    html.Div(id='filename_csv_temp_referencia', className='mt-2'),
                    html.Div(id='resultados_csv_temp_referencia', className='mt-2'),
                ],
                width=6,
                style={"textAlign": "center", "marginTop": "10px"}
            ),

        ], align="justify"),

        html.Div(id='warnings-nivel-minimo', className='mt-2'),
        html.Div(id='resultados-nivel-minimo', className='mt-2'),

        fac.AntdDivider(),

        html.Div(id='warnings-nivel-intermediario-superior', className='mt-2'),
        html.Div(id='resultados-nivel-intermediario-superior', className='mt-2'),

    ])

    return conteudo_analise

####################################################################################################################################################################

@callback(
Output('output-data-area', 'children'),
Input('arquivo-vn-para-as-areas', 'lastUploadTaskRecord'),
Input('tipologia', 'value'),
prevent_initial_call=True,
)
def encontra_areas_arquivo_VN(lastUploadTaskRecord, tipologia):

    if tipologia:

        try:
            file = pd.read_table(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='utf-8', header=None)

        except:
            file = pd.read_table(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='ISO-8859-1', header=None)

        # Retirando o \r\n do arquivo
        file = file.applymap(limpar_celula)

        CLASS_DELIMITER_IN_TXT = '!-   ===========' 
        sections_names = nome_secoes(file, CLASS_DELIMITER_IN_TXT)
        sections = separada_por_secao(file, CLASS_DELIMITER_IN_TXT) 

        sectios_to_check = ['zone']
        
        sections_less = check_mandatory_sections(sectios_to_check, sections_names)

        if len(sections_less) == 0:
        
            zone = find_section_index_by_name('zone', sections, sections_names)
            areas = get_zone_area_value(zone, tipologia)
            areas = areas.reset_index()

            if tipologia == 'unifamiliar':

                conteudo = html.Details([
                    html.Summary(html.B("Áreas")),
                    fac.AntdTable(
                        id='tabela_areas',
                        columns=[
                            {'title': col, 'dataIndex': col}
                            for col in areas.columns
                        ],
                        data=areas.to_dict('records'),
                        bordered=True,
                        locale="en-us",
                    ),
                    
                    # Tamanho do dataframe de areas
                    dbc.Alert(f"Total de areas {len(areas)} unidades encontradas", color="info", className='m-3'),
                    dcc.Store(id='tabela_areas_pavimentacao', data={}),
                ])

            else:

                tipo_pav = pd.DataFrame()
                tipo_pav.index = areas['Unidades']
                tipo_pav['TIPOLOGIA'] = np.nan
                tipo_pav['PAVIMENTO'] = np.nan
                tipo_pav.reset_index(inplace=True)
                
                conteudo = dbc.Row([

                    dbc.Col([

                        html.Details([
                            html.Summary(html.B("Áreas")),
                            fac.AntdTable(
                                id='tabela_areas',
                                columns=[
                                    {'title': col, 'dataIndex': col}
                                    for col in areas.columns
                                ],
                                data=areas.to_dict('records'),
                                bordered=True,
                                locale="en-us",
                            ),
                            
                            # Tamanho do dataframe de areas
                            dbc.Alert(f"Total: {len(areas)} unidades encontradas", color="info", className='m-3'),
                        ])

                    ], width=6),

                    dbc.Col([

                        html.Details([
                            html.Summary(html.B("Tipologia e pavimentação")),
                            fac.AntdTable(
                                id='tabela_areas_pavimentacao',
                                columns = [
                                    {
                                        'title': col,
                                        'dataIndex': col,
                                        'editable': False if col == 'Unidades' else True
                                    }
                                    for col in tipo_pav.columns
                                ],
                                data=tipo_pav.to_dict('records'),
                                bordered=True,
                                locale="en-us",
                            ),
                        ])

                    ], width=6),

            ])
                
            return conteudo

    else:
    
        return dash.no_update, dash.no_update

####################################################################################################################################################################

def create_table(df1, df2, tipo: str):

    conteudo = html.Div([

        # Tabela por unidade
        dbc.Row([
            dmc.Button(
                f"Mostrar/esconder resultados {tipo.upper()} por unidade",
                id=f"collapse-btn-csv_{tipo}_temperatura_unidade",
                n_clicks=0,
                radius="xl",
                variant="light"
            ),
            dmc.Collapse(
                id=f"collapse-csv_{tipo}_temperatura_unidade",
                opened=False,
                children=[
                    fac.AntdTable(
                        id=f'csv_{tipo}_temperatura_unidade',
                        columns=[{'title': col, 'dataIndex': col} for col in df1.reset_index().columns],
                        data=df1.reset_index().to_dict('records'),
                        bordered=True,
                        locale="en-us"
                    ),
                    # dbc.Button(
                    #     "Baixar resultados mínimos",
                    #     id={'type': "btn-download-resultados", 'index': f'{tipo}_temperatura_unidade'},
                    #     color="primary"
                    # ),
                    # dcc.Download(id={'type': "download-resultados", 'index': f'{tipo}_temperatura_unidade'})
                ],
                className='m-3'
            ),
        ], className='m-3'),

        # Tabela por ambiente
        dbc.Row([
            dmc.Button(
                f"Mostrar/esconder resultados {tipo.upper()} por ambiente",
                id=f"collapse-btn-csv_{tipo}_temperatura_ambiente",
                n_clicks=0,
                radius="xl",
                variant="light"
            ),
            dmc.Collapse(
                id=f"collapse-csv_{tipo}_temperatura_ambiente",
                opened=False,
                children=[
                    fac.AntdTable(
                        id=f'csv_{tipo}_temperatura_ambiente',
                        columns=[{'title': col, 'dataIndex': col} for col in df2.reset_index().columns],
                        data=df2.reset_index().to_dict('records'),
                        bordered=True,
                        locale="en-us"
                    ),

                    dbc.Button(
                        "Baixar resultados",
                        id=f'btn_baixa_csv_{tipo}_temperatura_ambiente',
                        color="primary"
                    ),

                    dcc.Download(id=f'donwload_baixa_csv_{tipo}_temperatura_ambiente')
                    
                ],
                className='m-3'
            ),
        ], className='m-3'),

        # Upload HVAC
        dbc.Row([
            fac.AntdUpload(
                id=f'upload-csv_hvac-{tipo}',
                apiUrl='/upload/',
                uploadId='csv-hvac',
                locale='en-us',
                fileMaxSize=500,
                fileTypes=['csv'],
                buttonContent=f'Carregue o resultado da simulação de condicionamento de ar (HVAC) do EDIFÍCIO {tipo.upper()} no formato csv',
            ),
            # dcc.Upload(
            #     id=f'upload-csv_hvac-{tipo}',
            #     children=dmc.Button(
            #         f"Carregue o resultado da simulação de condicionamento de ar (HVAC) do EDIFÍCIO {tipo.upper()} no formato csv",
            #         leftSection=DashIconify(icon="ic:baseline-plus"),
            #         style={'margin-bottom': '10px'},
            #         radius="xl",
            #         n_clicks=0
            #     ),
            # ),
            html.Div(id=f'filename_csv_hvac_{tipo}', className='mt-2'),
            html.Div(id=f'resultados_csv_hvac_{tipo}', className='mt-2'),
        ])

    ])

    return conteudo

####################################################################################################################################################################

def create_table_hvac(df1, df2, tipo: str):

    conteudo = html.Div([

        dbc.Row([

            dmc.Button(f"Mostrar/esconder resultados {tipo.upper()} por unidade", id=f"collapse-btn-csv_{tipo}_hvac_unidade", n_clicks=0, radius="xl", variant="light"),
            dmc.Collapse(
                
                id=f"collapse-csv_{tipo}_hvac_unidade",
                opened=False,
                children=fac.AntdTable(
                    id=f'csv_{tipo}_hvac_unidade',
                    columns=[
                        {'title': col, 'dataIndex': col}
                        for col in df1.reset_index().columns
                    ],
                    data=df1.reset_index().to_dict('records'),
                    bordered=True,
                    locale="en-us",

                ),
            className='m-3'),

        ], className='m-3'),

        dbc.Row([

            dmc.Button(f"Mostrar/esconder resultados {tipo.upper()} por ambiente", id=f"collapse-btn-csv_{tipo}_hvac_ambiente", n_clicks=0, radius="xl", variant="light"),
            dmc.Collapse(
                
                id=f"collapse-csv_{tipo}_hvac_ambiente",
                opened=False,
                children=fac.AntdTable(
                    id=f'csv_{tipo}_hvac_ambiente',
                    columns=[
                        {'title': col, 'dataIndex': col}
                        for col in df2.reset_index().columns
                    ],
                    data=df2.reset_index().to_dict('records'),
                    bordered=True,
                    locale="en-us",

                ),
            className='m-3'),

        ], className='m-3'),

    ])

    return conteudo

####################################################################################################################################################################

@callback(
    Output("donwload_baixa_csv_real_temperatura_ambiente", "data"),
    Input(f'btn_baixa_csv_real_temperatura_ambiente', "n_clicks"),
    Input(f'csv_real_temperatura_ambiente', 'data'),
    prevent_initial_call=True,
)
def baixar_dados(n_clicks, data):
    if data is None:
        return None

    # Converte o JSON armazenado no dcc.Store em um DataFrame
    df = pd.DataFrame(data)

    # Retorna o CSV para download
    return dcc.send_data_frame(df.to_csv, filename="dados_real_ambiente.csv", index=False)

####################################################################################################################################################################

@callback(
    Output("donwload_baixa_csv_referencia_temperatura_ambiente", "data"),
    Input(f'btn_baixa_csv_referencia_temperatura_ambiente', "n_clicks"),
    Input(f'csv_referencia_temperatura_ambiente', 'data'),
    prevent_initial_call=True,
)
def baixar_dados(n_clicks, data):
    if data is None:
        return None

    # Converte o JSON armazenado no dcc.Store em um DataFrame
    df = pd.DataFrame(data)

    # Retorna o CSV para download
    return dcc.send_data_frame(df.to_csv, filename="dados_referencia_ambiente.csv", index=False)

####################################################################################################################################################################

@callback(
    Output('resultados_csv_temp_real', 'children'),
    Input('upload-csv_temp-real', 'lastUploadTaskRecord'),
    Input('tipologia', 'value'),
    )
def resultados_csv_real(lastUploadTaskRecord, TIPOLOGIA):

    if lastUploadTaskRecord is not None:

        try:
            file = pd.read_csv(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='utf-8')

        except:
            file = pd.read_csv(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='ISO-8859-1')

        df1, df2 = gera_df_final(file, TIPOLOGIA)

        df1 = df1.round(2)
        df2 = df2.round(2)

        conteudo = create_table(df1, df2, 'real')

        return conteudo

    return dash.no_update

####################################################################################################################################################################

@callback(
    Output('resultados_csv_temp_referencia', 'children'),
    Input('upload-csv_temp-referencia', 'lastUploadTaskRecord'),
    Input('tipologia', 'value'),
)
def resultados_csv_referencia(lastUploadTaskRecord, TIPOLOGIA):

    if lastUploadTaskRecord is not None:

        try:
            file = pd.read_csv(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='utf-8')

        except:
            file = pd.read_csv(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='ISO-8859-1')

        df1, df2 = gera_df_final(file, TIPOLOGIA)

        df1 = df1.round(2)
        df2 = df2.round(2)

        conteudo = create_table(df1, df2, 'referencia')

        return conteudo

    return dash.no_update

####################################################################################################################################################################

@callback(
    Output('resultados_csv_hvac_real', 'children'),
    Input('upload-csv_temp-real', 'lastUploadTaskRecord'),
    Input('upload-csv_hvac-real', 'lastUploadTaskRecord'),
    Input('tipologia', 'value'),
)
def resultados_csv_hvac_real(data_temp, data_hvac, TIPOLOGIA):

    if data_temp is not None and data_hvac is not None:

        try:
            file_temp = pd.read_csv(f"upload/{data_temp.get('taskId')}/{data_temp.get('fileName')}", encoding='utf-8')
            file_hvac = pd.read_csv(f"upload/{data_hvac.get('taskId')}/{data_hvac.get('fileName')}", encoding='utf-8')

        except:
            file_temp = pd.read_csv(f"upload/{data_temp.get('taskId')}/{data_temp.get('fileName')}", encoding='ISO-8859-1')
            file_hvac = pd.read_csv(f"upload/{data_hvac.get('taskId')}/{data_hvac.get('fileName')}", encoding='ISO-8859-1')

        df1, df2 = gera_df_temperatura_e_cargatermica(file_temp, file_hvac, TIPOLOGIA)

        df1 = df1.round(2)
        df2 = df2.round(2)

        conteudo = create_table_hvac(df1, df2, 'real')

        return conteudo

    return dash.no_update

####################################################################################################################################################################

@callback(
    Output('resultados_csv_hvac_referencia', 'children'),
    Input('upload-csv_temp-referencia', 'lastUploadTaskRecord'),
    Input('upload-csv_hvac-referencia', 'lastUploadTaskRecord'),
    Input('tipologia', 'value'),
)
def resultados_csv_hvac_referencia(data_temp, data_hvac, TIPOLOGIA):

    if data_temp is not None and data_hvac is not None:

        try:
            file_temp = pd.read_csv(f"upload/{data_temp.get('taskId')}/{data_temp.get('fileName')}", encoding='utf-8')
            file_hvac = pd.read_csv(f"upload/{data_hvac.get('taskId')}/{data_hvac.get('fileName')}", encoding='utf-8')

        except:
            file_temp = pd.read_csv(f"upload/{data_temp.get('taskId')}/{data_temp.get('fileName')}", encoding='ISO-8859-1')
            file_hvac = pd.read_csv(f"upload/{data_hvac.get('taskId')}/{data_hvac.get('fileName')}", encoding='ISO-8859-1')

        df1, df2 = gera_df_temperatura_e_cargatermica(file_temp, file_hvac, TIPOLOGIA)

        df1 = df1.round(2)
        df2 = df2.round(2)

        conteudo = create_table_hvac(df1, df2, 'referencia')

        return conteudo

    return dash.no_update

####################################################################################################################################################################

@callback(
    Output('resultados-nivel-minimo', 'children'),
    Output('warnings-nivel-minimo', 'children'),
    Input('tipologia', 'value'),
    Input('csv_real_temperatura_unidade', 'data'),
    Input('csv_referencia_temperatura_unidade', 'data'), 
    Input('zona_bioclimatica', 'value'),
    Input('tabela_areas', 'data'),
    Input('tabela_areas_pavimentacao', 'data'),
    Input('upload-csv_temp-real', 'lastUploadTaskRecord'),
)
def resultados_nv_minimo(TIPOLOGIA, edificio_real, edificio_referencia, zona, areas, tipologia, lastUploadTaskRecord):

    warnings_resultados = []
    
    ### RESULTADOS NÍVEL MÍNIMO ####
    
    if edificio_real is not None and edificio_referencia is not None and tipologia is not None and areas is not None:

        # Transformando em dataframes
        edificio_real = pd.DataFrame(edificio_real)
        edificio_referencia = pd.DataFrame(edificio_referencia)
        tipologia = pd.DataFrame(tipologia)
        areas = pd.DataFrame(areas)

        if TIPOLOGIA != 'unifamiliar':

            if tipologia is None:
                warnings_resultados.append('Não há arquivo de tipologia e pavimentação!')

            elif len(tipologia) != len(edificio_real):
                warnings_resultados.append('❌ A quantidade de unidades no arquivo de tipologia e pavimentação é diferente do edifício REAL... Verifique!')
                if len(tipologia) > len(edificio_real):
                    faltando = set(tipologia.index.values) - set(edificio_real.index.values)
                    warnings_resultados.append('⚠️ Unidades faltando no edifício REAL: ' + ', '.join(list(faltando)))
                else:
                    faltando = set(edificio_real.index.values) - set(tipologia.index.values)
                    warnings_resultados.append('⚠️ Unidades faltando no arquivo de tipologia e pavimentação: ' + ', '.join(list(faltando)))

            elif len(tipologia) != len(edificio_referencia):
                warnings_resultados.append('❌ A quantidade de unidades no arquivo de tipologia e pavimentação é diferente do edifício REFERÊNCIA... Verifique!')
                if len(tipologia) > len(edificio_referencia):
                    faltando = set(tipologia.index.values) - set(edificio_referencia.index.values)
                    warnings_resultados.append('⚠️ Unidades faltando no edifício REFERÊNCIA: ' + ', '.join(list(faltando)))
                else:
                    faltando = set(edificio_referencia.index.values) - set(tipologia.index.values)
                    warnings_resultados.append('⚠️ Unidades faltando no arquivo de tipologia e pavimentação: ' + ', '.join(list(faltando)))

        if areas is None:
            warnings_resultados.append('❌ Há um problema com o arquivo de áreas... Verifique!')

        elif edificio_referencia is None:
            warnings_resultados.append('❌ Há um problema com o arquivo de temperatura para o edifício REFERÊNCIA... Verifique!')

        elif edificio_real is None:
            warnings_resultados.append('❌ Há um problema com o arquivo de temperatura para o edifício REAL... Verifique!')

        elif len(edificio_referencia) != len(edificio_real):
            warnings_resultados.append('❌ A quantidade de unidades das simulações de referência e real são diferentes... Verifique!')
            if len(edificio_referencia) > len(edificio_real):
                faltando = set(edificio_referencia['Unidades'].values) - set(edificio_real['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no edifício REAL: ' + ', '.join(list(faltando)))
            else:
                faltando = set(edificio_real['Unidades'].values) - set(edificio_referencia['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no edifício REFERÊNCIA: ' + ', '.join(list(faltando)))

        elif len(edificio_real) != len(areas):
            warnings_resultados.append('❌ A quantidade de unidades da simulação REAL e de ÁREAS são diferentes... Verifique!')
            if len(edificio_real) > len(areas):
                faltando = set(edificio_real['Unidades'].values) - set(areas['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no ARQUIVO DE ÁREAS: ' + ', '.join(list(faltando)))
            else:
                faltando = set(areas['Unidades'].values) - set(edificio_real['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no EDIFÍCIO REAL: ' + ', '.join(list(faltando)))

        elif len(edificio_referencia) != len(areas):
            warnings_resultados.append('❌ A quantidade de unidades da simulação REFERÊNCIA e de ÁREAS são diferentes... Verifique!')
            if len(edificio_referencia) > len(areas):
                faltando = set(edificio_referencia['Unidades'].values) - set(areas['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no ARQUIVO DE ÁREAS: ' + ', '.join(list(faltando)))
            else:
                faltando = set(areas['Unidades'].values) - set(edificio_referencia['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no EDIFÍCIO REFERÊNCIA: ' + ', '.join(list(faltando)))

        if len(warnings_resultados) > 0:
            warnings_component = html.Ul(
                children=[html.Li(msg) for msg in warnings_resultados],
                style={'color': 'red'}  # Você pode customizar o estilo aqui
            )

        else:
            warnings_component = html.Ul(
                children=[html.Li('Todos os arquivos foram carregados corretamente!')],
                style={'color': 'green'}  # Você pode customizar o estilo aqui
            )

        # Transformando em dataframes
        edificio_real = pd.DataFrame(edificio_real)
        edificio_referencia = pd.DataFrame(edificio_referencia)
        tipologia = pd.DataFrame(tipologia)

        res_nv_minimo = pd.DataFrame()
        res_nv_minimo.index = edificio_real.index
        res_nv_minimo['Unidades'] = edificio_real['Unidades'].values
        
        if TIPOLOGIA == 'unifamiliar':
            res_nv_minimo['TIPOLOGIA'] = 'UNIFAMILIAR'
            res_nv_minimo['PAVIMENTO'] = 'TERREO'

        else:
            res_nv_minimo['TIPOLOGIA'] = tipologia['TIPOLOGIA'].values
            res_nv_minimo['PAVIMENTO'] = tipologia['PAVIMENTO'].values

        res_nv_minimo['ZONA'] = zona
        res_nv_minimo['PHFT REAL'] = edificio_real['PHFT']
        res_nv_minimo['TOMAX REAL'] = edificio_real['TOMAX']
        res_nv_minimo['TOMIN REAL'] = edificio_real['TOMIN']
        res_nv_minimo['PHFT REFERENCIA'] = edificio_referencia['PHFT']
        res_nv_minimo['TOMAX REFERENCIA'] = edificio_referencia['TOMAX']
        res_nv_minimo['TOMIN REFERENCIA'] = edificio_referencia['TOMIN']
        res_nv_minimo['0.9PHFT REFERENCIA'] = edificio_referencia['PHFT']*0.9
        res_nv_minimo['PHFTreal-90PHFTref'] = edificio_real['PHFT'] - edificio_referencia['PHFT']*0.9

        deltatmax(res_nv_minimo, res_nv_minimo['TIPOLOGIA'], res_nv_minimo['PAVIMENTO'])

        deltatmin(res_nv_minimo, res_nv_minimo['ZONA'])

        criterio_tomax(res_nv_minimo, 
                    res_nv_minimo['TOMAX REAL'], 
                    res_nv_minimo['TOMAX REFERENCIA'],
                    res_nv_minimo['ΔTOMAX'])
        
        criterio_tomin(res_nv_minimo, 
                    res_nv_minimo['TOMIN REAL'], 
                    res_nv_minimo['TOMIN REFERENCIA'],
                    res_nv_minimo['ΔTOMIN'])
        
        criterio_phft(res_nv_minimo, res_nv_minimo['PHFTreal-90PHFTref'])

        atendimento_minimo(res_nv_minimo,
                        res_nv_minimo['CRITERIO TOMAX'],
                        res_nv_minimo['CRITERIO TOMIN'],
                        res_nv_minimo['CRITERIO PHFT'],
                        res_nv_minimo['ZONA'])
        
        # Resultados parciais
        res_nv_minimo_parical = res_nv_minimo[['Unidades',
                                                'PHFT REAL',
                                                'TOMAX REAL',
                                                'TOMIN REAL',
                                                'PHFT REFERENCIA',
                                                'TOMAX REFERENCIA',
                                                'TOMIN REFERENCIA',
                                                '0.9PHFT REFERENCIA',
                                                'ΔTOMIN',
                                                'ΔTOMAX',
                                                'ATENDIMENTO MINIMO'
                                                ]]

        # Tabela dos resultados parciais
        res_nv_minimo_parciais = html.Div([
            
                fac.AntdTable(
                id={'type': "resultados", 'index': 'parcial-minimo'},
                columns=[
                    {'title': col, 'dataIndex': col}
                    for col in res_nv_minimo_parical.columns
                ],
                data=res_nv_minimo_parical.round(2).to_dict('records'),
                bordered=True,
                locale="en-us",
            ),

            dmc.Button(
                "Baixar resultados mínimos parciais",
                leftSection=DashIconify(icon="material-symbols:arrow-circle-down-outline"),
                id={'type': "btn-download-resultados", 'index': 'parcial-minimo'},
                color='blue', radius='sm'
            ),

            # dbc.Button("Baixar resultados mínimos parciais", id={'type': "btn-download-resultados", 'index': 'parcial-minimo'}, color="primary"),
            dcc.Download(id={'type': "download-resultados", 'index': 'parcial-minimo'})
        
        ])

        # Tabela dos resultados completos
        res_nv_minimo_completo = html.Div([
            
                fac.AntdTable(
                id={'type': "resultados", 'index': 'completo-minimo'},   
                columns=[
                    {'title': col, 'dataIndex': col}
                    for col in res_nv_minimo.columns
                ],
                data=res_nv_minimo.round(2).to_dict('records'),
                bordered=True,
                locale="en-us",
            ),

            dmc.Button(
                "Baixar resultados mínimos completos",
                leftSection=DashIconify(icon="material-symbols:arrow-circle-down-outline"),
                id={'type': "btn-download-resultados", 'index': 'completo-minimo'},
                color='blue', radius='sm'
            ),

            # dbc.Button("Baixar resultados mínimos completos", id={'type': "btn-download-resultados", 'index': 'completo-minimo'}, color="primary"),
            dcc.Download(id={'type': "download-resultados", 'index': 'completo-minimo'})
        
        ])

        # Alguns resultados que vou usar nos gráficos
        res_nv_minimo['90%PHFT REFERENCIA'] = res_nv_minimo['0.9PHFT REFERENCIA'].values
        res_nv_minimo['TOMAX REF + ΔTOMAX'] = res_nv_minimo['TOMAX REFERENCIA'] + res_nv_minimo['ΔTOMAX']
        res_nv_minimo['TOMIN REF - ΔTOMIN'] = res_nv_minimo['TOMIN REFERENCIA'] - res_nv_minimo['ΔTOMIN']

        # Gerando o gráfico de resultado míninmo
        fig_pht = plot_resultado_minimo(res_nv_minimo, coluna='90%PHFT REFERENCIA')
        fig_tmax = plot_resultado_minimo(res_nv_minimo, coluna='TOMAX REF + ΔTOMAX')
        fig_tmin = plot_resultado_minimo(res_nv_minimo, coluna='TOMIN REF - ΔTOMIN')
        fig_pht = dcc.Graph(figure=fig_pht, config={"displaylogo": False})
        fig_tmax = dcc.Graph(figure=fig_tmax, config={"displaylogo": False})
        fig_tmin = dcc.Graph(figure=fig_tmin, config={"displaylogo": False})

        # Salvando os gráficos 
        filename = lastUploadTaskRecord.get('fileName').split('.csv')[0]
        plot_resultado_minimo_matplotlib(res_nv_minimo, coluna='90%PHFT REFERENCIA', filename=filename+'_PHFT')
        plot_resultado_minimo_matplotlib(res_nv_minimo, coluna='TOMAX REF + ΔTOMAX', filename=filename+'_TOMAX')
        plot_resultado_minimo_matplotlib(res_nv_minimo, coluna='TOMIN REF - ΔTOMIN', filename=filename+'_TOMIN')

        # Atribuindo os resultados parciais e completos a tabs
        tabs_content = {
            'Resultados parciais': res_nv_minimo_parciais,
            'Resultados completos': res_nv_minimo_completo,
            'Resultado PHFT':fig_pht,
            'Resultado TOMAX':fig_tmax,
            'Resultado TOMIN':fig_tmin,
        }

        tabs = ['Resultados parciais', 'Resultados completos', 'Resultado PHFT', 'Resultado TOMAX', 'Resultado TOMIN']

        conteudo = html.Div([

                html.H5('Resultados do nível mínimo de conforto térmico', className='fw-bold mb-2'),

                fac.AntdTabs(
                    centered=False,
                    items=[
                        {
                            'key': f'tab{tab}',
                            'label': f'{tab}',
                            'children': tabs_content[tab]
                        }

                        for tab in tabs if tab in tabs_content
                    ]
                ),

        ])

        return conteudo, warnings_component
        
    return dash.no_update, dash.no_update

####################################################################################################################################################################

@callback(
    Output('resultados-nivel-intermediario-superior', 'children'),
    Output('warnings-nivel-intermediario-superior', 'children'),
    Input('tipologia', 'value'),
    Input('csv_real_temperatura_unidade', 'data'),
    Input('csv_referencia_temperatura_unidade', 'data'), 
    Input('csv_real_hvac_unidade', 'data'),
    Input('csv_referencia_hvac_unidade', 'data'), # collapse-csv_{tipo}_hvac_unidade
    Input('zona_bioclimatica', 'value'),
    Input('tabela_areas', 'data'),
    Input('tabela_areas_pavimentacao', 'data'),
    Input('upload-csv_hvac-real', 'lastUploadTaskRecord'),
)
def resultados_nv_superior_intermediario(TIPOLOGIA, edificio_real, edificio_referencia, csv_file_real_temperatura, csv_file_referencia_temperatura, zona, areas, tipologia, lastUploadTaskRecord):

    warnings_resultados = []
    
    ### RESULTADOS NÍVEL INTERMEDIÁRIO SUPERIOR ####

    if edificio_real is not None and edificio_referencia is not None and zona is not None and areas is not None and csv_file_real_temperatura is not None and csv_file_referencia_temperatura is not None and TIPOLOGIA is not None:
        
        # Transformando em dataframes
        edificio_real = pd.DataFrame(edificio_real)
        edificio_referencia = pd.DataFrame(edificio_referencia)
        csv_file_real_temperatura = pd.DataFrame(csv_file_real_temperatura)
        csv_file_referencia_temperatura = pd.DataFrame(csv_file_referencia_temperatura)
        tipologia = pd.DataFrame(tipologia)
        areas = pd.DataFrame(areas)

        if len(csv_file_real_temperatura) != len(csv_file_real_temperatura):
            if len(csv_file_real_temperatura) > len(csv_file_real_temperatura):
                faltando = set(csv_file_real_temperatura['Unidades'].values) - set(csv_file_referencia_temperatura['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no arquivo de carga térmica REFERÊNCIA: ' + ', '.join(list(faltando)))
            else:
                faltando = set(csv_file_referencia_temperatura['Unidades'].values) - set(csv_file_real_temperatura['Unidades'].values)
                warnings_resultados.append('⚠️ Unidades faltando no arquivo de carga térmica REAL: ' + ', '.join(list(faltando)))

        else:
            if csv_file_real_temperatura['Unidades'].tolist() != csv_file_referencia_temperatura['Unidades'].tolist():
                dif_real = set(csv_file_real_temperatura['Unidades'].values) - set(csv_file_referencia_temperatura['Unidades'].values)
                dif_ref = set(csv_file_referencia_temperatura['Unidades'].values) - set(csv_file_real_temperatura['Unidades'].values)
                warnings_resultados.append(
                    '⚠️ Algumas unidades entre os arquivos de carga térmica estão diferentes. '
                    '**Real=** ' + ', '.join(list(dif_real)) + 
                    '. **Referência=** ' + ', '.join(list(dif_ref)) +
                    '. **Considerando as unidades do edifício REAL.**'
                )
                csv_file_referencia_temperatura['Unidades'] = csv_file_real_temperatura['Unidades']

        if len(warnings_resultados) > 0:
            warnings_component = html.Ul(
                children=[html.Li(msg) for msg in warnings_resultados],
                style={'color': 'red'}  # Você pode customizar o estilo aqui
            )

        else:
            warnings_component = html.Ul(
                children=[html.Li('Todos os arquivos foram carregados corretamente!')],
                style={'color': 'green'}  # Você pode customizar o estilo aqui
            )

        CONVERSAO = 0.000000277778

        res_nv_inter_sup = pd.DataFrame()
        res_nv_inter_sup['Unidades'] = edificio_real['Unidades']
        res_nv_inter_sup['PHFT REAL'] = edificio_real['PHFT']
        res_nv_inter_sup['TOMAX REAL'] = edificio_real['TOMAX']
        res_nv_inter_sup['TOMIN REAL'] = edificio_real['TOMIN']
        res_nv_inter_sup['PHFT REFERENCIA'] = edificio_referencia['PHFT']
        res_nv_inter_sup['TOMAX REFERENCIA'] = edificio_referencia['TOMAX']
        res_nv_inter_sup['TOMIN REFERENCIA'] = edificio_referencia['TOMIN']
        res_nv_inter_sup['PHFTreal-90PHFTref'] = edificio_real['PHFT'] - edificio_referencia['PHFT']*0.9
        res_nv_inter_sup['0.9PHFT REFERENCIA'] = edificio_referencia['PHFT']*0.9
        res_nv_inter_sup['ΔPHFT'] = edificio_real['PHFT'] - edificio_referencia['PHFT']

        if TIPOLOGIA == 'unifamiliar':
            res_nv_inter_sup['TIPOLOGIA'] = 'UNIFAMILIAR'
            res_nv_inter_sup['PAVIMENTO'] = 'TERREO'

        else:
            res_nv_inter_sup['TIPOLOGIA'] = tipologia['TIPOLOGIA'].values
            res_nv_inter_sup['PAVIMENTO'] = tipologia['PAVIMENTO'].values

        res_nv_inter_sup['ZONA'] = zona
        res_nv_inter_sup['CARGA TERMICA RESFRIAMENTO REAL'] = csv_file_real_temperatura['SOMA CARGA RESFRIAMENTO'] * CONVERSAO
        res_nv_inter_sup['CARGA TERMICA AQUECIMENTO REAL'] = csv_file_real_temperatura['SOMA CARGA AQUECIMENTO'] * CONVERSAO
        res_nv_inter_sup['SOMA CARGA TERMICA REAL'] = csv_file_real_temperatura['SOMA CARGA TOTAL'] * CONVERSAO
        res_nv_inter_sup['CARGA TERMICA RESFRIAMENTO REFERENCIA'] = csv_file_referencia_temperatura['SOMA CARGA RESFRIAMENTO'] * CONVERSAO
        res_nv_inter_sup['CARGA TERMICA AQUECIMENTO REFERENCIA'] = csv_file_referencia_temperatura['SOMA CARGA AQUECIMENTO'] * CONVERSAO
        res_nv_inter_sup['SOMA CARGA TERMICA REFERENCIA'] = csv_file_referencia_temperatura['SOMA CARGA TOTAL'] * CONVERSAO
        res_nv_inter_sup['AREA'] = areas['AREA']
        res_nv_inter_sup['CGTT/AREA REAL'] = res_nv_inter_sup['SOMA CARGA TERMICA REFERENCIA']/res_nv_inter_sup['AREA']
        res_nv_inter_sup['REDUCAO CARGA TERMICA TOTAL'] = (1 - (res_nv_inter_sup['SOMA CARGA TERMICA REAL']/res_nv_inter_sup['SOMA CARGA TERMICA REFERENCIA'])) * 100

        deltatmax(res_nv_inter_sup, res_nv_inter_sup['TIPOLOGIA'], res_nv_inter_sup['PAVIMENTO'])

        deltatmin(res_nv_inter_sup, res_nv_inter_sup['ZONA'])

        criterio_tomax(res_nv_inter_sup, 
                    edificio_real['TOMAX'], 
                    edificio_referencia['TOMAX'],
                    res_nv_inter_sup['ΔTOMAX'])
        
        criterio_tomin(res_nv_inter_sup, 
                    edificio_real['TOMIN'], 
                    edificio_referencia['TOMIN'],
                    res_nv_inter_sup['ΔTOMIN'])
        
        criterio_phft(res_nv_inter_sup, res_nv_inter_sup['PHFTreal-90PHFTref'])

        atendimento_minimo(res_nv_inter_sup,
                        res_nv_inter_sup['CRITERIO TOMAX'],
                        res_nv_inter_sup['CRITERIO TOMIN'],
                        res_nv_inter_sup['CRITERIO PHFT'],
                        res_nv_inter_sup['ZONA'])
        
        delta_phftmin(res_nv_inter_sup,
                                edificio_referencia['PHFT'],
                                res_nv_inter_sup['TIPOLOGIA'],
                                res_nv_inter_sup['PAVIMENTO']) 
        
        atendimento_intermediario_delta_phft(res_nv_inter_sup,
                                            res_nv_inter_sup['ΔPHFT'],
                                            res_nv_inter_sup['ΔPHFTmin'])
        
        reducao_carga_termica_minima_intermediaria(res_nv_inter_sup,
                                                edificio_referencia['PHFT'],
                                                res_nv_inter_sup['CGTT/AREA REAL'],
                                                res_nv_inter_sup['TIPOLOGIA'],
                                                res_nv_inter_sup['PAVIMENTO'])
        
        reducao_carga_termica_minima_superior(res_nv_inter_sup,
                                            res_nv_inter_sup['CGTT/AREA REAL'],
                                            res_nv_inter_sup['TIPOLOGIA'],
                                            res_nv_inter_sup['PAVIMENTO'])
        
        criterio_cgt_intermediaria(res_nv_inter_sup,
                                res_nv_inter_sup['REDUCAO CARGA TERMICA TOTAL'],
                                res_nv_inter_sup['RED CGTT MIN INTERMEDIARIO'],
                                )
        
        criterio_cgt_superior(res_nv_inter_sup,
                                res_nv_inter_sup['REDUCAO CARGA TERMICA TOTAL'],
                                res_nv_inter_sup['RED CGTT MIN SUPERIROR'],
                                )
        
        criterio_valor(res_nv_inter_sup,
                    res_nv_inter_sup['ZONA'],
                    res_nv_inter_sup['CRITERIO PHFT'],
                    res_nv_inter_sup['CRITERIO TOMAX'],
                    res_nv_inter_sup['CRITERIO TOMIN'],
                    res_nv_inter_sup['CRITERIO PHFT INTERMEDIARIO'],
                    res_nv_inter_sup['CRITERIO CARGA TERMICA INTERMEDIARIA'],
                    res_nv_inter_sup['CRITERIO CARGA TERMICA SUPERIOR'])
                
        res_nv_intersup_parcial = res_nv_inter_sup[['Unidades', 
                                                     'PHFT REAL',
                                                    'TOMAX REAL',
                                                    'TOMIN REAL',
                                                    'SOMA CARGA TERMICA REAL',
                                                    'CGTT/AREA REAL',
                                                    'PHFT REFERENCIA',
                                                    'TOMAX REFERENCIA',
                                                    'TOMIN REFERENCIA',
                                                    'SOMA CARGA TERMICA REFERENCIA',
                                                    '0.9PHFT REFERENCIA',
                                                    'ΔTOMAX',
                                                    'ΔTOMIN',
                                                    'ΔPHFT',
                                                    'ΔPHFTmin',
                                                    'REDUCAO CARGA TERMICA TOTAL',
                                                    'RED CGTT MIN INTERMEDIARIO',
                                                    'RED CGTT MIN SUPERIROR',
                                                    'NÍVEL DE ATENDIMENTO'
                                                    ]]  

        # Tabela dos resultados parciais
        res_nv_minimo_parciais = html.Div([
            
                fac.AntdTable(
                id={'type': "resultados", 'index': 'intermediario-parcial'},  
                columns=[
                    {'title': col, 'dataIndex': col}
                    for col in res_nv_intersup_parcial.columns
                ],
                data=res_nv_intersup_parcial.round(2).to_dict('records'),
                bordered=True,
                locale="en-us",
            ),

            dmc.Button(
                "Baixar resultados intermediarios parcial",
                leftSection=DashIconify(icon="material-symbols:arrow-circle-down-outline"),
                id={'type': "btn-download-resultados", 'index': 'intermediario-parcial'},
                color='blue', radius='sm'
            ),

            # dbc.Button("Baixar resultados intermediarios parcial", id={'type': "btn-download-resultados", 'index': 'intermediario-parcial'}, color="primary"),
            dcc.Download(id={'type': "download-resultados", 'index': 'intermediario-parcial'})
        
        ])

        # Tabela dos resultados completos
        res_nv_intersup_completo = html.Div([
            
                fac.AntdTable(
                id={'type': "resultados", 'index': 'intermediario-completo'},    
                columns=[
                    {'title': col, 'dataIndex': col}
                    for col in res_nv_inter_sup.columns
                ],
                data=res_nv_inter_sup.round(2).to_dict('records'),
                bordered=True,
                locale="en-us",
            ),

            dmc.Button(
                "Baixar resultados intermediarios completo",
                leftSection=DashIconify(icon="material-symbols:arrow-circle-down-outline"),
                id={'type': "btn-download-resultados", 'index': 'intermediario-completo'},
                color='blue', radius='sm'
            ),

            # dbc.Button("Baixar resultados intermediarios completos", id={'type': "btn-download-resultados", 'index': 'intermediario-completo'}, color="primary"),
            dcc.Download(id={'type': "download-resultados", 'index': 'intermediario-completo'})
        
        ])

        # Gerando o gráfico de resultado míninmo
        fig_redcgttminsup = plot_resultado_inter_sup(res_nv_inter_sup)
        fig_redcgttminsup = dcc.Graph(figure=fig_redcgttminsup, config={"displaylogo": False})

        # Salvando os gráficos
        filename = lastUploadTaskRecord.get("fileName").split('.csv')[0]
        plot_resultado_inter_sup_matplotlib(res_nv_inter_sup, filename=filename+'_REDCGTTMINSUP')

        # Atribuindo os resultados parciais e completos a tabs
        tabs_content = {
            'Resultados parciais': res_nv_minimo_parciais,
            'Resultados completos': res_nv_intersup_completo,
            'Resultado gráfico': fig_redcgttminsup,
        }

        tabs = ['Resultados parciais', 'Resultados completos', 'Resultado gráfico']

        conteudo = html.Div([

                html.H5('Resultados do nível intermediário e superior de conforto térmico', className='fw-bold mb-2'),

                fac.AntdTabs(
                    centered=False,
                    items=[
                        {
                            'key': f'tab{tab}',
                            'label': f'{tab}',
                            'children': tabs_content[tab]
                        }

                        for tab in tabs if tab in tabs_content
                    ]
                ),
        ])

        return conteudo, warnings_component

    return dash.no_update, dash.no_update

####################################################################################################################################################################

@callback(
    Output({'type': "download-resultados", 'index': MATCH}, "data"),
    Input({'type': "btn-download-resultados", 'index': MATCH}, "n_clicks"),
    Input({'type': "btn-download-resultados", 'index': MATCH}, "id"),
    State({'type': "resultados", 'index': MATCH}, "data"),
    prevent_initial_call=True
)
def download_resultados(n_clicks, id, table_data):
    # converte a lista de dicionários em DataFrame
    df = pd.DataFrame(table_data)
    filename = f'{id.get("index")}_resultados.csv'
    return dcc.send_data_frame(df.to_csv, filename, index=False)


####################################################################################################################################################################

# @callback(
#     Output("download-resultados_nivel_minimo_parciais", "data"),
#     Input('resultados_nivel_minimo_parciais', 'data'),
#     Input('btn-download-resultados_nivel_minimo_parciais', 'n_clicks'),
#     prevent_initial_call=True
# )
# def baixar_arquivo(data, n_clicks):

#     ctx = dash.callback_context

#     if ctx.triggered_id == "btn-download-resultados_nivel_minimo_parciais":
#         return dict(content=data, filename='resultados_minimos', type="text/csv")

#     else:

#         return dash.no_update

# ####################################################################################################################################################################

# @callback(
#     Output("download-resultados_nivel_minimo_completos", "data"),
#     Input('resultados_nivel_minimo_completos', 'data'),
#     Input('btn-download-resultados_nivel_minimo_completos', 'n_clicks'),
#     prevent_initial_call=True
# )
# def baixar_arquivo(data, n_clicks):

#     ctx = dash.callback_context

#     if ctx.triggered_id == "btn-download-resultados_nivel_minimo_completos":
#         return dict(content=data, filename='resultados_completos', type="text/csv")

#     else:

#         return dash.no_update

####################################################################################################################################################################

@callback(
    Output("collapse-csv_real_temperatura_unidade", "opened"),
    Input("collapse-btn-csv_real_temperatura_unidade", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################

@callback(
    Output("collapse-csv_real_temperatura_ambiente", "opened"),
    Input("collapse-btn-csv_real_temperatura_ambiente", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################

@callback(
    Output("collapse-csv_referencia_temperatura_unidade", "opened"),
    Input("collapse-btn-csv_referencia_temperatura_unidade", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################
@callback(
    Output("collapse-csv_referencia_temperatura_ambiente", "opened"),
    Input("collapse-btn-csv_referencia_temperatura_ambiente", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################

@callback(
    Output("collapse-csv_real_hvac_unidade", "opened"),
    Input("collapse-btn-csv_real_hvac_unidade", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################

@callback(
    Output("collapse-csv_real_hvac_ambiente", "opened"),
    Input("collapse-btn-csv_real_hvac_ambiente", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################

@callback(
    Output("collapse-csv_referencia_hvac_unidade", "opened"),
    Input("collapse-btn-csv_referencia_hvac_unidade", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################

@callback(
    Output("collapse-csv_referencia_hvac_ambiente", "opened"),
    Input("collapse-btn-csv_referencia_hvac_ambiente", "n_clicks"),
)
def update(n):
    if n % 2 == 0:
        return False
    return True

####################################################################################################################################################################