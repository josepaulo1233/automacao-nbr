"""
Script para gerenciar usuários no banco de dados local
Permite visualizar, adicionar, editar e deletar usuários
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import hashlib
from datetime import datetime
from db.db_local import LocalDatabase

def hash_senha(senha):
    """Gera hash da senha para segurança"""
    return hashlib.sha256(senha.encode()).hexdigest()

def mostrar_status_usuarios():
    """Mostra o status atual dos usuários no banco"""
    print("=" * 60)
    print("👥 STATUS ATUAL DOS USUÁRIOS")
    print("=" * 60)
    
    db = LocalDatabase()
    
    try:

        cursor = db.conn.cursor()
        # Verificar se a tabela existe
        result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'", fetch=True)
        if not result:
            print("⚠️ Tabela 'usuarios' não encontrada no banco!")
            print("💡 A tabela será criada automaticamente ao adicionar o primeiro usuário.")
            return
        
        # Contar usuários
        total_result = db.execute_query("SELECT COUNT(*) FROM usuarios", fetch=True)
        total = total_result[0][0] if total_result else 0
        print(f"Total de usuários no banco: {total}")
        
        if total > 0:
            cursor.execute("SELECT * FROM usuarios LIMIT 5")
            usuarios = cursor.fetchall()
            print("\nPrimeiros 5 usuários:")
            for i, usuario in enumerate(usuarios):
                nome = usuario[1] if len(usuario) > 1 else 'N/A'
                email = usuario[2] if len(usuario) > 2 else 'N/A'
                perfil = usuario[4] if len(usuario) > 4 else 'N/A'
                ativo = "Ativo" if (len(usuario) > 5 and usuario[5]) else "Inativo"
                print(f"  {i+1}. ID: {usuario[0]} | Nome: {nome} | Email: {email} | Perfil: {perfil} | Status: {ativo}")
            
            if total > 5:
                print(f"  ... e mais {total - 5} usuários")
        else:
            print("⚠️ Nenhum usuário encontrado no banco!")
            
    except Exception as e:
        print(f"❌ Erro ao consultar usuários: {str(e)}")
    
    print()

def criar_tabela_usuarios():
    """Cria a tabela de usuários se não existir"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                perfil TEXT DEFAULT 'usuario',
                ativo INTEGER DEFAULT 1,
                data_criacao TEXT DEFAULT (datetime('now')),
                ultimo_acesso TEXT
            )
        """)
        db.conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela de usuários: {str(e)}")
        return False

def listar_todos_usuarios():
    """Lista todos os usuários do banco (sem mostrar senhas)"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT id, nome, email, perfil, ativo, data_criacao, ultimo_acesso FROM usuarios")
        usuarios = cursor.fetchall()
        
        if usuarios:
            print(f"\n👥 LISTA COMPLETA ({len(usuarios)} usuários):")
            print("-" * 120)
            print("ID  | Nome                | Email               | Perfil      | Status   | Criação     | Último Acesso")
            print("-" * 120)
            
            for usuario in usuarios:
                id_user, nome, email, perfil, ativo, data_criacao, ultimo_acesso = usuario
                status = "Ativo" if ativo else "Inativo"
                data_criacao = data_criacao[:10] if data_criacao else 'N/A'
                ultimo_acesso = ultimo_acesso[:10] if ultimo_acesso else 'Nunca'
                
                print(f"{id_user:3d} | {nome[:19]:<19} | {email[:19]:<19} | {perfil[:11]:<11} | {status:<8} | {data_criacao:<11} | {ultimo_acesso}")
            print("-" * 120)
        else:
            print("⚠️ Nenhum usuário encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {str(e)}")

def deletar_todos_usuarios():
    """Deleta todos os usuários do banco"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM usuarios")
        db.conn.commit()
        print("✅ Todos os usuários foram deletados!")
        return True
    except Exception as e:
        print(f"❌ Erro ao deletar usuários: {str(e)}")
        return False

def deletar_usuario_por_id(usuario_id):
    """Deleta um usuário específico por ID"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        
        if cursor.rowcount > 0:
            db.conn.commit()
            print(f"✅ Usuário ID {usuario_id} deletado com sucesso!")
            return True
        else:
            print(f"❌ Nenhum usuário encontrado com ID {usuario_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar usuário: {str(e)}")
        return False

