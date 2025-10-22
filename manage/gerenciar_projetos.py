"""
Script para gerenciar projetos no banco de dados local
Permite visualizar, adicionar, editar e deletar projetos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from db.db_local import LocalDatabase

def mostrar_status_projetos():
    """Mostra o status atual dos projetos no banco"""
    print("=" * 60)
    print("📋 STATUS ATUAL DOS PROJETOS")
    print("=" * 60)
    
    db = LocalDatabase()
    
    try:
        # Verificar se a tabela existe
        result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='projetos'", fetch=True)
        if not result:
            print("⚠️ Tabela 'projetos' não encontrada no banco!")
            return
        
        # Contar projetos
        total_result = db.execute_query("SELECT COUNT(*) FROM projetos", fetch=True)
        total = total_result[0][0] if total_result else 0
        print(f"Total de projetos no banco: {total}")
        
        if total > 0:
            projetos = db.execute_query("SELECT * FROM projetos LIMIT 5", fetch=True)
            print("\nPrimeiros 5 projetos:")
            for i, projeto in enumerate(projetos):
                nome = projeto[1] if len(projeto) > 1 else 'N/A'
                status = projeto[3] if len(projeto) > 3 else 'N/A'
                print(f"  {i+1}. ID: {projeto[0]} | Nome: {nome} | Status: {status}")
            
            if total > 5:
                print(f"  ... e mais {total - 5} projetos")
        else:
            print("⚠️ Nenhum projeto encontrado no banco!")
            
    except Exception as e:
        print(f"❌ Erro ao consultar projetos: {str(e)}")
    
    print()

def listar_todos_projetos():
    """Lista todos os projetos do banco"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM projetos")
        projetos = cursor.fetchall()
        
        if projetos:
            # Obter nomes das colunas
            cursor.execute("PRAGMA table_info(projetos)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            print(f"\n📋 LISTA COMPLETA ({len(projetos)} projetos):")
            print("-" * 120)
            
            # Cabeçalho
            header = " | ".join([col[:15] for col in colunas[:6]])  # Primeiras 6 colunas
            print(header)
            print("-" * 120)
            
            for i, projeto in enumerate(projetos):
                linha = " | ".join([str(projeto[j])[:15] if j < len(projeto) else 'N/A' for j in range(min(6, len(colunas)))])
                print(f"{i+1:3d}. {linha}")
            print("-" * 120)
        else:
            print("⚠️ Nenhum projeto encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao listar projetos: {str(e)}")

def deletar_todos_projetos():
    """Deleta todos os projetos do banco"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM projetos")
        db.conn.commit()
        print("✅ Todos os projetos foram deletados!")
        return True
    except Exception as e:
        print(f"❌ Erro ao deletar projetos: {str(e)}")
        return False

def deletar_projeto_por_id(projeto_id):
    """Deleta um projeto específico por ID"""
    db = LocalDatabase()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM projetos WHERE id = ?", (projeto_id,))
        
        if cursor.rowcount > 0:
            db.conn.commit()
            print(f"✅ Projeto ID {projeto_id} deletado com sucesso!")
            return True
        else:
            print(f"❌ Nenhum projeto encontrado com ID {projeto_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar projeto: {str(e)}")
        return False

def adicionar_projeto():
    """Adiciona um novo projeto ao banco"""
    db = LocalDatabase()
    
    print("\n📋 ADICIONAR NOVO PROJETO")
    print("-" * 35)
    
    nome = input("Nome do projeto: ").strip()
    descricao = input("Descrição: ").strip()
    status = input("Status (Planejamento/Em Andamento/Concluído/Pausado): ").strip()
    cliente = input("Cliente: ").strip()
    data_inicio = input("Data de início (YYYY-MM-DD): ").strip()
    data_fim = input("Data de fim (YYYY-MM-DD - opcional): ").strip()
    
    if not nome:
        print("❌ Nome do projeto é obrigatório!")
        return False
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            INSERT INTO projetos (nome, descricao, status, cliente, data_inicio, data_fim)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nome, 
            descricao if descricao else None,
            status if status else 'Planejamento',
            cliente if cliente else None,
            data_inicio if data_inicio else None,
            data_fim if data_fim else None
        ))
        
        db.conn.commit()
        print(f"✅ Projeto '{nome}' adicionado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar projeto: {str(e)}")
        return False

def alterar_status_projeto():
    """Altera o status de um projeto"""
    db = LocalDatabase()
    
    try:
        listar_todos_projetos()
        projeto_id = int(input("\nDigite o ID do projeto para alterar status: ").strip())
        
        print("\nStatus disponíveis:")
        print("1. Planejamento")
        print("2. Em Andamento")  
        print("3. Concluído")
        print("4. Pausado")
        print("5. Cancelado")
        
        opcao = input("Escolha o novo status (1-5): ").strip()
        
        status_map = {
            '1': 'Planejamento',
            '2': 'Em Andamento',
            '3': 'Concluído',
            '4': 'Pausado',
            '5': 'Cancelado'
        }
        
        if opcao not in status_map:
            print("❌ Opção inválida!")
            return False
        
        novo_status = status_map[opcao]
        
        cursor = db.conn.cursor()
        cursor.execute("UPDATE projetos SET status = ? WHERE id = ?", (novo_status, projeto_id))
        
        if cursor.rowcount > 0:
            db.conn.commit()
            print(f"✅ Status do projeto ID {projeto_id} alterado para '{novo_status}'!")
            return True
        else:
            print(f"❌ Nenhum projeto encontrado com ID {projeto_id}")
            return False
            
    except ValueError:
        print("❌ ID deve ser um número!")
        return False
    except Exception as e:
        print(f"❌ Erro ao alterar status: {str(e)}")
        return False

def menu_principal():
    """Menu principal para gerenciar projetos"""
    while True:
        print("=" * 60)
        print("📋 GERENCIADOR DE PROJETOS - BANCO LOCAL")
        print("=" * 60)
        print("1. 📊 Mostrar status dos projetos")
        print("2. ➕ Adicionar novo projeto")
        print("3. 🔄 Alterar status de projeto")
        print("4. 🗑️ Deletar TODOS os projetos")
        print("5. 🎯 Deletar projeto específico por ID")
        print("6. 📋 Listar todos os projetos")
        print("0. ❌ Sair")
        print()
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            mostrar_status_projetos()
            
        elif opcao == "2":
            adicionar_projeto()
            
        elif opcao == "3":
            alterar_status_projeto()
            
        elif opcao == "4":
            print("⚠️ ATENÇÃO: Esta operação irá deletar TODOS os projetos!")
            confirmacao = input("Digite 'CONFIRMAR' para continuar: ").strip()
            
            if confirmacao == "CONFIRMAR":
                print("🗑️ Deletando todos os projetos...")
                deletar_todos_projetos()
            else:
                print("❌ Operação cancelada!")
            
        elif opcao == "5":
            mostrar_status_projetos()
            try:
                projeto_id = int(input("Digite o ID do projeto a ser deletado: ").strip())
                deletar_projeto_por_id(projeto_id)
            except ValueError:
                print("❌ ID deve ser um número!")
                
        elif opcao == "6":
            listar_todos_projetos()
                
        elif opcao == "0":
            print("👋 Saindo do gerenciador de projetos!")
            break
            
        else:
            print("❌ Opção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")
        print()

if __name__ == "__main__":
    # Mostra status inicial
    mostrar_status_projetos()
    
    # Inicia menu interativo
    menu_principal()