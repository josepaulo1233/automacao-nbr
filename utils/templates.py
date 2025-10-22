from datetime import datetime
import numpy as np

####################################################################################################################################################################

checklists = {

    'informacoes_administrativas' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'completamente_preenchido': {

        'recebido': 'nao',
        'comentario': 'N/A'
        
    },

    'arquivos_recebidos': {

        'recebido': 'nao',
        'comentario': 'Arquivo1, Arquivo2, Arquivo3',   
    },

    'norte' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'Posição_do_terreno_no_tecido_urbano_(indicação das ruas)' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'Endereço_da_obra' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'Indicação_de_cortes' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'Indicação_da_topografia,_caso_o_projeto_esteja_em_desnível' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'Desenho_das_unidades_habitacionais_com_paredes_internas' : {

        'recebido': 'nao',
        'comentario': 'N/A'

    },

    'Desenho_de_janelas_e_portas': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Nome_dos_ambientes_se_houver': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Numeracao_das_unidades_habitacionais_se_houver': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Indicacao_de_muros_barrilete_parapeitos_e_respectivas_alturas': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Altura_do_pe_direito_laje_a_laje': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Altura_do_barrilete': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Altura_do_peitoril_se_houver': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Indicacao_dos_niveis': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Cores_e_caso_exista_absortancia_externa_do_fornecedor_de_tintas': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Nome_de_materiais': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Dimensoes_de_aberturas_portas_e_janelas': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Altura_de_guarda_corpo_caso_possuam_varanda': {
        'recebido': 'nao',
        'comentario': 'N/A'
    },

    'Lista_de_portas_e_janelas_com_dimensoes': {
        'recebido': 'nao',
        'comentario': 'N/A'
    }

}

cores = {

    'numero_pavimentos': 2,
    'pe_direito': 1,

    'Fachada 1': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',

    },

    'Fachada 2': {

        'nome': 'Outro',
        'r':0,
        'g':0,
        'b':0,
        'cor_prox':'Preto',
        'abs_prox':'97.25',
    },

    'Fachada 3': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',

    },

    'Parede interna': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Piso': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Teto ou forro': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Cobertura': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Piso da varanda': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Piso externo': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Elemento de sombreamento': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

    'Muro/fechamento': {

        'nome': 'Alecrim',
        'r':168,
        'g':182,
        'b':172,
        'cor_prox':'Alecrim',
        'abs_prox':'64',
        
    },

}

informacoes_projeto = {
    
    "numero_projeto": 123,
    "nome_projeto": "Projeto Teste",
    "numero_proposta": 456,
    "nome_requerente": "João Silva",
    "numero_unidades": 10,
    "cnpj": "12345678000199",
    "nome_empreendimento": "Empreendimento X",
    "cep_empreendimento": "03177010",
    "link_entorno": "https://exemplo.com",
    "nome_requisitante": 'Mitsid',
    'cep_requisitante': '03177010',
    'zona_bioclimatica': 1,
    'regiao': 'Norte',
    'data_acesso': datetime.now().strftime("%m/%Y"),
}

esquadrias = {

    0: {

        'index': 0,
        'Indicador': 'indicador1',
        'Divisores verticais': 7,
        'Largura [m]': 5,
        'Altura [m]': 9,
        'Parapeito [m]': 9,
        'Número de molduras': 2,
        'Espessura da moldura [m]': 3,
        'Tipo de vidro': 'Vidro Duplo Teste',
        'Divisores horizontais': 6,
        'Espessura dos divisores [m]': 7,
        'Folhas de vidro na horizontal': 10,
        'Folhas de vidro na vertical': 11,
        'Tipo de janela': 'Abrir 1 folha',
        'Coeficiente de abertura': 0.9,
        'Coeficiente de vidro': 0.9,
        'Cor do caixilho': np.nan,
        'Trânsmitancia luminosa': np.nan,
        'Trânsmitancia térmica [W/(m²K)]': np.nan,
        'Fator solar': np.nan,
        'Área [m²]': np.nan,
        'Largura das folhas de vidro [m]': np.nan,
        'Altura das folhas de vidro [m]': np.nan,
        'Área total do vidro [m²]': np.nan
    },

}

materiais = {

    'Parede externa': {

        1: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        2: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        'R total': 0.2,
        'CT': 1.4,
        'U': 4.6,
        'Criterio': 'Não aplicado'

    }, 

    'Parede interna': {

        1: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        2: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        'R total': 0.2,
        'CT': 1.4,
        'U': 4.6,
        'Criterio': 'Não aplicado'

    }, 

    'Cobertura edifício': {

        1: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        2: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6

        },

        'R total': 0.2,
        'CT': 1.4,
        'U': 4.6,
        'Criterio': 'Não aplicado'


    }, 

    'Piso (laje)': {

        1: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        2: {

            'Tipo do material': 'Gelo a 0ºC',
            'Espessura [m]': 1,
            'Resistência [m²K/W]': 0.1,
            'Calor específico [kJ/(kgK)]': 4.18,
            'Densidade [kg/m³]': 1000,
            'Condutividade [W/mK]': 0.6
        },

        'R total': 0.2,
        'CT': 1.4,
        'U': 4.6,
        'Criterio': 'Não aplicado'

    }, 

}

ambientes = {

    'ambiente1': {

        'torre_casa': 'Padrão',
        'pavimento': 'Terreo',
        'unidade': 'UHX',
        'ambiente': 'sala',
        'area_ambiente': 10,
        'esquadrias': [],
        'qtdade_esquadrias':[{'esquadrias': 'indicador1', 'quantidade': 1}],
    },

    'ambiente2': {

        'torre_casa': 'Padrão',
        'pavimento': 'Terreo',
        'unidade': 'UHX',
        'ambiente': 'sala',
        'area_ambiente': 20,
        'esquadrias': [],   
        'qtdade_esquadrias': [{'esquadrias': 'indicador1', 'quantidade': 1}],
    },

}

status = 'Incompleto'

dados_projeto = {
    'informacoes_projeto': informacoes_projeto,
    'checklists': checklists,
    'cores': cores,
    'esquadrias': esquadrias,
    'materiais': materiais,
    'ambientes': ambientes,
    'status': status,
    'usuario': 'test-dev',
}

####################################################################################################################################################################