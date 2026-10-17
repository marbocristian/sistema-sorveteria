import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database

class TelaLogin:
    """Classe para gerenciar a tela de login"""

    def __init__(self, root, callback_sucesso):
        self.root = root
        self.callback_sucesso = callback_sucesso
        self.db = Database()

        self.root.title("🍦 Sorveteria - Login")
        self.root.geometry("450x450")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')

        self.centralizar_janela()
        self.criar_widgets()

        print("🚀 Tela de login carregada")

    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')

    def criar_widgets(self):
        """Cria todos os elementos visuais da tela"""

        # Frame principal
        frame_principal = tk.Frame(self.root, bg='#f0f0f0')
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho
        frame_header = tk.Frame(frame_principal, bg='#4a90e2', height=80)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="🍦 Sistema Sorveteria",
                font=('Arial', 22, 'bold'),
                bg='#4a90e2', fg='white').pack(expand=True)

        # Área de conteúdo (login direto, sem abas)
        frame_conteudo = tk.Frame(frame_principal, bg='white')
        frame_conteudo.pack(fill=tk.BOTH, expand=True)

        container_login = tk.Frame(frame_conteudo, bg='white')
        container_login.pack(expand=True)

        tk.Label(container_login, text="Usuário:",
                font=('Arial', 11), bg='white').pack(anchor=tk.W, pady=(30, 5), padx=20)
        self.entry_usuario_login = ttk.Entry(container_login, width=30, font=('Arial', 11))
        self.entry_usuario_login.pack(pady=5, padx=20)

        tk.Label(container_login, text="Senha:",
                font=('Arial', 11), bg='white').pack(anchor=tk.W, pady=(15, 5), padx=20)
        self.entry_senha_login = ttk.Entry(container_login, width=30,
                                           font=('Arial', 11), show="●")
        self.entry_senha_login.pack(pady=5, padx=20)

        # Botão de login
        btn_login = tk.Button(container_login, text="Entrar",
                             command=self.fazer_login,
                             bg='#4a90e2', fg='white',
                             font=('Arial', 12, 'bold'),
                             cursor='hand2', relief=tk.FLAT,
                             padx=40, pady=10)
        btn_login.pack(pady=25)

        # Link recuperar senha
        link_recuperar = tk.Label(container_login, text="Esqueci minha senha",
                                 font=('Arial', 9, 'underline'),
                                 fg='#4a90e2', bg='white', cursor='hand2')
        link_recuperar.pack()
        link_recuperar.bind('<Button-1>', lambda e: self.recuperar_senha())

        # Binds
        self.entry_usuario_login.bind('<Return>', lambda e: self.entry_senha_login.focus())
        self.entry_senha_login.bind('<Return>', lambda e: self.fazer_login())

        self.entry_usuario_login.focus()

    def fazer_login(self):
        """Processa o login do usuário"""
        usuario = self.entry_usuario_login.get().strip()
        senha = self.entry_senha_login.get()

        if not usuario or not senha:
            messagebox.showwarning("⚠️ Aviso", "Preencha todos os campos!")
            return

        resultado = self.db.verificar_login(usuario, senha)

        if resultado:
            usuario_id, usuario_nome, perfil = resultado
            messagebox.showinfo("✅ Sucesso", f"Bem-vindo(a), {usuario_nome}!")
            self.callback_sucesso(usuario_id, usuario_nome, perfil)
        else:
            messagebox.showerror("❌ Erro", "Usuário ou senha incorretos!")
            self.entry_senha_login.delete(0, tk.END)
            self.entry_senha_login.focus()

    def recuperar_senha(self):
        """Fluxo de recuperação de senha via pergunta de segurança"""
        usuario = simpledialog.askstring(
            "🔑 Recuperar Senha",
            "Digite seu nome de usuário:",
            parent=self.root
        )

        if not usuario:
            return

        usuario = usuario.strip()
        pergunta = self.db.obter_pergunta_seguranca(usuario)

        if not pergunta:
            messagebox.showerror("❌ Erro", "Usuário não encontrado!")
            return

        resposta = simpledialog.askstring(
            "🔑 Pergunta de Segurança",
            f"{pergunta}",
            parent=self.root
        )

        if not resposta:
            return

        if self.db.recuperar_senha(usuario, resposta):
            nova_senha = simpledialog.askstring(
                "🔑 Nova Senha",
                "Resposta correta! Digite sua nova senha:",
                parent=self.root, show='*'
            )

            if not nova_senha:
                return

            if len(nova_senha) < 4:
                messagebox.showwarning("⚠️ Aviso", "A senha deve ter no mínimo 4 caracteres!")
                return

            confirma_senha = simpledialog.askstring(
                "🔑 Confirmar Senha",
                "Confirme sua nova senha:",
                parent=self.root, show='*'
            )

            if nova_senha != confirma_senha:
                messagebox.showerror("❌ Erro", "As senhas não coincidem!")
                return

            self.db.alterar_senha(usuario, nova_senha)
            messagebox.showinfo("✅ Sucesso", "Senha alterada com sucesso!\nFaça login com a nova senha.")

            self.entry_usuario_login.delete(0, tk.END)
            self.entry_usuario_login.insert(0, usuario)
            self.entry_senha_login.focus()
        else:
            messagebox.showerror("❌ Erro", "Resposta de segurança incorreta!")