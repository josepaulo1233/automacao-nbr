import os
import json
from dotenv import load_dotenv
import firebase_admin
import dash_mantine_components as dmc
from dash import html
from firebase_admin import credentials, firestore
import feffery_antd_components as fac
from dash_iconify import DashIconify

load_dotenv()  # carrega o .env
firebase_key_json = os.getenv("FIREBASE_KEY_JSON3")
cred_dict = json.loads(firebase_key_json)  # converte string JSON para dict

####################################################################################################################################################################

# Verificar se o Firebase já foi inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Inicializando
db = firestore.client() 

####################################################################################################################################################################

def get_projetos(id=None):

    projetos = db.collection('projetos').stream()

    if id is not None:
        projetos = db.collection('projetos').document(id).get()
        projetos = projetos.to_dict()
    return projetos

####################################################################################################################################################################

def delete_projeto(id):
    try:
        db.collection('projetos').document(id).delete()
        return True
    except Exception as e:
        return False

####################################################################################################################################################################

def get_cores():
    
    cores = db.collection('cores').stream()
    
    resultado = {
        "Nomes": [],
        "Rs": [],
        "Gs": [],
        "Bs": [],
        "abs_fosca": [],
        "abs_semibrilho": [],
        "latex_pvafosca": [],
        "acrilica_fosca": [],
        "latex_pvafoscaII": [],
    }

    for cor in cores:
        resultado["Nomes"].append(cor.id)
        data = cor.to_dict()
        resultado["Rs"].append(data.get('R', None))
        resultado["Gs"].append(data.get('G', None))
        resultado["Bs"].append(data.get('B', None))
        resultado["abs_fosca"].append(data.get('abs_fosca', None))
        resultado["abs_semibrilho"].append(data.get('abs_semibrilho', None))
        resultado["latex_pvafosca"].append(data.get('latex_pvafosca', None))
        resultado["acrilica_fosca"].append(data.get('acrilica_fosca', None))
        resultado["latex_pvafoscaII"].append(data.get('latex_pvafoscaII', None))

    return resultado

####################################################################################################################################################################

def get_db_colection(collection: str, document:str, return_type='dataframe'):

    import pandas as pd

    df = db.collection(collection).document(document).get().to_dict()
    
    if return_type == 'dataframe':
        return pd.DataFrame(df[document])
    elif return_type == 'dict':
        return df

#####################################################################################

def get_users():

    usuarios = db.collection("usuarios").document("usuarios").get().to_dict()

    return usuarios

#####################################################################################

