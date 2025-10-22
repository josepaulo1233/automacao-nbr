coeficientes_janela = {
    "Abrir 1 folha": {"Coef. De vidro": 0.9, "Coef de abertura": 0.9},
    "Abrir 2 folhas": {"Coef. De vidro": 0.9, "Coef de abertura": 0.9},
    "Correr 2 folhas": {"Coef. De vidro": 0.8, "Coef de abertura": 0.45},
    "Correr 2 folhas com veneziana": {"Coef. De vidro": 0.45, "Coef de abertura": 0.45},
    "Correr 3 folhas": {"Coef. De vidro": 0.75, "Coef de abertura": 0.6},
    "Correr 4 folhas": {"Coef. De vidro": 0.7, "Coef de abertura": 0.4},
    "Basculante 45°": {"Coef. De vidro": 0.65, "Coef de abertura": 0.7},
    "Basculante 90°": {"Coef. De vidro": 0.65, "Coef de abertura": 0.9},
    "Basculante sem esquadria": {"Coef. De vidro": 0.8, "Coef de abertura": 0.8},
    "Maxim-ar": {"Coef. De vidro": 0.8, "Coef de abertura": 0.8},
    "Tombar 45°": {"Coef. De vidro": 0.9, "Coef de abertura": 0.6},
    "Tombar 90°": {"Coef. De vidro": 0.9, "Coef de abertura": 0.9},
    "Oscilobatente": {"Coef. De vidro": 0.9, "Coef de abertura": 0.9},
    "Cortina de vidro": {"Coef. De vidro": 0.95, "Coef de abertura": 0.95},
    "Guilhotina tripla": {"Coef. De vidro": 0.75, "Coef de abertura": 0.6},
    "Guilhotina dupla": {"Coef. De vidro": 0.8, "Coef de abertura": 0.4},
    "Correr 2 folhas com veneziana integrada": {"Coef. De vidro": 0.75, "Coef de abertura": 0.4},
    "Camarão": {"Coef. De vidro": 0.9, "Coef de abertura": 0.9},
    "Pinázio": {"Coef. De vidro": 0.6, "Coef de abertura": 0.4},
    "Pivotante": {"Coef. De vidro": 0.9, "Coef de abertura": 0.9},
    "Outro": {"Coef. De vidro": None, "Coef de abertura": None},
}

opcoes_esquadrias = list(coeficientes_janela.keys())

#####################################################################################

opcoes_checklist = ['Sim', 'Não', 'N/A']

#####################################################################################

opcoes_projeto = ["Incompleto", "Finalizado", "Cancelado"]

#####################################################################################

tipos_estruturas = ['Parede interna', 'Parede externa', 'Cobertura edifício', 'Piso (laje)']

#####################################################################################

# lista_materiais = get_db_colection('materiais', 'materiais')
# lista_materiais = pd.read_csv('./arquivos/materiais.csv')
# opcoes_materiais = lista_materiais['TIPO MATERIAL'].unique()

#####################################################################################

# vidros = get_db_colection('materiais', 'vidros')
# vidros = pd.read_csv('./arquivos/vidros.csv')
# opcoes_vidros = vidros['TIPO DE VIDRO'].unique()

#####################################################################################

# ambientes = get_db_colection('ambientes', 'ambientes')
# ambientes = pd.read_csv('./arquivos/ambientes.csv')

#####################################################################################
