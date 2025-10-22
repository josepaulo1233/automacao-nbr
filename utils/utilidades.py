import requests
from utils.styles import *
import numpy as np
from utils.informacoes import *

##########################################################################################################

def buscar_rua_por_cep(cep: str) -> dict:
    # Remove caracteres não numéricos do CEP
    cep = ''.join(filter(str.isdigit, cep))
    
    # Verifica se o CEP tem 8 dígitos
    if len(cep) != 8:
        return "CEP inválido. Deve conter 8 dígitos."

    # URL da API ViaCEP
    url = f"https://viacep.com.br/ws/{cep}/json/"
    
    # Faz a requisição GET
    response = requests.get(url)
    
    # Verifica o status da requisição
    if response.status_code == 200:
        dados = response.json()
        
        # Verifica se o CEP foi encontrado
        if "erro" not in dados:

            # Retorna o endereço formatado
            return dados
        else:
            return "CEP não encontrado."
    else:
        return "Erro na requisição."
    
##########################################################################################################

def abs_mais_prox(R, G, B, Rs, Gs, Bs, Nomes, abs_fosca, abs_semibrilho, latex_pvafosca, acrilica_fosca, latex_pvafoscaII):
    
    my_color_R = R
    my_color_G = G
    my_color_B = B

    if my_color_R > 255 or my_color_G > 255 or my_color_B > 255:

        print ('Confira os valores... Precisam ser menores do que 255')

        return

    dif_colors_R = []
    dif_colors_G = []
    dif_colors_B = []

    for numero in Rs:

        if numero > 255:

            print ('Confira os valores de R, precisam ser menores do que 255')
            return

        else:

            dif_colors_R.append((my_color_R - numero)**2)

    for numero in Gs:

        if numero > 255:

            print ('Confira os valores de G, precisam ser menores do que 255')
            return

        else:

            dif_colors_G.append((my_color_G - numero)**2)

    for numero in Bs:

        if numero > 255:

            print ('Confira os valores de B, precisam ser menores do que 255')
            return

        else:

            dif_colors_B.append((my_color_B - numero)**2)

    soma = np.sum([dif_colors_R, dif_colors_G, dif_colors_B], axis=0)

    raiz_da_soma = np.sqrt(soma)

    index_min = np.argmin(raiz_da_soma)

    rgb = [Rs[index_min], Gs[index_min], Bs[index_min]]

    cor_mais_proxima = Nomes[index_min]
    R_mais_proximo = rgb[0]
    G_mais_proximo = rgb[1]
    B_mais_proximo = rgb[2]
    absortancia_media = np.nanmean([
        abs_fosca[index_min], 
        abs_semibrilho[index_min], 
        latex_pvafosca[index_min], 
        acrilica_fosca[index_min],
        latex_pvafoscaII[index_min],
    ])
    Absortancia_media = absortancia_media

    return cor_mais_proxima, Absortancia_media

####################################################################################################################################################################

def calc_largura_folhas_de_vidro(largura, numero_molduras, espessura_molduras, divisores_verticais, espessura_divisores, folhas_vidro_horizontais):

    largura = float(largura)
    numero_molduras = float(numero_molduras)
    espessura_molduras = float(espessura_molduras)
    divisores_verticais = float(divisores_verticais)
    espessura_divisores = float(espessura_divisores)
    folhas_vidro_horizontais = float(folhas_vidro_horizontais)

    calculo = (largura - (numero_molduras*espessura_molduras) - (divisores_verticais*espessura_divisores))/folhas_vidro_horizontais

    return calculo

#####################################################################################

def calc_altura_folhas_de_vidro(altura, numero_molduras, espessura_molduras, divisores_horizontais, espessura_divisores, folhas_vidro_verticais):

    altura = float(altura)
    numero_molduras = int(numero_molduras)
    espessura_molduras = float(espessura_molduras)
    divisores_horizontais = int(divisores_horizontais)
    espessura_divisores = float(espessura_divisores)
    folhas_vidro_verticais = int(folhas_vidro_verticais)

    calculo = (altura - (numero_molduras*espessura_molduras) - (divisores_horizontais*espessura_divisores))/folhas_vidro_verticais

    return calculo

#####################################################################################

def calc_area(largura, altura):

    largura = float(largura)
    altura = float(altura)

    return largura*altura

#####################################################################################

def calc_area_total_vidro(folhas_vidro_vertical, folhas_vidro_horizontal, qtade_folha_vertical, qtade_folha_horizontal):

    folhas_vidro_vertical = float(folhas_vidro_vertical)
    folhas_vidro_horizontal = float(folhas_vidro_horizontal)
    qtade_folha_vertical = float(qtade_folha_vertical)
    qtade_folha_horizontal = float(qtade_folha_horizontal)
    
    return folhas_vidro_vertical*folhas_vidro_horizontal*qtade_folha_vertical*qtade_folha_horizontal

#####################################################################################

