import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback, _dash_renderer, ALL, MATCH, ctx
import feffery_antd_components as fac
import feffery_utils_components as fuc
from db.db_local import delete_material_by_name, delete_vidro_by_type, delete_color_by_name, get_cores, get_projetos, get_users, add_projeto, checa_projeto, add_material_custom, add_vidro_custom, add_rgb_custom, form_user, add_usuarios, delete_usuario, form_projeto, delete_projeto, get_materiais, get_vidros
from projetos.projetos import Projeto
import dash_mantine_components as dmc
from utils.templates import dados_projeto
from flask import Flask, request, session, redirect, url_for, render_template_string
from projetos.forms_apresentacao import form_apresentacao
from dash_iconify import DashIconify
import os
from functools import wraps

import warnings
warnings.filterwarnings("ignore")

_dash_renderer._set_react_version("18.2.0")

# usuarios = get_users()
# credentials = usuarios.get('credentials')

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.FLATLY, 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css', 'https://fonts.googleapis.com/css?family=Poppins'], 
                suppress_callback_exceptions=True,
                title='Automação NBR',
                )

app._favicon = "logo-mit.png"
server = app.server  # Necessário para acessar Flask
server.secret_key = "minha_chave_super_secreta"

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to get current user
def get_current_user():
    return session.get('username')

def get_current_user_type():
    return session.get('user_type')

####################################################################################################################################################################

