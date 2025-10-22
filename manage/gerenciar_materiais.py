"""
Script para gerenciar materiais no banco de dados local
Demonstra como deletar materiais individuais ou todos de uma vez
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_local import get_materiais, delete_all_materiais, delete_material_by_name, count_materiais

def mostrar_status_materiais():
    """Mostra o status atual dos materiais no banco"""
    print("=" * 60)
    print("📊 STATUS ATUAL DOS MATERIAIS")
    print("=" * 60)
    
    total = count_materiais()
    print(f"Total de materiais no banco: {total}")
    
    if total > 0:
        materiais = get_materiais()
        print("\nPrimeiros 5 materiais:")
        for i, material in enumerate(materiais[:5].to_dict('records')):
            nome = material.get('MATERIAL', 'N/A')
            tipo = material.get('TIPO MATERIAL', 'N/A')
            print(f"  {i+1}. {nome} ({tipo})")
        
        if total > 5:
            print(f"  ... e mais {total - 5} materiais")
    else:
        print("⚠️ Nenhum material encontrado no banco!")
    
    print()

def menu_principal():
    """Menu principal para gerenciar materiais"""
    while True:
        print("=" * 60)
        print("🛠️ GERENCIADOR DE MATERIAIS - BANCO LOCAL")
        print("=" * 60)
        print("1. 📊 Mostrar status dos materiais")
        print("2. 🗑️ Deletar TODOS os materiais")
        print("3. 🎯 Deletar material específico por nome")
        print("4. 📋 Listar todos os materiais")
        print("0. ❌ Sair")
        print()
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            mostrar_status_materiais()
            
        elif opcao == "2":
            print("⚠️ ATENÇÃO: Esta operação irá deletar TODOS os materiais!")
            confirmacao = input("Digite 'CONFIRMAR' para continuar: ").strip()
            
            if confirmacao == "CONFIRMAR":
                print("🗑️ Deletando todos os materiais...")
                success = delete_all_materiais()
                if success:
                    print("✅ Operação concluída!")
                else:
                    print("❌ Falha na operação!")
            else:
                print("❌ Operação cancelada!")
            
        elif opcao == "3":
            mostrar_status_materiais()
            nome_material = input("Digite o nome EXATO do material a ser deletado: ").strip()
            
            if nome_material:
                print(f"🎯 Deletando material '{nome_material}'...")
                success = delete_material_by_name(nome_material)
                if not success:
                    print("💡 Dica: O nome deve ser exato, incluindo maiúsculas/minúsculas")
            else:
                print("❌ Nome do material não pode estar vazio!")
                
        elif opcao == "4":
            total = count_materiais()
            if total > 0:
                materiais = get_materiais()
                print(f"\n📋 LISTA COMPLETA ({total} materiais):")
                print("-" * 80)
                for i, material in enumerate(materiais.to_dict('records')):
                    nome = material.get('MATERIAL', 'N/A')
                    tipo = material.get('TIPO MATERIAL', 'N/A')
                    condutividade = material.get('CONDUTIVIDADE', 'N/A')
                    print(f"{i+1:3d}. {nome:<25} | {tipo:<30} | λ={condutividade}")
                print("-" * 80)
            else:
                print("⚠️ Nenhum material encontrado!")
                
        elif opcao == "0":
            print("👋 Saindo do gerenciador de materiais!")
            break
            
        else:
            print("❌ Opção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")
        print()

if __name__ == "__main__":
    # Mostra status inicial
    mostrar_status_materiais()
    
    # Inicia menu interativo
    menu_principal()