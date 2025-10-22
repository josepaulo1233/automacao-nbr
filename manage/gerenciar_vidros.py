"""
Script para gerenciar vidros no banco de dados local
Permite visualizar, adicionar, editar e deletar vidros
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from db.db_local import LocalDatabase

def mostrar_status_vidros():
    """Mostra o status atual dos vidros no banco"""
    print("=" * 60)
    print("🪟 STATUS ATUAL DOS VIDROS")
    print("=" * 60)
    
    db = LocalDatabase()
    
    try:
        # Verificar se a tabela existe
        result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='vidros'", fetch=True)
        if not result:
            print("⚠️ Tabela 'vidros' não encontrada no banco!")
            return
        
        # Contar vidros
        total_result = db.execute_query("SELECT COUNT(*) FROM vidros", fetch=True)
        total = total_result[0][0] if total_result else 0
        print(f"Total de vidros no banco: {total}")
        
        if total > 0:
            vidros = db.execute_query("SELECT * FROM vidros LIMIT 5", fetch=True)
            print("\nPrimeiros 5 vidros:")
            for i, vidro in enumerate(vidros):
                print(f"  {i+1}. ID: {vidro[0]} | Tipo: {vidro[1] if len(vidro) > 1 else 'N/A'}")
            
            if total > 5:
                print(f"  ... e mais {total - 5} vidros")
        else:
            print("⚠️ Nenhum vidro encontrado no banco!")
            
    except Exception as e:
        print(f"❌ Erro ao consultar vidros: {str(e)}")
    
    print()

def listar_todos_vidros():
    """Lista todos os vidros do banco"""
    db = LocalDatabase()
    
    try:
        vidros = db.execute_query("SELECT * FROM vidros", fetch=True)
        
        if vidros:
            # Obter nomes das colunas
            colunas_info = db.execute_query("PRAGMA table_info(vidros)", fetch=True)
            colunas = [col[1] for col in colunas_info]
            
            print(f"\n🪟 LISTA COMPLETA ({len(vidros)} vidros):")
            print("-" * 100)
            
            # Cabeçalho
            header = " | ".join([col[:15] for col in colunas[:5]])  # Primeiras 5 colunas
            print(header)
            print("-" * 100)
            
            for i, vidro in enumerate(vidros):
                linha = " | ".join([str(vidro[j])[:15] if j < len(vidro) else 'N/A' for j in range(min(5, len(colunas)))])
                print(f"{i+1:3d}. {linha}")
            print("-" * 100)
        else:
            print("⚠️ Nenhum vidro encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao listar vidros: {str(e)}")

def deletar_todos_vidros():
    """Deleta todos os vidros do banco"""
    db = LocalDatabase()
    
    try:
        db.execute_query("DELETE FROM vidros")
        print("✅ Todos os vidros foram deletados!")
        return True
    except Exception as e:
        print(f"❌ Erro ao deletar vidros: {str(e)}")
        return False

def deletar_vidro_por_id(vidro_id):
    """Deleta um vidro específico por ID"""
    db = LocalDatabase()
    
    try:
        rowcount = db.execute_query("DELETE FROM vidros WHERE id = ?", (vidro_id,))
        
        if rowcount > 0:
            print(f"✅ Vidro ID {vidro_id} deletado com sucesso!")
            return True
        else:
            print(f"❌ Nenhum vidro encontrado com ID {vidro_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar vidro: {str(e)}")
        return False

def menu_principal():
    """Menu principal para gerenciar vidros"""
    while True:
        print("=" * 60)
        print("🪟 GERENCIADOR DE VIDROS - BANCO LOCAL")
        print("=" * 60)
        print("1. 📊 Mostrar status dos vidros")
        print("2. 🗑️ Deletar TODOS os vidros")
        print("3. 🎯 Deletar vidro específico por ID")
        print("4. 📋 Listar todos os vidros")
        print("0. ❌ Sair")
        print()
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            mostrar_status_vidros()
            
        elif opcao == "2":
            print("⚠️ ATENÇÃO: Esta operação irá deletar TODOS os vidros!")
            confirmacao = input("Digite 'CONFIRMAR' para continuar: ").strip()
            
            if confirmacao == "CONFIRMAR":
                print("🗑️ Deletando todos os vidros...")
                deletar_todos_vidros()
            else:
                print("❌ Operação cancelada!")
            
        elif opcao == "3":
            mostrar_status_vidros()
            try:
                vidro_id = int(input("Digite o ID do vidro a ser deletado: ").strip())
                deletar_vidro_por_id(vidro_id)
            except ValueError:
                print("❌ ID deve ser um número!")
                
        elif opcao == "4":
            listar_todos_vidros()
                
        elif opcao == "0":
            print("👋 Saindo do gerenciador de vidros!")
            break
            
        else:
            print("❌ Opção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")
        print()

if __name__ == "__main__":
    # Mostra status inicial
    mostrar_status_vidros()
    
    # Inicia menu interativo
    menu_principal()