"""
Script para gerenciar cores no banco de dados local
Permite visualizar, adicionar, editar e deletar cores
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from db.db_local import LocalDatabase

def mostrar_status_cores():
    """Mostra o status atual das cores no banco"""
    print("=" * 60)
    print("🎨 STATUS ATUAL DAS CORES")
    print("=" * 60)
    
    db = LocalDatabase()
    
    try:
        # Verificar se a tabela existe
        result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='cores'", fetch=True)
        if not result:
            print("⚠️ Tabela 'cores' não encontrada no banco!")
            return
        
        # Contar cores
        total_result = db.execute_query("SELECT COUNT(*) FROM cores", fetch=True)
        total = total_result[0][0] if total_result else 0
        print(f"Total de cores no banco: {total}")
        
        if total > 0:
            cores = db.execute_query("SELECT * FROM cores LIMIT 5", fetch=True)
            print("\nPrimeiras 5 cores:")
            for i, cor in enumerate(cores):
                nome = cor[1] if len(cor) > 1 else 'N/A'
                codigo = cor[2] if len(cor) > 2 else 'N/A'
                print(f"  {i+1}. ID: {cor[0]} | Nome: {nome} | Código: {codigo}")
            
            if total > 5:
                print(f"  ... e mais {total - 5} cores")
        else:
            print("⚠️ Nenhuma cor encontrada no banco!")
            
    except Exception as e:
        print(f"❌ Erro ao consultar cores: {str(e)}")
    
    print()

def listar_todas_cores():
    """Lista todas as cores do banco"""
    db = LocalDatabase()
    
    try:
        cores = db.execute_query("SELECT * FROM cores", fetch=True)
        
        if cores:
            # Obter nomes das colunas
            colunas_info = db.execute_query("PRAGMA table_info(cores)", fetch=True)
            colunas = [col[1] for col in colunas_info]
            
            print(f"\n🎨 LISTA COMPLETA ({len(cores)} cores):")
            print("-" * 100)
            
            # Cabeçalho
            header = " | ".join([col[:15] for col in colunas[:5]])  # Primeiras 5 colunas
            print(header)
            print("-" * 100)
            
            for i, cor in enumerate(cores):
                linha = " | ".join([str(cor[j])[:15] if j < len(cor) else 'N/A' for j in range(min(5, len(colunas)))])
                print(f"{i+1:3d}. {linha}")
            print("-" * 100)
        else:
            print("⚠️ Nenhuma cor encontrada!")
            
    except Exception as e:
        print(f"❌ Erro ao listar cores: {str(e)}")

def deletar_todas_cores():
    """Deleta todas as cores do banco"""
    db = LocalDatabase()
    
    try:
        db.execute_query("DELETE FROM cores")
        print("✅ Todas as cores foram deletadas!")
        return True
    except Exception as e:
        print(f"❌ Erro ao deletar cores: {str(e)}")
        return False

def deletar_cor_por_id(cor_id):
    """Deleta uma cor específica por ID"""
    db = LocalDatabase()
    
    try:
        rowcount = db.execute_query("DELETE FROM cores WHERE id = ?", (cor_id,))
        
        if rowcount > 0:
            print(f"✅ Cor ID {cor_id} deletada com sucesso!")
            return True
        else:
            print(f"❌ Nenhuma cor encontrada com ID {cor_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar cor: {str(e)}")
        return False

def adicionar_cor():
    """Adiciona uma nova cor ao banco"""
    db = LocalDatabase()
    
    print("\n🎨 ADICIONAR NOVA COR")
    print("-" * 30)
    
    nome = input("Nome da cor: ").strip()
    codigo_hex = input("Código hexadecimal (ex: #FF0000): ").strip()
    codigo_rgb = input("Código RGB (ex: 255,0,0): ").strip()
    descricao = input("Descrição (opcional): ").strip()
    
    if not nome or not codigo_hex:
        print("❌ Nome e código hexadecimal são obrigatórios!")
        return False
    
    try:
        db.execute_query("""
            INSERT INTO cores (nome, codigo_hex, codigo_rgb, descricao)
            VALUES (?, ?, ?, ?)
        """, (nome, codigo_hex, codigo_rgb if codigo_rgb else None, descricao if descricao else None))
        
        print(f"✅ Cor '{nome}' adicionada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar cor: {str(e)}")
        return False

def menu_principal():
    """Menu principal para gerenciar cores"""
    while True:
        print("=" * 60)
        print("🎨 GERENCIADOR DE CORES - BANCO LOCAL")
        print("=" * 60)
        print("1. 📊 Mostrar status das cores")
        print("2. ➕ Adicionar nova cor")
        print("3. 🗑️ Deletar TODAS as cores")
        print("4. 🎯 Deletar cor específica por ID")
        print("5. 📋 Listar todas as cores")
        print("0. ❌ Sair")
        print()
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            mostrar_status_cores()
            
        elif opcao == "2":
            adicionar_cor()
            
        elif opcao == "3":
            print("⚠️ ATENÇÃO: Esta operação irá deletar TODAS as cores!")
            confirmacao = input("Digite 'CONFIRMAR' para continuar: ").strip()
            
            if confirmacao == "CONFIRMAR":
                print("🗑️ Deletando todas as cores...")
                deletar_todas_cores()
            else:
                print("❌ Operação cancelada!")
            
        elif opcao == "4":
            mostrar_status_cores()
            try:
                cor_id = int(input("Digite o ID da cor a ser deletada: ").strip())
                deletar_cor_por_id(cor_id)
            except ValueError:
                print("❌ ID deve ser um número!")
                
        elif opcao == "5":
            listar_todas_cores()
                
        elif opcao == "0":
            print("👋 Saindo do gerenciador de cores!")
            break
            
        else:
            print("❌ Opção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")
        print()

if __name__ == "__main__":
    # Mostra status inicial
    mostrar_status_cores()
    
    # Inicia menu interativo
    menu_principal()