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
    print("🍦 SISTEMA DE SORVETERIA v1.0")
    print("="*50)
    print("Iniciando aplicação...")
    
    # Criar janela principal
    root = tk.Tk()
    root.configure(bg='white')
    
    def abrir_sistema(usuario_id, usuario_nome):
        """
        Callback executado após login bem-sucedido
        
        Args:
            usuario_id: ID do usuário logado
            usuario_nome: Nome do usuário logado
        """
        print(f"✅ Login realizado: {usuario_nome} (ID: {usuario_id})")
        
        # Limpar janela atual
        for widget in root.winfo_children():
            widget.destroy()
        
        # MAXIMIZAR JANELA
        root.state('zoomed')  # Windows
        # Para Linux/Mac use: root.attributes('-zoomed', True)
        
        # Abrir sistema principal
        try:
            SistemaSorveteria(root, usuario_id, usuario_nome)
        except Exception as e:
            print(f"❌ Erro ao abrir sistema: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir sistema:\n{e}")
            import traceback
            traceback.print_exc()
    
    # Abrir tela de login
    print("Carregando tela de login...")
    try:
        TelaLogin(root, abrir_sistema)
    except Exception as e:
        print(f"❌ Erro ao abrir tela de login: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir tela de login:\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Protocolo de fechamento de janela
    def ao_fechar():
        if messagebox.askyesno("❓ Sair", "Deseja realmente fechar o sistema?"):
            print("👋 Encerrando sistema...")
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", ao_fechar)
    
    # Iniciar loop principal
    print("✅ Sistema pronto para uso!\n")
    print("="*50)
    print("INSTRUÇÕES:")
    print("1. Digite o peso em GRAMAS")
    print("2. O sistema converte automaticamente para KG")
    print("3. Pressione Enter para calcular")
    print("4. Clique em 'Registrar' ou pressione F2")
    print("="*50)
    
    root.mainloop()
    
    print("\n" + "="*50)
    print("Sistema encerrado com sucesso!")
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