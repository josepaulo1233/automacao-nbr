import dash_mantine_components as dmc
from dash import html

####################################################################################################################################################################

def checklist_form(checklists: dict):

    opcoes_checklist = ['sim', 'nao', 'n/a']

    # Agrupamento das seções principais
    secoes = {
        "Ficha de confirmação de dados (Google forms)": [
            'arquivos_recebidos',
            'informacoes_administrativas',
            'completamente_preenchido'
        ],
        "Implantação em .dwg": [
            'norte',
            'Endereço_da_obra',
            'Indicação_de_cortes',
            'Indicação_da_topografia,_caso_o_projeto_esteja_em_desnível',
            'Posição_do_terreno_no_tecido_urbano_(indicação das ruas)',
        ],
        "Plantas em .dwg": [
            'Desenho_das_unidades_habitacionais_com_paredes_internas',
            'Desenho_de_janelas_e_portas',
            'Nome_dos_ambientes_se_houver',
            'Numeracao_das_unidades_habitacionais_se_houver',
            'Indicacao_de_muros_barrilete_parapeitos_e_respectivas_alturas'
        ],
        "Cortes em .dwg": [
            'Altura_do_pe_direito_laje_a_laje',
            'Altura_do_barrilete',
            'Altura_do_peitoril_se_houver',
            'Indicacao_dos_niveis'
        ],
        "Fachadas em .dwg": [
            'Cores_e_caso_exista_absortancia_externa_do_fornecedor_de_tintas',
            'Nome_de_materiais',
            'Dimensoes_de_aberturas_portas_e_janelas',
            'Altura_de_guarda_corpo_caso_possuam_varanda'
        ],
        "Outros": [
            'Lista_de_portas_e_janelas_com_dimensoes'
        ]
    }

    # Função auxiliar para criar o conteúdo de cada seção
    def criar_coluna(titulo_secao, itens):
        children = []
        for titulo in itens:
            if titulo not in checklists:
                continue

            titulo_fmt = titulo.replace('_', ' ').capitalize()
            value_recebido = checklists[titulo].get('recebido', '')
            value_comentario = checklists[titulo].get('comentario', '')

            radio = dmc.RadioGroup(
                value=value_recebido,
                children=[dmc.Radio(opt.upper(), value=opt) for opt in opcoes_checklist],
                id={'type': 'confirmacao_dados', 'index': titulo},
                size="xs",

            )

            comentario = dmc.Textarea(
                value=value_comentario,
                id={'type': 'comentario_confirmacao_dados', 'index': titulo},
                autosize=True,
                minRows=1,
                maxRows=2,
                size="xs"
            )

            item = dmc.Stack([
                dmc.Text(titulo_fmt, fw=500, size="sm", style={"marginBottom": "4px"}),
                radio,
                comentario,
                dmc.Divider(my=8)
            ])
            children.append(item)

        return dmc.Paper(
            [
                dmc.Title(titulo_secao, order=4,  mb=10,),
                html.Div(children)
            ],
            shadow="sm",
            radius="md",
            p="md",
            style={
                "backgroundColor": "#f9fdf9",
                "border": "1px solid #d4ede0",
                "minHeight": "100%",
            }
        )

    # Criar colunas (cada seção é uma coluna)
    colunas = []
    for titulo_secao, itens in secoes.items():
        colunas.append(
            dmc.GridCol(
                criar_coluna(titulo_secao, itens),
                span="auto",  # Mantém responsivo
                style={"minWidth": "260px"}
            )
        )

    layout = dmc.Grid(
        colunas,
        gutter="xl",
        justify="space-around",
        style={"overflowX": "auto", "padding": "10px"}
    )

    return layout

####################################################################################################################################################################