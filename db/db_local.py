import os
import json
import sqlite3
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import dash_mantine_components as dmc
from dash import html
import feffery_antd_components as fac
from dash_iconify import DashIconify

class LocalDatabase:
    """Classe para gerenciar banco de dados SQLite local"""
    
    def __init__(self, db_path: str = "./db/local_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de projetos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projetos (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                usuario TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de cores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cores (
                nome TEXT PRIMARY KEY,
                R INTEGER,
                G INTEGER,
                B INTEGER,
                abs_fosca REAL,
                abs_semibrilho REAL,
                latex_pvafosca REAL,
                acrilica_fosca REAL,
                latex_pvafoscaII REAL
            )
        ''')
        
        # Tabela de materiais (armazena dados como JSON para manter compatibilidade com Firebase)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materiais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL
            )
        ''')
        
        # Tabela de vidros (armazena dados como JSON para manter compatibilidade com Firebase)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vidros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL
            )
        ''')
        
        # Tabela de usuários (armazena como JSON)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config TEXT NOT NULL
            )
        ''')
        
        # Tabela genérica para coleções (similar ao Firebase)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                collection_name TEXT,
                document_name TEXT,
                data TEXT,
                PRIMARY KEY (collection_name, document_name)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """Executa uma query no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# Instância global do banco de dados
db = LocalDatabase()

####################################################################################################################################################################

class MockDocument:
    """Classe para simular documento do Firebase"""
    def __init__(self, doc_id: str, data: dict):
        self.id = doc_id
        self._data = data
    
    def to_dict(self):
        return self._data

def get_projetos(id: Optional[str] = None):
    """Obtém projetos do banco local"""
    if id is not None:
        result = db.execute_query(
            "SELECT data FROM projetos WHERE id = ?", 
            (id,), 
            fetch=True
        )
        if result:
            return json.loads(result[0][0])
        return None
    else:
        result = db.execute_query(
            "SELECT id, data FROM projetos", 
            fetch=True
        )
        projetos = []
        for row in result:
            projetos.append(MockDocument(row[0], json.loads(row[1])))
        return projetos

####################################################################################################################################################################

def delete_projeto(id: str) -> bool:
    """Remove um projeto do banco local"""
    try:
        db.execute_query("DELETE FROM projetos WHERE id = ?", (id,))
        return True
    except Exception as e:
        print(f"Erro ao deletar projeto: {e}")
        return False

####################################################################################################################################################################

def get_cores():
    """Obtém cores do banco local"""
    result = db.execute_query("""
        SELECT nome, R, G, B, abs_fosca, abs_semibrilho, 
               latex_pvafosca, acrilica_fosca, latex_pvafoscaII 
        FROM cores
    """, fetch=True)
    
    cores_dict = {
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
    
    for row in result:
        cores_dict["Nomes"].append(row[0])
        cores_dict["Rs"].append(row[1])
        cores_dict["Gs"].append(row[2])
        cores_dict["Bs"].append(row[3])
        cores_dict["abs_fosca"].append(row[4])
        cores_dict["abs_semibrilho"].append(row[5])
        cores_dict["latex_pvafosca"].append(row[6])
        cores_dict["acrilica_fosca"].append(row[7])
        cores_dict["latex_pvafoscaII"].append(row[8])
    
    return cores_dict

####################################################################################################################################################################

def get_db_colection(collection: str, document: str, return_type: str = 'dataframe'):
    """Obtém uma coleção do banco local - compatível com estrutura Firebase"""
    
    # Casos especiais para coleções que têm tabelas próprias
    if collection == 'materiais' and document == 'vidros':
        # Busca dados da tabela vidros
        result = db.execute_query("SELECT data FROM vidros", fetch=True)
        if result:
            vidros_data = [json.loads(row[0]) for row in result]
            if return_type == 'dataframe':
                return pd.DataFrame(vidros_data)
            else:
                return {'vidros': vidros_data}
        else:
            return pd.DataFrame() if return_type == 'dataframe' else {'vidros': []}
    
    elif collection == 'materiais' and document == 'materiais':
        # Busca dados da tabela materiais
        result = db.execute_query("SELECT data FROM materiais", fetch=True)
        if result:
            materiais_data = [json.loads(row[0]) for row in result]
            if return_type == 'dataframe':
                return pd.DataFrame(materiais_data)
            else:
                return {'materiais': materiais_data}
        else:
            return pd.DataFrame() if return_type == 'dataframe' else {'materiais': []}
    
    # Busca genérica na tabela collections
    result = db.execute_query(
        "SELECT data FROM collections WHERE collection_name = ? AND document_name = ?",
        (collection, document),
        fetch=True
    )
    
    if not result:
        return pd.DataFrame() if return_type == 'dataframe' else {}
    
    data = json.loads(result[0][0])
    
    if return_type == 'dataframe':
        return pd.DataFrame(data.get(document, []))
    elif return_type == 'dict':
        return data

#####################################################################################

def get_users():
    """Obtém usuários do banco local"""
    result = db.execute_query(
        "SELECT config FROM usuarios ORDER BY id DESC LIMIT 1",
        fetch=True
    )
    
    if result:
        return json.loads(result[0][0])
    return {}

#####################################################################################

def add_ambientes(ambientes_data):
    """Adiciona dados de ambientes ao banco local"""
    try:
        # Converte DataFrame para dict se necessário
        if hasattr(ambientes_data, 'to_dict'):
            ambientes_dict = {'ambientes': ambientes_data.to_dict('records')}
        elif isinstance(ambientes_data, dict):
            ambientes_dict = ambientes_data if 'ambientes' in ambientes_data else {'ambientes': ambientes_data}
        else:
            ambientes_dict = {'ambientes': ambientes_data}
        
        # Remove dados existentes de ambientes
        db.execute_query(
            "DELETE FROM collections WHERE collection_name = ? AND document_name = ?",
            ('ambientes', 'ambientes')
        )
        
        # Adiciona os novos dados
        db.execute_query(
            "INSERT INTO collections (collection_name, document_name, data) VALUES (?, ?, ?)",
            ('ambientes', 'ambientes', json.dumps(ambientes_dict))
        )
        
        return True
    except Exception as e:
        print(f"Erro ao adicionar ambientes: {e}")
        return False

#####################################################################################

def get_ambientes(return_type='dataframe'):
    """Obtém dados de ambientes do banco local"""
    try:
        result = db.execute_query(
            "SELECT data FROM collections WHERE collection_name = ? AND document_name = ?",
            ('ambientes', 'ambientes'),
            fetch=True
        )
        
        if not result:
            return pd.DataFrame() if return_type == 'dataframe' else {}
        
        data = json.loads(result[0][0])
        
        if return_type == 'dataframe':
            return pd.DataFrame(data.get('ambientes', []))
        elif return_type == 'dict':
            return data
    except Exception as e:
        print(f"Erro ao obter ambientes: {e}")
        return pd.DataFrame() if return_type == 'dataframe' else {}

#####################################################################################

def add_projeto(projeto: dict):
    """Adiciona um projeto ao banco local"""
    
    def convert_dict_keys_to_str(data):
        if isinstance(data, dict):
            return {str(k): convert_dict_keys_to_str(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_dict_keys_to_str(item) for item in data]
        else:
            return data

    id_projeto = str(projeto.get('informacoes_projeto', {}).get('numero_projeto', ''))
    
    if not id_projeto:
        raise ValueError("ID do projeto não encontrado")
    
    # Verifica se o projeto já existe e o remove se existir
    existing = db.execute_query(
        "SELECT id FROM projetos WHERE id = ?", 
        (id_projeto,), 
        fetch=True
    )
    
    if existing:
        print(f"Projeto {id_projeto} já existe. Removendo projeto existente...")
        delete_projeto(id_projeto)
        print(f"Projeto {id_projeto} removido com sucesso.")
    
    print(f"Adicionando projeto {id_projeto} ao banco local")

    # Converte todas as chaves para string
    projeto_str_keys = convert_dict_keys_to_str(projeto)
    
    # Extrai informações do usuário se existir
    usuario = projeto_str_keys.get('usuario', '')
    
    # Salva no banco
    db.execute_query(
        "INSERT INTO projetos (id, data, usuario) VALUES (?, ?, ?)",
        (id_projeto, json.dumps(projeto_str_keys), usuario)
    )

#####################################################################################

def checa_projeto(projeto: dict):
    """Verifica se um projeto já existe"""
    id_projeto = str(projeto.get('informacoes_projeto', {}).get('numero_projeto', ''))
    
    existing = db.execute_query(
        "SELECT id FROM projetos WHERE id = ?", 
        (id_projeto,), 
        fetch=True
    )
    
    if existing:
        print(f"O projeto {id_projeto} já existe no banco local.")
        return 'O projeto já existe no banco local.'
    
    return None

#####################################################################################

def add_material_custom(material: str, calor_especifico: float, tipo_material: str, 
                       condutividade: float, densidade: float, resistencia: float, 
                       capacidade_termica=None) -> bool:
    
    """Adiciona um material customizado no banco local (não sobrescreve se TODOS os dados forem idênticos)"""
    
    def values_are_equal(val1, val2):
        """Compara dois valores tratando None, NaN e valores vazios como iguais"""
        import math
        
        # Trata None como igual
        if val1 is None and val2 is None:
            return True
        
        # Se um é None e outro não, são diferentes
        if val1 is None or val2 is None:
            return False
            
        # Trata NaN como iguais
        try:
            if math.isnan(float(val1)) and math.isnan(float(val2)):
                return True
        except (TypeError, ValueError):
            pass
            
        return val1 == val2
    
    try:
        # Cria dicionário com nomes de campos idênticos ao Firebase
        material_dict = {
            'MATERIAL': material,
            'CALOR ESPECIFICO': calor_especifico,
            'TIPO MATERIAL': tipo_material,
            'CONDUTIVIDADE': condutividade,
            'DENSIDADE': densidade,
            'RESISTENCIA': resistencia,
            'CAPACIDADE TERMICA': capacidade_termica,
        }
        
        # Busca materiais existentes para verificar duplicatas
        result = db.execute_query("SELECT id, data FROM materiais", fetch=True)
        
        for row in result:
            existing_data = json.loads(row[1])
            
            # Verifica se TODOS os elementos são iguais (material completamente idêntico)
            material_identical = True
            for key, value in material_dict.items():
                existing_value = existing_data.get(key)
                
                if not values_are_equal(value, existing_value):
                    material_identical = False
                    break
            
            if material_identical:
                # Material completamente idêntico já existe, não adiciona
                print(f"⚠️ Material '{material}' com tipo '{tipo_material}' já existe com TODOS os dados idênticos. Não foi sobrescrito.")
                return False
        
        # Se chegou aqui, o material não existe - adiciona novo
        db.execute_query(
            "INSERT INTO materiais (data) VALUES (?)",
            (json.dumps(material_dict),)
        )
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar material: {e}")
        return False

#####################################################################################

def add_vidro_custom(cor_caixilho: str, fator_solar: float, tipo_de_vidro: str, 
                    trans_luminosa: float, trans_termica: float) -> bool:
    """Adiciona ou atualiza um vidro customizado no banco local"""
    try:
        # Cria dicionário com nomes de campos idênticos ao Firebase
        vidro_dict = {
            'COR CAIXILHO': cor_caixilho,
            'FATOR SOLAR': fator_solar,
            'TIPO DE VIDRO': tipo_de_vidro,
            'TRANS LUMINOSA': trans_luminosa,
            'TRANS TERMICA': trans_termica
        }
        
        # Busca vidros existentes
        result = db.execute_query("SELECT id, data FROM vidros", fetch=True)
        existing_id = None
        
        for row in result:
            existing_data = json.loads(row[1])
            if existing_data.get('TIPO DE VIDRO') == tipo_de_vidro:
                existing_id = row[0]
                break
        
        if existing_id:
            # Atualiza existente
            db.execute_query(
                "UPDATE vidros SET data = ? WHERE id = ?",
                (json.dumps(vidro_dict), existing_id)
            )
        else:
            # Adiciona novo
            db.execute_query(
                "INSERT INTO vidros (data) VALUES (?)",
                (json.dumps(vidro_dict),)
            )
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar vidro: {e}")
        return False

#####################################################################################

def add_rgb_custom(Nome_cor: str, R: int, G: int, B: int, afosca: float, 
                  asemibrilho: float, lpvafosca: float, acfosca: float, 
                  lpvafoscaII: float) -> bool:
    """Adiciona ou atualiza uma cor RGB customizada no banco local"""
    try:
        # Verifica se já existe
        existing = db.execute_query(
            "SELECT nome FROM cores WHERE nome = ?",
            (Nome_cor,),
            fetch=True
        )
        
        if existing:
            # Atualiza existente
            db.execute_query("""
                UPDATE cores 
                SET R = ?, G = ?, B = ?, abs_fosca = ?, abs_semibrilho = ?, 
                    latex_pvafosca = ?, acrilica_fosca = ?, latex_pvafoscaII = ?
                WHERE nome = ?
            """, (R, G, B, afosca, asemibrilho, lpvafosca, acfosca, lpvafoscaII, Nome_cor))
        else:
            # Adiciona novo
            db.execute_query("""
                INSERT INTO cores (nome, R, G, B, abs_fosca, abs_semibrilho, 
                                 latex_pvafosca, acrilica_fosca, latex_pvafoscaII)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (Nome_cor, R, G, B, afosca, asemibrilho, lpvafosca, acfosca, lpvafoscaII))
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar cor: {e}")
        return False

