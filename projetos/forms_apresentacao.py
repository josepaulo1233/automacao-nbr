from dash import dcc, html, callback, Output, Input, State
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import feffery_antd_components as fac
import base64
import os
import dash
import io
from pptx import Presentation
from funcoes.modificar_slides import extrair_textos, alterar_texto, adicionar_imagem_com_proporcao
from funcoes.modificar_tabelas import get_tables_as_dataframes, update_table, substituir_valores_df
from datetime import datetime
import pandas as pd

####################################################################################################################################################################

def form_apresentacao(projeto):

    project_info = [
        {"label": "Nome do projeto", "value": projeto.get('informacoes_projeto', {}).get('nome_projeto', 'NOME PROJETO')},
        {"label": "Número do projeto", "value": projeto.get('informacoes_projeto', {}).get('numero_projeto', 'Nº PROJETO')},
        {"label": "Total de Ambientes", "value": len(projeto.get('ambientes', {}))},
        {"label": "Total de Esquadrias", "value": len(projeto.get('esquadrias', {}))},
    ]

    rows = [
        dmc.TableTr(
            [
                dmc.TableTd(info["label"]),
                dmc.TableTd(info["value"]),
            ]
        )
        for info in project_info
    ]

    head = dmc.TableThead(
        dmc.TableTr(
            [
                dmc.TableTh("Informação"),
                dmc.TableTh("Valor"),
            ]
        )
    )
    body = dmc.TableTbody(rows)
    caption = dmc.TableCaption("Resumo do projeto")

    conteudo = html.Div([

        html.H5('Montando relatório ...', className='fw-bold mb-3'),

        dcc.Store(id='armazenar-apresentacao', data=projeto),

        dbc.Row([

            dbc.Col([
                html.Label("Slide inicial das esquadrias"),
                fac.AntdInputNumber(
                    id='chave-inicial-esquadrias',
                    min=1,
                    value=7,
                    style={"width": "100%"}
                ),

                html.Label("Slide inicial dos ambientes", style={"marginTop": "10px"}),
                fac.AntdInputNumber(
                    id='chave-inicial-ambientes',
                    min=1,
                    value=10,
                    style={"width": "100%"}
                ),
            ], width=4),

            dbc.Col([
                html.Label("Slide inicial da parede externa"),
                fac.AntdInputNumber(
                    id='chave-inicial-parede-externa',
                    min=1,
                    value=13,
                    style={"width": "100%"}
                ),

                html.Label("Slide inicial da parede interna", style={"marginTop": "10px"}),
                fac.AntdInputNumber(
                    id='chave-inicial-parede-interna',
                    min=1,
                    value=14,
                    style={"width": "100%"}
                ),
            ], width=4),

            dbc.Col([
                html.Label("Slide inicial da cobertura"),
                fac.AntdInputNumber(
                    id='chave-inicial-cobertura',
                    min=1,
                    value=15,
                    style={"width": "100%"}
                ),

                html.Label("Slide inicial do piso/laje", style={"marginTop": "10px"}),
                fac.AntdInputNumber(
                    id='chave-inicial-piso-laje',
                    min=1,
                    value=16,
                    style={"width": "100%"}
                ),
            ], width=4),

        ]),

        fac.AntdDivider(),

        # Display do nome do projeto
        dmc.Table([caption, head, body], striped=True, highlightOnHover=True, withColumnBorders=True, withTableBorder=True,),

        fac.AntdDivider(),

        fac.AntdUpload(
            id='upload-pptx',
            apiUrl='/upload/',
            uploadId='pptx',
            locale='en-us',
            fileMaxSize=500,
            fileTypes=['pptx'],
            buttonProps={'block': True},
            buttonContent="Faça upload do arquivo de apresentação base",
        ),

        dbc.Row([

            dbc.Spinner(html.Div(id='output-upload-pptx', style={'margin-top': '10px'})),
            dcc.Download(id="download-ppt"),

        ])

    ])
    
    return conteudo

####################################################################################################################################################################

