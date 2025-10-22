import feffery_antd_components as fac
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
# from utils.informacoes import ambientes
from projetos.forms_ambientes import ambientes_form
from projetos.forms_cores import cores_form
from projetos.forms_checklist import checklist_form
from projetos.forms_infosprojeto import informacoes_projeto_form
# from projetos.forms_esquadrias_dashtable import esquadrias_form
from projetos.forms_esquadrias_factable import esquadrias_form
from projetos.forms_materiais import materiais_form
from projetos.forms_organizatxt import forms_organiza_txt
from projetos.forms_analise import forms_analise
from utils.styles import *

####################################################################################################################################################################

tabs = ['Projeto', 'Checklist', 'Cores', 'Materiais', 'Esquadrias', 'Ambientes', 'Status', 'Organiza txt', 'Análise e resultados']
tab_icons = {
    'Projeto': 'folder-open',
    'Checklist': 'check-circle',
    'Cores': 'highlight',
    'Materiais': 'table',
    'Esquadrias': 'swap',
    'Ambientes': 'home',
    'Status': 'check',
    'Organiza txt': 'clear',
    'Análise e resultados': 'bar-chart'
}

####################################################################################################################################################################

class Projeto():

    def __init__(self,
                informacoes_projeto,
                checklists,
                cores,  
                esquadrias,     
                materiais,
                ambientes,
                status,
                usuario
               ):

        self.informacoes_projeto = informacoes_projeto
        self.checklists = checklists
        self.cores = cores
        self.esquadrias = esquadrias
        self.materiais = materiais
        self.ambientes = ambientes
        self.status = status
        self.usuario = usuario

    ####################################################################################################################################################################

    def exibir_infos(self):
        
        # Informações do projeto
        conteudo_projeto = informacoes_projeto_form(self.informacoes_projeto)

        ##########################################################################################################

        # Checklists informações adms
        checklists_administrativos = checklist_form(self.checklists)
        conteudo_checklist = html.Div([

            html.H5('Checklist de recebimento', className='mb-4'),

            dbc.Row([

                dbc.Col([

                    dmc.Divider(),
                    html.Div(checklists_administrativos, style={'margin-top': '5px'})

                ], width=12),

            ], justify='center')

        ])

        ##########################################################################################################

        # Cores
        conteudo_cores = cores_form(self.cores)

        ##########################################################################################################

        # Esquadrias
        conteudo_esquadrias = esquadrias_form(self.esquadrias)

        ##########################################################################################################

        # Materiais
        conteudo_materiais = materiais_form(self.materiais)

        ##########################################################################################################

        # Ambientes
        conteudo_ambientes = ambientes_form(self.ambientes)

        ##########################################################################################################

        # Status
        conteudo_status =  html.Div([
            dmc.RadioGroup(
                id='status_projeto',
                value=self.status,
                my=10,
                size='sm',
                label="Status do projeto",
                description="Selecione o status do projeto",
                children=dmc.Group([
                    dmc.Radio(value="Incompleto", label="Incompleto"),
                    dmc.Radio(value="Finalizado", label="Finalizado"),
                    dmc.Radio(value="Cancelado", label="Cancelado"),
                ], my=10),
            )
        ])

        ##########################################################################################################

        # Organiza txt
        conteudo_txt = forms_organiza_txt()

        ##########################################################################################################

        # Análise e resultados
        conteudo_analise = forms_analise()

        ##########################################################################################################

        # Conteudos
        tabs_content = {
            'Projeto': conteudo_projeto,
            'Checklist': conteudo_checklist,
            'Cores': conteudo_cores,
            'Esquadrias': conteudo_esquadrias,
            'Materiais': conteudo_materiais,
            'Ambientes': conteudo_ambientes,
            'Status': conteudo_status,
            'Organiza txt': conteudo_txt,
            'Análise e resultados': conteudo_analise
        }

        ##########################################################################################################

        # Tabs
        conteudo = dmc.MantineProvider(
            
            html.Div([

                dmc.Button(
                    'Salvar projeto',
                    id='enviar-banco-btn',
                    color='green',
                    radius='md',
                    variant='filled',
                    fullWidth=True,
                    style={'margin-bottom': '10px', 'border': '2px solid black'}
                ),

                
                # Colocando um disclamaimer de que o decimal separator é ponto
                dmc.Alert("Atenção: O separador decimal é o ponto (.)", color="yellow", variant="filled", radius="md", mb=10),

                fac.AntdDivider(),

                fac.AntdTabs(
                    # type='card',
                    centered=True,
                    tabBarGutter=60,
                    items=[
                        {
                            'key': f'tab{tab}',
                            'label': f'{tab}',
                            'icon': fac.AntdIcon(icon=f'antd-{tab_icons.get(tab, "question-circle")}'),
                            'children': tabs_content[tab]
                        }

                        for tab in tabs if tab in tabs_content
                    ]
                )           

        ]))

        return conteudo
    
    ####################################################################################################################################################################

####################################################################################################################################################################
