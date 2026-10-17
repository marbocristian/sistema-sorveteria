import tkinter as tk
from tkinter import messagebox
import sys

try:
    from login import TelaLogin
    from sistema import SistemaSorveteria
    print("✅ Todos os módulos carregados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    messagebox.showerror("Erro", f"Erro ao carregar módulos:\n{e}")
    sys.exit(1)

def main():
    """Função principal que inicia o sistema"""
    
    print("="*50)
    print("🍦 SISTEMA DE SORVETERIA v2.0")
    print("="*50)
    print("Iniciando aplicação...")
    
    # Criar janela de login
    janela_login = tk.Tk()
    janela_login.configure(bg='white')
    
    def abrir_sistema(usuario_id, usuario_nome, perfil):
        """
        Callback executado após login bem-sucedido
        
        Args:
            usuario_id: ID do usuário logado
            usuario_nome: Nome do usuário logado
            perfil: Perfil do usuário (funcionario/administrador/desenvolvedor)
        """
        print(f"✅ Login realizado: {usuario_nome} (ID: {usuario_id}) - Perfil: {perfil}")
        
        # ========== FECHAR JANELA DE LOGIN ==========
        janela_login.destroy()
        
        # ========== CRIAR NOVA JANELA PARA O SISTEMA ==========
        janela_sistema = tk.Tk()
        janela_sistema.configure(bg='white')
        
        # Verificar se é desenvolvedor (modo teste)
        modo_teste = (perfil == 'desenvolvedor')
        
        if modo_teste:
            print("⚠️ MODO TESTE ATIVADO - Dados não serão salvos permanentemente!")
        
        # Maximizar janela
        try:
            janela_sistema.state('zoomed')  # Windows
        except:
            try:
                janela_sistema.attributes('-zoomed', True)  # Linux/Mac
            except:
                # Fallback para tela cheia manual
                largura = janela_sistema.winfo_screenwidth()
                altura = janela_sistema.winfo_screenheight()
                janela_sistema.geometry(f"{largura}x{altura}+0+0")
        
        # Abrir sistema principal
        try:
            SistemaSorveteria(janela_sistema, usuario_id, usuario_nome, perfil, modo_teste)
            
            # Protocolo de fechamento
            def ao_fechar_sistema():
                if messagebox.askyesno("❓ Sair", "Deseja realmente fechar o sistema?"):
                    print("👋 Encerrando sistema...")
                    janela_sistema.destroy()
            
            janela_sistema.protocol("WM_DELETE_WINDOW", ao_fechar_sistema)
            
            # Iniciar loop da janela do sistema
            janela_sistema.mainloop()
            
        except Exception as e:
            print(f"❌ Erro ao abrir sistema: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir sistema:\n{e}")
            import traceback
            traceback.print_exc()
            janela_sistema.destroy()
    
    # Abrir tela de login
    print("Carregando tela de login...")
    try:
        TelaLogin(janela_login, abrir_sistema)
    except Exception as e:
        print(f"❌ Erro ao abrir tela de login: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir tela de login:\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Protocolo de fechamento da janela de login
    def ao_fechar_login():
        if messagebox.askyesno("❓ Sair", "Deseja realmente fechar?"):
            print("👋 Saindo...")
            janela_login.destroy()
            sys.exit(0)
    
    janela_login.protocol("WM_DELETE_WINDOW", ao_fechar_login)
    
    # Iniciar loop principal do login
    print("✅ Sistema pronto para uso!\n")
    print("="*50)
    print("INSTRUÇÕES:")
    print("1. Faça login com: admin / admin123")
    print("2. Ou cadastre um novo usuário")
    print("="*50)
    print("\n💡 PERFIS DISPONÍVEIS:")
    print("   👤 Funcionário - Apenas vendas")
    print("   👨‍💼 Administrador - Acesso total")
    print("   🧑‍💻 Desenvolvedor - Modo teste (não salva dados)")
    print("="*50)
    
    janela_login.mainloop()
    
    print("\n" + "="*50)
    print("Sistema encerrado!")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para fechar...")