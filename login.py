import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class TelaLogin:
    """Classe para gerenciar a tela de login e cadastro"""
    
    def __init__(self, root, callback_sucesso):
        self.root = root
        self.callback_sucesso = callback_sucesso
        self.db = Database()
        
        self.root.title("🍦 Sorveteria - Login")
        self.root.geometry("500x650")
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
                font=('Arial', 24, 'bold'), 
                bg='#4a90e2', fg='white').pack(expand=True)
        
        # Área de conteúdo
        frame_conteudo = tk.Frame(frame_principal, bg='#f0f0f0')
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(frame_conteudo)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # ========== ABA LOGIN ==========
        self.criar_aba_login()
        
        # ========== ABA CADASTRO ==========
        self.criar_aba_cadastro()
        
        # Focar no campo de usuário ao abrir
        self.entry_usuario_login.focus()
    
    def criar_aba_login(self):
        """Cria a aba de login"""
        self.frame_login = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.frame_login, text="  Login  ")
        
        # Container centralizado
        container_login = tk.Frame(self.frame_login, bg='white')
        container_login.pack(expand=True)
        
        tk.Label(container_login, text="Usuário:", 
                font=('Arial', 11), bg='white').pack(anchor=tk.W, pady=(20,5), padx=20)
        self.entry_usuario_login = ttk.Entry(container_login, width=30, font=('Arial', 11))
        self.entry_usuario_login.pack(pady=5, padx=20)
        
        tk.Label(container_login, text="Senha:", 
                font=('Arial', 11), bg='white').pack(anchor=tk.W, pady=(15,5), padx=20)
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
    
    def criar_aba_cadastro(self):
        """Cria a aba de cadastro com scroll"""
        self.frame_cadastro = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.frame_cadastro, text="  Cadastrar  ")
        
        # Canvas e Scrollbar
        canvas = tk.Canvas(self.frame_cadastro, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame_cadastro, orient="vertical", command=canvas.yview)
        
        # Frame scrollável
        frame_scrollavel = tk.Frame(canvas, bg='white')
        
        frame_scrollavel.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_scrollavel, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo dentro do frame scrollável
        container = tk.Frame(frame_scrollavel, bg='white')
        container.pack(padx=40, pady=30)
        
        # CAMPO: Nome Completo
        tk.Label(container, text="Nome Completo:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(10,5))
        self.entry_nome = ttk.Entry(container, width=40, font=('Arial', 10))
        self.entry_nome.pack(pady=(0,15))
        
        # CAMPO: Usuário
        tk.Label(container, text="Usuário (login):", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(5,5))
        self.entry_usuario_cadastro = ttk.Entry(container, width=40, font=('Arial', 10))
        self.entry_usuario_cadastro.pack(pady=(0,15))
        
        # CAMPO: Senha
        tk.Label(container, text="Senha:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(5,5))
        self.entry_senha_cadastro = ttk.Entry(container, width=40, 
                                              font=('Arial', 10), show="●")
        self.entry_senha_cadastro.pack(pady=(0,15))
        
        # CAMPO: Confirmar Senha
        tk.Label(container, text="Confirmar Senha:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(5,5))
        self.entry_confirma_senha = ttk.Entry(container, width=40, 
                                             font=('Arial', 10), show="●")
        self.entry_confirma_senha.pack(pady=(0,15))
        
        # CAMPO: Pergunta de Segurança
        tk.Label(container, text="Pergunta de Segurança:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(5,5))
        
        self.combo_pergunta = ttk.Combobox(container, width=38, 
                                          font=('Arial', 10), state='readonly')
        self.combo_pergunta['values'] = (
            'Qual o nome da sua mãe?',
            'Qual sua cor favorita?',
            'Qual o nome do seu primeiro animal de estimação?',
            'Em qual cidade você nasceu?',
            'Qual o nome da sua escola primária?'
        )
        self.combo_pergunta.current(0)
        self.combo_pergunta.pack(pady=(0,15))
        
        # CAMPO: Resposta
        tk.Label(container, text="Resposta:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(5,5))
        self.entry_resposta = ttk.Entry(container, width=40, font=('Arial', 10))
        self.entry_resposta.pack(pady=(0,25))
        
        # BOTÃO: Cadastrar (DESTAQUE)
        btn_cadastrar = tk.Button(container, text="✓ CADASTRAR", 
                                 command=self.cadastrar_usuario,
                                 bg='#5cb85c', fg='white',
                                 font=('Arial', 12, 'bold'),
                                 cursor='hand2', relief=tk.FLAT,
                                 padx=50, pady=15)
        btn_cadastrar.pack(pady=20)
        
        # Espaço extra no final
        tk.Frame(container, bg='white', height=20).pack()
        
        # Bind do scroll com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def fazer_login(self):
        """Processa o login do usuário"""
        usuario = self.entry_usuario_login.get().strip()
        senha = self.entry_senha_login.get()
        
        if not usuario or not senha:
            messagebox.showwarning("⚠️ Aviso", "Preencha todos os campos!")
            return
        
        resultado = self.db.verificar_login(usuario, senha)
        
        if resultado:
            usuario_id, usuario_nome = resultado
            messagebox.showinfo("✅ Sucesso", f"Bem-vindo(a), {usuario_nome}!")
            self.callback_sucesso(usuario_id, usuario_nome)
        else:
            messagebox.showerror("❌ Erro", "Usuário ou senha incorretos!")
            self.entry_senha_login.delete(0, tk.END)
            self.entry_senha_login.focus()
    
    def cadastrar_usuario(self):
        """Processa o cadastro de novo usuário"""
        nome = self.entry_nome.get().strip()
        usuario = self.entry_usuario_cadastro.get().strip()
        senha = self.entry_senha_cadastro.get()
        confirma = self.entry_confirma_senha.get()
        pergunta = self.combo_pergunta.get()
        resposta = self.entry_resposta.get().strip()
        
        # Validações
        if not all([nome, usuario, senha, pergunta, resposta]):
            messagebox.showwarning("⚠️ Aviso", "Preencha todos os campos!")
            return
        
        if len(usuario) < 3:
            messagebox.showwarning("⚠️ Aviso", "Usuário deve ter no mínimo 3 caracteres!")
            return
        
        if len(senha) < 4:
            messagebox.showwarning("⚠️ Aviso", "Senha deve ter no mínimo 4 caracteres!")
            return
        
        if senha != confirma:
            messagebox.showerror("❌ Erro", "As senhas não coincidem!")
            self.entry_senha_cadastro.delete(0, tk.END)
            self.entry_confirma_senha.delete(0, tk.END)
            self.entry_senha_cadastro.focus()
            return
        
        # Criar usuário
        sucesso, mensagem = self.db.criar_usuario(nome, usuario, senha, pergunta, resposta)
        
        if sucesso:
            messagebox.showinfo("✅ Sucesso", 
                              f"{mensagem}\n\nVocê já pode fazer login com:\nUsuário: {usuario}")
            self.notebook.select(0)  # Volta para aba de login
            self.limpar_campos_cadastro()
            self.entry_usuario_login.delete(0, tk.END)
            self.entry_usuario_login.insert(0, usuario)
            self.entry_senha_login.focus()
        else:
            messagebox.showerror("❌ Erro", mensagem)
    
    def recuperar_senha(self):
        """Abre janela de recuperação de senha"""
        janela = tk.Toplevel(self.root)
        janela.title("🔑 Recuperar Senha")
        janela.geometry("500x500")
        janela.resizable(False, False)
        janela.grab_set()
        
        # Centralizar
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 250
        y = (janela.winfo_screenheight() // 2) - 250
        janela.geometry(f'500x500+{x}+{y}')
        
        # Header
        header = tk.Frame(janela, bg='#e74c3c', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🔑 Recuperar Senha", 
                font=('Arial', 18, 'bold'), 
                bg='#e74c3c', fg='white').pack(expand=True)
        
        # Conteúdo
        frame = tk.Frame(janela, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Usuário
        tk.Label(frame, text="Digite seu usuário:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(10,5))
        entry_usuario = ttk.Entry(frame, width=45, font=('Arial', 11))
        entry_usuario.pack(pady=(0,15))
        
        # Frame para pergunta
        frame_pergunta = tk.Frame(frame, bg='#fff3cd', relief=tk.RIDGE, bd=2)
        frame_pergunta.pack(fill=tk.X, pady=15)
        
        label_pergunta = tk.Label(frame_pergunta, text="A pergunta aparecerá aqui...", 
                                 wraplength=420, 
                                 font=('Arial', 10, 'italic'), 
                                 bg='#fff3cd', fg='#856404', justify='left')
        label_pergunta.pack(pady=15, padx=15)
        
        # Resposta
        tk.Label(frame, text="Resposta:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(10,5))
        entry_resposta = ttk.Entry(frame, width=45, font=('Arial', 11))
        entry_resposta.pack(pady=(0,15))
        entry_resposta.config(state='disabled')
        
        # Nova Senha
        tk.Label(frame, text="Nova Senha:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(10,5))
        entry_nova_senha = ttk.Entry(frame, width=45, font=('Arial', 11), show="●")
        entry_nova_senha.pack(pady=(0,25))
        entry_nova_senha.config(state='disabled')
        
        def verificar():
            usuario = entry_usuario.get().strip()
            if not usuario:
                messagebox.showwarning("⚠️ Aviso", "Digite o usuário!", parent=janela)
                return
            
            pergunta = self.db.obter_pergunta_seguranca(usuario)
            if pergunta:
                label_pergunta.config(text=f"Pergunta: {pergunta}", fg='#004085', bg='#cce5ff')
                frame_pergunta.config(bg='#cce5ff')
                entry_resposta.config(state='normal')
                entry_nova_senha.config(state='normal')
                entry_resposta.focus()
                messagebox.showinfo("✅ Encontrado", 
                                  "Usuário encontrado!\nResponda a pergunta de segurança.", 
                                  parent=janela)
            else:
                messagebox.showerror("❌ Erro", "Usuário não encontrado!", parent=janela)
                label_pergunta.config(text="A pergunta aparecerá aqui...", fg='#856404', bg='#fff3cd')
                frame_pergunta.config(bg='#fff3cd')
                entry_resposta.config(state='disabled')
                entry_nova_senha.config(state='disabled')
        
        def redefinir():
            usuario = entry_usuario.get().strip()
            resposta = entry_resposta.get().strip()
            nova_senha = entry_nova_senha.get()
            
            if not all([usuario, resposta, nova_senha]):
                messagebox.showwarning("⚠️ Aviso", "Preencha todos os campos!", parent=janela)
                return
            
            if len(nova_senha) < 4:
                messagebox.showwarning("⚠️ Aviso", 
                                     "A senha deve ter no mínimo 4 caracteres!", 
                                     parent=janela)
                return
            
            if self.db.recuperar_senha(usuario, resposta):
                self.db.alterar_senha(usuario, nova_senha)
                messagebox.showinfo("✅ Sucesso", 
                                  "Senha alterada com sucesso!\n\n"
                                  "Você já pode fazer login com a nova senha.", 
                                  parent=janela)
                janela.destroy()
            else:
                messagebox.showerror("❌ Erro", "Resposta incorreta!", parent=janela)
                entry_resposta.delete(0, tk.END)
                entry_resposta.focus()
        
        # Botões
        frame_btns = tk.Frame(frame, bg='white')
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="🔍 Verificar", 
                 command=verificar,
                 bg='#007bff', fg='white',
                 font=('Arial', 11, 'bold'),
                 cursor='hand2', relief=tk.FLAT,
                 padx=25, pady=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_btns, text="✅ Redefinir", 
                 command=redefinir,
                 bg='#28a745', fg='white',
                 font=('Arial', 11, 'bold'),
                 cursor='hand2', relief=tk.FLAT,
                 padx=25, pady=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_btns, text="❌ Cancelar", 
                 command=janela.destroy,
                 bg='#6c757d', fg='white',
                 font=('Arial', 11, 'bold'),
                 cursor='hand2', relief=tk.FLAT,
                 padx=25, pady=12).pack(side=tk.LEFT, padx=5)
        
        entry_usuario.focus()
    
    def limpar_campos_cadastro(self):
        """Limpa todos os campos do formulário de cadastro"""
        self.entry_nome.delete(0, tk.END)
        self.entry_usuario_cadastro.delete(0, tk.END)
        self.entry_senha_cadastro.delete(0, tk.END)
        self.entry_confirma_senha.delete(0, tk.END)
        self.entry_resposta.delete(0, tk.END)
        self.combo_pergunta.current(0)