def ajusta_materiais(material: str, projeto: dict):

    limite_materiais = 9  # Quantidade máxima por chave
    materiais = projeto.get('materiais', {}).get(material, {})

    # Filtra somente as chaves numéricas
    materiais_numerados = {k: v for k, v in materiais.items() if k.isdigit()}

    # Ordena pelas chaves numéricas (caso '1', '2', '10' estejam fora de ordem)
    materiais_ordenados = dict(sorted(materiais_numerados.items(), key=lambda x: int(x[0])))

    # Lista de valores
    valores_materiais = list(materiais_ordenados.values())

    for i in range(0, len(valores_materiais), limite_materiais):

        substituicoes_por_slide = {

            **{f'M{x+1}': valores_materiais[x].get('Tipo do material') for x in range(i, min(i + limite_materiais, len(valores_materiais)))},
            **{f'E{x+1}': valores_materiais[x].get('Espessura [m]') for x in range(i, min(i + limite_materiais, len(valores_materiais)))},
            **{f'D{x+1}': valores_materiais[x].get('Densidade [kg/m³]') for x in range(i, min(i + limite_materiais, len(valores_materiais)))},
            **{f'C{x+1}': valores_materiais[x].get('Condutividade [W/mK]') for x in range(i, min(i + limite_materiais, len(valores_materiais)))},
            **{f'CE{x+1}': valores_materiais[x].get('Calor específico [kJ/KgK]') for x in range(i, min(i + limite_materiais, len(valores_materiais)))},
            **{f'R{x+1}': valores_materiais[x].get('Resistência [m²K/W]') for x in range(i, min(i + limite_materiais, len(valores_materiais)))},
            'UTER': round(projeto.get('materiais', {}).get(material, {}).get('U'), 2),
            'CTER': round(projeto.get('materiais', {}).get(material, {}).get('CT'), 2),
            '[ATENDE/NÃO ATENDE]': projeto.get('materiais', {}).get(material, {}).get('Criterio'),
            'indices_para_nao_mudar': [],
            'tipo': 'tabela',
            'tamanho_fonte': 10,
            'with_pct': False,
        }

    return substituicoes_por_slide

####################################################################################################################################################################