#####################################################################################

def form_user(name: str, password: str, email: str, type: str):
    """Formulário para usuário (mantém a interface original)"""
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

def form_projeto(projeto_id: str):
    """Formulário para projeto (mantém a interface original)"""
    projeto = get_projetos(projeto_id)
    usuario = projeto.get('usuario', '') if projeto else ''
    
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
                disabled=True,
            ),
            dmc.NumberInput(
                label="Número do projeto",
                id={'type': 'input-numero-projeto', 'index': projeto_id},
                value=projeto_id,
                disabled=True,
            ),
            dmc.Group(
                mt="md",
                children=[
                    html.Div(id={'type': 'projeto-message', 'index': projeto_id}),
                    dmc.Button(
                        "Deletar",
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

def add_usuarios(username: str, email: str, name: str, password: str, tipo: str, verify: bool = False) -> bool:
    """Adiciona ou atualiza um usuário no banco local"""
    try:
        # Busca configuração existente
        existing_config = get_users()
        
        # Se não existe configuração, cria estrutura básica
        if not existing_config:
            existing_config = {
                'credentials': {'usernames': {}},
                'cookie': {
                    'expiry_days': 1,
                    'key': 'mitsid-automacao',
                    'name': 'mitsid-automacao'
                }
            }
        
        # Adiciona/atualiza usuário
        existing_config['credentials']['usernames'][username] = {
            'email': email,
            'name': name,
            'password': password,
            'type': tipo
        }
        
        # Remove configuração existente
        db.execute_query("DELETE FROM usuarios")
        
        # Adiciona nova configuração
        db.execute_query(
            "INSERT INTO usuarios (config) VALUES (?)",
            (json.dumps(existing_config),)
        )
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar usuário: {e}")
        return False

#####################################################################################

def delete_usuario(username: str) -> bool:
    """Remove um usuário do banco local"""
    try:
        # Busca configuração existente
        existing_config = get_users()
        
        if not existing_config:
            return False
        
        usernames = existing_config.get('credentials', {}).get('usernames', {})
        
        if username in usernames:
            # Remove o usuário
            del usernames[username]
            
            # Remove configuração existente
            db.execute_query("DELETE FROM usuarios")
            
            # Adiciona configuração atualizada
            db.execute_query(
                "INSERT INTO usuarios (config) VALUES (?)",
                (json.dumps(existing_config),)
            )
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False

#####################################################################################

def set_collection_data(collection_name: str, document_name: str, data: dict):
    """Adiciona dados a uma coleção genérica (similar ao Firebase)"""
    try:
        # Casos especiais para coleções que têm tabelas próprias
        if collection_name == 'materiais' and document_name == 'vidros':
            # Se for vidros, salva na tabela vidros
            vidros_list = data.get('vidros', [])
            
            # Limpa tabela atual
            db.execute_query("DELETE FROM vidros")
            
            # Adiciona cada vidro
            for vidro in vidros_list:
                db.execute_query(
                    "INSERT INTO vidros (data) VALUES (?)",
                    (json.dumps(vidro),)
                )
            return True
        
        elif collection_name == 'materiais' and document_name == 'materiais':
            # Se for materiais, salva na tabela materiais
            materiais_list = data.get('materiais', [])
            
            # Limpa tabela atual
            db.execute_query("DELETE FROM materiais")
            
            # Adiciona cada material
            for material in materiais_list:
                db.execute_query(
                    "INSERT INTO materiais (data) VALUES (?)",
                    (json.dumps(material),)
                )
            return True
        
        # Remove dados existentes da tabela genérica
        db.execute_query(
            "DELETE FROM collections WHERE collection_name = ? AND document_name = ?",
            (collection_name, document_name)
        )
        
        # Adiciona novos dados na tabela genérica
        db.execute_query(
            "INSERT INTO collections (collection_name, document_name, data) VALUES (?, ?, ?)",
            (collection_name, document_name, json.dumps(data))
        )
        
        return True
        
    except Exception as e:
        print(f"Erro ao salvar dados da coleção: {e}")
        return False

#####################################################################################

def get_materiais():
    """Obtém todos os materiais do banco local"""
    result = db.execute_query("SELECT data FROM materiais", fetch=True)
    
    materiais = []
    for row in result:
        materiais.append(json.loads(row[0]))
    
    return pd.DataFrame(materiais)

#####################################################################################

def delete_all_materiais() -> bool:
    """Deleta todos os materiais do banco local"""
    try:
        db.execute_query("DELETE FROM materiais")
        print("✅ Todos os materiais foram deletados com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao deletar materiais: {e}")
        return False

#####################################################################################

def delete_color_by_name(color_name: str) -> bool:
    """Deleta uma cor específica pelo nome"""       
    try:

        if isinstance(color_name, list) and len(color_name) > 0:
            color_name = color_name[0]

        # Busca todas as cores no banco
        result = db.execute_query("SELECT nome FROM cores", fetch=True)
        
        # Verifica se a cor existe
        nomes = [row[0] for row in result]
        if color_name not in nomes:
            print(f"⚠️ Nome da cor '{color_name}' não encontrado!")
            return False
        
        # Deleta a cor correspondente
        db.execute_query("DELETE FROM cores WHERE nome = ?", (color_name,))
        print(f"✅ Cor '{color_name}' deletada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao deletar cor '{color_name}': {e}")
        return False

#####################################################################################

def delete_vidro_by_type(tipo_vidro: str) -> bool:
    """Deleta um vidro específico pelo tipo"""
    try:
        # Se vier lista, converte para string
        if isinstance(tipo_vidro, list) and len(tipo_vidro) > 0:
            tipo_vidro = tipo_vidro[0]

        result = db.execute_query("SELECT data FROM vidros", fetch=True)

        for row in result:
            vidro_data = json.loads(row[0])
            if str(vidro_data.get('TIPO DE VIDRO')) == str(tipo_vidro):
                db.execute_query("DELETE FROM vidros WHERE data = ?", (row[0],))
                print(f"✅ Vidro '{tipo_vidro}' deletado com sucesso!")
                return True
        
        print(f"⚠️ Vidro '{tipo_vidro}' não encontrado!")
        return False

    except Exception as e:
        print(f"❌ Erro ao deletar vidro '{tipo_vidro}': {e}")
        return False

#####################################################################################

def delete_material_by_name(material_name: str) -> bool:
    """Deleta um material específico pelo nome"""
    try:

        # Se vier lista, converte para string
        if isinstance(material_name, list) and len(material_name) > 0:
            material_name = material_name[0]

        # Busca o material pelo nome
        result = db.execute_query("SELECT id, data FROM materiais", fetch=True)
        
        for row in result:
            material_data = json.loads(row[1])
            if material_data.get('MATERIAL') == material_name:
                db.execute_query("DELETE FROM materiais WHERE id = ?", (row[0],))
                print(f"✅ Material '{material_name}' deletado com sucesso!")
                return True
        
        print(f"⚠️ Material '{material_name}' não encontrado!")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao deletar material '{material_name}': {e}")
        return False

#####################################################################################

def count_materiais() -> int:
    """Conta o número total de materiais no banco local"""
    try:
        result = db.execute_query("SELECT COUNT(*) FROM materiais", fetch=True)
        return result[0][0] if result else 0
    except Exception as e:
        print(f"❌ Erro ao contar materiais: {e}")
        return 0

#####################################################################################

def get_vidros():
    """Obtém todos os vidros do banco local"""
    result = db.execute_query("SELECT data FROM vidros", fetch=True)
    
    vidros = []
    for row in result:
        vidros.append(json.loads(row[0]))
    
    return vidros

#####################################################################################

def export_database(export_path: str = "database_backup.json") -> bool:
    """Exporta todo o banco de dados para um arquivo JSON"""
    try:
        export_data = {
            'projetos': [],
            'cores': get_cores(),
            'materiais': get_materiais(),
            'vidros': get_vidros(),
            'usuarios': get_users()
        }
        
        # Adiciona projetos
        projetos = get_projetos()
        for projeto in projetos:
            export_data['projetos'].append({
                'id': projeto.id,
                'data': projeto.to_dict()
            })
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"Erro ao exportar banco de dados: {e}")
        return False

#####################################################################################

def import_database(import_path: str) -> bool:
    """Importa dados de um arquivo JSON para o banco de dados"""
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Importa projetos
        for projeto_data in import_data.get('projetos', []):
            add_projeto(projeto_data['data'])
        
        # Importa cores
        cores = import_data.get('cores', {})
        nomes = cores.get('Nomes', [])
        for i, nome in enumerate(nomes):
            add_rgb_custom(
                nome,
                cores['Rs'][i],
                cores['Gs'][i], 
                cores['Bs'][i],
                cores['abs_fosca'][i],
                cores['abs_semibrilho'][i],
                cores['latex_pvafosca'][i],
                cores['acrilica_fosca'][i],
                cores['latex_pvafoscaII'][i]
            )
        
        # Importa materiais
        for material in import_data.get('materiais', []):
            add_material_custom(
                material['MATERIAL'],
                material['CALOR ESPECIFICO'],
                material['TIPO MATERIAL'],
                material['CONDUTIVIDADE'],
                material['DENSIDADE'],
                material['RESISTENCIA']
            )
        
        # Importa vidros
        for vidro in import_data.get('vidros', []):
            add_vidro_custom(
                vidro['COR CAIXILHO'],
                vidro['FATOR SOLAR'],
                vidro['TIPO DE VIDRO'],
                vidro['TRANS LUMINOSA'],
                vidro['TRANS TERMICA']
            )
        
        # Importa usuários
        usuarios_config = import_data.get('usuarios', {})
        if usuarios_config and 'credentials' in usuarios_config:
            for username, user_data in usuarios_config['credentials']['usernames'].items():
                add_usuarios(
                    username,
                    user_data['email'],
                    user_data['name'],
                    user_data['password'],
                    user_data['type']
                )
        
        return True
        
    except Exception as e:
        print(f"Erro ao importar banco de dados: {e}")
        return False

#####################################################################################