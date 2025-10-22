import dash
from dash import html, dcc, dash_table, Output, Input, callback
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import feffery_antd_components as fac
from dash_iconify import DashIconify
import pandas as pd
from funcoes.funcoes_app_txt import *
from funcoes.funcoes_txt_vn import *
from funcoes.funcoes_txt_hvac import *
import time
from db.db_local import get_ambientes

####################################################################################################################################################################

def forms_organiza_txt():

    # from utils.informacoes import ambientes

    ambientes = get_ambientes()
    print(ambientes)
    ambientes = ambientes.dropna(axis=1)

    conteudo_txt = html.Div([

        html.H5('Planilha de ambientes', className='fw-bold'),

        html.Details([
            html.Summary(html.B("Ambientes")),
            fac.AntdTable(
                id='csv_real_temperatura_unidade',
                columns=[
                    {'title': col, 'dataIndex': col}
                    for col in ambientes.columns
                ],
                data=ambientes.to_dict('records'),
                bordered=True,
                locale="en-us",

            ),
        ]),

        fac.AntdDivider(),

        html.H5('Planilha de Esquadrias', className='fw-bold'),

        html.Details([
            html.Summary(html.B("Esquadrias do projeto")),
            dash_table.DataTable(
                id='tabela_esquadrias',
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
                style_table={'overflowX': 'auto', 'overflowY': 'auto'},
            )
        ]),

        fac.AntdDivider(),

        html.H5('Arquivos de entrada', className='fw-bold'),
        # Colocando os uploads em duas colunas
        dmc.Grid([

            # Arquivo VN
            dmc.GridCol(
                children=[
                    html.H5('Arquivo VN', className='fw-bold'),
                    fac.AntdUpload(
                        id='upload-data',
                        apiUrl='/upload/',
                        uploadId='vn',
                        locale='en-us',
                        fileMaxSize=500,
                        fileTypes=['txt'],
                        buttonContent="Selecione o arquivo VN",
                    ),
                    html.Div(id='output-data-upload'),
                    dcc.Store(id='stored-data', data=None),
                ],
                span=6,
                style={"textAlign": "center", "marginTop": "10px"}
            ),

            # Arquivo HVAC
            dmc.GridCol(
                children=[
                    html.H5('Arquivo HVAC', className='fw-bold'),
                    fac.AntdUpload(
                        id='upload-data-hvac',
                        apiUrl='/upload/',
                        uploadId='hvac',
                        locale='en-us',
                        fileMaxSize=500,
                        fileTypes=['txt'],
                        buttonContent="Selecione o arquivo HVAC",
                    ),
                    html.Div(id='output-data-upload-hvac'),
                    dcc.Store(id='stored-data-hvac', data=None),
                ],
                span=6,
                style={"textAlign": "center", "marginTop": "10px"}
            ),

        ], align="center"),
          
    ])

    return conteudo_txt

####################################################################################################################################################################

# Função para extrair apenas o valor selecionado (value)
def extrai_value(d):
    if isinstance(d, dict) and 'value' in d:
        return d['value']
    return d

####################################################################################################################################################################

# Função geral para processar cada item (sem criar *_options)
def processa_item(item):
    novo_item = {}
    for chave, valor in item.items():
        if isinstance(valor, dict) and 'options' in valor and 'value' in valor:
            novo_item[chave] = extrai_value(valor)
        else:
            novo_item[chave] = valor
    return novo_item

####################################################################################################################################################################

@callback(
    Output('tabela_esquadrias', 'data'),
    Input("editable-table", "data"),
)
def update_table(data):

    esquadrias = [processa_item(item) for item in data]

    return esquadrias

###################################################################################################################################################################

