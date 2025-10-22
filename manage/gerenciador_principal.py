"""
Sistema de Gerenciamento Centralizado
Acesso a todos os gerenciadores do sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def mostrar_logo():
    """Exibe o logo do sistema"""
    print("=" * 70)
    print("                 🏢 SISTEMA MITSID DASH")
    print("                GERENCIAMENTO DE DADOS")
    print("=" * 70)

def menu_principal():
    """Menu principal do sistema de gerenciamento"""
    while True:
        mostrar_logo()
        print()
        print("📋 MÓDULOS DE GERENCIAMENTO DISPONÍVEIS:")
        print("-" * 50)
        print("1. 🧱 Gerenciar Materiais")
        print("2. 🪟 Gerenciar Vidros")
        print("3. 🎨 Gerenciar Cores")
        print("4. 📋 Gerenciar Projetos")
        print("5. 👥 Gerenciar Usuários")
        print()
        print("9. ℹ️  Informações do Sistema")
        print("0. ❌ Sair do Sistema")
        print()
        
        opcao = input("Escolha um módulo (0-9): ").strip()
        
        if opcao == "1":
            executar_gerenciador("materiais")
            
        elif opcao == "2":
            executar_gerenciador("vidros")
            
        elif opcao == "3":
            executar_gerenciador("cores")
            
        elif opcao == "4":
            executar_gerenciador("projetos")
            
        elif opcao == "5":
            executar_gerenciador("usuarios")
            
        elif opcao == "9":
            mostrar_informacoes_sistema()
            
        elif opcao == "0":
            print("👋 Saindo do Sistema de Gerenciamento!")
            print("Obrigado por usar o MITSID Dash!")
            break
            
        else:
            print("❌ Opção inválida! Escolha um número de 0 a 9.")
        
        if opcao != "0":
            input("\nPressione Enter para voltar ao menu principal...")
            print()

def executar_gerenciador(modulo):
    """Executa o gerenciador específico"""
    try:
        if modulo == "materiais":
            from gerenciar_materiais import menu_principal as menu_materiais
            menu_materiais()
            
        elif modulo == "vidros":
            from gerenciar_vidros import menu_principal as menu_vidros
            menu_vidros()
            
        elif modulo == "cores":
            from gerenciar_cores import menu_principal as menu_cores
            menu_cores()
            
        elif modulo == "projetos":
            from gerenciar_projetos import menu_principal as menu_projetos
            menu_projetos()
            
        elif modulo == "usuarios":
            from gerenciar_usuarios import menu_principal as menu_usuarios
            menu_usuarios()
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulo {modulo}: {str(e)}")
        print("💡 Verifique se todos os arquivos estão presentes na pasta 'manage'")
    except Exception as e:
        print(f"❌ Erro ao executar gerenciador {modulo}: {str(e)}")

def mostrar_informacoes_sistema():
    """Mostra informações sobre o sistema"""
    print("\n" + "=" * 60)
    print("ℹ️  INFORMAÇÕES DO SISTEMA MITSID DASH")
    print("=" * 60)
    print("📅 Versão: 1.0.0")
    print("📍 Localização: manage/")
    print("🗄️  Banco de Dados: SQLite Local")
    print()
    print("📋 MÓDULOS DISPONÍVEIS:")
    print("   • Materiais - Gestão de materiais de construção")
    print("   • Vidros - Gestão de tipos de vidro")
    print("   • Cores - Gestão de paleta de cores")
    print("   • Projetos - Gestão de projetos")
    print("   • Usuários - Gestão de usuários do sistema")
    print()
    print("🛠️  FUNCIONALIDADES PRINCIPAIS:")
    print("   • Visualização de dados")
    print("   • Adição de novos registros")
    print("   • Edição de registros existentes")
    print("   • Exclusão de registros")
    print("   • Listagem completa")
    print("   • Gestão de status e permissões")
    print()
    print("🔧 DESENVOLVIDO PARA:")
    print("   • Análise térmica de edifícios")
    print("   • Gestão de materiais de construção")
    print("   • Controle de projetos de engenharia")
    print("   • Interface web com Dash/Plotly")
    print()
    
    # Verificar status dos arquivos
    modulos = [
        ("gerenciar_materiais.py", "🧱 Materiais"),
        ("gerenciar_vidros.py", "🪟 Vidros"),
        ("gerenciar_cores.py", "🎨 Cores"),
        ("gerenciar_projetos.py", "📋 Projetos"),
        ("gerenciar_usuarios.py", "👥 Usuários")
    ]
    
    print("📁 STATUS DOS MÓDULOS:")
    for arquivo, nome in modulos:
        caminho = os.path.join(os.path.dirname(__file__), arquivo)
        if os.path.exists(caminho):
            status = "✅ Disponível"
        else:
            status = "❌ Não encontrado"
        print(f"   {nome}: {status}")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Erro inesperado no sistema: {str(e)}")
        print("💡 Entre em contato com o suporte técnico")