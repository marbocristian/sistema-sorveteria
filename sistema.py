import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime

class SistemaSorveteria:
    """Classe principal do sistema de caixa"""
    
    def __init__(self, root, usuario_id, usuario_nome):
        """
        Inicializa o sistema principal
        
        Args:
            root: Janela principal
            usuario_id: ID do usuário logado
            usuario_nome: Nome do usuário logado
        """
        self.root = root
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.db = Database()
        
        self.root.title(f"🍦 Sorveteria - {usuario_nome}")
        
        # MAXIMIZAR JANELA (TELA CHEIA)
        self.root.state('zoomed')  # Windows
        # Para Linux/Mac use: self.root.attributes('-zoomed', True)
        
        # Valor padrão por kg (buscar do banco ou usar 45.00)
        self.valor_kg = self.db.obter_valor_kg_padrao()
        
        # Configurar tema
        self.configurar_tema()
        
        # Criar interface
        self.criar_widgets()
        
        # Atualizar estatísticas
        self.atualizar_estatisticas()
        
        print(f"✅ Sistema iniciado para usuário: {usuario_nome}")
    
    def configurar_tema(self):
        """Configura o tema visual do sistema"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('Header.TFrame', background='#4a90e2')
        style.configure('Card.TFrame', background='white', relief='raised')
    
    def criar_widgets(self):
        """Cria todos os elementos da interface"""
        
        # ==== MENU SUPERIOR ====
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Configurações", command=self.abrir_configuracoes)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.sair_sistema)
        
        # Menu Relatórios
        menu_relatorios = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Relatórios", menu=menu_relatorios)
        menu_relatorios.add_command(label="Relatório do Dia", 
                                   command=lambda: self.mostrar_relatorio('dia'))
        menu_relatorios.add_command(label="Relatório do Mês", 
                                   command=lambda: self.mostrar_relatorio('mes'))
        menu_relatorios.add_command(label="Relatório do Ano", 
                                   command=lambda: self.mostrar_relatorio('ano'))
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_ajuda.add_command(label="Atalhos", command=self.mostrar_atalhos)
        
        # ==== HEADER ====
        frame_header = tk.Frame(self.root, bg='#4a90e2', height=60)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)
        
        tk.Label(frame_header, text="🍦 Caixa da Sorveteria", 
                font=('Arial', 20, 'bold'), 
                bg='#4a90e2', fg='white').pack(side=tk.LEFT, padx=20)
        
        tk.Label(frame_header, text=f"👤 {self.usuario_nome}", 
                font=('Arial', 11), 
                bg='#4a90e2', fg='white').pack(side=tk.RIGHT, padx=20)
        
        # ==== CONTAINER PRINCIPAL ====
        container = tk.Frame(self.root, bg='#f5f5f5')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==== COLUNA ESQUERDA (Venda) ====
        frame_esquerda = tk.Frame(container, bg='#f5f5f5')
        frame_esquerda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        # Card de Venda
        card_venda = tk.Frame(frame_esquerda, bg='white', relief=tk.RAISED, bd=2)
        card_venda.pack(fill=tk.BOTH, expand=True)
        
        # Título do card
        tk.Label(card_venda, text="💰 Nova Venda", 
                font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=15)
        
        # Separador
        ttk.Separator(card_venda, orient='horizontal').pack(fill=tk.X, padx=20)
        
        # Área de conteúdo
        conteudo_venda = tk.Frame(card_venda, bg='white')
        conteudo_venda.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Configuração de valor por kg
        frame_config = tk.Frame(conteudo_venda, bg='white')
        frame_config.pack(fill=tk.X, pady=(0,20))
        
        tk.Label(frame_config, text="Valor por Kg:", 
                font=('Arial', 11, 'bold'), bg='white').pack(side=tk.LEFT)
        
        frame_valor = tk.Frame(frame_config, bg='white')
        frame_valor.pack(side=tk.LEFT, padx=10)
        
        tk.Label(frame_valor, text="R$", 
                font=('Arial', 11), bg='white').pack(side=tk.LEFT)
        
        self.entry_valor_kg = ttk.Entry(frame_valor, width=10, font=('Arial', 11))
        self.entry_valor_kg.insert(0, f"{self.valor_kg:.2f}")
        self.entry_valor_kg.pack(side=tk.LEFT, padx=5)
        
        btn_atualizar = tk.Button(frame_config, text="✓ Atualizar", 
                                 command=self.atualizar_valor_kg,
                                 bg='#5cb85c', fg='white',
                                 font=('Arial', 9, 'bold'),
                                 cursor='hand2', relief=tk.FLAT,
                                 padx=10, pady=5)
        btn_atualizar.pack(side=tk.LEFT, padx=5)
        
        # Campo de peso (DESTAQUE) - GRAMAS
        frame_peso = tk.Frame(conteudo_venda, bg='#f0f8ff', 
                             relief=tk.RIDGE, bd=2)
        frame_peso.pack(fill=tk.X, pady=20)
        
        tk.Label(frame_peso, text="⚖️ Peso (Gramas)", 
                font=('Arial', 14, 'bold'), 
                bg='#f0f8ff').pack(pady=10)
        
        self.entry_peso = ttk.Entry(frame_peso, width=15, 
                                   font=('Arial', 32, 'bold'),
                                   justify='center')
        self.entry_peso.pack(pady=10)
        self.entry_peso.focus()
        
        # Label para mostrar conversão
        self.label_kg = tk.Label(frame_peso, text="0.000 kg", 
                                font=('Arial', 12, 'italic'), 
                                bg='#f0f8ff', fg='#666')
        self.label_kg.pack(pady=(0,10))
        
        # Valor total (GRANDE)
        self.label_total = tk.Label(conteudo_venda, text="Total: R$ 0,00", 
                                   font=('Arial', 36, 'bold'), 
                                   fg='#2ecc71', bg='white')
        self.label_total.pack(pady=30)
        
        # Botões de ação
        frame_botoes = tk.Frame(conteudo_venda, bg='white')
        frame_botoes.pack(pady=10)
        
        btn_calcular = tk.Button(frame_botoes, text="🔢 Calcular", 
                                command=self.calcular_valor,
                                bg='#3498db', fg='white',
                                font=('Arial', 12, 'bold'),
                                cursor='hand2', relief=tk.FLAT,
                                padx=20, pady=12, width=12)
        btn_calcular.grid(row=0, column=0, padx=5)
        
        btn_registrar = tk.Button(frame_botoes, text="✅ Registrar", 
                                 command=self.registrar_venda,
                                 bg='#2ecc71', fg='white',
                                 font=('Arial', 12, 'bold'),
                                 cursor='hand2', relief=tk.FLAT,
                                 padx=20, pady=12, width=12)
        btn_registrar.grid(row=0, column=1, padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="🗑️ Limpar", 
                              command=self.limpar_campos,
                              bg='#e74c3c', fg='white',
                              font=('Arial', 12, 'bold'),
                              cursor='hand2', relief=tk.FLAT,
                              padx=20, pady=12, width=12)
        btn_limpar.grid(row=0, column=2, padx=5)
        
        # ==== COLUNA DIREITA (Informações) ====
        frame_direita = tk.Frame(container, bg='#f5f5f5', width=350)
        frame_direita.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5,0))
        frame_direita.pack_propagate(False)
        
        # Card de Estatísticas
        card_stats = tk.Frame(frame_direita, bg='white', relief=tk.RAISED, bd=2)
        card_stats.pack(fill=tk.X, pady=(0,10))
        
        tk.Label(card_stats, text="📈 Estatísticas de Hoje", 
                font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)
        
        ttk.Separator(card_stats, orient='horizontal').pack(fill=tk.X, padx=10)
        
        stats_content = tk.Frame(card_stats, bg='white')
        stats_content.pack(fill=tk.X, padx=20, pady=15)
        
        self.label_vendas_dia = tk.Label(stats_content, text="Vendas: 0", 
                                        font=('Arial', 11), bg='white', anchor='w')
        self.label_vendas_dia.pack(fill=tk.X, pady=3)
        
        self.label_kg_dia = tk.Label(stats_content, text="Total Kg: 0.000", 
                                     font=('Arial', 11), bg='white', anchor='w')
        self.label_kg_dia.pack(fill=tk.X, pady=3)
        
        self.label_valor_dia = tk.Label(stats_content, text="Total R$: 0,00", 
                                       font=('Arial', 11, 'bold'), 
                                       bg='white', fg='#27ae60', anchor='w')
        self.label_valor_dia.pack(fill=tk.X, pady=3)
        
        # Card de Histórico
        card_historico = tk.Frame(frame_direita, bg='white', relief=tk.RAISED, bd=2)
        card_historico.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(card_historico, text="📋 Últimas Vendas", 
                font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)
        
        ttk.Separator(card_historico, orient='horizontal').pack(fill=tk.X, padx=10)
        
        # Treeview com scrollbar
        frame_tree = tk.Frame(card_historico, bg='white')
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_vendas = ttk.Treeview(frame_tree, 
                                        columns=('Hora', 'Gramas', 'Kg', 'Valor'), 
                                        show='headings',
                                        yscrollcommand=scrollbar.set)
        
        self.tree_vendas.heading('Hora', text='Hora')
        self.tree_vendas.heading('Gramas', text='Gramas')
        self.tree_vendas.heading('Kg', text='Kg')
        self.tree_vendas.heading('Valor', text='Valor (R$)')
        
        self.tree_vendas.column('Hora', width=60, anchor='center')
        self.tree_vendas.column('Gramas', width=70, anchor='center')
        self.tree_vendas.column('Kg', width=70, anchor='center')
        self.tree_vendas.column('Valor', width=80, anchor='center')
        
        self.tree_vendas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_vendas.yview)
        
        # ==== BINDS (Atalhos) ====
        self.entry_peso.bind('<Return>', lambda e: self.calcular_valor())
        self.entry_peso.bind('<F2>', lambda e: self.registrar_venda())
        self.entry_peso.bind('<F4>', lambda e: self.limpar_campos())
        self.entry_peso.bind('<KeyRelease>', lambda e: self.atualizar_conversao_kg())
        
        # Atualizar histórico inicial
        self.atualizar_historico()
    
    def atualizar_conversao_kg(self):
        """Atualiza a conversão de gramas para kg em tempo real"""
        try:
            gramas_str = self.entry_peso.get().replace(',', '.')
            if gramas_str:
                gramas = float(gramas_str)
                kg = gramas / 1000
                self.label_kg.config(text=f"{kg:.3f} kg")
            else:
                self.label_kg.config(text="0.000 kg")
        except ValueError:
            self.label_kg.config(text="0.000 kg")
    
    def atualizar_valor_kg(self):
        """Atualiza o valor por kg"""
        try:
            valor_str = self.entry_valor_kg.get().replace(',', '.')
            novo_valor = float(valor_str)
            
            if novo_valor <= 0:
                raise ValueError("Valor deve ser maior que zero")
            
            self.valor_kg = novo_valor
            self.db.salvar_valor_kg_padrao(novo_valor)
            
            messagebox.showinfo("✅ Sucesso", 
                              f"Valor atualizado para R$ {self.valor_kg:.2f}/kg")
            
            # Recalcular se houver peso digitado
            if self.entry_peso.get():
                self.calcular_valor()
                
        except ValueError as e:
            messagebox.showerror("❌ Erro", "Valor inválido!")
            self.entry_valor_kg.delete(0, tk.END)
            self.entry_valor_kg.insert(0, f"{self.valor_kg:.2f}")
    
    def calcular_valor(self):
        """Calcula o valor total baseado no peso em GRAMAS"""
        try:
            gramas_str = self.entry_peso.get().replace(',', '.')
            gramas = float(gramas_str)
            
            if gramas < 0:
                raise ValueError("Peso não pode ser negativo")
            
            # Converter gramas para kg
            kg = gramas / 1000
            
            total = kg * self.valor_kg
            self.label_total.config(text=f"Total: R$ {total:.2f}")
            self.label_kg.config(text=f"{kg:.3f} kg")
            
            # Efeito visual de sucesso
            self.label_total.config(fg='#2ecc71')
            
        except ValueError:
            self.label_total.config(text="Total: R$ 0,00", fg='#e74c3c')
            self.label_kg.config(text="0.000 kg")
    
    def registrar_venda(self):
        """Registra uma nova venda no banco de dados (GRAMAS → KG)"""
        try:
            gramas_str = self.entry_peso.get().replace(',', '.')
            gramas = float(gramas_str)
            
            if gramas <= 0:
                messagebox.showwarning("⚠️ Aviso", "Peso deve ser maior que zero!")
                return
            
            # Converter gramas para kg
            kg = gramas / 1000
            
            # Registrar no banco
            valor_total = self.db.registrar_venda(kg, self.valor_kg, self.usuario_id)
            
            # Feedback visual
            messagebox.showinfo("✅ Venda Registrada", 
                              f"Peso: {gramas:.0f} gramas ({kg:.3f} kg)\n"
                              f"Valor/Kg: R$ {self.valor_kg:.2f}\n"
                              f"Total: R$ {valor_total:.2f}")
            
            # Atualizar interface
            self.limpar_campos()
            self.atualizar_historico()
            self.atualizar_estatisticas()
            
        except ValueError:
            messagebox.showerror("❌ Erro", "Peso inválido!")
    
    def limpar_campos(self):
        """Limpa os campos e reseta a tela"""
        self.entry_peso.delete(0, tk.END)
        self.label_total.config(text="Total: R$ 0,00", fg='#2ecc71')
        self.label_kg.config(text="0.000 kg")
        self.entry_peso.focus()
    
    def atualizar_historico(self):
        """Atualiza a lista de vendas do dia"""
        # Limpar tree
        for item in self.tree_vendas.get_children():
            self.tree_vendas.delete(item)
        
        # Buscar vendas do dia
        relatorio = self.db.obter_relatorio('dia')
        
        # Adicionar vendas (mais recentes primeiro)
        for venda in reversed(relatorio['vendas'][-20:]):  # Últimas 20
            hora = venda[4].split()[1][:5]  # HH:MM
            kg = venda[1]  # peso em kg
            gramas = kg * 1000  # converter para gramas
            
            self.tree_vendas.insert('', 0, values=(
                hora,
                f"{gramas:.0f}g",
                f"{kg:.3f}",
                f"{venda[3]:.2f}"
            ))
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas do dia"""
        relatorio = self.db.obter_relatorio('dia')
        
        self.label_vendas_dia.config(text=f"Vendas: {relatorio['total_vendas']}")
        self.label_kg_dia.config(text=f"Total Kg: {relatorio['total_kg']:.3f}")
        self.label_valor_dia.config(text=f"Total R$: {relatorio['total_valor']:.2f}")
    
    def mostrar_relatorio(self, periodo):
        """Abre janela com relatório detalhado"""
        janela_relatorio = tk.Toplevel(self.root)
        
        titulos = {'dia': 'Dia', 'mes': 'Mês', 'ano': 'Ano'}
        janela_relatorio.title(f"📊 Relatório do {titulos[periodo]}")
        janela_relatorio.geometry("900x650")
        janela_relatorio.grab_set()
        
        # Centralizar
        janela_relatorio.update_idletasks()
        x = (janela_relatorio.winfo_screenwidth() // 2) - 450
        y = (janela_relatorio.winfo_screenheight() // 2) - 325
        janela_relatorio.geometry(f'900x650+{x}+{y}')
        
        # Header
        frame_header = tk.Frame(janela_relatorio, bg='#3498db', height=60)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)
        
        tk.Label(frame_header, 
                text=f"📊 Relatório do {titulos[periodo]} - {datetime.now().strftime('%d/%m/%Y')}", 
                font=('Arial', 16, 'bold'), 
                bg='#3498db', fg='white').pack(expand=True)
        
        # Conteúdo
        frame_conteudo = tk.Frame(janela_relatorio, bg='white')
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Buscar dados
        relatorio = self.db.obter_relatorio(periodo)
        
        # Card de resumo
        card_resumo = tk.Frame(frame_conteudo, bg='#ecf0f1', relief=tk.RAISED, bd=2)
        card_resumo.pack(fill=tk.X, pady=(0,20))
        
        resumo_content = tk.Frame(card_resumo, bg='#ecf0f1')
        resumo_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Grid de informações
        info_vendas = tk.Frame(resumo_content, bg='#3498db', relief=tk.RAISED, bd=1)
        info_vendas.grid(row=0, column=0, padx=10, sticky='ew')
        tk.Label(info_vendas, text=str(relatorio['total_vendas']), 
                font=('Arial', 24, 'bold'), bg='#3498db', fg='white').pack(pady=5)
        tk.Label(info_vendas, text="Vendas", 
                font=('Arial', 10), bg='#3498db', fg='white').pack(pady=5)
        
        info_kg = tk.Frame(resumo_content, bg='#9b59b6', relief=tk.RAISED, bd=1)
        info_kg.grid(row=0, column=1, padx=10, sticky='ew')
        tk.Label(info_kg, text=f"{relatorio['total_kg']:.2f} kg", 
                font=('Arial', 24, 'bold'), bg='#9b59b6', fg='white').pack(pady=5)
        tk.Label(info_kg, text="Total em Kg", 
                font=('Arial', 10), bg='#9b59b6', fg='white').pack(pady=5)
        
        info_valor = tk.Frame(resumo_content, bg='#27ae60', relief=tk.RAISED, bd=1)
        info_valor.grid(row=0, column=2, padx=10, sticky='ew')
        tk.Label(info_valor, text=f"R$ {relatorio['total_valor']:.2f}", 
                font=('Arial', 24, 'bold'), bg='#27ae60', fg='white').pack(pady=5)
        tk.Label(info_valor, text="Faturamento", 
                font=('Arial', 10), bg='#27ae60', fg='white').pack(pady=5)
        
        resumo_content.columnconfigure(0, weight=1)
        resumo_content.columnconfigure(1, weight=1)
        resumo_content.columnconfigure(2, weight=1)
        
        # Tabela de vendas
        tk.Label(frame_conteudo, text="Detalhamento de Vendas", 
                font=('Arial', 12, 'bold'), bg='white').pack(anchor=tk.W, pady=(10,5))
        
        frame_tree = tk.Frame(frame_conteudo, bg='white')
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(frame_tree, orient='horizontal')
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        tree = ttk.Treeview(frame_tree, 
                           columns=('ID', 'Data/Hora', 'Gramas', 'Kg', 'Valor/Kg', 'Total'), 
                           show='headings',
                           yscrollcommand=scroll_y.set,
                           xscrollcommand=scroll_x.set)
        
        tree.heading('ID', text='ID')
        tree.heading('Data/Hora', text='Data/Hora')
        tree.heading('Gramas', text='Gramas')
        tree.heading('Kg', text='Kg')
        tree.heading('Valor/Kg', text='Valor/Kg')
        tree.heading('Total', text='Total (R$)')
        
        tree.column('ID', width=50, anchor='center')
        tree.column('Data/Hora', width=150, anchor='center')
        tree.column('Gramas', width=80, anchor='center')
        tree.column('Kg', width=80, anchor='center')
        tree.column('Valor/Kg', width=80, anchor='center')
        tree.column('Total', width=100, anchor='center')
        
        # Adicionar vendas
        for venda in relatorio['vendas']:
            kg = venda[1]
            gramas = kg * 1000
            tree.insert('', tk.END, values=(
                venda[0],  # ID
                venda[4],  # Data/Hora
                f"{gramas:.0f}g",  # Gramas
                f"{kg:.3f}",  # Kg
                f"R$ {venda[2]:.2f}",  # Valor/Kg
                f"R$ {venda[3]:.2f}"  # Total
            ))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        
        # Botão fechar
        btn_fechar = tk.Button(frame_conteudo, text="Fechar", 
                              command=janela_relatorio.destroy,
                              bg='#95a5a6', fg='white',
                              font=('Arial', 11, 'bold'),
                              cursor='hand2', relief=tk.FLAT,
                              padx=30, pady=10)
        btn_fechar.pack(pady=15)
    
    def abrir_configuracoes(self):
        """Abre janela de configurações"""
        janela_config = tk.Toplevel(self.root)
        janela_config.title("⚙️ Configurações")
        janela_config.geometry("400x300")
        janela_config.resizable(False, False)
        janela_config.grab_set()
        
        # Centralizar
        janela_config.update_idletasks()
        x = (janela_config.winfo_screenwidth() // 2) - 200
        y = (janela_config.winfo_screenheight() // 2) - 150
        janela_config.geometry(f'400x300+{x}+{y}')
        
        frame = tk.Frame(janela_config, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="⚙️ Configurações do Sistema", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=15)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Valor padrão por kg
        frame_valor = tk.Frame(frame, bg='white')
        frame_valor.pack(fill=tk.X, pady=15)
        
        tk.Label(frame_valor, text="Valor padrão por Kg:", 
                font=('Arial', 11), bg='white').pack(side=tk.LEFT)
        
        tk.Label(frame_valor, text="R$", 
                font=('Arial', 11), bg='white').pack(side=tk.LEFT, padx=(10,5))
        
        entry_config_valor = ttk.Entry(frame_valor, width=10, font=('Arial', 11))
        entry_config_valor.insert(0, f"{self.valor_kg:.2f}")
        entry_config_valor.pack(side=tk.LEFT)
        
        def salvar_config():
            try:
                novo_valor = float(entry_config_valor.get().replace(',', '.'))
                if novo_valor > 0:
                    self.valor_kg = novo_valor
                    self.db.salvar_valor_kg_padrao(novo_valor)
                    self.entry_valor_kg.delete(0, tk.END)
                    self.entry_valor_kg.insert(0, f"{novo_valor:.2f}")
                    messagebox.showinfo("✅ Sucesso", "Configuração salva!")
                    janela_config.destroy()
                else:
                    messagebox.showwarning("⚠️ Aviso", "Valor deve ser maior que zero!")
            except ValueError:
                messagebox.showerror("❌ Erro", "Valor inválido!")
        
        btn_salvar = tk.Button(frame, text="💾 Salvar", 
                              command=salvar_config,
                              bg='#27ae60', fg='white',
                              font=('Arial', 11, 'bold'),
                              cursor='hand2', relief=tk.FLAT,
                              padx=30, pady=10)
        btn_salvar.pack(pady=20)
    
    def mostrar_sobre(self):
        """Mostra informações sobre o sistema"""
        messagebox.showinfo("ℹ️ Sobre", 
                          "🍦 Sistema de Sorveteria v1.0\n\n"
                          "Desenvolvido para gestão de vendas\n"
                          "de sorvete por peso.\n\n"
                          "Funcionalidades:\n"
                          "✓ Controle de vendas\n"
                          "✓ Conversão gramas → kg\n"
                          "✓ Relatórios detalhados\n"
                          "✓ Múltiplos usuários\n"
                          "✓ Recuperação de senha\n\n"
                          "© 2024")
    
    def mostrar_atalhos(self):
        """Mostra os atalhos do teclado"""
        janela_atalhos = tk.Toplevel(self.root)
        janela_atalhos.title("⌨️ Atalhos do Teclado")
        janela_atalhos.geometry("400x300")
        janela_atalhos.resizable(False, False)
        janela_atalhos.grab_set()
        
        # Centralizar
        janela_atalhos.update_idletasks()
        x = (janela_atalhos.winfo_screenwidth() // 2) - 200
        y = (janela_atalhos.winfo_screenheight() // 2) - 150
        janela_atalhos.geometry(f'400x300+{x}+{y}')
        
        frame = tk.Frame(janela_atalhos, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="⌨️ Atalhos do Teclado", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=15)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        atalhos = [
            ("Enter", "Calcular valor da venda"),
            ("F2", "Registrar venda"),
            ("F4", "Limpar campos"),
        ]
        
        for tecla, acao in atalhos:
            frame_atalho = tk.Frame(frame, bg='#ecf0f1', relief=tk.RAISED, bd=1)
            frame_atalho.pack(fill=tk.X, pady=5, padx=10)
            
            tk.Label(frame_atalho, text=tecla, 
                    font=('Courier', 10, 'bold'), 
                    bg='#3498db', fg='white',
                    padx=15, pady=8, width=10).pack(side=tk.LEFT)
            
            tk.Label(frame_atalho, text=acao, 
                    font=('Arial', 10), 
                    bg='#ecf0f1', anchor='w').pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        btn_fechar = tk.Button(frame, text="OK", 
                              command=janela_atalhos.destroy,
                              bg='#3498db', fg='white',
                              font=('Arial', 10, 'bold'),
                              cursor='hand2', relief=tk.FLAT,
                              padx=30, pady=8)
        btn_fechar.pack(pady=20)
    
    def sair_sistema(self):
        """Sai do sistema"""
        if messagebox.askyesno("❓ Confirmar", "Deseja realmente sair do sistema?"):
            print("👋 Usuário saiu do sistema")
            self.db.fechar()
            self.root.quit()