@callback(
Output("stored-data", "data"),
Output('output-data-upload', 'children'),
Input('upload-data', 'lastUploadTaskRecord'),
Input("tabela_esquadrias", "data"),
)
def ajusta_arquivo_VN(lastUploadTaskRecord, esquadrias):

    ambientes = get_ambientes()

    if lastUploadTaskRecord is not None:

        VENTILACAO = 'Completa'

        # Iniciando o contador do tempo 
        start_time = time.time()

        # esquadrias = pd.read_csv('exemplo/lista_esquadrias_real_R00.csv', encoding='latin1', sep=';')
        esquadrias = pd.DataFrame(esquadrias)
        esquadrias = esquadrias.dropna()
        esquadrias.reset_index(drop=True, inplace=True)
        bib_ambiente = ambientes.dropna(axis=1)

        try:
            file = pd.read_table(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='utf-8', header=None)

        except:
            file = pd.read_table(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='ISO-8859-1', header=None)

        # Retirando o \r\n do arquivo
        file = file.applymap(limpar_celula)
        
        CLASS_DELIMITER_IN_TXT = '!-   ===========' 
        sections_names = nome_secoes(file, CLASS_DELIMITER_IN_TXT)
        sections = separada_por_secao(file, CLASS_DELIMITER_IN_TXT) 

        # Seções necessárias dentro do txt. Caso não houver alguma delas, retorna erro. 
        sectios_to_check = [
                            'zone',
                            'AirflowNetwork:MultiZone:Surface',
                            'AirflowNetwork:MultiZone:Zone',
                            'FenestrationSurface:Detailed',
                            'AirflowNetwork:MultiZone:Component:DetailedOpening',
                            ]
        sections_less = check_mandatory_sections(sectios_to_check, sections_names)

        # Confere se há todas as seções necessárias
        if len(sections_less) == 0: 
            output_file_name = lastUploadTaskRecord.get('fileName').split('.')[0] + '_FINAL.' + lastUploadTaskRecord.get('fileName').split('.')[1]
            output_file_name = './outputs/' + output_file_name

            if os.path.isfile(output_file_name):
                os.remove(output_file_name)

            # Separando as classes que vamos arrumar/retirar do arquivo original
            people = find_section_index_by_name('people', sections, sections_names)
            zone = find_section_index_by_name('zone', sections, sections_names)
            airflowsurface = find_section_index_by_name('AirflowNetwork:MultiZone:Surface', sections, sections_names)
            airflowzone = find_section_index_by_name('AirflowNetwork:MultiZone:Zone', sections, sections_names)
            schedule_year = find_section_index_by_name('Schedule:Year', sections, sections_names)
            schedule_weekly_daily = find_section_index_by_name('Schedule:Week:Daily', sections, sections_names)
            schedule_day_hourly = find_section_index_by_name('Schedule:Day:Hourly', sections, sections_names)
            schedule_type_limits = find_section_index_by_name('ScheduleTypeLimits', sections, sections_names)
            output_variable = find_section_index_by_name('Output:Variable', sections, sections_names)
            schedule_compact = find_section_index_by_name('Schedule:Compact', sections, sections_names)
            buildingsurface_detailed = find_section_index_by_name('BuildingSurface:Detailed', sections, sections_names)
            shadingbuilding_detailed = find_section_index_by_name('Shading:Building:Detailed', sections, sections_names)
            output_meter = find_section_index_by_name('Output:Meter', sections, sections_names)
            lights = find_section_index_by_name('Lights', sections, sections_names)
            otherequipament = find_section_index_by_name('OtherEquipment', sections, sections_names)
            airflow_detailedopening = find_section_index_by_name('AirflowNetwork:MultiZone:Component:DetailedOpening', sections, sections_names)
            fenestration = find_section_index_by_name('FenestrationSurface:Detailed', sections, sections_names)
            output_table_timebins = find_section_index_by_name('Output:Table:Timebins', sections, sections_names)
            
            # Secões que vamos deletar do arquivo original
            sections_to_delet = [people, 
                    airflowsurface, 
                    airflowzone, 
                    schedule_year, 
                    schedule_weekly_daily, 
                    schedule_day_hourly, 
                    schedule_type_limits, 
                    output_variable, 
                    schedule_compact,
                    output_meter,
                    lights,
                    otherequipament,
                    output_table_timebins
            ]
        
            # Deletando as seções do arquivo original
            remove_cracks(buildingsurface_detailed)
            replace_to_blank(shadingbuilding_detailed, '!- Transmittance Schedule Name')
            fix_airflow_detailedopening(airflow_detailedopening, fenestration, esquadrias)        

            # NOME DOS AMBIENTES
            ZONES_WHIT_PEOPLE = ['DORM', 'SUITE', 'SALADEESTAR', 'STUDIO']
            ZONES_ONLY_SALA_STUDIO = ['SALADEESTAR', 'STUDIO']

            zone_names = get_zone_with_people_names(zone, ZONES_WHIT_PEOPLE)
            zone_names = [x.replace(" ", "").split(',')[0] for x in zone_names]

            zone_names_sala_studio = get_zone_with_people_names(zone, ZONES_ONLY_SALA_STUDIO)
            zone_names_sala_studio = [x.replace(" ", "").split(',')[0] for x in zone_names_sala_studio]

            zone_names_all = get_zone_with_all(zone)
            zone_names_all = [x.replace(" ", "").split(',')[0] for x in zone_names_all]

            # Parâmetros para o multizone_surface
            if VENTILACAO == 'Completa':
                surface_names = get_surfaces_names(airflowsurface)
                leake_name = get_leake_component_name(airflowsurface)    
                external_node_name = get_external_node_name(airflowsurface)
                surface_names_whitout_desc = [surface_names[name].split('!')[0].replace(' ', '') for name in range(len(surface_names))] 

            else:
                surface_names = get_surfaces_names_simplificada(airflowsurface)
                leake_name = get_leake_component_name_simplificada(surface_names)    
                surface_names_whitout_desc = [surface_names[name].split('!')[0].replace(' ', '') for name in range(len(surface_names))]     

        # Abrindo um arquivo para escrever o txt final ...
        print (f'Abrindo o arquivo de saida em {output_file_name}')
        to_txt_file = open(output_file_name, 'a', encoding='utf-8')

        while True:

            delete_sections_from_original_file(file, sections_to_delet)

            for linhas_do_df in file.values:
                to_txt_file.write(linhas_do_df[0]+'\n')

            gera_txt_OUTPUTVARIABLE(to_txt_file)
            gera_txt_SCHEDULETYPELIMITS(to_txt_file)
            gera_txt_SCHEDULE_COMPACT(to_txt_file)

            if VENTILACAO == 'Completa':
                gera_txt_AIRFLOWNETWORKMULTIZONE_SURFACE(to_txt_file, surface_names_whitout_desc, bib_ambiente, ambientes, leake_name, external_node_name)
            else:
                gera_txt_AIRFLOWNETWORKMULTIZONE_SURFACE_SIMPLIFICADA(to_txt_file, surface_names_whitout_desc, bib_ambiente, ambientes, leake_name)

            gera_txt_OTHEREQUIPAMENT(to_txt_file, zone_names_sala_studio)
            gera_txt_LIGHT(to_txt_file, zone_names)
            gera_txt_PEOPLE(to_txt_file, zone_names)
            gera_txt_AIRFLOWNETWORKMULTIZONE_ZONE(to_txt_file, zone_names_all)
            to_txt_file.close()

            break

        if os.path.isfile(output_file_name):

            with open(output_file_name, 'r') as file_f:

                data = file_f.read()
                tfinal = round((time.time() - start_time), 2)
                return data, html.Div([

                    fac.AntdAlert(
                        message='Sucesso!!',
                        description=f'Tempo total decorrido: {tfinal} segundos.',
                        type='success',
                        closable=True,
                        showIcon=True,
                        style={'marginTop': '10px'}
                    ),
                
                    dmc.Button(
                        "Baixar arquivo VN ajustado",
                        leftSection=DashIconify(icon="material-symbols:arrow-circle-down-outline"),
                        id="btn-download-vn",
                        color='blue', radius='sm'
                    ),

                    # dbc.Alert(f"Sucesso! Tempo total decorrido: {tfinal} segundos.", color="success"),
                    # dbc.Button("Baixar arquivo VN ajustado", id="btn-download-vn", color="primary", className="mt-2"),
                    dcc.Download(id="download-txt"),
                ])
            
        else:
            return None, html.Div([

                fac.AntdAlert(
                    message='Erro!',
                    description=f'O arquivo não foi encontrado.',
                    type='error',
                    closable=True,
                    showIcon=True,
                    style={'marginTop': '10px'}
                ),

                # dbc.Alert("Erro! O arquivo não foi encontrado.", color="danger"),
            ])

    return dash.no_update, dash.no_update

