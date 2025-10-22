import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import pdb
from dotenv import load_dotenv

load_dotenv()  # carrega o .env
firebase_key_json_origem = os.getenv("FIREBASE_KEY_JSON2")
cred_dict_origem = json.loads(firebase_key_json_origem)  # converte string JSON para dict

firebase_key_json_destino = os.getenv("FIREBASE_KEY_JSON3")
cred_dict_destino = json.loads(firebase_key_json_destino)  # converte string JSON para dict

# Conectar ao primeiro projeto (origem)
cred_origem = credentials.Certificate(cred_dict_origem)
app_origem = firebase_admin.initialize_app(cred_origem, name='origem')
db_origem = firestore.client(app_origem)

# Conectar ao segundo projeto (destino)
cred_destino = credentials.Certificate(cred_dict_destino)
app_destino = firebase_admin.initialize_app(cred_destino, name='destino')
db_destino = firestore.client(app_destino)

for colecao in ['cores', 'materiais', 'projetos', 'ambientes', 'usuarios']:

    # Buscar dados da coleção no projeto origem
    docs = db_origem.collection(colecao).stream()

    # Copiar cada documento para o projeto destino
    for doc in docs:
        db_destino.collection(colecao).document(doc.id).set(doc.to_dict())

    print(f"Dados transferidos com sucesso da coleção {colecao}.")