def add_projeto(projeto: dict):

    def convert_dict_keys_to_str(data):
        if isinstance(data, dict):
            return {str(k): convert_dict_keys_to_str(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_dict_keys_to_str(item) for item in data]
        else:
            return data

    id_projeto = str(projeto.get('informacoes_projeto')['numero_projeto'])
    
    # Verifica se o projeto já existe e o remove se existir
    projetos = get_projetos()
    projeto_ids = [x.id for x in projetos]
    
    if id_projeto in projeto_ids:
        print(f"Projeto {id_projeto} já existe. Removendo projeto existente...")
        delete_projeto(id_projeto)
        print(f"Projeto {id_projeto} removido com sucesso.")
    
    print(f"Adicionando projeto {id_projeto} na coleção 'projetos'")

    # Converte todas as chaves para string
    projeto_str_keys = convert_dict_keys_to_str(projeto)
    db.collection("projetos").document(id_projeto).set(projeto_str_keys)

#####################################################################################

def checa_projeto(projeto: dict):

    # Verifica os projetos já existentes
    projetos = get_projetos()
    projeto_ids = [x.id for x in projetos]
    id_projeto = str(projeto.get('informacoes_projeto')['numero_projeto'])

    if id_projeto in projeto_ids:
        print(f"O projeto {id_projeto} já existe na coleção 'projetos'.")
        erro = 'O projeto já existe na coleção projetos.'
        return erro

    return None

#####################################################################################

def add_material_custom(material, calor_especifico, tipo_material, condutividade, densidade, resistencia):
    """
    Adiciona ou atualiza um material customizado no Firebase Firestore.

    Args:
        material (str): Nome do material.
        calor_especifico (float): Calor específico do material.
        tipo_material (str): Tipo ou descrição do material.
        condutividade (float): Condutividade térmica do material.
        densidade (float): Densidade do material.

    Returns:
        bool: True se operação foi bem-sucedida, False caso contrário.
    """

    material_dict = {
        'MATERIAL': material,
        'CALOR ESPECIFICO': calor_especifico,
        'TIPO MATERIAL': tipo_material,
        'CONDUTIVIDADE': condutividade,
        'DENSIDADE': densidade,
        'RESISTENCIA': resistencia,
    }

    try:
        # Requisitar o documento "materiais" na coleção "materiais"
        doc_ref = db.collection("materiais").document("materiais")
        doc = doc_ref.get()

        if doc.exists:
            # Obter a lista de materiais atual
            materiais = doc.to_dict().get("materiais", [])

            # Verificar se já existe um material com o mesmo nome
            atualizado = False
            for i, m in enumerate(materiais):
                if m.get('MATERIAL') == material:
                    materiais[i] = material_dict  # Atualiza o material existente
                    atualizado = True
                    break

            if not atualizado:
                materiais.append(material_dict)  # Adiciona novo material se não encontrado

            # Atualiza o documento com a nova lista
            doc_ref.update({"materiais": materiais})
        else:
            # Se o documento não existir, cria um novo com o material
            doc_ref.set({"materiais": [material_dict]})

        resultado = True

    except Exception as e:
        print(f"Erro ao adicionar material: {e}")
        resultado = False

    return resultado

#####################################################################################

def add_vidro_custom(cor_caixilho, fator_solar, tipo_de_vidro, trans_luminosa, trans_termica):
    """
    Adiciona ou atualiza um vidro customizado no Firebase Firestore.

    Args:
        cor_caixilho (str): Cor do caixilho do vidro.
        fator_solar (float): Fator solar do vidro.
        tipo_de_vidro (str): Tipo de vidro (usado como identificador).
        trans_luminosa (float): Transmitância luminosa.
        trans_termica (float): Transmitância térmica.

    Returns:
        bool: True se operação foi bem-sucedida, False caso contrário.
    """

    material_dict = {
        'COR CAIXILHO': cor_caixilho,
        'FATOR SOLAR': fator_solar,
        'TIPO DE VIDRO': tipo_de_vidro,
        'TRANS LUMINOSA': trans_luminosa,
        'TRANS TERMICA': trans_termica
    }

    try:
        # Requisitar o documento "vidros" na coleção "materiais"
        doc_ref = db.collection("materiais").document("vidros")
        doc = doc_ref.get()

        if doc.exists:
            # Obter a lista de vidros atual, garantindo que seja uma lista
            data = doc.to_dict()
            vidros = data.get("vidros", [])

            if not isinstance(vidros, list):
                vidros = []

            # Verificar se já existe um vidro com o mesmo tipo
            atualizado = False
            for i, v in enumerate(vidros):
                if v.get('TIPO DE VIDRO') == tipo_de_vidro:
                    vidros[i] = material_dict  # Atualiza o vidro existente
                    atualizado = True
                    break

            if not atualizado:
                vidros.append(material_dict)  # Adiciona novo vidro se não encontrado

            # Atualizar o documento com a nova lista
            doc_ref.update({"vidros": vidros})
        else:
            # Se o documento não existir, criar um novo com o vidro inicial
            doc_ref.set({"vidros": [material_dict]})

        resultado = True

    except Exception as e:
        print(f"Erro ao adicionar vidro: {e}")
        resultado = False

    return resultado

#####################################################################################

def add_rgb_custom(Nome_cor, R, G, B, afosca, asemibrilho, lpvafosca, acfosca, lpvafoscaII):
    """
    Adiciona ou atualiza uma cor RGB customizada no Firestore.

    Args:
        Nome_cor (str): Nome da cor (usado como ID do documento).
        R, G, B (int): Valores de cor RGB.
        afosca, asemibrilho, lpvafosca, acfosca, lpvafoscaII (float): Propriedades da cor.

    Returns:
        bool: True se operação foi bem-sucedida, False caso contrário.
    """

    rgbs = {
        'R': R,
        'G': G,
        'B': B,
        'abs_fosca': afosca,
        'abs_semibrilho': asemibrilho,
        'latex_pvafosca': lpvafosca,
        'acrilica_fosca': acfosca,
        'latex_pvafoscaII': lpvafoscaII
    }

    print(rgbs)

    try:
        # Cria ou sobrescreve o documento com o nome da cor
        db.collection("cores").document(Nome_cor).set(rgbs)
        resultado = True

    except Exception as e:
        print(f"Erro ao adicionar cor: {e}")
        resultado = False

    return resultado

#####################################################################################

def form_user(name, password, email, type):
    return fac.AntdCollapse(
        title=name.capitalize(),
        isOpen=False,
        style={'margin': '10px'},
        children=[
            dmc.Paper(
                withBorder=True,
                shadow="sm",
                p="md",
                radius="md",
                children=[
                    dmc.TextInput(
                        label="Nome do usuário",
                        id={'type': 'input-username', 'index': name},
                        value=name,
                    ),
                    dmc.PasswordInput(
                        label="Senha",
                        id={'type': 'input-password', 'index': name},
                        value=password,
                    ),
                    dmc.TextInput(
                        label="Email",
                        id={'type': 'input-email', 'index': name},
                        value=email,
                    ),
                    dmc.RadioGroup(
                        label="Tipo de usuário",
                        id={'type': 'input-tipo', 'index': name},
                        value=type,
                        children=[
                            dmc.Group([
                                dmc.Radio(label="Normal", value="normal"),
                                dmc.Radio(label="Administrador", value="admin"),
                            ], my=10)
                        ],
                        mb="md"
                    ),
                    dmc.Group(
                        # position="apart",
                        mt="md",
                        children=[
                            html.Div(id={'type': 'user-message', 'index': name}),
                            dmc.Button(
                                "Salvar",
                                id={'type': 'btn-save-user', 'index': name},
                                leftSection=DashIconify(icon="mynaui:save"),
                                color="green",
                                radius="md",
                            ),
                            dmc.Button(
                                f"Deletar {name}",
                                id={'type': 'btn-delete-user', 'index': name},
                                leftSection=DashIconify(icon="icon-park-outline:people-delete"),
                                color="red",
                                radius="md",
                            ),
                        ]
                    ),
                ]
            )

        ]
    )

#####################################################################################

def form_projeto(projeto_id):
    projeto = get_projetos(projeto_id)
    usuario = projeto['usuario'] if 'usuario' in projeto else ''
    return dmc.Paper(
        withBorder=True,
        shadow="sm",
        p="md",
        mb="md",
        radius="md",
        children=[
            dmc.TextInput(
                label="Usuário do projeto",
                id={'type': 'input-nome-projeto', 'index': projeto_id},
                value=usuario,
                disabled=True,  # Desabilitado para edição
            ),
            dmc.NumberInput(
                label="Número do projeto",
                id={'type': 'input-numero-projeto', 'index': projeto_id},
                value=projeto_id,
                disabled=True,  # Desabilitado para edição
            ),
            dmc.Group(
                mt="md",
                children=[
                    html.Div(id={'type': 'projeto-message', 'index': projeto_id}),
                    # dmc.Button(
                    #     "Salvar",
                    #     id={'type': 'btn-save-projeto', 'index': projeto_id},
                    #     leftSection=DashIconify(icon="mynaui:save"),
                    #     color="green",
                    #     radius="md",
                    # ),
                    dmc.Button(
                        f"Deletar",
                        id={'type': 'btn-delete-projeto', 'index': projeto_id},
                        leftSection=DashIconify(icon="icon-park-outline:delete"),
                        color="red",
                        radius="md",
                    ),
                ]
            ),

            dmc.Text(id={'type': 'projeto-text-delete', 'index': projeto_id}),
        ]
    )

#####################################################################################

def add_usuarios(username, email, name, password, tipo, verify=False):
    """
    Adiciona ou atualiza um usuário na coleção 'usuarios' no Firestore.

    Se o usuário existir, atualiza seus dados. Se não existir, adiciona.

    Args:
        username (str): Nome de usuário.
        email (str): Email do usuário.
        name (str): Nome completo do usuário.
        password (str): Senha do usuário.
        tipo (str): Tipo de usuário ('admin', 'normal', etc.).
    """
    config = {
        'credentials': {
            'usernames': {
                username: {
                    'email': email,
                    'name': name,
                    'password': password,
                    'type': tipo
                }
            }
        },
        'cookie': {
            'expiry_days': 1,
            'key': 'mitsid-automacao',
            'name': 'mitsid-automacao'
        }
    }

    try:
        # Referência ao documento "usuarios"
        doc_ref = db.collection("usuarios").document("usuarios")
        doc = doc_ref.get()

        if doc.exists:
            # Dados existentes
            existing_data = doc.to_dict()

            # Pega usuários existentes ou inicializa vazio
            existing_usernames = existing_data.get("credentials", {}).get("usernames", {})

            # Atualiza ou cria o usuário
            existing_usernames[username] = {
                'email': email,
                'name': name,
                'password': password,
                'type': tipo
            }

            # Atualiza o documento completo
            updated_data = {
                "credentials": {
                    "usernames": existing_usernames
                },
                "cookie": existing_data.get("cookie", config["cookie"])
            }
            doc_ref.set(updated_data)  # usa set para garantir sobrescrever tudo certinho
            valor = True

        else:
            # Cria o documento caso não exista
            doc_ref.set(config)
            valor = True

    except Exception as e:
        print(f"Erro ao adicionar/atualizar usuário: {e}")
        valor = False

    return valor

#####################################################################################

def delete_usuario(username):
    """
    Deleta um usuário específico do documento 'usuarios' no Firestore.

    Args:
        username (str): Nome do usuário a ser deletado.
    """
    try:

        # Referência ao documento "usuarios"
        doc_ref = db.collection("usuarios").document("usuarios")
        doc = doc_ref.get()

        if doc.exists:
            # Obter os dados existentes
            data = doc.to_dict()
            usernames = data.get("credentials", {}).get("usernames", {})

            if username in usernames:
                # Remover o usuário
                del usernames[username]

                # Atualizar o documento no Firestore
                doc_ref.update({"credentials.usernames": usernames})

                return True  # Usuário deletado com sucesso
                
            else:
                return False
        else:
            return False

    except Exception as e:
        return False

#####################################################################################