###################################################################################################################################################################

@callback(
Output("download-txt", "data"),
Input("stored-data", "data"),
Input('upload-data', 'lastUploadTaskRecord'),
Input("btn-download-vn", "n_clicks"),
prevent_initial_call=True
)
def baixar_arquivo(data, lastUploadTaskRecord, n_clicks):

    ctx = dash.callback_context

    if ctx.triggered_id == "btn-download-vn":
        outputfile_name = lastUploadTaskRecord.get('fileName').split('.')[0] + '_FINAL.' + lastUploadTaskRecord.get('fileName').split('.')[1]
        return dict(content=data, filename=outputfile_name, type='text/plain')

    else:

        return dash.no_update

###################################################################################################################################################################

@callback(
Output("stored-data-hvac", "data"),
Output('output-data-upload-hvac', 'children'),
Input('upload-data-hvac', 'lastUploadTaskRecord'),   
)
def ajusta_arquivo_HVAC(lastUploadTaskRecord):

    if lastUploadTaskRecord is not None:

        # Abrindo o arquivo como dataframe
        start_time = time.time()

        try:
            file = pd.read_table(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='utf-8', header=None)

        except:
            file = pd.read_table(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}", encoding='ISO-8859-1', header=None)


        # Retirando o \r\n do arquivo
        file = file.applymap(limpar_celula)

        CLASS_DELIMITER_IN_TXT = '!-   ===========' 
        sections_names = nome_secoes(file, CLASS_DELIMITER_IN_TXT)
        sections = separada_por_secao(file, CLASS_DELIMITER_IN_TXT) 

        output_file_name = lastUploadTaskRecord.get('fileName').split('.')[0] + '_HVAC.' + lastUploadTaskRecord.get('fileName').split('.')[1]
        output_file_name = './outputs/' + output_file_name

        if os.path.isfile(output_file_name):
            os.remove(output_file_name)

        # Abrindo txt para escrever ...
        print (f'Abrindo o arquivo de saida em {output_file_name}')
        to_txt_file = open(output_file_name, 'a', encoding='utf-8')

        airflowsurface = find_section_index_by_name('AirflowNetwork:MultiZone:Surface', sections, sections_names)
        zone = find_section_index_by_name('zone', sections, sections_names)
        output_variable = find_section_index_by_name('Output:Variable', sections, sections_names)

        # Colocar aqui apenas as classes que serão retiradas no txt de input
        sections_to_delet = [ 
                        output_variable,
                        ] 
        
        # NOME DOS AMBIENTES
        ZONES_WHIT_PEOPLE = ['DORM', 'SUITE', 'SALADEESTAR', 'STUDIO']

        zone_names_only_sala_dorm = get_zone_with_people_names(zone, ZONES_WHIT_PEOPLE)
        zone_names_only_sala_dorm = [x.replace(" ", "").split(',')[0] for x in zone_names_only_sala_dorm]

        fix_airflor_surface(airflowsurface)

        while True:

            delete_sections_from_original_file(file, sections_to_delet)

            for linhas_do_df in file.values:
                to_txt_file.write(linhas_do_df[0]+'\n')

            gera_txt_HVACTEMPLATETHERMOSTAT(to_txt_file)
            gera_txt_HVACTEMPLATEZONEIDEALLOADSAIRSYSTEM(to_txt_file, zone_names_only_sala_dorm)
            gera_txt_OUTPUTVARIABLEHVAC(to_txt_file)

            to_txt_file.close()
            break

        if os.path.isfile(output_file_name):

            with open(output_file_name, 'r') as file_f:
                data = file_f.read()
                tfinal = round((time.time() - start_time),2)
                return data, html.Div([

                        fac.AntdAlert(
                                message='Sucesso!!',
                                description=f'Tempo total decorrido: {tfinal} segundos.',
                                type='success',
                                closable=True,
                                showIcon=True,
                                style={'marginTop': '10px'}
                            ),

                        # dbc.Alert(f"Sucesso! Tempo total decorrido: {tfinal} segundos.", color="success"),
                        dmc.Button(
                            "Baixar arquivo VN ajustado",
                            leftSection=DashIconify(icon="material-symbols:arrow-circle-down-outline"),
                            id="btn-download-hvac",
                            color='blue', radius='sm'
                        ),
                        dcc.Download(id="download-txt-hvac"),
                        # dbc.Button("Baixar arquivo HVAC ajustado", id="btn-download-hvac", color="primary", className="mt-2"),
                    ])
            
    return dash.no_update, dash.no_update

###################################################################################################################################################################

@callback(
Output("download-txt-hvac", "data"),
Input("stored-data-hvac", "data"),
Input('upload-data-hvac', 'lastUploadTaskRecord'),
Input("btn-download-hvac", "n_clicks"),
prevent_initial_call=True
)
def baixar_arquivo_hvac(data, lastUploadTaskRecord, n_clicks):

    ctx = dash.callback_context

    if ctx.triggered_id == "btn-download-hvac":

        outputfile_name = lastUploadTaskRecord.get('fileName').split('.')[0] + '_HVAC.' + lastUploadTaskRecord.get('fileName').split('.')[1]
        return dict(content=data, filename=outputfile_name, type='text/plain')
    
    else:

        return dash.no_update

###################################################################################################################################################################