# Login page template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Automação NBR - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="icon" type="image/x-icon" href="/assets/logo-mit.png">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center; /* centraliza horizontalmente */
        }
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 2rem;
            max-width: 400px;
            width: 100%;
        }
        .logo {
            max-width: 150px;
            margin: 0 auto 2rem;
            display: block;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-login {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            padding: 12px;
            font-weight: 600;
        }
        .btn-login:hover {
            background: linear-gradient(45deg, #5a6fd8, #6a42a0);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <img src="/assets/logo-mit.png" alt="Logo" class="logo">
        <h3 class="text-center mb-4">Automação NBR</h3>
        {% if error %}
            <div class="alert alert-danger" role="alert">
                {{ error }}
            </div>
        {% endif %}
        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">Usuário</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Senha</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary btn-login w-100">Entrar</button>
        </form>
    </div>
</body>
</html>
"""

@app.server.route('/login', methods=['GET', 'POST'])
def login():
    # Recarregar usuários do banco de dados a cada tentativa de login
    usuarios_atualizados = get_users()
    credentials_atualizados = usuarios_atualizados.get('credentials')
    USER_PWD = {username: data['password'] for username, data in credentials_atualizados['usernames'].items()}
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials
        if username in USER_PWD and USER_PWD[username] == password:
            session['username'] = username
            session['user_type'] = credentials_atualizados['usernames'][username]['type']
            return redirect('/')
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Usuário ou senha inválidos')
    
    # If user is already logged in, redirect to main page
    if 'username' in session:
        return redirect('/')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.server.route('/logout')
def logout():
    # Clear the session
    session.clear()
    
    # Create a response with cache-control headers to prevent caching
    response = redirect(url_for('login'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# Middleware to check authentication for Dash app
@app.server.before_request
def require_login():
    # Allow access to login, logout pages and static assets
    if request.endpoint in ['login', 'logout', 'static'] or request.path.startswith('/assets/'):
        return
    
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

@app.server.route('/upload/', methods=['POST'])
def upload():

    uploadId = request.values.get('uploadId')
    filename = request.files['file'].filename

    try:
        os.makedirs(os.path.join('upload', uploadId), exist_ok=True)
    except FileExistsError:
        pass

    with open(os.path.join('upload', uploadId, filename), 'wb') as f:
        for chunk in iter(lambda: request.files['file'].read(1024 * 1024 * 100), b''):
            f.write(chunk)

    return {'filename': filename}

####################################################################################################################################################################

def layout():
    layout = dmc.MantineProvider([
        dmc.NotificationProvider(position="top-right"),

        fac.AntdLayout([

            # ===== SIDEBAR =====
            fac.AntdAffix(
                fac.AntdSider(
                    [
                        html.Div(
                            id='usuario-logado',
                            style={
                                'textAlign': 'center',
                                'padding': '10px',
                                'marginTop': '10px',
                                'color': 'black'
                            }
                        ),

                        html.Div([
                            dmc.Button(
                                "Logout",
                                leftSection=DashIconify(icon="ic:baseline-logout"),
                                id='logout-btn',
                                color='red',
                                variant='light',
                                size='sm',
                                radius='md',
                                fullWidth=True,
                                style={'marginTop': '10px'}
                            )
                        ]),

                        fac.AntdDivider(),

                        fac.AntdImage(
                            src='assets/logo-mit.png',
                            preview=False,
                            style={'margin': 'auto', 'display': 'block', 'width': '80%'}
                        ),

                        fac.AntdDivider(),

                        fac.AntdMenu(
                            menuItems=[
                                {'component': 'Item', 'props': {'key': 'Novo projeto', 'title': 'Novo projeto', 'icon': 'antd-folder-add'}},
                                {'component': 'Item', 'props': {'key': 'Seus projetos cadastrados', 'title': 'Seus projetos cadastrados', 'icon': 'antd-folder-open'}},
                                {'component': 'Item', 'props': {'key': 'Montar relatório', 'title': 'Montar relatório', 'icon': 'antd-line-chart'}},
                                {'component': 'Item', 'props': {'key': 'Enviar ao banco de dados', 'title': 'Enviar ao banco de dados', 'icon': 'fc-add-database'}},
                            ],
                            mode='inline',
                            id='sidebar-menu',
                            style={'color': 'black'},
                            defaultSelectedKey='Novo projeto'
                        ),

                        fac.AntdDivider(),

                        html.Div(id='menu_projetos'),
                        
                    ],

                    theme='light',
                    # collapsible=True,
                    width=250,
                    style={
                        'height': '100vh',
                        'overflowY': 'auto',  # rolagem própria só na sidebar
                        'padding': '20px 15px',
                        'color': 'black',
                        'border': '2px solid lightcyan',
                        'borderTopRightRadius': '20px',
                        'borderBottomRightRadius': '20px',
                        'boxShadow': '4px 0 10px rgba(0, 0, 0, 0.2)',
                    },
                ),
            ),

            # ===== CONTEÚDO PRINCIPAL =====
            fac.AntdLayout([
                fac.AntdContent([
                    html.Div(id="mensagem"),
                    html.Div(id="mensagem-confirmacao"),

                    # Conteúdo principal
                    html.Div(
                        id='page-content',
                        style={
                            'padding': '20px',
                            'minHeight': '100vh',  # substitui height fixo
                            'overflowY': 'auto',   # rola apenas conteúdo
                        }
                    ),

                    dcc.Store(id='json-projeto'),

                    dbc.Modal([
                        dbc.ModalHeader("Projeto já existe"),
                        dbc.ModalBody("Deseja sobrescrever o projeto existente?"),
                        dbc.ModalFooter([
                            dbc.Button("Cancelar", id="btn-cancelar", color="secondary"),
                            dbc.Button("Sobrescrever", id="btn-sobrescrever", color="danger"),
                        ]),
                    ], id="modal-confirmacao", is_open=False),
                ])
            ], style={
                'backgroundColor': 'white',
                'height': '100vh',
                # 'overflow': 'hidden'  # impede rolagem dupla
            }),

            fac.AntdBackTop(duration=0),
        ], style={
            # 'minHeight': '100vh',  # permite expansão sem criar segunda barra
            # 'overflow': 'hidden'   # evita barra global
        })
    ])

    return layout

####################################################################################################################################################################

app.layout = fuc.FefferyTopProgress(layout())

####################################################################################################################################################################

@callback(
Output('menu_projetos', 'children'),
Output('page-content', 'children'),
Input('sidebar-menu', 'currentKey'),
suppress_callback_exceptions=True
)
def menu_projetos(selected_key):

    user = session.get('username') # Obtém o nome do usuário autenticado

    # Pegando os projetos no DB
    projetos_cadastrados = get_projetos()
    projetos_cadastrados_ids = [x.id for x in projetos_cadastrados]
    
    if selected_key == 'Seus projetos cadastrados':

        # Separando os projetos por status
        status = {"Incompleto": [], "Finalizado": [], "Cancelado": []}
        for id in projetos_cadastrados_ids:
            tmp = get_projetos(id=id)
            tmp_status = tmp['status']
            tmp_user = tmp['usuario']
            if tmp_user == user:
                if tmp_status in status:
                    status[tmp_status].append(id)
                else:
                    status[tmp_status] = [id] 

        menu = html.Div([
                       
            fac.AntdMenu(
            
                menuItems=[

                    {
                        'component': 'SubMenu',
                        'props': {
                            'key': sub_menu,
                            'title': sub_menu,
                            'icon': 'antd-folder',
                        },

                        'children': [
                            {
                                'component': 'Item',
                                'props': {
                                    'key': projeto,
                                    'title': projeto,
                                },
                            }

                            for projeto in status[sub_menu]
                        ]
                    }

                    for sub_menu in status
                ],
            mode='inline',
            id='projetos_cadastrados',
            style={'position': 'relative', }, # 'backgroundColor': 'rgb(240, 242, 245)' 'background': 'linear-gradient(180deg, #0E3D48 0%, #0B2F37 100%)', 'color': 'white'
        )])

        content = dbc.Alert(" 📂 Selecione um projeto ao lado para edita-lo ...", color="info", className='m-3'),

    elif selected_key == 'Novo projeto':

        # Vem dos templetates
        content = Projeto(**dados_projeto).exibir_infos()
        menu = ''

    elif selected_key == 'Montar relatório':

        content = dbc.Alert(" 📂 Selecione um projeto ao lado para gerar o relatório ...", color="info", className='m-3')

        # Separando os projetos por status
        status = {"Incompleto": [], "Finalizado": [], "Cancelado": []}
        for id in projetos_cadastrados_ids:
            tmp = get_projetos(id=id)
            tmp_status = tmp['status']
            tmp_user = tmp['usuario']
            if tmp_user == user:
                if tmp_status in status:
                    status[tmp_status].append(id)
                else:
                    status[tmp_status] = [id] 

        menu = html.Div([
            
            fac.AntdMenu(
            
            menuItems=[

                {
                    'component': 'SubMenu',
                    'props': {
                        'key': sub_menu,
                        'title': sub_menu,
                        'icon': 'antd-folder',
                    },
                    'children': [
                        {
                            'component': 'Item',
                            'props': {
                                'key': projeto,
                                'title': projeto,
                            },
                        }

                        for projeto in status[sub_menu]
                    ]
                }
                for sub_menu in status
            ],
            mode='inline',
            id='projetos_cadastrados_apresentacao',
            style={'position': 'relative', 'color': 'black'}, # 'backgroundColor': 'rgb(240, 242, 245)' 'background': 'linear-gradient(180deg, #0E3D48 0%, #0B2F37 100%)', 'color': 'white'
        )])

    elif selected_key == 'Gerenciar usuários':

        menu = ''

        usuarios_dict = get_users()['credentials']['usernames'] # config['credentials']['usernames']
        usuarios_gerenciados = list(usuarios_dict.keys())

        usuarios_existentes = html.Div([

            html.H5("Gerenciar usuários", className='fw-bold'),

            dcc.Store(id="reload-usuarios", data=0),

            html.Div([

                form_user(**usuarios_dict[usuario_gerenciado]) for usuario_gerenciado in usuarios_gerenciados 

            ], id='usuarios_existentes'),

        ])

        novo_usuario = dmc.Paper(
            withBorder=True,
            shadow="sm",
            p="md",
            radius="md",
            children=[

                dmc.Title("Adicionar novo usuário", order=2, style={"marginBottom": 10}),

                dmc.TextInput(
                    label="Digite o nome do usuário",
                    placeholder="Nome do usuário",
                    id="input-usuario",
                    style={"marginBottom": 10},
                ),

                dmc.TextInput(
                    label="Digite a senha do usuário",
                    placeholder="Senha do usuário",
                    id="input-senha-usuario",
                    style={"marginBottom": 10},
                ),

                dmc.TextInput(
                    label="Digite o e-mail do usuário",
                    placeholder="E-mail do usuário",
                    id="input-email-usuario",
                    style={"marginBottom": 10},
                ),

                dmc.RadioGroup(
                    label="Tipo de usuário",
                    id="select-user-type",
                    value="normal",
                    children= dmc.Group([
                        dmc.Radio(label="Normal", value="normal"),
                        dmc.Radio(label="Administrador", value="admin"),
                    ], my=10),
                    mb="md"
                ),

                dmc.Button("Adicionar ao banco de dados", id="btn-submit-usuario", color="blue", style={"marginTop": 10}, leftSection=DashIconify(icon="typcn:user-add"), radius="md",),

                html.Div(id="output-feedback-usuario", style={"marginTop": 20}),

        ])

        tabs_content = {
            'Novo usuário': novo_usuario,
            'Usuários existentes': usuarios_existentes,
        }

        content = html.Div([

            fac.AntdTabs(
                # type='card',
                centered=True,
                tabBarGutter=60,
                items=[
                    {
                        'key': f'tab{tab}',
                        'label': f'{tab}',
                        # 'icon': fac.AntdIcon(icon=f'antd-{tab_icons.get(tab, "question-circle")}'),
                        'children': tabs_content[tab]
                    }

                    for tab in tabs_content
                ]
            )   

        ])

    elif selected_key == 'Gerenciar itens do banco':

        projetos_cadastrados = get_projetos()
        projetos_cadastrados_ids = [x.id for x in projetos_cadastrados]
        projetos_cadastrados = [{'label': str(id), 'value': str(id)} for id in projetos_cadastrados_ids]
        materiais_cadastrados = get_materiais()
        vidros_cadastrados = pd.DataFrame(get_vidros())
        vidros_cadastrados = vidros_cadastrados[['TIPO DE VIDRO', 'COR CAIXILHO', 'FATOR SOLAR', 'TRANS LUMINOSA', 'TRANS TERMICA']]
        cores_cadastrados = pd.DataFrame(get_cores())

        menu = ''

        material_customizado = dmc.Paper(
            withBorder=True,
            shadow="sm",
            p="md",
            radius="md",
            children=[
            dmc.Title("Adicionar material customizado ao DB", order=2, mb=10),

            dmc.TextInput(
                label="Digite o material",
                placeholder="Nome do material",
                id="input-material",
                required=True,
                style={"marginBottom": 10},
            ),

            dmc.TextInput(
                label="Digite o tipo material",
                placeholder="Tipo do material",
                id="input-tipo-material",
                required=True,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Calor específico [kJ/KgK]",
                id="input-calor-especifico",
                required=True,
                step=0.01,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Condutividade [W/mK]",
                id="input-condutividade",
                required=True,
                step=0.01,
                min=0,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Densidade [kg/m³]",
                id="input-densidade",
                required=True,
                step=0.01,
                min=0,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Resistência [m²K/W]",
                id="input-resistencia",
                step=0.01,
                min=0,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Capacidade termica [kJ/(m²K)]",
                id="input-capacidade-termica",
                step=0.01,
                min=0,
                style={"marginBottom": 10},
            ),

            dmc.Button("Enviar ao banco de dados", id="btn-submit-material", color="blue", style={"marginTop": 10}),

            html.Div(id="output-feedback", style={"marginTop": 20}),

            fac.AntdDivider(),

            dmc.Button("Remover linha selecionada", id="remove-material-btn", color="red", style={"marginBottom": 10} , leftSection=DashIconify(icon="mdi:delete-outline"), radius="md",),

            fac.AntdTable(
                columns=[{"title": col, "dataIndex": col} for col in materiais_cadastrados.columns],
                data=materiais_cadastrados.to_dict('records'),
                id="materiais_cadastrados_table",
                locale="en-us",
                pagination=False,
                bordered=True,
                filterOptions={'MATERIAL': {'filterMode': 'keyword'}},
                rowSelectionType='checkbox',
            )

        ])

        vidro_customizado = dmc.Paper(
            withBorder=True,
            shadow="sm",
            p="md",
            radius="md",
            children=[
                dmc.Title("Adicionar vidro customizado ao DB", order=2, mb=10),

                dmc.TextInput(
                    label="Cor do caixilho",
                    placeholder="Cor do caixilho",
                    id="input-cor-caixilho",
                    style={"marginBottom": 10},
                ),

                dmc.TextInput(
                label="Tipo de vidro",
                placeholder="Tipo de vidro",
                id="input-tipo-vidro",
                required=True,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Fator solar",
                id="input-fator-solar",
                step=0.01,
                required=True,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Transmitância luminosa",
                id="input-transmitancia-luminosa",
                step=0.01,
                min=0,
                required=True,
                style={"marginBottom": 10},
            ),

            dmc.NumberInput(
                label="Transmitância térmica",
                id="input-transmitancia-termica",
                step=0.01,
                min=0,
                required=True,
                style={"marginBottom": 10},
            ),

            dmc.Button("Enviar ao banco de dados", id="btn-submit-vidrocustom", color="blue", style={"marginTop": 10}),

            html.Div(id="output-feedback-vidro-custom", style={"marginTop": 20}),

            fac.AntdDivider(),

            dmc.Button("Remover linha selecionada", id="remove-vidro-btn", color="red", style={"marginBottom": 10} , leftSection=DashIconify(icon="mdi:delete-outline"), radius="md",),

            fac.AntdTable(
                columns=[{"title": col, "dataIndex": col} for col in vidros_cadastrados.columns],
                data=vidros_cadastrados.to_dict('records'),
                id="vidros_cadastrados_table",
                locale="en-us",
                pagination=False,
                bordered=True,
                filterOptions={'TIPO DE VIDRO': {'filterMode': 'keyword'}},
                rowSelectionType='checkbox',
            )            

        ])

        cor_customizado = dmc.Paper(
            withBorder=True,
            shadow="sm",
            p="md",
            radius="md",
            children=[

                dmc.Title("Adicionar cor customizado ao DB", order=2, mb=10),

                dmc.TextInput(
                    label="Nome da cor",
                    placeholder="Digite o nome da cor",
                    id="input-nome-cor",
                    required=True,
                    style={"marginBottom": 10},
                ),

                    dmc.NumberInput(
                    label="R",
                    placeholder="Digite o valor de R",
                    id="input-r-corcustom",
                    step=0.01,
                    required=True,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="G",
                    placeholder="Digite o valor de G",
                    id="input-g-corcustom",
                    step=0.01,
                    required=True,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="B",
                    placeholder="Digite o valor de B",
                    id="input-b-corcustom",
                    step=0.01,
                    required=True,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="Digite o valor da Absortância fosca",
                    placeholder="Digite o valor da Absortância fosca",
                    id="input-afosca-corcustom",
                    step=0.01,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="Digite o valor da Absortância semibrilho",
                    placeholder="Digite o valor da Absortância semibrilho",
                    id="input-asemibrilho-corcustom",
                    step=0.01,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="Digite o valor da lpvafosca",
                    placeholder="Digite o valor da lpvafosca",
                    id="input-lpvafosca-corcustom",
                    step=0.01,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="Digite o valor da acfosca",
                    placeholder="Digite o valor da acfosca",
                    id="input-acfosca-corcustom",
                    step=0.01,
                    style={"marginBottom": 10},
                ),

                dmc.NumberInput(
                    label="Digite o valor da lpvafoscaII",
                    placeholder="Digite o valor da lpvafoscaII",
                    id="input-lpvafoscaII-corcustom",
                    step=0.01,
                    style={"marginBottom": 10},
                ),

                dmc.Button("Enviar ao banco de dados", id="btn-submit-corcustom", color="blue", style={"marginTop": 10}),
                
                html.Div(id="output-feedback-corcustom", style={"marginTop": 20}),

                fac.AntdDivider(),

                dmc.Button("Remover linha selecionada", id="remove-cor-btn", color="red", style={"marginBottom": 10} , leftSection=DashIconify(icon="mdi:delete-outline"), radius="md",),

                fac.AntdTable(
                    columns=[{"title": col, "dataIndex": col} for col in cores_cadastrados.columns],
                    data=cores_cadastrados.to_dict('records'),
                    id="cores_cadastrados_table",
                    locale="en-us",
                    pagination=False,
                    bordered=True,
                    filterOptions={'Nomes': {'filterMode': 'keyword'}},
                    rowSelectionType='checkbox',
                )    

        ])

        projetos_cadastrados_customizado = dmc.Paper(
            withBorder=False,
            shadow="sm",
            p="md",
            radius="md",
            id='projetos_cadastrados_customizado',
            children=(
                [form_projeto(x) for x in projetos_cadastrados_ids]
                if len(projetos_cadastrados_ids) > 0
                else [fac.AntdEmpty(locale='en-us')]
            )
        )

        tabs_content = {
            'Adicionar material customizado': material_customizado,
            'Adicionar vidro customizado': vidro_customizado,
            'Adicionar cor customizada': cor_customizado,  
            'Projetos cadastrados': projetos_cadastrados_customizado,
        }

        content = html.Div([

            fac.AntdTabs(
                # type='card',
                centered=True,
                tabBarGutter=60,
                items=[
                    {
                        'key': f'tab{tab}',
                        'label': f'{tab}',
                        # 'icon': fac.AntdIcon(icon=f'antd-{tab_icons.get(tab, "question-circle")}'),
                        'children': tabs_content[tab]
                    }

                    for tab in tabs_content
                ]
            ), 

        ])

    elif selected_key == 'Enviar ao banco de dados':

        return '', dbc.Alert(" 📂 Volte para a seção de projetos (Novo projeto ou Seus projetos cadastrados) para salva-lo no banco de dados", color="warning", className='m-3')

    return menu, content

####################################################################################################################################################################

@callback(
    Output("cores_cadastrados_table", "data"),
    Output('cores_cadastrados_table', 'selectedRowKeys'),
    Input("remove-cor-btn", "n_clicks"),
    Input("cores_cadastrados_table", "data"),
    Input('cores_cadastrados_table', 'selectedRows'),
    Input('cores_cadastrados_table', 'selectedRowKeys'),
)
def remover_cor_selecionada(n_clicks, data, selectedRows, selectedRowKeys):
    
    ctx = dash.callback_context

    if ctx.triggered_id == "remove-cor-btn" and selectedRows:

        keys = selectedRowKeys
        indices_para_remover = [int(key) for key in keys]

        data_df = pd.DataFrame(data)
        data_df = data_df.drop(indices_para_remover)
        data = data_df.to_dict('records')
        for row in selectedRows:
            delete_color_by_name(row['Nomes'])

        return data, []

    return dash.no_update, selectedRowKeys

####################################################################################################################################################################

@callback(
    Output("vidros_cadastrados_table", "data"),
    Output('vidros_cadastrados_table', 'selectedRowKeys'),
    Input("remove-vidro-btn", "n_clicks"),
    Input("vidros_cadastrados_table", "data"),
    Input('vidros_cadastrados_table', 'selectedRows'),
    Input('vidros_cadastrados_table', 'selectedRowKeys'),
)
def remover_vidro_selecionado(n_clicks, data, selectedRows, selectedRowKeys):

    ctx = dash.callback_context

    if ctx.triggered_id == "remove-vidro-btn" and selectedRows:

        keys = selectedRowKeys
        indices_para_remover = [int(key) for key in keys]

        data_df = pd.DataFrame(data)
        data_df = data_df.drop(indices_para_remover)
        data = data_df.to_dict('records')
        for row in selectedRows:
            delete_vidro_by_type(row['TIPO DE VIDRO'])

        return data, []

    return dash.no_update, selectedRowKeys

####################################################################################################################################################################

@callback(
    Output("materiais_cadastrados_table", "data"),
    Output('materiais_cadastrados_table', 'selectedRowKeys'),
    Input("remove-material-btn", "n_clicks"),
    Input("materiais_cadastrados_table", "data"),
    Input('materiais_cadastrados_table', 'selectedRows'),
    Input('materiais_cadastrados_table', 'selectedRowKeys'),
)
def remover_material_selecionado(n_clicks, data, selectedRows, selectedRowKeys):

    ctx = dash.callback_context

    if ctx.triggered_id == "remove-material-btn" and selectedRows:

        keys = selectedRowKeys
        indices_para_remover = [int(key) for key in keys]

        data_df = pd.DataFrame(data)
        data_df = data_df.drop(indices_para_remover)
        data = data_df.to_dict('records')
        for row in selectedRows:
            delete_material_by_name(row['MATERIAL'])

        return data, []

    return dash.no_update, selectedRowKeys

####################################################################################################################################################################

@callback(
    Output("usuario-logado", "children"),
    Output('sidebar-menu', 'menuItems'),
    Input("usuario-logado", "id"),  # Dispara o callback ao carregar a página
)
def mostrar_usuario(_):

    user = session.get('username')  # Obtém o nome do usuário autenticado
    user_type = session.get('user_type')

    if user_type == 'admin':

        menuItems = [
            {'component': 'Item', 'props': {'key': 'Novo projeto', 'title': 'Novo projeto', 'icon': 'antd-folder-add'}},
            {'component': 'Item', 'props': {'key': 'Seus projetos cadastrados', 'title': 'Seus projetos cadastrados', 'icon': 'antd-folder-open'}},
            {'component': 'Item', 'props': {'key': 'Montar relatório', 'title': 'Montar relatório', 'icon': 'antd-line-chart'}},
            # {'component': 'Item', 'props': {'key': 'Enviar ao banco de dados', 'title': 'Enviar ao banco de dados', 'icon': 'fc-add-database'}},
            {'component': 'Item', 'props': {'key': 'Gerenciar itens do banco', 'title': 'Gerenciar itens do banco', 'icon': 'antd-cloud-server'}},
            {'component': 'Item', 'props': {'key': 'Gerenciar usuários', 'title': 'Gerenciar usuários', 'icon': 'antd-team'}},
        ]

    else:

        menuItems = [
            {'component': 'Item', 'props': {'key': 'Novo projeto', 'title': 'Novo projeto', 'icon': 'antd-folder-add'}},
            {'component': 'Item', 'props': {'key': 'Seus projetos cadastrados', 'title': 'Seus projetos cadastrados', 'icon': 'antd-folder-open'}},
            {'component': 'Item', 'props': {'key': 'Montar relatório', 'title': 'Montar relatório', 'icon': 'antd-line-chart'}},
            # {'component': 'Item', 'props': {'key': 'Enviar ao banco de dados', 'title': 'Enviar ao banco de dados', 'icon': 'fc-add-database'}},
        ]    

    return html.H5(f"Bem vindo\n{user.title()}", className='fw-bold'), menuItems

####################################################################################################################################################################

@callback(
Output('page-content', 'children', allow_duplicate=True),
Input('projetos_cadastrados', 'currentKey'),
prevent_initial_call='initial_duplicate',
)
def update_content(id_projeto):

    if id_projeto is not None:

        dados_projeto = get_projetos(id_projeto)

        # Verifica se o objeto ambientes esta vazio
        if not dados_projeto.get('ambientes'):

            # Se estiver vazio, inicializa como uma lista vazia
            dados_projeto['ambientes'] = {

                    'ambiente1': {

                        'torre_casa': 'Padrão',
                        'pavimento': 'Terreo',
                        'unidade': 'UHX',
                        'ambiente': 'sala',
                        'area_ambiente': 10,
                        'esquadrias': [],
                        'qtdade_esquadrias':[{'esquadrias': 'indicador1', 'quantidade': 1}],
                    },

            }

        projeto = Projeto(**dados_projeto).exibir_infos()
        
        return projeto
    
    elif id_projeto:

        projeto = get_projetos(id_projeto)
        projeto = Projeto(**projeto).exibir_infos()

        return projeto
    
    else:
        return dash.no_update
     
####################################################################################################################################################################

@callback(
Output("json-projeto", "data"),
Output("modal-confirmacao", "is_open", allow_duplicate=True),
Output("mensagem", "children"),
Output("enviar-banco-btn", "n_clicks"),
Input("enviar-banco-btn", "n_clicks"),
Input("numero_projeto", "value"),
Input("nome_projeto", "value"),
Input("numero_pavimentos", "value"),
Input("pe_direito", "value"),
Input({'type': 'comentario_confirmacao_dados', 'index': ALL}, 'value'),
Input({'type': 'confirmacao_dados', 'index': ALL}, 'value'),
Input({'type': 'cores-nome', 'index': ALL}, 'value'),
Input({'type': 'cores-R', 'index': ALL}, 'value'),
Input({'type': 'cores-G', 'index': ALL}, 'value'),
Input({'type': 'cores-B', 'index': ALL}, 'value'),
Input({'type': 'cores-mais-proxima', 'index': ALL}, 'value'),
Input({'type': 'absortancia-mais-proxima', 'index': ALL}, 'value'),
Input("numero_proposta", "value"),
Input("nome_requerente", "value"),
Input("numero_unidades", "value"),
Input("cnpj", "value"),
Input("nome_empreendimento", "value"),
Input("cep_empreendimento", "value"),
Input("link_entorno", "value"),
Input("nome_requisitante", "value"),
Input("cep_requisitante", "value"),
Input("zona_bioclimatica", "value"),
Input("regiao", "value"),
Input("editable-table", "data"),
Input({'type': 'materiais-table', 'index': ALL}, 'data'),
Input({'type': 'Rtotal', 'index': ALL}, 'value'),
Input({'type': 'CT', 'index': ALL}, 'value'),
Input({'type': 'U', 'index': ALL}, 'value'),
Input({'type': 'criterio', 'index': ALL}, 'value'),
Input('status_projeto', 'value'),
Input({'type': 'area_ambiente', 'index': ALL}, 'value'),
Input({'type': 'ambiente', 'index': ALL}, 'value'),
Input({'type': 'torre_casa', 'index': ALL}, 'value'),
Input({'type': 'pavimento', 'index': ALL}, 'value'),
Input({'type': 'unidade', 'index': ALL}, 'value'),
Input({'type': 'ambiente-esquadria-checkbox', 'index': ALL}, 'value'),
Input("rua_requisitante", "value"), # 37
Input("numero_requisitante", "value"),
Input("bairro_requisitante", "value"),
Input("cidade_requisitante", "value"),
Input("estado_requisitante", "value"),
Input("complemento_requisitante", "value"),
Input("rua_empreendimento", "value"),
Input("numero_empreendimento", "value"),
Input("bairro_empreendimento", "value"),
Input("cidade_empreendimento", "value"),
Input("estado_empreendimento", "value"),
Input("arquivo_climatico", "value"), # 48
Input({'type': 'lado_maior2_ambiente', 'index': ALL}, 'value'),
Input({'type': 'lado_menor2_ambiente', 'index': ALL}, 'value'),
Input({'type': 'situacao_abertura_ventilacao', 'index': ALL}, 'children'),
Input({'type': 'situacao_elementos_transparentes', 'index': ALL}, 'children'),
Input('data_acesso', 'children'),
Input({'type': 'quantidade-ambiente-esquadria', 'index': ALL}, 'data'),
prevent_initial_call='initial_duplicate',
)
def salvar_infos(*valores):
    
    if ctx.triggered_id == "enviar-banco-btn" and valores[0] > 0:

        # Montando o template para enviar ao banco de dados

        ##################### CHECKLISTS #######################
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

        keys = [item for itens in secoes.values() for item in itens]
        i = len(valores[5])

        checklists = {
            key: {
                'recebido': valores[6][idx] if idx < len(valores[6]) else None,
                'comentario': valores[5][idx] if idx < len(valores[5]) else None
            }
            for key, idx in zip(keys, range(i))
        }

        ##################### CORES #######################
        cores = {

            'numero_pavimentos': valores[3],
            'pe_direito': valores[4],

            'Fachada 1': {

                'nome': valores[7][0],
                'r': valores[8][0],
                'g': valores[9][0],
                'b': valores[10][0],
                'cor_prox': valores[11][0],
                'abs_prox': valores[12][0],
            },

            'Fachada 2': {

                'nome': valores[7][1],
                'r': valores[8][1],
                'g': valores[9][1],
                'b': valores[10][1],
                'cor_prox': valores[11][1],
                'abs_prox': valores[12][1],

            },

            'Fachada 3': {

                'nome': valores[7][2],
                'r': valores[8][2],
                'g': valores[9][2],
                'b': valores[10][2],
                'cor_prox': valores[11][2],
                'abs_prox': valores[12][2],

            },

            'Parede interna': {

                'nome': valores[7][3],
                'r': valores[8][3],
                'g': valores[9][3],
                'b': valores[10][3],
                'cor_prox': valores[11][3],
                'abs_prox': valores[12][3],
                
            },

            'Piso': {

                'nome': valores[7][4],
                'r': valores[8][4],
                'g': valores[9][4],
                'b': valores[10][4],
                'cor_prox': valores[11][4],
                'abs_prox': valores[12][4],
   
            },

            'Teto ou forro': {

                'nome': valores[7][5],
                'r': valores[8][5],
                'g': valores[9][5],
                'b': valores[10][5],
                'cor_prox': valores[11][5],
                'abs_prox': valores[12][5],

            },

            'Cobertura': {

                'nome': valores[7][6],
                'r': valores[8][6],
                'g': valores[9][6],
                'b': valores[10][6],
                'cor_prox': valores[11][6],
                'abs_prox': valores[12][6],
                
            },

            'Piso da varanda': {

                'nome': valores[7][7],
                'r': valores[8][7],
                'g': valores[9][7],
                'b': valores[10][7],
                'cor_prox': valores[11][7],
                'abs_prox': valores[12][7],

            },

            'Piso externo': {

                'nome': valores[7][8],
                'r': valores[8][8],
                'g': valores[9][8],
                'b': valores[10][8],
                'cor_prox': valores[11][8],
                'abs_prox': valores[12][8],
                
            },

            'Elemento de sombreamento': {

                'nome': valores[7][9],
                'r': valores[8][9],
                'g': valores[9][9],
                'b': valores[10][9],
                'cor_prox': valores[11][9],
                'abs_prox': valores[12][9],
                
            },

            'Muro/fechamento': {

                'nome': valores[7][10],
                'r': valores[8][10],
                'g': valores[9][10],
                'b': valores[10][10],
                'cor_prox': valores[11][10],
                'abs_prox': valores[12][10],

            },

        }

        ##################### INFORMACOES DO PROJETO #######################
        informacoes_projeto = {
    
            "numero_projeto": valores[1],
            "nome_projeto": valores[2],
            "numero_proposta": valores[13],
            "nome_requerente": valores[14],
            "numero_unidades": valores[15],
            "cnpj": valores[16],
            "nome_empreendimento": valores[17],
            "cep_empreendimento": valores[18],
            "link_entorno": valores[19],
            "nome_requisitante": valores[20],
            'cep_requisitante': valores[21],
            'zona_bioclimatica': valores[22],
            'regiao': valores[23],
            'rua_requisitante': valores[37],
            'numero_requisitante': valores[38],
            'bairro_requisitante': valores[39],
            'cidade_requisitante': valores[40],
            'estado_requisitante': valores[41],
            'complemento_requisitante': valores[42],
            'rua_empreendimento': valores[43],
            'numero_empreendimento': valores[44],
            'bairro_empreendimento': valores[45],
            'cidade_empreendimento': valores[46],
            'estado_empreendimento': valores[47],
            'arquivo_climatico': valores[48],
            'data_acesso': valores[53],   
        }

        ##################### ESQUADRIAS #######################
        # esquadrias = {f'esquadria{i+1}': dados for i, dados in enumerate(valores[24])}
        esquadrias = {i: dados for i, dados in enumerate(valores[24])}

        ##################### MATERIAIS #######################
        materiais_data = valores[25]
        r_totais = valores[26]
        cts = valores[27]
        us = valores[28]
        criterios = valores[29]

        # Criando o dicionário dos materiais
        materiais = {}
        nomes_elementos = ['Parede externa', 'Parede interna', 'Cobertura edifício', 'Piso (laje)']

        for idx, (nome, camadas) in enumerate(zip(nomes_elementos, materiais_data)):
            materiais[nome] = {}
            for i, camada in enumerate(camadas, 1):
                materiais[nome][i] = {
                    'Tipo do material': camada['Tipo do material'].get('value', ''),
                    'Espessura [m]': camada['Espessura [m]'],
                    'Densidade [kg/m³]': camada['Densidade [kg/m³]'],
                    'Condutividade [W/mK]': camada['Condutividade [W/mK]'],
                    'Calor específico [kJ/KgK]': camada['Calor específico [kJ/KgK]'],
                    'Resistência [m²K/W]': camada['Resistência [m²K/W]'],
                }

            # Inserindo os dados gerais do elemento
            materiais[nome]['R total'] = r_totais[idx]
            materiais[nome]['CT'] = cts[idx]
            materiais[nome]['U'] = us[idx]
            materiais[nome]['Criterio'] = criterios[idx]

        ##################### AMBIENTES #######################
        ambientes = {}
        for idx, (area_ambiente, ambiente, torre_casa, pavimento, unidade, esquadrias_ambiente, lado_maior2, lado_menor2, situacao_abertura_ventilacao, situacao_elementos_transparentes, qtdade_esquadrias) in enumerate(zip(valores[31], valores[32], valores[33], valores[34], valores[35], valores[36], valores[49], valores[50], valores[51], valores[52], valores[54]), 1):
            
            situacao_abertura_ventilacao = situacao_abertura_ventilacao.split('Situação:')[-1]
            situacao_elementos_transparentes = situacao_elementos_transparentes.split('Situação:')[-1]
            
            ambientes[f'ambiente{idx}'] = {
                'torre_casa': torre_casa,
                'pavimento': pavimento,
                'unidade': unidade,
                'ambiente': ambiente,
                'area_ambiente': area_ambiente,
                'esquadrias': esquadrias_ambiente,
                'qtdade_esquadrias': qtdade_esquadrias,
                'lado_maior2': lado_maior2,
                'lado_menor2': lado_menor2,
                'situacao_abertura_ventilacao': situacao_abertura_ventilacao,
                'situacao_elementos_transparentes': situacao_elementos_transparentes,

            }

        ##################### PROJETO MONTADO #######################
        dados_projeto = {
            'informacoes_projeto': informacoes_projeto,
            'checklists': checklists,
            'cores': cores,
            'esquadrias': esquadrias,
            'materiais': materiais,
            'ambientes': ambientes,
            'status': valores[30],
            'usuario': session.get('username') ,
        }

        ##################### VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS #######################
        def validar_campos_obrigatorios(dados_projeto):
            erros = []
            
            # Validar informações básicas do projeto
            info_proj = dados_projeto.get('informacoes_projeto', {})
            campos_obrigatorios_info = {
                'numero_projeto': 'Número do projeto',
                'nome_projeto': 'Nome do projeto',
                'nome_requerente': 'Nome do requerente',
                'nome_empreendimento': 'Nome do empreendimento',
                'zona_bioclimatica': 'Zona bioclimática',
                'regiao': 'Região'
            }
            
            for campo, nome_campo in campos_obrigatorios_info.items():
                if not info_proj.get(campo) or str(info_proj.get(campo)).strip() == '':
                    erros.append(f"❌ {nome_campo} é obrigatório")
            
            # Validar cores
            cores_data = dados_projeto.get('cores', {})
            if not cores_data.get('numero_pavimentos') or cores_data.get('numero_pavimentos') == 0:
                erros.append("❌ Número de pavimentos é obrigatório")
            if not cores_data.get('pe_direito') or cores_data.get('pe_direito') == 0:
                erros.append("❌ Pé direito é obrigatório")
            
            # Validar se pelo menos uma cor foi definida com valores válidos
            cores_principais = ['Fachada 1', 'Parede interna', 'Piso', 'Teto ou forro', 'Cobertura']
            cores_validas = 0
            for cor_nome in cores_principais:
                cor_info = cores_data.get(cor_nome, {})
                if (cor_info.get('nome') and 
                    cor_info.get('r') is not None and 
                    cor_info.get('g') is not None and 
                    cor_info.get('b') is not None):
                    cores_validas += 1
            
            if cores_validas == 0:
                erros.append("❌ Pelo menos uma cor principal deve ser definida (Fachada 1, Parede interna, Piso, Teto ou Cobertura)")
            
            # Validar esquadrias
            esquadrias_data = dados_projeto.get('esquadrias', {})
            if not esquadrias_data or len(esquadrias_data) == 0:
                erros.append("❌ Pelo menos uma esquadria deve ser cadastrada")
            
            # Validar materiais
            materiais_data = dados_projeto.get('materiais', {})
            elementos_obrigatorios = ['Parede externa', 'Parede interna', 'Cobertura edifício', 'Piso (laje)']
            
            for elemento in elementos_obrigatorios:
                elemento_data = materiais_data.get(elemento, {})
                if not elemento_data:
                    erros.append(f"❌ Material para {elemento} é obrigatório")
                else:
                    # Verificar se há pelo menos uma camada
                    camadas = {k: v for k, v in elemento_data.items() if isinstance(k, int)}
                    if not camadas:
                        erros.append(f"❌ {elemento} deve ter pelo menos uma camada de material")
            
            # Validar ambientes
            ambientes_data = dados_projeto.get('ambientes', {})
            if not ambientes_data or len(ambientes_data) == 0:
                erros.append("❌ Pelo menos um ambiente deve ser cadastrado")
            
            return erros

        # Executar validação
        erros_validacao = validar_campos_obrigatorios(dados_projeto)
        
        if erros_validacao:
            mensagem_erro = html.Div([
                dmc.Alert(
                    title="❌ Campos obrigatórios não preenchidos",
                    children=[
                        html.P("Por favor, preencha os seguintes campos:"),
                        html.Ul([html.Li(erro) for erro in erros_validacao])
                    ],
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ])
            return dados_projeto, False, mensagem_erro, 0

        ##################### ERROS E ADICIONAR AO DB #######################
        erro = checa_projeto(dados_projeto)
        id_projeto = str(dados_projeto.get('informacoes_projeto')['numero_projeto'])

        if erro == None:
            add_projeto(dados_projeto)
            return dados_projeto, False, dmc.Notification(
                title="Projeto enviado com sucesso!",
                color="green",
                action="show",
                message=f"Projeto {id_projeto} adicionado ao banco de dados",
                icon=DashIconify(icon="flat-color-icons:ok"),
            ), 0

        else:
            # return dados_projeto, True, 0
            return dados_projeto, True, '', 0

    return dash.no_update, dash.no_update, '', 0

####################################################################################################################################################################

@callback(
Output("modal-confirmacao", "is_open"),
Output("mensagem-confirmacao", "children"),
Input('json-projeto', 'data'),
Input("btn-sobrescrever", "n_clicks"),
Input("btn-cancelar", "n_clicks"),
)
def mostrar_mensagem(json_projeto, n_clicks_sobrescrever, n_clicks_cancelar):
    
    ctx = dash.callback_context

    if ctx.triggered_id == "btn-sobrescrever":

        add_projeto(json_projeto)
        id_projeto = str(json_projeto.get('informacoes_projeto')['numero_projeto'])
        # return False
        return False, dmc.Notification(
                title="Projeto enviado com sucesso!",
                color="green",
                action="show",
                message=f"Projeto {id_projeto} adicionado ao banco de dados",
                icon=DashIconify(icon="flat-color-icons:ok"),
            ),
    
    elif ctx.triggered_id == "btn-cancelar":

        return False, ''

    return dash.no_update

####################################################################################################################################################################

@callback(
Output('page-content', 'children', allow_duplicate=True),
Input('projetos_cadastrados_apresentacao', 'currentKey'),
prevent_initial_call='initial_duplicate',
)
def ajusta_apresentacao(id_projeto):

    if id_projeto is None:
        return dash.no_update
    
    else:

        # Pegando os dados do projeto
        dados_projeto = get_projetos(id_projeto)
        conteudo = form_apresentacao(dados_projeto)

        return conteudo

####################################################################################################################################################################

@callback(
    Output("output-feedback", "children"),
    Input("btn-submit-material", "n_clicks"),
    Input("input-material", "value"),
    Input("input-tipo-material", "value"),
    Input("input-calor-especifico", "value"),
    Input("input-condutividade", "value"),
    Input("input-densidade", "value"),
    Input("input-resistencia", "value"),
    Input("input-capacidade-termica", "value"),
)
def salvar_material(n_clicks, material, tipo, calor, cond, dens, resistencia, capacidade_termica):

    ctx = dash.callback_context

    if ctx.triggered_id == "btn-submit-material":

        resultado = add_material_custom(material, calor, tipo, cond, dens, resistencia, capacidade_termica)

        if resultado:
            return dmc.Alert("Material adicionado com sucesso!", color="green", duration=1000)
        else:
            return dmc.Alert(f"Erro: {resultado}", color="red", duration=1000)

####################################################################################################################################################################

@callback(
    Output("output-feedback-vidro-custom", "children"),
    Input("btn-submit-vidrocustom", "n_clicks"),
    Input("input-cor-caixilho", "value"),
    Input("input-tipo-vidro", "value"),
    Input("input-fator-solar", "value"),
    Input("input-transmitancia-luminosa", "value"),
    Input("input-transmitancia-termica", "value"),
)
def salvar_vidro_custom(n_clicks, cor_caixilho, tipo_vidro, fator_solar, transmitancia_luminosa, transmitancia_termica):

    ctx = dash.callback_context

    if ctx.triggered_id == "btn-submit-vidrocustom":

        resultado = add_vidro_custom(cor_caixilho, tipo_vidro, fator_solar, transmitancia_luminosa, transmitancia_termica)

        if resultado:
            return dmc.Alert("Vidro adicionado com sucesso!", color="green", duration=1000)
        else:
            return dmc.Alert(f"Erro: {resultado}", color="red", duration=1000)

####################################################################################################################################################################

@callback(
    Output("output-feedback-corcustom", "children"),
    Input("btn-submit-corcustom", "n_clicks"),
    Input("input-nome-cor", "value"),
    Input("input-r-corcustom", "value"),
    Input("input-g-corcustom", "value"),
    Input("input-b-corcustom", "value"),
    Input("input-afosca-corcustom", "value"),
    Input("input-asemibrilho-corcustom", "value"),
    Input("input-lpvafosca-corcustom", "value"),
    Input("input-acfosca-corcustom", "value"),
    Input("input-lpvafoscaII-corcustom", "value"),
)
def salvar_cor_custom(n_clicks, nome_cor, r, g, b, afosca, asemibrilho, lpvafosca, acfosca, lpvafoscaII):

    ctx = dash.callback_context

    if ctx.triggered_id == "btn-submit-corcustom":

        resultado = add_rgb_custom(nome_cor, r, g, b, afosca, asemibrilho, lpvafosca, acfosca, lpvafoscaII)

        if resultado:
            return dmc.Alert("Cor adicionada com sucesso!", color="green", duration=1000)
        else:
            return dmc.Alert(f"Erro: {resultado}", color="red", duration=1000)
        
####################################################################################################################################################################

@callback(
    Output({'type': 'user-message', 'index': MATCH}, 'children'),
    Output({'type': 'input-username', 'index': MATCH}, 'value'),
    Output({'type': 'input-email', 'index': MATCH}, 'value'),
    Output({'type': 'input-password', 'index': MATCH}, 'value'),
    Output({'type': 'input-tipo', 'index': MATCH}, 'value'),
    Input({'type': 'btn-save-user', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'btn-delete-user', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'input-username', 'index': MATCH}, 'value'),
    Input({'type': 'input-email', 'index': MATCH}, 'value'),
    Input({'type': 'input-password', 'index': MATCH}, 'value'),
    Input({'type': 'input-tipo', 'index': MATCH}, 'value'),
)
def altera_deleta_usuario(n_clicks_save, n_clicks_delete, username, email, password, tipo):
    if not ctx.triggered_id:
        raise dash.exceptions.PreventUpdate

    if ctx.triggered_id['type'] == 'btn-save-user':
        resultado = add_usuarios(username=username, email=email, password=password, tipo=tipo, name=username)

        if resultado is True:
            return (
                dmc.Alert("Usuário alterado com sucesso!", color="green", duration=1000),
                username, email, password, tipo  # mantém os dados após alteração
            )
        else:
            return (
                dmc.Alert(f"Erro: {resultado}", color="red", duration=1000),
                username, email, password, tipo
            )

    elif ctx.triggered_id['type'] == 'btn-delete-user':
        resultado = delete_usuario(username)

        if resultado is True:
            return (
                dmc.Alert("Usuário deletado com sucesso!", color="green", duration=1000),
                "", "", "", ""  # limpa os campos depois do delete
            )
        else:
            return (
                dmc.Alert(f"Erro: {resultado}", color="red", duration=1000),
                username, email, password, tipo
            )

    else:
        raise dash.exceptions.PreventUpdate

####################################################################################################################################################################

@callback(
    Output("output-feedback-usuario", "children"),
    Output("reload-usuarios", "data"),
    Input("btn-submit-usuario", "n_clicks"),
    Input("input-usuario", "value"),
    Input("input-senha-usuario", "value"),
    Input("select-user-type", "value"),
    Input("input-email-usuario", "value"),
)
def salvar_usuario(n_clicks, usuario, senha, tipo_usuario, email):
    
        ctx = dash.callback_context
    
        if ctx.triggered_id == "btn-submit-usuario":
    
            resultado = add_usuarios(username=usuario, password=senha, tipo=tipo_usuario, name=usuario, email=email)
    
            if resultado:
                return dmc.Alert("Usuário adicionado com sucesso!", color="green", duration=1000), n_clicks
            else:
                return dmc.Alert(f"Erro: {resultado}", color="red", duration=1000), 0
        
        return "", 0

####################################################################################################################################################################

@callback(
    Output("usuarios_existentes", "children"),
    Input("reload-usuarios", "data"),
    prevent_initial_call=True
)
def atualizar_lista_usuarios(trigger):
    """Atualiza a lista de usuários existentes quando novos usuários são adicionados"""
    if trigger > 0:
        # Recarregar usuários do banco de dados
        usuarios_dict = get_users()['credentials']['usernames']
        usuarios_gerenciados = list(usuarios_dict.keys())
        
        return [
            dcc.Store(id="reload-usuarios", data=0),
            html.Div([
                form_user(**usuarios_dict[usuario_gerenciado]) for usuario_gerenciado in usuarios_gerenciados 
            ]),
        ]
    
    return dash.no_update

####################################################################################################################################################################

@callback(
    Output({'type': 'projeto-text-delete', 'index': MATCH}, 'children'),
    Input({'type': 'btn-delete-projeto', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'input-numero-projeto', 'index': MATCH}, 'value'),
)
def del_projeto_custom(n_clicks, numero_projeto):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    resultado = delete_projeto(numero_projeto)
    if resultado is True:
        return dmc.Alert("Projeto deletado com sucesso!", color="green", mt=10)
    else:
        return dmc.Alert(f"Erro: {resultado}", color="red")

####################################################################################################################################################################


@callback(
    Output('page-content', 'children', allow_duplicate=True),
    Input('logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    if not n_clicks:
        return dash.no_update

    # Use both dcc.Location and JavaScript fallback for reliable logout
    return html.Div([
        dcc.Location(pathname='/logout', id='logout-redirect'),
        dmc.Container([
            dmc.Center([
                dmc.Paper([
                    dmc.Title("Saindo...", order=2, style={"textAlign": "center", "marginBottom": "20px"}),
                    dmc.Loader(color="red", size="lg", style={"margin": "0 auto"})
                ], p="xl", shadow="md", radius="md")
            ])
        ], style={"marginTop": "50px"}),
        
        # JavaScript fallback
        html.Script("""
            setTimeout(function() {
                if (window.location.pathname !== '/logout') {
                    window.location.href = '/logout';
                }
            }, 500);
        """)
    ])

####################################################################################################################################################################

if __name__ == '__main__':
    app.run(debug=False)