def adicionar_usuario():
    """Adiciona um novo usuário ao banco"""
    db = LocalDatabase()
    
    # Garante que a tabela existe
    if not criar_tabela_usuarios():
        return False
    
    print("\n👥 ADICIONAR NOVO USUÁRIO")
    print("-" * 35)
    
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()
    confirma_senha = input("Confirme a senha: ").strip()
    
    print("\nPerfis disponíveis:")
    print("1. admin - Administrador do sistema")
    print("2. gerente - Gerente de projetos")
    print("3. usuario - Usuário comum")
    print("4. visualizador - Apenas visualização")
    
    opcao_perfil = input("Escolha o perfil (1-4): ").strip()
    
    perfil_map = {
        '1': 'admin',
        '2': 'gerente',
        '3': 'usuario',
        '4': 'visualizador'
    }
    
    perfil = perfil_map.get(opcao_perfil, 'usuario')
    
    # Validações
    if not nome or not email or not senha:
        print("❌ Nome, email e senha são obrigatórios!")
        return False
    
    if senha != confirma_senha:
        print("❌ Senhas não conferem!")
        return False
    
    if len(senha) < 6:
        print("❌ Senha deve ter pelo menos 6 caracteres!")
        return False
    
    try:
        cursor = db.conn.cursor()
        
        # Verificar se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"❌ Já existe um usuário com o email '{email}'!")
            return False
        
        # Hash da senha
        senha_hash = hash_senha(senha)
        
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, perfil, ativo, data_criacao)
            VALUES (?, ?, ?, ?, 1, datetime('now'))
        """, (nome, email, senha_hash, perfil))
        
        db.conn.commit()
        print(f"✅ Usuário '{nome}' adicionado com sucesso!")
        print(f"   Email: {email}")
        print(f"   Perfil: {perfil}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar usuário: {str(e)}")
        return False

def alterar_status_usuario():
    """Altera o status (ativo/inativo) de um usuário"""
    db = LocalDatabase()
    
    try:
        listar_todos_usuarios()
        usuario_id = int(input("\nDigite o ID do usuário para alterar status: ").strip())
        
        cursor = db.conn.cursor()
        cursor.execute("SELECT nome, ativo FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"❌ Nenhum usuário encontrado com ID {usuario_id}")
            return False
        
        nome, ativo_atual = resultado
        novo_status = 0 if ativo_atual else 1
        status_texto = "ativo" if novo_status else "inativo"
        
        cursor.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (novo_status, usuario_id))
        db.conn.commit()
        
        print(f"✅ Usuário '{nome}' agora está {status_texto}!")
        return True
        
    except ValueError:
        print("❌ ID deve ser um número!")
        return False
    except Exception as e:
        print(f"❌ Erro ao alterar status: {str(e)}")
        return False

def resetar_senha_usuario():
    """Reseta a senha de um usuário"""
    db = LocalDatabase()
    
    try:
        listar_todos_usuarios()
        usuario_id = int(input("\nDigite o ID do usuário para resetar senha: ").strip())
        
        nova_senha = input("Nova senha: ").strip()
        confirma_senha = input("Confirme a nova senha: ").strip()
        
        if nova_senha != confirma_senha:
            print("❌ Senhas não conferem!")
            return False
        
        if len(nova_senha) < 6:
            print("❌ Senha deve ter pelo menos 6 caracteres!")
            return False
        
        cursor = db.conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"❌ Nenhum usuário encontrado com ID {usuario_id}")
            return False
        
        nome = resultado[0]
        senha_hash = hash_senha(nova_senha)
        
        cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (senha_hash, usuario_id))
        db.conn.commit()
        
        print(f"✅ Senha do usuário '{nome}' resetada com sucesso!")
        return True
        
    except ValueError:
        print("❌ ID deve ser um número!")
        return False
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {str(e)}")
        return False

def menu_principal():
    """Menu principal para gerenciar usuários"""
    while True:
        print("=" * 60)
        print("👥 GERENCIADOR DE USUÁRIOS - BANCO LOCAL")
        print("=" * 60)
        print("1. 📊 Mostrar status dos usuários")
        print("2. ➕ Adicionar novo usuário")
        print("3. 🔄 Alterar status (ativar/desativar)")
        print("4. 🔑 Resetar senha de usuário")
        print("5. 🗑️ Deletar TODOS os usuários")
        print("6. 🎯 Deletar usuário específico por ID")
        print("7. 📋 Listar todos os usuários")
        print("0. ❌ Sair")
        print()
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            mostrar_status_usuarios()
            
        elif opcao == "2":
            adicionar_usuario()
            
        elif opcao == "3":
            alterar_status_usuario()
            
        elif opcao == "4":
            resetar_senha_usuario()
            
        elif opcao == "5":
            print("⚠️ ATENÇÃO: Esta operação irá deletar TODOS os usuários!")
            confirmacao = input("Digite 'CONFIRMAR' para continuar: ").strip()
            
            if confirmacao == "CONFIRMAR":
                print("🗑️ Deletando todos os usuários...")
                deletar_todos_usuarios()
            else:
                print("❌ Operação cancelada!")
            
        elif opcao == "6":
            mostrar_status_usuarios()
            try:
                usuario_id = int(input("Digite o ID do usuário a ser deletado: ").strip())
                deletar_usuario_por_id(usuario_id)
            except ValueError:
                print("❌ ID deve ser um número!")
                
        elif opcao == "7":
            listar_todos_usuarios()
                
        elif opcao == "0":
            print("👋 Saindo do gerenciador de usuários!")
            break
            
        else:
            print("❌ Opção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")
        print()

if __name__ == "__main__":
    # Mostra status inicial
    mostrar_status_usuarios()
    
    # Inicia menu interativo
    menu_principal()