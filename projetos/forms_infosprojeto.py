from dash import callback, Input, Output
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from utils.utilidades import buscar_rua_por_cep
from dash import html
import feffery_antd_components as fac
from datetime import datetime
from utils.styles import input_classnames, number_input_classnames, select_classnames

####################################################################################################################################################################

def informacoes_projeto_form(informacoes_projeto: dict):
    
    # Infos do projeto
    infos_projeto = [
        dmc.NumberInput(label="Número do Projeto", value=informacoes_projeto.get('numero_projeto'), classNames=number_input_classnames, id="numero_projeto"),
        dmc.TextInput(label="Nome do Projeto", value=informacoes_projeto.get('nome_projeto'), classNames=input_classnames, id="nome_projeto"),
        dmc.NumberInput(label="Número da Proposta", value=informacoes_projeto.get('numero_proposta'), classNames=number_input_classnames, id="numero_proposta"),
        dmc.TextInput(label="Nome Requerente", value=informacoes_projeto.get('nome_requerente'), classNames=input_classnames, id="nome_requerente"),
        dmc.NumberInput(label="Número de Unidades", value=informacoes_projeto.get('numero_unidades'), classNames=number_input_classnames, id="numero_unidades"),
        dmc.NumberInput(label="CNPJ", value=informacoes_projeto.get('cnpj'), classNames=number_input_classnames, id="cnpj"),
        dmc.NumberInput(label="Zona bioclimática", value=informacoes_projeto.get('zona_bioclimatica'), classNames=number_input_classnames, id="zona_bioclimatica", min=1, max=8),
        dmc.Select(label="Região", data=['Norte', 'Nordeste', 'Sudeste', 'Sul'], value=informacoes_projeto.get('regiao'), classNames=select_classnames, id="regiao"),
        dmc.TextInput(label="Arquivo climátio", value=informacoes_projeto.get('arquivo_climatico'), classNames=input_classnames, id="arquivo_climatico", description="Ex: arquivo_climatico.epw"),

    ]

    # Infos pro empreendimento
    infos_empreendimento = [
        dmc.TextInput(label="Nome do Empreendimento", value=informacoes_projeto.get('nome_empreendimento'), classNames=input_classnames, id="nome_empreendimento"),
        dmc.TextInput(label="CEP Empreendimento", value=informacoes_projeto.get('cep_empreendimento'), classNames=input_classnames, id="cep_empreendimento"),
        dmc.TextInput(label="Link do Entorno", value=informacoes_projeto.get('link_entorno'), classNames=input_classnames, id="link_entorno"),
        dmc.Anchor("Clique para ver o entorno", href=informacoes_projeto.get('link_entorno', '#'), target="_blank", id="anchor_link_entorno"), 
        dmc.TextInput(label="Rua do Empreendimento", value=informacoes_projeto.get('rua_empreendimento'), classNames=input_classnames, id="rua_empreendimento"),
        dmc.TextInput(label="Bairro do Empreendimento", value=informacoes_projeto.get('bairro_empreendimento'), classNames=input_classnames, id="bairro_empreendimento"),
        dmc.TextInput(label="Cidade do Empreendimento", value=informacoes_projeto.get('cidade_empreendimento'), classNames=input_classnames, id="cidade_empreendimento"),
        dmc.TextInput(label="Estado do Empreendimento", value=informacoes_projeto.get('estado_empreendimento'), classNames=input_classnames, id="estado_empreendimento"),
        dmc.TextInput(label="Complemento do Empreendimento", value=informacoes_projeto.get('complemento_empreendimento'), classNames=input_classnames, id="complemento_empreendimento"),
        dmc.TextInput(label="Número do Empreendimento", value=informacoes_projeto.get('numero_empreendimento'), classNames=input_classnames, id="numero_empreendimento"),
        dmc.TextInput(label='Data de acesso', value=informacoes_projeto.get('data_acesso', datetime.now().strftime("%m/%Y")), classNames=input_classnames, id="data_acesso"),
    ]
    
    # Infos do requisitante
    infos_requisitante = [
        dmc.TextInput(label="Nome do requisitante", value=informacoes_projeto.get('nome_requisitante'), classNames=input_classnames, id="nome_requisitante"),
        dmc.TextInput(label="CEP requisitante", value=informacoes_projeto.get('cep_requisitante'), classNames=input_classnames, id="cep_requisitante"),
        dmc.TextInput(label="Rua do requisitante", value=informacoes_projeto.get('rua_requisitante'), classNames=input_classnames, id="rua_requisitante"),
        dmc.TextInput(label="Bairro do requisitante", value=informacoes_projeto.get('bairro_requisitante'), classNames=input_classnames, id="bairro_requisitante"),
        dmc.TextInput(label="Cidade do requisitante", value=informacoes_projeto.get('cidade_requisitante'), classNames=input_classnames, id="cidade_requisitante"),
        dmc.TextInput(label="Estado do requisitante", value=informacoes_projeto.get('estado_requisitante'), classNames=input_classnames, id="estado_requisitante"),
        dmc.TextInput(label="Complemento do requisitante", value=informacoes_projeto.get('complemento_requisitante'), classNames=input_classnames, id="complemento_requisitante"),
        dmc.NumberInput(label="Número do requisitante", value=informacoes_projeto.get('numero_requisitante'), classNames=number_input_classnames, id="numero_requisitante")
    ]

    # Layout do projeto
    conteudo_projeto = html.Div([
        dbc.Row([
            dbc.Col([
                html.H5('Informações do projeto'),
                fac.AntdDivider(),
                dmc.Paper(withBorder=True, shadow="sm", p="md", radius="md", children=infos_projeto),
                # html.Div(infos_projeto, style={'margin-top': '5px'})
            ], width=4),
            dbc.Col([
                html.H5('Informações do empreendimento'),
                fac.AntdDivider(),
                dmc.Paper(withBorder=True, shadow="sm", p="md", radius="md", children=infos_empreendimento),
                # html.Div(infos_empreendimento, style={'margin-top': '5px'})
            ], width=4),
            dbc.Col([
                html.H5('Informações do requisitante'),
                fac.AntdDivider(),
                dmc.Paper(withBorder=True, shadow="sm", p="md", radius="md", children=infos_requisitante),
                # html.Div(infos_requisitante, style={'margin-top': '5px'})
            ], width=4)
        ], justify='center')
    ])

    return conteudo_projeto

####################################################################################################################################################################

@callback(
    Output('anchor_link_entorno', 'href'),
    Input('link_entorno', 'value')
)
def update_link_entorno(link):
    if link:
        return link
    return '#'

# @callback(
#     Output('rua_empreendimento', 'value'),   
#     Output('bairro_empreendimento', 'value'),
#     Output('cidade_empreendimento', 'value'),
#     Output('estado_empreendimento', 'value'),
#     Input('cep_empreendimento', 'value')
# )
# def completa_cep_empreendimento(cep):

#     infos = buscar_rua_por_cep(cep)
#     return infos.get('logradouro', ''), infos.get('bairro', ''), infos.get('localidade', ''), infos.get('uf', '')

# ##########################################################################################################

# @callback(
#     Output('rua_requisitante', 'value'),
#     Output('bairro_requisitante', 'value'), 
#     Output('cidade_requisitante', 'value'),
#     Output('estado_requisitante', 'value'),
#     Input('cep_requisitante', 'value')
# )
# def completa_cep_requisitante(cep):

#     infos = buscar_rua_por_cep(cep)
#     return infos.get('logradouro', ''), infos.get('bairro', ''), infos.get('localidade', ''), infos.get('uf', '')

# ##########################################################################################################