@callback(
    Output("download-ppt", "data"),
    Output('output-upload-pptx', 'children'),
    Input('upload-pptx', 'lastUploadTaskRecord'),
    Input('armazenar-apresentacao', 'data'),
    Input('chave-inicial-esquadrias', 'value'),
    Input('chave-inicial-ambientes', 'value'),
    Input('chave-inicial-parede-externa', 'value'),
    Input('chave-inicial-parede-interna', 'value'),
    Input('chave-inicial-cobertura', 'value'),
    Input('chave-inicial-piso-laje', 'value'),
    prevent_initial_call=True
)
def ajusta_pptx(lastUploadTaskRecord, projeto, chave_inicial_esquadrias, chave_inicial_ambientes, chave_inicial_materiais_parede_externa, chave_inicial_materiais_parede_interna, chave_inicial_materiais_cobertura, chave_inicial_materiais_piso_laje):

    try:

        chave_inicial_esquadrias = chave_inicial_esquadrias -1
        chave_inicial_ambientes = chave_inicial_ambientes -1
        chave_inicial_materiais_parede_externa = chave_inicial_materiais_parede_externa -1
        chave_inicial_materiais_parede_interna = chave_inicial_materiais_parede_interna -1
        chave_inicial_materiais_cobertura = chave_inicial_materiais_cobertura -1
        chave_inicial_materiais_piso_laje = chave_inicial_materiais_piso_laje -1

        # Nome do projeto
        nome_projeto = projeto.get('informacoes_projeto').get('numero_projeto', 'NOME PROJETO')
        files = os.listdir('./outputs/')
        filename_tomax = [f'./outputs/{f}' for f in files if 'TOMAX' in f if str(nome_projeto) in f][0] # 2533_REAL_FINAL_TOMAX
        filename_tomin = [f'./outputs/{f}' for f in files if 'TOMIN' in f if str(nome_projeto) in f][0] # 2533_REAL_FINAL_TOMIN
        filename_phft = [f'./outputs/{f}' for f in files if 'PHFT' in f if str(nome_projeto) in f][0] # 2533_REAL_FINAL_PHFT
        filename_hvac = [f'./outputs/{f}' for f in files if 'HVAC_REDCGTTMINSUP' in f if str(nome_projeto) in f][0] # 2533_REAL_FINAL_HVAC_REDCGTTMINSUP
        
        # Verifica se os arquivos de imagem existem
        if not all([
            os.path.exists(filename_tomax),
            os.path.exists(filename_tomin),
            os.path.exists(filename_phft),
            os.path.exists(filename_hvac),
        ]):
            return dash.no_update, dmc.Alert(
                "Arquivos de imagem não encontrados. Verifique se os arquivos foram gerados corretamente.",
                color="red",
                icon=DashIconify(icon="material-symbols:warning-rounded"),
                withCloseButton=True,
            )

        else:

            now = datetime.now()
            mes_ano = now.strftime('%m/%Y')

            # Abrindo como pptx
            ppt = Presentation(f"upload/{lastUploadTaskRecord.get('taskId')}/{lastUploadTaskRecord.get('fileName')}")

            # Extraindo textos
            textos = extrair_textos(ppt)

            # Dicionário de substituições
            substituicoes_por_slide = {

                0: {
                    '[NOME EMPREENDIMENTO]': projeto.get('informacoes_projeto').get('nome_empreendimento', 'NOME EMPREENDIMENTO'),
                    '[MÊS]/[ANO]' : mes_ano,
                    "Ref.: PRJ[Nº DO PROJETO].[Nº DA PROPOSTA]": f"Ref.: PRJ{projeto.get('informacoes_projeto', {}).get('numero_projeto', 'Erro')}.{projeto.get('informacoes_projeto', {}).get('numero_proposta', 'Erro')}",
                    'indices_para_nao_mudar': [0, 1, 3],
                    'tipo': 'texto',
                    'tamanho_fonte': 20,
                    'color_fonte': 'white',
                    'bold': False,
                },

                2: {
                    '[NOME REQUISITANTE]': projeto.get('informacoes_projeto', {}).get('nome_requisitante', 'NOME REQUISITANTE'),
                    '[RUA REQ]': projeto.get('informacoes_projeto', {}).get('rua_requisitante', 'RUA REQ'),
                    '[Nº REQU]': projeto.get('informacoes_projeto', {}).get('numero_requisitante', 'Nº REQU'),
                    '[BAIRRO REQ]': projeto.get('informacoes_projeto', {}).get('bairro_requisitante', 'BAIRRO REQ'),
                    '[MUNICÍPIO REQ]': projeto.get('informacoes_projeto', {}).get('cidade_requisitante', 'MUNICÍPIO REQ'),
                    '[ESTADO REQ]': projeto.get('informacoes_projeto', {}).get('estado_requisitante', 'ESTADO REQ'),
                    '[CEP REQ]': projeto.get('informacoes_projeto', {}).get('cep_requisitante', 'CEP REQ'),
                    '[CNPJ REQ]': projeto.get('informacoes_projeto', {}).get('cnpj', 'CNPJ REQ'),
                    '[NOME REQUERENTE]': projeto.get('informacoes_projeto', {}).get('nome_requerente', 'NOME REQUERENTE'),
                    '[RUA EMPREENDIMENTO]': projeto.get('informacoes_projeto', {}).get('rua_empreendimento', 'RUA EMPREENDIMENTO'),
                    '[Nº EMP]': projeto.get('informacoes_projeto', {}).get('numero_empreendimento', 'Nº EMP'),
                    '[BAIRRO EMP]': projeto.get('informacoes_projeto', {}).get('bairro_empreendimento', 'BAIRRO EMP'),
                    '[MUNICÍPIO EMP]': projeto.get('informacoes_projeto', {}).get('cidade_empreendimento', 'MUNICÍPIO EMP'),
                    '[ESTADO EMP]': projeto.get('informacoes_projeto', {}).get('estado_empreendimento', 'ESTADO EMP'),
                    '[CEP EMP]': projeto.get('informacoes_projeto', {}).get('cep_empreendimento', 'CEP EMP'),
                    'indices_para_nao_mudar': [0, 1, 2],
                    'tipo': 'texto',
                    'tamanho_fonte': 18,
                    'color_fonte': 'black',
                    'bold': False,
                },

                3: {
                    '[NOME EMPREENDIMENTO]': projeto.get('informacoes_projeto', {}).get('nome_empreendimento', 'NOME EMPREENDIMENTO'),
                    '[NOME REQUISITANTE]': projeto.get('informacoes_projeto', {}).get('nome_requisitante', 'NOME REQUISITANTE'),
                    '[RUA EMPREENDIMENTO]': projeto.get('informacoes_projeto', {}).get('rua_empreendimento', 'RUA EMPREENDIMENTO'),
                    '[Nº EMP]': projeto.get('informacoes_projeto', {}).get('numero_empreendimento', 'Nº EMP'),
                    '[BAIRRO EMP]': projeto.get('informacoes_projeto', {}).get('bairro_empreendimento', 'BAIRRO EMP'),
                    '[MUNICÍPIO EMP]': projeto.get('informacoes_projeto', {}).get('cidade_empreendimento', 'MUNICÍPIO EMP'),
                    '[ESTADO EMP]': projeto.get('informacoes_projeto', {}).get('estado_empreendimento', 'ESTADO EMP'),
                    '[DESCRIÇÃO EMP]': projeto.get('informacoes_projeto', {}).get('descricao_empreendimento', 'DESCRIÇÃO EMP'),
                    '[Nº UNIDADES]': projeto.get('informacoes_projeto', {}).get('numero_unidades', 'Nº UNIDADES'),
                    '[MÊS]/[ANO]': projeto.get('informacoes_projeto', {}).get('data_acesso', 'MÊS/ANO'),
                    'indices_para_nao_mudar': [0, 1, 2, 4, 6, 7],
                    'tipo': 'texto',
                    'tamanho_fonte': 11,
                    'color_fonte': 'black',
                    'bold': False,
                },

                'link_entorno': {
                    'link de acesso': projeto.get('informacoes_projeto', {}).get('link_entorno', 'LINK DE ACESSO'),
                    'indices_para_nao_mudar': [0, 1, 2, 3, 4, 5, 6, 8],
                    'tipo': 'texto',
                    'tamanho_fonte': 11,
                    'color_fonte': 'black',
                    'bold': False,
                },

                5: {

                    '[ARQUIVOS RECEBIDOS]': projeto.get('checklists').get('arquivos_recebidos', 'ARQUIVOS RECEBIDOS')['comentario'].replace(',', '\n').replace(' ', ''),
                    '[Nº ZB], [REGIÃO]': f"{projeto.get('informacoes_projeto').get('zona_bioclimatica', 'ZONA BIOCLIMATICA')}/ {projeto.get('informacoes_projeto').get('regiao', 'REGIAO')}",
                    '[ARQUIVO CLIMÁTICO]': projeto.get('informacoes_projeto').get('arquivo_climatico', 'ARQUIVO CLIMATICO'),
                    'indices_para_nao_mudar': [0, 1, 3],
                    'tipo': 'texto',
                    'tamanho_fonte': 10.5,
                    'color_fonte': 'black',
                    'bold': False,
                },

                6: {

                    '[COR FACHADA 1]': projeto.get('cores').get('Fachada 1').get('nome'),
                    '[COR FACHADA 2]': projeto.get('cores').get('Fachada 2').get('nome'),
                    '[COR FACHADA 3]': projeto.get('cores').get('Fachada 3').get('nome'),
                    '[COR COBERTURA]': projeto.get('cores').get('Cobertura').get('cor_prox'),
                    '[COR PISO EXT]': projeto.get('cores').get('Piso externo').get('cor_prox'),
                    '[COR PAREDE INT]': projeto.get('cores').get('Parede interna').get('cor_prox'),
                    '[COR TETO]': projeto.get('cores').get('Teto').get('cor_prox'),
                    '[COR PISO]': projeto.get('cores').get('Piso').get('cor_prox'),
                    '[COR ENTORNO]': projeto.get('cores').get('Muro/fechamento').get('cor_prox'),
                    '[ABSF1]': projeto.get('cores').get('Fachada 1').get('abs_prox'),
                    '[ABSF2]': projeto.get('cores').get('Fachada 2').get('abs_prox'),
                    '[ABSF3]': projeto.get('cores').get('Fachada 3').get('abs_prox'),
                    '[ABSCOB]': projeto.get('cores').get('Cobertura').get('abs_prox'),
                    '[ABSPIEXT]': projeto.get('cores').get('Piso externo').get('abs_prox'),
                    '[ABS ENT]': projeto.get('cores').get('Muro/fechamento').get('abs_prox'),
                    '[ABSPAINT]': projeto.get('cores').get('Parede interna').get('abs_prox'),
                    '[ABSTETO]': projeto.get('cores').get('Teto').get('abs_prox'),
                    '[ABSPIINT]': projeto.get('cores').get('Piso').get('abs_prox'),
                    '58%': '    58.00',
                    '65%': '    65.00',
                    'indices_para_nao_mudar': [0],
                    'tipo': 'tabela',
                    'tamanho_fonte': 11,
                    'with_pct': False,
                },

                24: {

                    'tipo': 'figura',
                    'filename': f'{filename_tomax}',
                    'largura': 29,
                    'altura': 9,
                    'indices_para_nao_mudar': [],
                },

                25: {

                    'tipo': 'figura',
                    'filename': f'{filename_tomin}',
                    'largura': 29,
                    'altura': 9,
                    'indices_para_nao_mudar': [],
                },

                26: {

                    'tipo': 'figura',
                    'filename': f'{filename_phft}',
                    'largura': 29,
                    'altura': 9,
                    'indices_para_nao_mudar': [],
                },

                27: {

                    'tipo': 'figura',
                    'filename': f'{filename_hvac}',
                    'largura': 29,
                    'altura': 9,
                    'indices_para_nao_mudar': [],
                },

            }

            ####################################### ESQUADRIAS ########################################
            esquadrias = pd.DataFrame(projeto.get('esquadrias')).transpose()
            esquadrias = esquadrias.sort_values(by='index')
            esquadrias['Tipo de vidro'] = esquadrias['Tipo de vidro'].apply(lambda d: d.get('value') if isinstance(d, dict) and 'value' in d else d)
            esquadrias['Tipo de janela'] = esquadrias['Tipo de janela'].apply(lambda d: d.get('value') if isinstance(d, dict) and 'value' in d else d)
            limite = 5  # Quantidade máxima por chave

            # Divida os itens em lotes das esquadrias
            for i in range(0, len(esquadrias), limite):
                # Defina o índice para a nova chave
                chave = chave_inicial_esquadrias
                substituicoes_por_slide[chave] = {
                    **{f'[INDICADOR{x+1}]': esquadrias['Indicador'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Indicador'])))},
                    **{f'[TIPO DE ESQUADRIA{x+1}]': esquadrias['Tipo de janela'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Tipo de janela'])))},
                    **{f'[TIPO DE VIDRO{x+1}]': esquadrias['Tipo de vidro'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Tipo de vidro'])))},
                    **{f'[FS{x+1}]': esquadrias['Fator solar'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Fator solar'])))},
                    **{f'[TL{x+1}]': esquadrias['Trânsmitancia luminosa'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Trânsmitancia luminosa'])))},
                    **{f'[UV{x+1}]': esquadrias['Trânsmitancia térmica [W/(m²K)]'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Trânsmitancia térmica [W/(m²K)]'])))},
                    **{f'[COR CAIXILHO{x+1}]': esquadrias['Cor do caixilho'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Cor do caixilho'])))},
                    **{f'[CA{x+1}]': esquadrias['Coeficiente de abertura'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Coeficiente de abertura'])))},
                    **{f'[CV{x+1}]': esquadrias['Coeficiente de vidro'].iloc[x] for x in range(i, min(i + limite, len(esquadrias['Coeficiente de vidro'])))},
                    **{
                        f'[LV{x+1}] x [HV{y+1}] x [PV{z+1}]': 
                        f"{esquadrias['Largura [m]'].iloc[x]} x {esquadrias['Altura [m]'].iloc[y]} x {esquadrias['Parapeito [m]'].iloc[z]}"
                        for x, y, z in zip(
                            range(i, min(i + limite, len(esquadrias['Largura [m]']))),
                            range(i, min(i + limite, len(esquadrias['Altura [m]']))),
                            range(i, min(i + limite, len(esquadrias['Parapeito [m]'])))
                        )
                    },
                    'indices_para_nao_mudar': [],
                    'tipo': 'tabela',
                    'tamanho_fonte': 11,
                    'with_pct': False,

                }
                chave_inicial_esquadrias += 1 

            ######################################## AMBIENTES ########################################
            ambientes = pd.DataFrame(projeto.get('ambientes')).transpose()
            ambientes = ambientes.explode('esquadrias', ignore_index=False)
            ambientes['Coeficiente de abertura'] = ambientes['esquadrias'].apply(lambda x: esquadrias[esquadrias['Indicador'] == x]['Coeficiente de abertura'].values[0] if len(esquadrias[esquadrias['Indicador'] == x]['Coeficiente de abertura'].values) > 0 else None)
            ambientes_grouped = ambientes.reset_index().rename(columns={'index': 'ambiente_index'}).groupby('ambiente_index')['esquadrias'].count().reset_index(name='quantidade_esquadrias')
            limite_ambientes = 10  # Quantidade máxima por chave

            # Divida os itens em lotes dos ambientes
            for i in range(0, len(ambientes), limite_ambientes):

                chave = chave_inicial_ambientes
                substituicoes_por_slide[chave] = {
                    **{f'[TORRE/CASA{x+1}]': ambientes['torre_casa'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['torre_casa'])))},
                    **{f'[PAV{x+1}]': ambientes['pavimento'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['pavimento'])))},
                    **{f'[UH{x+1}]': ambientes['unidade'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['unidade'])))},
                    **{f'[AMBIENTE{x+1}]': ambientes['ambiente'].iloc[x].title() for x in range(i, min(i + limite_ambientes, len(ambientes['ambiente'])))},
                    **{f'[ÁREA AMB{x+1}]': ambientes['area_ambiente'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['area_ambiente'])))},
                    **{f'[Nº ESQ POR AMBIENTE{x+1}]': ambientes_grouped['quantidade_esquadrias'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes_grouped['ambiente_index'])))},
                    **{f'[INDICADOR{x+1}]': ambientes['esquadrias'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['esquadrias'])))},
                    **{f'[SIM/NÃOV{x+1}]': ambientes['situacao_abertura_ventilacao'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['situacao_abertura_ventilacao'])))},
                    **{f'[SIM/NÃOT{x+1}]': ambientes['situacao_elementos_transparentes'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['situacao_elementos_transparentes'])))},
                    **{f'[CA{x+1}]': ambientes['Coeficiente de abertura'].iloc[x] for x in range(i, min(i + limite_ambientes, len(ambientes['Coeficiente de abertura'])))},
                    **{
                        f'[LADO{x+1}] x [LADO{y+1}]': 
                        f"{round(ambientes['lado_maior2'].iloc[x], 2)} x {round(ambientes['lado_menor2'].iloc[x], 2)}"
                        for x, y in zip(
                            range(i, min(i + limite_ambientes, len(ambientes['lado_maior2']))),
                            range(i, min(i + limite_ambientes, len(ambientes['lado_menor2']))),
                        )
                    },
                    'indices_para_nao_mudar': [],
                    'tipo': 'tabela',
                    'tamanho_fonte': 9,
                    'with_pct': False,
                }
                
                chave_inicial_ambientes += 1 

            ####################################### MATERIAIS PAREDE EXTERNA ########################################
            substituicoes_por_slide[chave_inicial_materiais_parede_externa] = ajusta_materiais('Parede externa', projeto)

            ######################################### MATERIAIS PAREDE INTERNA ########################################
            substituicoes_por_slide[chave_inicial_materiais_parede_interna] = ajusta_materiais('Parede interna', projeto)

            ############################################ MATERIAIS COBERTURA ########################################
            substituicoes_por_slide[chave_inicial_materiais_cobertura] = ajusta_materiais('Cobertura edifício', projeto)

            ############################################# MATERIAIS PISO/LAJE ########################################
            substituicoes_por_slide[chave_inicial_materiais_piso_laje] = ajusta_materiais('Piso (laje)', projeto)

            # Montando o relatório
            for slide in substituicoes_por_slide.keys():

                if slide == 'link_entorno':
                    slide = 3
                    key_slide = 'link_entorno'

                else:
                    key_slide = int(slide)
                    slide = int(slide)

                text_slide = [text[2] for text in textos if text[0] == slide]
                texto_antigo = [text[2] for text in textos if text[0] == slide]
                tables = get_tables_as_dataframes(ppt, slide)

                # Verifica se há substituições para este slide
                if slide in substituicoes_por_slide or key_slide in substituicoes_por_slide:
                    substituicoes = substituicoes_por_slide[key_slide]

                    text_slide = [v for i, v in enumerate(text_slide) if i not in substituicoes['indices_para_nao_mudar']]
                    texto_antigo = [v for i, v in enumerate(texto_antigo) if i not in substituicoes['indices_para_nao_mudar']]
                    tables = [v for i, v in enumerate(tables) if i not in substituicoes['indices_para_nao_mudar']]
                    substituicoes.pop('indices_para_nao_mudar')
                    
                    if substituicoes['tipo'] == 'tabela':

                        # Aplica as substituições nas tabelas para o slide específico
                        for shape, df in tables:
                            edited_df = df.copy()
                            edited_df = substituir_valores_df(df, substituicoes, with_pct=substituicoes['with_pct'])
                            update_table(shape, edited_df, substituicoes['tamanho_fonte'])

                    elif substituicoes['tipo'] == 'texto':

                        # Aplica as substituições para o slide específico
                        for t, t_antigo in zip(text_slide, texto_antigo):
                            for placeholder, novo_valor in substituicoes.items():
                                t = t.replace(str(placeholder), str(novo_valor))

                            if key_slide == 'link_entorno':
                                ppt = alterar_texto(ppt, slide, t_antigo, t, font_size=substituicoes['tamanho_fonte'], color_fonte=substituicoes['color_fonte'], bold=substituicoes['bold'], hyper_link=True)
                            else:
                                ppt = alterar_texto(ppt, slide, t_antigo, t, font_size=substituicoes['tamanho_fonte'], color_fonte=substituicoes['color_fonte'], bold=substituicoes['bold'])

                    elif substituicoes['tipo'] == 'figura':

                        filename = substituicoes['filename']
                        adicionar_imagem_com_proporcao(ppt, slide, filename)

            # Salvar o arquivo modificado em memória
            modified_stream = io.BytesIO()
            ppt.save(modified_stream)
            modified_stream.seek(0)

            return dcc.send_bytes(modified_stream.read(), f"apresentacao_modificada_{nome_projeto}.pptx"), dmc.Alert(
                "Apresentação gerada com sucesso!",
                color="green",
                icon=DashIconify(icon="material-symbols:check"),
                withCloseButton=True,
            )

    except Exception as e:
        print(e)
        return dash.no_update, dash.no_update #dmc.Alert(e, color="red",withCloseButton=True)

####################################################################################################################################################################