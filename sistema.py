import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from database import Database
from datetime import datetime

class SistemaSorveteria:
    """Classe principal do sistema de caixa"""

    def __init__(self, root, usuario_id, usuario_nome, perfil, modo_teste=False):
        self.root = root
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.perfil = perfil
        self.modo_teste = modo_teste

        self.db = Database(modo_teste=modo_teste)

        self.root.title(f"🍦 Sorveteria - {usuario_nome} ({perfil.upper()})")

        # Estado da venda atual
        self.carrinho = []
        self.produto_selecionado = None
        self.valor_kg = self.db.obter_valor_kg_padrao()

        self.configurar_tema()
        self.criar_widgets()
        self.atualizar_estatisticas()

        print(f"✅ Sistema iniciado para usuário: {usuario_nome}")

    def configurar_tema(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Header.TFrame', background='#4a90e2')
        style.configure('Card.TFrame', background='white', relief='raised')

    # ============================================================
    # CRIAÇÃO DA INTERFACE
    # ============================================================

    def criar_widgets(self):
        """Cria todos os elementos da interface"""

        # ==== MENU SUPERIOR ====
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Arquivo", menu=menu_arquivo)

        if self.perfil in ['administrador', 'desenvolvedor']:
            menu_arquivo.add_command(label="👥 Gerenciar Usuários", command=self.gerenciar_usuarios)
            menu_arquivo.add_separator()
            menu_arquivo.add_command(label="⚙️ Configurações", command=self.abrir_configuracoes)
            menu_arquivo.add_separator()

        menu_arquivo.add_command(label="🚪 Sair", command=self.sair_sistema)

        if self.perfil in ['administrador', 'desenvolvedor']:
            menu_produtos = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="📦 Produtos", menu=menu_produtos)
            menu_produtos.add_command(label="🗂️ Categorias", command=self.gerenciar_categorias)
            menu_produtos.add_command(label="➕ Gerenciar Produtos", command=self.gerenciar_produtos)

        if self.perfil in ['administrador', 'desenvolvedor']:
            menu_relatorios = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="📊 Relatórios", menu=menu_relatorios)
            menu_relatorios.add_command(label="Relatório do Dia", command=lambda: self.mostrar_relatorio('dia'))
            menu_relatorios.add_command(label="Relatório do Mês", command=lambda: self.mostrar_relatorio('mes'))
            menu_relatorios.add_command(label="Relatório do Ano", command=lambda: self.mostrar_relatorio('ano'))

        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_ajuda.add_command(label="Atalhos", command=self.mostrar_atalhos)

        if self.modo_teste:
            frame_aviso = tk.Frame(self.root, bg='#ff6b6b', height=30)
            frame_aviso.pack(fill=tk.X)
            frame_aviso.pack_propagate(False)
            tk.Label(frame_aviso, text="⚠️ MODO DESENVOLVEDOR - DADOS NÃO SERÃO SALVOS ⚠️",
                    bg='#ff6b6b', fg='white', font=('Arial', 12, 'bold')).pack(expand=True)

        # ==== HEADER ====
        frame_header = tk.Frame(self.root, bg='#4a90e2', height=60)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="🍦 Caixa da Sorveteria",
                font=('Arial', 20, 'bold'), bg='#4a90e2', fg='white').pack(side=tk.LEFT, padx=20)

        tk.Label(frame_header, text=f"👤 {self.usuario_nome}",
                font=('Arial', 11), bg='#4a90e2', fg='white').pack(side=tk.RIGHT, padx=20)

        # ==== CONTAINER PRINCIPAL ====
        container = tk.Frame(self.root, bg='#f5f5f5')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ==== COLUNA ESQUERDA (Venda) ====
        frame_esquerda = tk.Frame(container, bg='#f5f5f5')
        frame_esquerda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        card_venda = tk.Frame(frame_esquerda, bg='white', relief=tk.RAISED, bd=2)
        card_venda.pack(fill=tk.BOTH, expand=True)

        tk.Label(card_venda, text="💰 Nova Venda", font=('Arial', 16, 'bold'),
                bg='white').pack(pady=15)

        ttk.Separator(card_venda, orient='horizontal').pack(fill=tk.X, padx=20)

        # Área dinâmica: categorias -> produtos -> quantidade -> pagamento
        self.frame_venda_dinamico = tk.Frame(card_venda, bg='white')
        self.frame_venda_dinamico.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        ttk.Separator(card_venda, orient='horizontal').pack(fill=tk.X, padx=20)

        # Área do carrinho (sempre visível)
        self.criar_area_carrinho(card_venda)

        # ==== COLUNA DIREITA (Informações) ====
        frame_direita = tk.Frame(container, bg='#f5f5f5', width=350)
        frame_direita.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        frame_direita.pack_propagate(False)

        card_stats = tk.Frame(frame_direita, bg='white', relief=tk.RAISED, bd=2)
        card_stats.pack(fill=tk.X, pady=(0, 10))

        tk.Label(card_stats, text="📈 Estatísticas de Hoje",
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)

        ttk.Separator(card_stats, orient='horizontal').pack(fill=tk.X, padx=10)

        stats_content = tk.Frame(card_stats, bg='white')
        stats_content.pack(fill=tk.X, padx=20, pady=15)

        self.label_vendas_dia = tk.Label(stats_content, text="Vendas: 0",
                                        font=('Arial', 11), bg='white', anchor='w')
        self.label_vendas_dia.pack(fill=tk.X, pady=3)

        self.label_kg_dia = tk.Label(stats_content, text="Total: R$ 0,00",
                                     font=('Arial', 11), bg='white', anchor='w')
        self.label_kg_dia.pack(fill=tk.X, pady=3)

        self.label_valor_dia = tk.Label(stats_content, text="Faturamento: R$ 0,00",
                                       font=('Arial', 11, 'bold'),
                                       bg='white', fg='#27ae60', anchor='w')
        self.label_valor_dia.pack(fill=tk.X, pady=3)

        card_historico = tk.Frame(frame_direita, bg='white', relief=tk.RAISED, bd=2)
        card_historico.pack(fill=tk.BOTH, expand=True)

        tk.Label(card_historico, text="📋 Últimas Vendas",
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)

        ttk.Separator(card_historico, orient='horizontal').pack(fill=tk.X, padx=10)

        frame_tree = tk.Frame(card_historico, bg='white')
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_vendas = ttk.Treeview(frame_tree,
                                        columns=('Hora', 'Produto', 'Valor'),
                                        show='headings',
                                        yscrollcommand=scrollbar.set)

        self.tree_vendas.heading('Hora', text='Hora')
        self.tree_vendas.heading('Produto', text='Produto')
        self.tree_vendas.heading('Valor', text='Valor (R$)')

        self.tree_vendas.column('Hora', width=60, anchor='center')
        self.tree_vendas.column('Produto', width=150)
        self.tree_vendas.column('Valor', width=80, anchor='center')

        self.tree_vendas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_vendas.yview)

        # Inicia o fluxo pela tela de categorias
        self.mostrar_view_categorias()
        self.atualizar_historico()

    def criar_area_carrinho(self, parent):
        """Cria a área do carrinho, sempre visível na tela de venda"""
        frame_carrinho = tk.Frame(parent, bg='white')
        frame_carrinho.pack(fill=tk.X, padx=20, pady=(10, 15))

        tk.Label(frame_carrinho, text="🛒 Carrinho", font=('Arial', 12, 'bold'),
                bg='white').pack(anchor='w')

        tree_frame = tk.Frame(frame_carrinho, bg='white')
        tree_frame.pack(fill=tk.X, pady=(5, 5))

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_carrinho = ttk.Treeview(tree_frame, columns=('Produto', 'Qtd', 'Valor'),
                                          show='headings', height=4, yscrollcommand=scroll.set)
        self.tree_carrinho.heading('Produto', text='Produto')
        self.tree_carrinho.heading('Qtd', text='Qtd/Peso')
        self.tree_carrinho.heading('Valor', text='Valor (R$)')
        self.tree_carrinho.column('Produto', width=180)
        self.tree_carrinho.column('Qtd', width=100, anchor='center')
        self.tree_carrinho.column('Valor', width=90, anchor='center')
        self.tree_carrinho.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scroll.config(command=self.tree_carrinho.yview)

        self.label_total_carrinho = tk.Label(frame_carrinho, text="Total do Carrinho: R$ 0,00",
                                             font=('Arial', 14, 'bold'), bg='white', fg='#2ecc71')
        self.label_total_carrinho.pack(pady=(5, 10))

        frame_btns_carrinho = tk.Frame(frame_carrinho, bg='white')
        frame_btns_carrinho.pack()

        tk.Button(frame_btns_carrinho, text="🗑️ Remover Item",
                 command=self.remover_item_carrinho,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=8).grid(row=0, column=0, padx=5)

        self.btn_finalizar_venda = tk.Button(frame_btns_carrinho, text="✅ Finalizar Venda",
                 command=self.mostrar_view_pagamento,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=8, state='disabled')
        self.btn_finalizar_venda.grid(row=0, column=1, padx=5)

        tk.Button(frame_btns_carrinho, text="❌ Cancelar Venda",
                 command=self.cancelar_venda,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=8).grid(row=0, column=2, padx=5)

    # ============================================================
    # FLUXO DE VENDA: CATEGORIA -> PRODUTO -> QUANTIDADE -> PAGAMENTO
    # ============================================================

    def limpar_frame_dinamico(self):
        for widget in self.frame_venda_dinamico.winfo_children():
            widget.destroy()

    def mostrar_view_categorias(self):
        """Tela 1: grid de botões de categorias"""
        self.limpar_frame_dinamico()
        self.produto_selecionado = None

        tk.Label(self.frame_venda_dinamico, text="🗂️ Escolha uma categoria:",
                font=('Arial', 13, 'bold'), bg='white').pack(pady=(0, 15))

        categorias = self.db.listar_categorias()

        if not categorias:
            tk.Label(self.frame_venda_dinamico,
                    text="Nenhuma categoria cadastrada.\nCadastre em Produtos → Categorias",
                    font=('Arial', 11), bg='white', fg='#999').pack(pady=30)
            return

        frame_grid = tk.Frame(self.frame_venda_dinamico, bg='white')
        frame_grid.pack()

        colunas = 3
        for i, cat in enumerate(categorias):
            cat_id, cat_nome, cat_desc = cat
            row, col = divmod(i, colunas)
            btn = tk.Button(frame_grid, text=f"🗂️\n{cat_nome}",
                            font=('Arial', 11, 'bold'), bg='#4a90e2', fg='white',
                            width=14, height=3, cursor='hand2', relief=tk.FLAT,
                            command=lambda cid=cat_id, cnome=cat_nome: self.mostrar_view_produtos(cid, cnome))
            btn.grid(row=row, column=col, padx=8, pady=8)

    def mostrar_view_produtos(self, categoria_id, categoria_nome):
        """Tela 2: grid de produtos da categoria escolhida"""
        self.limpar_frame_dinamico()

        topo = tk.Frame(self.frame_venda_dinamico, bg='white')
        topo.pack(fill=tk.X, pady=(0, 10))

        tk.Button(topo, text="⬅️ Voltar", command=self.mostrar_view_categorias,
                 bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'),
                 cursor='hand2', relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT)

        tk.Label(topo, text=f"📦 Produtos - {categoria_nome}",
                font=('Arial', 13, 'bold'), bg='white').pack(side=tk.LEFT, padx=15)

        produtos = self.db.listar_produtos(categoria_id=categoria_id, ativos_apenas=True)

        if not produtos:
            tk.Label(self.frame_venda_dinamico, text="Nenhum produto nesta categoria.",
                    font=('Arial', 11), bg='white', fg='#999').pack(pady=30)
            return

        frame_grid = tk.Frame(self.frame_venda_dinamico, bg='white')
        frame_grid.pack()

        colunas = 3
        for i, prod in enumerate(produtos):
            prod_id, nome, cat_nome, tipo_venda, valor, ativo = prod
            tipo_texto = 'Kg' if tipo_venda == 'peso' else 'Un'
            row, col = divmod(i, colunas)
            btn = tk.Button(frame_grid, text=f"🍦 {nome}\nR$ {valor:.2f}/{tipo_texto}",
                            font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                            width=16, height=3, cursor='hand2', relief=tk.FLAT,
                            command=lambda pid=prod_id, cid=categoria_id, cnome=categoria_nome:
                                self.mostrar_view_quantidade(pid, cid, cnome))
            btn.grid(row=row, column=col, padx=8, pady=8)

    def mostrar_view_quantidade(self, produto_id, categoria_id, categoria_nome):
        """Tela 3: digitar peso/quantidade do produto escolhido"""
        produto = self.db.obter_produto(produto_id)
        if not produto:
            messagebox.showerror("❌ Erro", "Produto não encontrado!")
            return

        self.produto_selecionado = {
            'id': produto[0], 'nome': produto[1], 'categoria_id': produto[2],
            'tipo_venda': produto[3], 'valor': produto[4], 'ativo': produto[5]
        }

        self.limpar_frame_dinamico()

        topo = tk.Frame(self.frame_venda_dinamico, bg='white')
        topo.pack(fill=tk.X, pady=(0, 10))
        tk.Button(topo, text="⬅️ Voltar",
                 command=lambda: self.mostrar_view_produtos(categoria_id, categoria_nome),
                 bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'),
                 cursor='hand2', relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT)

        tipo_texto = 'Kg' if self.produto_selecionado['tipo_venda'] == 'peso' else 'Un'
        tk.Label(self.frame_venda_dinamico,
                text=f"📦 {self.produto_selecionado['nome']} - R$ {self.produto_selecionado['valor']:.2f}/{tipo_texto}",
                font=('Arial', 13, 'bold'), bg='#e3f2fd', fg='#1565c0').pack(fill=tk.X, pady=10, ipady=8)

        label_tipo = "⚖️ Peso (Gramas)" if self.produto_selecionado['tipo_venda'] == 'peso' else "🔢 Quantidade"
        tk.Label(self.frame_venda_dinamico, text=label_tipo,
                font=('Arial', 12, 'bold'), bg='white').pack(pady=(15, 5))

        self.entry_peso_quantidade = ttk.Entry(self.frame_venda_dinamico, width=12,
                                              font=('Arial', 28, 'bold'), justify='center')
        self.entry_peso_quantidade.pack(pady=5)
        self.entry_peso_quantidade.focus()

        texto_inicial = "0.000 kg" if self.produto_selecionado['tipo_venda'] == 'peso' else "0 unidades"
        self.label_conversao = tk.Label(self.frame_venda_dinamico, text=texto_inicial,
                                        font=('Arial', 11, 'italic'), bg='white', fg='#666')
        self.label_conversao.pack()

        self.label_total_item = tk.Label(self.frame_venda_dinamico, text="Total: R$ 0,00",
                                         font=('Arial', 22, 'bold'), fg='#2ecc71', bg='white')
        self.label_total_item.pack(pady=15)

        self.entry_peso_quantidade.bind('<KeyRelease>', lambda e: self.atualizar_conversao_item())
        self.entry_peso_quantidade.bind('<Return>', lambda e: self.confirmar_adicionar_item())

        frame_botoes = tk.Frame(self.frame_venda_dinamico, bg='white')
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="✅ Adicionar ao Carrinho",
                 command=self.confirmar_adicionar_item,
                 bg='#2ecc71', fg='white', font=('Arial', 11, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack()

    def atualizar_conversao_item(self):
        if not self.produto_selecionado:
            return
        try:
            valor_str = self.entry_peso_quantidade.get().replace(',', '.')
            if not valor_str:
                texto = "0.000 kg" if self.produto_selecionado['tipo_venda'] == 'peso' else "0 unidades"
                self.label_conversao.config(text=texto)
                self.label_total_item.config(text="Total: R$ 0,00")
                return

            valor = float(valor_str)

            if self.produto_selecionado['tipo_venda'] == 'peso':
                kg = valor / 1000
                total = kg * self.produto_selecionado['valor']
                self.label_conversao.config(text=f"{kg:.3f} kg")
            else:
                total = valor * self.produto_selecionado['valor']
                self.label_conversao.config(text=f"{int(valor)} unidades")

            self.label_total_item.config(text=f"Total: R$ {total:.2f}")
        except ValueError:
            pass

    def confirmar_adicionar_item(self):
        """Adiciona o produto atual ao carrinho e volta para categorias"""
        if not self.produto_selecionado:
            return

        try:
            valor_str = self.entry_peso_quantidade.get().replace(',', '.')
            valor_input = float(valor_str)
            if valor_input <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("❌ Erro", "Digite um valor válido!")
            return

        if self.produto_selecionado['tipo_venda'] == 'peso':
            kg = valor_input / 1000
            valor_total = kg * self.produto_selecionado['valor']
            item = {
                'produto_id': self.produto_selecionado['id'],
                'nome': self.produto_selecionado['nome'],
                'peso': kg,
                'quantidade': None,
                'valor_unitario': self.produto_selecionado['valor'],
                'valor_total': valor_total,
                'descricao_qtd': f"{kg:.3f} kg"
            }
        else:
            qtd = int(valor_input)
            valor_total = qtd * self.produto_selecionado['valor']
            item = {
                'produto_id': self.produto_selecionado['id'],
                'nome': self.produto_selecionado['nome'],
                'peso': None,
                'quantidade': qtd,
                'valor_unitario': self.produto_selecionado['valor'],
                'valor_total': valor_total,
                'descricao_qtd': f"{qtd} un"
            }

        self.carrinho.append(item)
        self.atualizar_exibicao_carrinho()
        self.mostrar_view_categorias()

    # ============================================================
    # CARRINHO
    # ============================================================

    def atualizar_exibicao_carrinho(self):
        for i in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(i)

        total_geral = 0
        for idx, item in enumerate(self.carrinho):
            self.tree_carrinho.insert('', tk.END, iid=str(idx), values=(
                item['nome'], item['descricao_qtd'], f"{item['valor_total']:.2f}"
            ))
            total_geral += item['valor_total']

        self.label_total_carrinho.config(text=f"Total do Carrinho: R$ {total_geral:.2f}")
        self.btn_finalizar_venda.config(state='normal' if self.carrinho else 'disabled')

    def remover_item_carrinho(self):
        sel = self.tree_carrinho.selection()
        if not sel:
            messagebox.showwarning("⚠️ Aviso", "Selecione um item do carrinho para remover!")
            return
        idx = int(sel[0])
        del self.carrinho[idx]
        self.atualizar_exibicao_carrinho()

    def cancelar_venda(self):
        if not self.carrinho:
            return
        if messagebox.askyesno("❓ Confirmar", "Deseja cancelar a venda e limpar o carrinho?"):
            self.carrinho = []
            self.atualizar_exibicao_carrinho()
            self.mostrar_view_categorias()

    # ============================================================
    # PAGAMENTO
    # ============================================================

    def mostrar_view_pagamento(self):
        """Tela 4: escolha da forma de pagamento"""
        if not self.carrinho:
            messagebox.showwarning("⚠️ Aviso", "Carrinho vazio!")
            return

        self.limpar_frame_dinamico()

        total = sum(item['valor_total'] for item in self.carrinho)

        topo = tk.Frame(self.frame_venda_dinamico, bg='white')
        topo.pack(fill=tk.X, pady=(0, 10))
        tk.Button(topo, text="⬅️ Voltar ao Carrinho", command=self.mostrar_view_categorias,
                 bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'),
                 cursor='hand2', relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT)

        tk.Label(self.frame_venda_dinamico, text="💳 Escolha a forma de pagamento",
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(10, 5))

        tk.Label(self.frame_venda_dinamico, text=f"Total a pagar: R$ {total:.2f}",
                font=('Arial', 24, 'bold'), fg='#2ecc71', bg='white').pack(pady=15)

        frame_pagamentos = tk.Frame(self.frame_venda_dinamico, bg='white')
        frame_pagamentos.pack(pady=20)

        tk.Button(frame_pagamentos, text="💵\nDinheiro", font=('Arial', 13, 'bold'),
                 bg='#27ae60', fg='white', width=12, height=4, cursor='hand2',
                 relief=tk.FLAT, command=lambda: self.processar_pagamento_dinheiro(total)
                 ).grid(row=0, column=0, padx=10)

        tk.Button(frame_pagamentos, text="💳\nCartão", font=('Arial', 13, 'bold'),
                 bg='#3498db', fg='white', width=12, height=4, cursor='hand2',
                 relief=tk.FLAT, command=lambda: self.processar_pagamento_cartao(total)
                 ).grid(row=0, column=1, padx=10)

        tk.Button(frame_pagamentos, text="📱\nPix", font=('Arial', 13, 'bold'),
                 bg='#9b59b6', fg='white', width=12, height=4, cursor='hand2',
                 relief=tk.FLAT, command=lambda: self.finalizar_venda('pix', None, total)
                 ).grid(row=0, column=2, padx=10)

    def processar_pagamento_dinheiro(self, total):
        """Pergunta o valor recebido e calcula o troco"""
        valor_recebido = simpledialog.askfloat(
            "💵 Pagamento em Dinheiro",
            f"Total a pagar: R$ {total:.2f}\n\nValor recebido do cliente:",
            parent=self.root, minvalue=0
        )
        if valor_recebido is None:
            return
        if valor_recebido < total:
            messagebox.showwarning("⚠️ Aviso", "Valor recebido é menor que o total da venda!")
            return

        troco = valor_recebido - total
        detalhes = f"Recebido: R$ {valor_recebido:.2f} | Troco: R$ {troco:.2f}"
        self.finalizar_venda('dinheiro', detalhes, total)

    def processar_pagamento_cartao(self, total):
        """Pergunta se é crédito ou débito"""
        janela = tk.Toplevel(self.root)
        janela.title("💳 Tipo de Cartão")
        janela.geometry("320x160")
        janela.grab_set()
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 160
        y = (janela.winfo_screenheight() // 2) - 80
        janela.geometry(f'320x160+{x}+{y}')

        tk.Label(janela, text="Selecione o tipo de cartão:",
                font=('Arial', 11, 'bold')).pack(pady=15)

        frame_btns = tk.Frame(janela)
        frame_btns.pack(pady=10)

        def escolher(tipo):
            janela.destroy()
            self.finalizar_venda('cartao', tipo, total)

        tk.Button(frame_btns, text="Crédito", command=lambda: escolher("Crédito"),
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                 relief=tk.FLAT, padx=15, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btns, text="Débito", command=lambda: escolher("Débito"),
                 bg='#2980b9', fg='white', font=('Arial', 10, 'bold'),
                 relief=tk.FLAT, padx=15, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=10)

    def finalizar_venda(self, forma_pagamento, detalhes_pagamento, total):
        """Salva o pedido completo no banco de dados"""
        try:
            pedido_id, valor_total = self.db.registrar_pedido(
                itens=self.carrinho,
                forma_pagamento=forma_pagamento,
                detalhes_pagamento=detalhes_pagamento,
                usuario_id=self.usuario_id
            )

            resumo = "\n".join([
                f"• {item['nome']} - {item['descricao_qtd']} - R$ {item['valor_total']:.2f}"
                for item in self.carrinho
            ])

            msg = (f"Pedido #{pedido_id} registrado!\n\n{resumo}\n\n"
                   f"Total: R$ {valor_total:.2f}\nPagamento: {forma_pagamento.title()}")
            if detalhes_pagamento:
                msg += f"\n{detalhes_pagamento}"

            messagebox.showinfo("✅ Venda Finalizada", msg)

            self.carrinho = []
            self.atualizar_exibicao_carrinho()
            self.mostrar_view_categorias()
            self.atualizar_historico()
            self.atualizar_estatisticas()

        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao registrar venda: {e}")

    # ============================================================
    # HISTÓRICO E ESTATÍSTICAS
    # ============================================================

    def atualizar_historico(self):
        """Atualiza a lista de itens vendidos no dia"""
        for item in self.tree_vendas.get_children():
            self.tree_vendas.delete(item)

        relatorio = self.db.obter_relatorio('dia')

        for item in reversed(relatorio['itens'][-20:]):
            # item = (id, pedido_id, produto_nome, peso, quantidade, valor_total, data_hora, forma_pagamento)
            hora = item[6].split()[1][:5] if item[6] else "00:00"
            nome_produto = item[2] or "Produto"
            valor_total = item[5] or 0

            self.tree_vendas.insert('', 0, values=(hora, nome_produto[:20], f"{valor_total:.2f}"))

    def atualizar_estatisticas(self):
        relatorio = self.db.obter_relatorio('dia')
        self.label_vendas_dia.config(text=f"Vendas: {relatorio['total_vendas']}")
        self.label_kg_dia.config(text=f"Total: R$ {relatorio['total_valor']:.2f}")
        self.label_valor_dia.config(text=f"Faturamento: R$ {relatorio['total_valor']:.2f}")

    # ============================================================
    # DEMAIS TELAS (menus)
    # ============================================================

    def mostrar_relatorio(self, periodo):
        """Abre janela com relatório detalhado (dia, mês ou ano)"""

        # 🔒 Verificação de segurança extra
        if self.perfil not in ['administrador', 'desenvolvedor']:
            messagebox.showerror("🔒 Acesso Negado",
                                "Apenas administradores e desenvolvedores\n"
                                "podem acessar relatórios!")
            return

        titulos = {
            'dia': f"Hoje ({datetime.now().strftime('%d/%m/%Y')})",
            'mes': f"Este Mês ({datetime.now().strftime('%m/%Y')})",
            'ano': f"Este Ano ({datetime.now().strftime('%Y')})"
        }
        titulo_periodo = titulos.get(periodo, periodo)

        janela = tk.Toplevel(self.root)
        janela.title(f"📊 Relatório - {titulo_periodo}")
        janela.geometry("900x650")
        janela.grab_set()

        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 450
        y = (janela.winfo_screenheight() // 2) - 325
        janela.geometry(f'900x650+{x}+{y}')

        header = tk.Frame(janela, bg='#2c3e50', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text=f"📊 Relatório de Vendas - {titulo_periodo}",
                font=('Arial', 15, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Busca os dados
        relatorio = self.db.obter_relatorio(periodo)
        pagamentos = self.db.obter_resumo_pagamentos(periodo)
        ranking = self.db.obter_ranking_produtos(periodo)

        # ==== ABAS ====
        notebook = ttk.Notebook(janela)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        aba_resumo = tk.Frame(notebook, bg='white')
        aba_pedidos = tk.Frame(notebook, bg='white')
        aba_ranking = tk.Frame(notebook, bg='white')

        notebook.add(aba_resumo, text="  📈 Resumo  ")
        notebook.add(aba_pedidos, text="  🧾 Pedidos  ")
        notebook.add(aba_ranking, text="  🏆 Mais Vendidos  ")

        # ============================================================
        # ABA 1: RESUMO
        # ============================================================
        total_vendas = relatorio['total_vendas']
        total_valor = relatorio['total_valor']
        total_kg = relatorio['total_kg']
        ticket_medio = (total_valor / total_vendas) if total_vendas > 0 else 0

        frame_cards = tk.Frame(aba_resumo, bg='white')
        frame_cards.pack(fill=tk.X, pady=20, padx=20)

        def criar_card(parent, titulo, valor, cor):
            card = tk.Frame(parent, bg=cor, relief=tk.RAISED, bd=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            tk.Label(card, text=titulo, font=('Arial', 10, 'bold'),
                    bg=cor, fg='white').pack(pady=(15, 5))
            tk.Label(card, text=valor, font=('Arial', 18, 'bold'),
                    bg=cor, fg='white').pack(pady=(0, 15))

        criar_card(frame_cards, "🧾 Total de Vendas", str(total_vendas), '#3498db')
        criar_card(frame_cards, "💰 Faturamento", f"R$ {total_valor:.2f}", '#27ae60')
        criar_card(frame_cards, "🎯 Ticket Médio", f"R$ {ticket_medio:.2f}", '#9b59b6')
        criar_card(frame_cards, "⚖️ Total em Kg", f"{total_kg:.3f} kg", '#e67e22')

        # Breakdown por forma de pagamento
        tk.Label(aba_resumo, text="💳 Faturamento por Forma de Pagamento",
                font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', padx=20, pady=(20, 10))

        frame_pag = tk.Frame(aba_resumo, bg='white')
        frame_pag.pack(fill=tk.X, padx=20)

        icones_pagamento = {'dinheiro': '💵', 'cartao': '💳', 'pix': '📱'}

        if not pagamentos:
            tk.Label(frame_pag, text="Nenhuma venda registrada neste período.",
                    font=('Arial', 10), bg='white', fg='#999').pack(pady=10)
        else:
            for forma, qtd, valor in pagamentos:
                forma_nome = (forma or "Não informado").title()
                icone = icones_pagamento.get(forma, '❓')
                linha = tk.Frame(frame_pag, bg='#f8f9fa', relief=tk.GROOVE, bd=1)
                linha.pack(fill=tk.X, pady=4)
                tk.Label(linha, text=f"{icone} {forma_nome}", font=('Arial', 11, 'bold'),
                        bg='#f8f9fa', width=20, anchor='w').pack(side=tk.LEFT, padx=15, pady=8)
                tk.Label(linha, text=f"{qtd} venda(s)", font=('Arial', 10),
                        bg='#f8f9fa', width=15, anchor='w').pack(side=tk.LEFT)
                tk.Label(linha, text=f"R$ {valor:.2f}", font=('Arial', 11, 'bold'),
                        bg='#f8f9fa', fg='#27ae60', anchor='e').pack(side=tk.RIGHT, padx=15)

        # ============================================================
        # ABA 2: LISTA DE PEDIDOS
        # ============================================================
        tk.Label(aba_pedidos, text="🧾 Pedidos do Período",
                font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', padx=15, pady=(15, 10))

        # Conta quantos itens tem cada pedido
        itens_por_pedido = {}
        for item in relatorio['itens']:
            pedido_id = item[1]
            itens_por_pedido[pedido_id] = itens_por_pedido.get(pedido_id, 0) + 1

        frame_tree_pedidos = tk.Frame(aba_pedidos, bg='white')
        frame_tree_pedidos.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        scroll_pedidos = ttk.Scrollbar(frame_tree_pedidos)
        scroll_pedidos.pack(side=tk.RIGHT, fill=tk.Y)

        tree_pedidos = ttk.Treeview(frame_tree_pedidos,
                           columns=('ID', 'Data/Hora', 'Itens', 'Pagamento', 'Total'),
                           show='headings', yscrollcommand=scroll_pedidos.set)
        tree_pedidos.heading('ID', text='#Pedido')
        tree_pedidos.heading('Data/Hora', text='Data/Hora')
        tree_pedidos.heading('Itens', text='Qtd Itens')
        tree_pedidos.heading('Pagamento', text='Pagamento')
        tree_pedidos.heading('Total', text='Total (R$)')

        tree_pedidos.column('ID', width=70, anchor='center')
        tree_pedidos.column('Data/Hora', width=150, anchor='center')
        tree_pedidos.column('Itens', width=80, anchor='center')
        tree_pedidos.column('Pagamento', width=120, anchor='center')
        tree_pedidos.column('Total', width=100, anchor='center')

        tree_pedidos.pack(fill=tk.BOTH, expand=True)
        scroll_pedidos.config(command=tree_pedidos.yview)

        for pedido in reversed(relatorio['pedidos']):
            pedido_id, data_hora, valor_total, forma_pagamento, detalhes, usuario_id = pedido
            qtd_itens = itens_por_pedido.get(pedido_id, 0)
            forma_texto = (forma_pagamento or "N/A").title()
            tree_pedidos.insert('', tk.END, values=(
                f"#{pedido_id}", data_hora, qtd_itens, forma_texto, f"{valor_total:.2f}"
            ))

        # ============================================================
        # ABA 3: RANKING DE PRODUTOS
        # ============================================================
        tk.Label(aba_ranking, text="🏆 Produtos Mais Vendidos",
                font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', padx=15, pady=(15, 10))

        frame_tree_ranking = tk.Frame(aba_ranking, bg='white')
        frame_tree_ranking.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        scroll_ranking = ttk.Scrollbar(frame_tree_ranking)
        scroll_ranking.pack(side=tk.RIGHT, fill=tk.Y)

        tree_ranking = ttk.Treeview(frame_tree_ranking,
                           columns=('Pos', 'Produto', 'Vendas', 'Qtd/Peso', 'Faturamento'),
                           show='headings', yscrollcommand=scroll_ranking.set)
        tree_ranking.heading('Pos', text='#')
        tree_ranking.heading('Produto', text='Produto')
        tree_ranking.heading('Vendas', text='Nº de Vendas')
        tree_ranking.heading('Qtd/Peso', text='Qtd Total')
        tree_ranking.heading('Faturamento', text='Faturamento (R$)')

        tree_ranking.column('Pos', width=40, anchor='center')
        tree_ranking.column('Produto', width=220)
        tree_ranking.column('Vendas', width=100, anchor='center')
        tree_ranking.column('Qtd/Peso', width=140, anchor='center')
        tree_ranking.column('Faturamento', width=130, anchor='center')

        tree_ranking.pack(fill=tk.BOTH, expand=True)
        scroll_ranking.config(command=tree_ranking.yview)

        if not ranking:
            tree_ranking.insert('', tk.END, values=('-', 'Nenhuma venda no período', '-', '-', '-'))
        else:
            for pos, prod in enumerate(ranking, start=1):
                nome, vezes, unidades, peso, valor = prod
                nome = nome or "Produto removido"

                partes_qtd = []
                if unidades:
                    partes_qtd.append(f"{int(unidades)} un")
                if peso:
                    partes_qtd.append(f"{peso:.3f} kg")
                qtd_texto = " / ".join(partes_qtd) if partes_qtd else "-"

                medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, str(pos))

                tree_ranking.insert('', tk.END, values=(
                    medalha, nome, vezes, qtd_texto, f"{valor:.2f}"
                ))

        # ============================================================
        # BOTÕES INFERIORES
        # ============================================================
        frame_btns = tk.Frame(janela, bg='#f0f0f0')
        frame_btns.pack(fill=tk.X, padx=15, pady=(0, 15))

        def exportar_txt():
            caminho = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt")],
                initialfile=f"relatorio_{periodo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                parent=janela
            )
            if not caminho:
                return

            try:
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(f"{'='*50}\n")
                    f.write(f"RELATÓRIO DE VENDAS - {titulo_periodo.upper()}\n")
                    f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(f"{'='*50}\n\n")

                    f.write("RESUMO GERAL\n")
                    f.write(f"Total de Vendas: {total_vendas}\n")
                    f.write(f"Faturamento Total: R$ {total_valor:.2f}\n")
                    f.write(f"Ticket Médio: R$ {ticket_medio:.2f}\n")
                    f.write(f"Total em Kg vendido: {total_kg:.3f} kg\n\n")

                    f.write("FATURAMENTO POR FORMA DE PAGAMENTO\n")
                    for forma, qtd, valor in pagamentos:
                        f.write(f"  {(forma or 'N/A').title()}: {qtd} venda(s) - R$ {valor:.2f}\n")
                    f.write("\n")

                    f.write("PRODUTOS MAIS VENDIDOS\n")
                    for pos, prod in enumerate(ranking, start=1):
                        nome, vezes, unidades, peso, valor = prod
                        f.write(f"  {pos}º {nome or 'Produto removido'} - "
                                f"{vezes} venda(s) - R$ {valor:.2f}\n")
                    f.write("\n")

                    f.write("PEDIDOS DETALHADOS\n")
                    for pedido in relatorio['pedidos']:
                        pedido_id, data_hora, valor_total, forma_pagamento, detalhes, usuario_id = pedido
                        f.write(f"  Pedido #{pedido_id} | {data_hora} | "
                                f"{(forma_pagamento or 'N/A').title()} | R$ {valor_total:.2f}\n")

                messagebox.showinfo("✅ Sucesso", f"Relatório exportado para:\n{caminho}", parent=janela)
            except Exception as e:
                messagebox.showerror("❌ Erro", f"Erro ao exportar: {e}", parent=janela)

        tk.Button(frame_btns, text="📄 Exportar para TXT",
                 command=exportar_txt, bg='#16a085', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack(side=tk.LEFT)

        tk.Button(frame_btns, text="✖️ Fechar",
                 command=janela.destroy, bg='#95a5a6', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack(side=tk.RIGHT)

    def abrir_configuracoes(self):
        if self.perfil == 'funcionario':
            messagebox.showwarning("⚠️ Acesso Negado",
                                 "Apenas administradores podem acessar configurações!")
            return
        messagebox.showinfo("⚙️ Configurações", "Configurações disponíveis em breve!")

    def mostrar_sobre(self):
        messagebox.showinfo("ℹ️ Sobre",
                          "🍦 Sistema de Sorveteria v2.0\n\n"
                          "Desenvolvido para gestão de vendas\n"
                          "de sorvete por peso e unidade.\n\n"
                          "Funcionalidades:\n"
                          "✓ Venda por categoria/produto (grid)\n"
                          "✓ Carrinho com múltiplos itens\n"
                          "✓ Pagamento: Dinheiro, Cartão e Pix\n"
                          "✓ Categorias de produtos\n"
                          "✓ Relatórios detalhados\n"
                          "✓ Múltiplos usuários e perfis\n\n"
                          "© 2024")

    def mostrar_atalhos(self):
        messagebox.showinfo("⌨️ Atalhos",
                          "Enter - Adicionar item ao carrinho\n"
                          "(durante a digitação de peso/quantidade)")

    def gerenciar_categorias(self):
        """Janela de gerenciamento de categorias"""
        janela = tk.Toplevel(self.root)
        janela.title("🗂️ Gerenciar Categorias")
        janela.geometry("700x600")
        janela.grab_set()

        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 350
        y = (janela.winfo_screenheight() // 2) - 300
        janela.geometry(f'700x600+{x}+{y}')

        header = tk.Frame(janela, bg='#3498db', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🗂️ Categorias de Produtos",
                font=('Arial', 16, 'bold'), bg='#3498db', fg='white').pack(expand=True)

        frame = tk.Frame(janela, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        frame_add = tk.LabelFrame(frame, text="Nova Categoria",
                                 bg='white', font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame_add.pack(fill=tk.X, pady=(0, 20))

        tk.Label(frame_add, text="Nome:", bg='white').grid(row=0, column=0, sticky='e', padx=5)
        entry_nome = ttk.Entry(frame_add, width=30)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Descrição:", bg='white').grid(row=1, column=0, sticky='e', padx=5)
        entry_desc = ttk.Entry(frame_add, width=30)
        entry_desc.grid(row=1, column=1, padx=5, pady=5)

        def adicionar():
            nome = entry_nome.get().strip()
            desc = entry_desc.get().strip()
            if nome:
                sucesso, msg = self.db.criar_categoria(nome, desc)
                if sucesso:
                    messagebox.showinfo("✅ Sucesso", msg, parent=janela)
                    entry_nome.delete(0, tk.END)
                    entry_desc.delete(0, tk.END)
                    atualizar_lista()
                    self.mostrar_view_categorias()
                else:
                    messagebox.showerror("❌ Erro", msg, parent=janela)
            else:
                messagebox.showwarning("⚠️ Aviso", "Digite o nome da categoria!", parent=janela)

        tk.Button(frame_add, text="➕ Adicionar",
                 command=adicionar, bg='#27ae60', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=20, pady=8).grid(row=0, column=2, rowspan=2, padx=10)

        tk.Label(frame, text="Categorias Existentes:",
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(10, 5))

        tree_frame = tk.Frame(frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame, columns=('ID', 'Nome', 'Descrição'),
                           show='headings', yscrollcommand=scroll.set)
        tree.heading('ID', text='ID')
        tree.heading('Nome', text='Nome')
        tree.heading('Descrição', text='Descrição')
        tree.column('ID', width=50)
        tree.column('Nome', width=200)
        tree.column('Descrição', width=400)
        tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=tree.yview)

        def atualizar_lista():
            tree.delete(*tree.get_children())
            categorias = self.db.listar_categorias()
            for cat in categorias:
                tree.insert('', tk.END, values=cat)

        def excluir():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                cat_id = item['values'][0]
                cat_nome = item['values'][1]
                if messagebox.askyesno("Confirmar",
                                      f"Deseja excluir a categoria '{cat_nome}'?",
                                      parent=janela):
                    self.db.excluir_categoria(cat_id)
                    messagebox.showinfo("✅ Sucesso", "Categoria excluída!", parent=janela)
                    atualizar_lista()
                    self.mostrar_view_categorias()
            else:
                messagebox.showwarning("⚠️ Aviso", "Selecione uma categoria!", parent=janela)

        frame_btns = tk.Frame(frame, bg='white')
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="🗑️ Excluir Selecionado",
                 command=excluir, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=20, pady=10).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="✖️ Fechar",
                 command=janela.destroy, bg='#95a5a6', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=20, pady=10).pack(side=tk.LEFT, padx=5)

        atualizar_lista()

    def gerenciar_produtos(self):
        """Janela de gerenciamento de produtos (CRUD completo)"""
        janela = tk.Toplevel(self.root)
        janela.title("📦 Gerenciar Produtos")
        janela.geometry("800x650")
        janela.grab_set()

        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 400
        y = (janela.winfo_screenheight() // 2) - 325
        janela.geometry(f'800x650+{x}+{y}')

        header = tk.Frame(janela, bg='#27ae60', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="📦 Produtos",
                font=('Arial', 16, 'bold'), bg='#27ae60', fg='white').pack(expand=True)

        frame = tk.Frame(janela, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ==== FORMULÁRIO ====
        frame_form = tk.LabelFrame(frame, text="Produto",
                                   bg='white', font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame_form.pack(fill=tk.X, pady=(0, 15))

        # Nome
        tk.Label(frame_form, text="Nome:", bg='white').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        entry_nome = ttk.Entry(frame_form, width=30)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)

        # Categoria
        tk.Label(frame_form, text="Categoria:", bg='white').grid(row=0, column=2, sticky='e', padx=5, pady=5)
        combo_categoria = ttk.Combobox(frame_form, width=20, state='readonly')
        combo_categoria.grid(row=0, column=3, padx=5, pady=5)

        # Tipo de venda
        tk.Label(frame_form, text="Tipo de Venda:", bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        combo_tipo = ttk.Combobox(frame_form, width=27, state='readonly',
                                  values=["peso - Vendido por Kg", "unidade - Vendido por Unidade"])
        combo_tipo.grid(row=1, column=1, padx=5, pady=5)

        # Valor
        tk.Label(frame_form, text="Valor (R$):", bg='white').grid(row=1, column=2, sticky='e', padx=5, pady=5)
        entry_valor = ttk.Entry(frame_form, width=20)
        entry_valor.grid(row=1, column=3, padx=5, pady=5)

        # Guarda o ID do produto em edição (None = criando novo)
        produto_editando = {'id': None}

        def carregar_categorias_combo():
            categorias = self.db.listar_categorias()
            if categorias:
                combo_categoria['values'] = [f"{cat[0]} - {cat[1]}" for cat in categorias]
            else:
                combo_categoria['values'] = []

        def limpar_formulario():
            produto_editando['id'] = None
            entry_nome.delete(0, tk.END)
            combo_categoria.set('')
            combo_tipo.set('')
            entry_valor.delete(0, tk.END)
            btn_salvar.config(text="➕ Adicionar Produto", bg='#27ae60')

        def salvar():
            nome = entry_nome.get().strip()
            categoria_sel = combo_categoria.get()
            tipo_sel = combo_tipo.get()
            valor_str = entry_valor.get().strip().replace(',', '.')

            if not nome:
                messagebox.showwarning("⚠️ Aviso", "Digite o nome do produto!", parent=janela)
                return
            if not categoria_sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione uma categoria!", parent=janela)
                return
            if not tipo_sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione o tipo de venda!", parent=janela)
                return
            try:
                valor = float(valor_str)
                if valor <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("⚠️ Aviso", "Digite um valor válido!", parent=janela)
                return

            categoria_id = int(categoria_sel.split(' - ')[0])
            tipo_venda = tipo_sel.split(' - ')[0]  # 'peso' ou 'unidade'

            if produto_editando['id'] is None:
                # Criando novo produto
                sucesso, msg = self.db.criar_produto(nome, categoria_id, tipo_venda, valor)
            else:
                # Editando produto existente
                sucesso, msg = self.db.atualizar_produto(produto_editando['id'], nome, valor, ativo=1)
                msg = "Produto atualizado com sucesso!"

            if sucesso:
                messagebox.showinfo("✅ Sucesso", msg, parent=janela)
                limpar_formulario()
                atualizar_lista()
                self.mostrar_view_categorias()  # atualiza a tela de venda
            else:
                messagebox.showerror("❌ Erro", msg, parent=janela)

        btn_salvar = tk.Button(frame_form, text="➕ Adicionar Produto",
                 command=salvar, bg='#27ae60', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=8)
        btn_salvar.grid(row=0, column=4, rowspan=2, padx=10)

        tk.Button(frame_form, text="🗑️ Limpar",
                 command=limpar_formulario, bg='#95a5a6', fg='white',
                 font=('Arial', 9, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=10, pady=8).grid(row=0, column=5, rowspan=2, padx=5)

        # ==== LISTA DE PRODUTOS ====
        tk.Label(frame, text="Produtos Cadastrados:",
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(5, 5))

        tree_frame = tk.Frame(frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame,
                           columns=('ID', 'Nome', 'Categoria', 'Tipo', 'Valor', 'Status'),
                           show='headings', yscrollcommand=scroll.set)
        tree.heading('ID', text='ID')
        tree.heading('Nome', text='Nome')
        tree.heading('Categoria', text='Categoria')
        tree.heading('Tipo', text='Tipo')
        tree.heading('Valor', text='Valor (R$)')
        tree.heading('Status', text='Status')

        tree.column('ID', width=40, anchor='center')
        tree.column('Nome', width=180)
        tree.column('Categoria', width=140)
        tree.column('Tipo', width=80, anchor='center')
        tree.column('Valor', width=90, anchor='center')
        tree.column('Status', width=80, anchor='center')

        tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=tree.yview)

        def atualizar_lista():
            tree.delete(*tree.get_children())
            produtos = self.db.listar_produtos(ativos_apenas=False)
            for prod in produtos:
                prod_id, nome, cat_nome, tipo_venda, valor, ativo = prod
                tipo_texto = 'Kg' if tipo_venda == 'peso' else 'Un'
                status_texto = '✅ Ativo' if ativo else '❌ Inativo'
                tree.insert('', tk.END, values=(
                    prod_id, nome, cat_nome or '-', tipo_texto, f"{valor:.2f}", status_texto
                ))

        def carregar_para_edicao():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um produto!", parent=janela)
                return
            item = tree.item(sel[0])
            prod_id = item['values'][0]

            produto = self.db.obter_produto(prod_id)
            if not produto:
                return

            _, nome, categoria_id, tipo_venda, valor, ativo = produto

            entry_nome.delete(0, tk.END)
            entry_nome.insert(0, nome)

            categorias = self.db.listar_categorias()
            for cat in categorias:
                if cat[0] == categoria_id:
                    combo_categoria.set(f"{cat[0]} - {cat[1]}")
                    break

            tipo_texto = "peso - Vendido por Kg" if tipo_venda == 'peso' else "unidade - Vendido por Unidade"
            combo_tipo.set(tipo_texto)

            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, f"{valor:.2f}")

            produto_editando['id'] = prod_id
            btn_salvar.config(text="💾 Salvar Alterações", bg='#3498db')

        def alternar_status():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um produto!", parent=janela)
                return
            item = tree.item(sel[0])
            prod_id = item['values'][0]
            status_atual = item['values'][5]

            produto = self.db.obter_produto(prod_id)
            if not produto:
                return

            _, nome, categoria_id, tipo_venda, valor, ativo = produto
            novo_status = 0 if ativo else 1

            self.db.atualizar_produto(prod_id, nome, valor, novo_status)
            atualizar_lista()
            self.mostrar_view_categorias()

            texto = "ativado" if novo_status else "desativado"
            messagebox.showinfo("✅ Sucesso", f"Produto {texto}!", parent=janela)

        def excluir():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um produto!", parent=janela)
                return
            item = tree.item(sel[0])
            prod_id = item['values'][0]
            prod_nome = item['values'][1]

            if messagebox.askyesno("Confirmar",
                                  f"Deseja excluir o produto '{prod_nome}'?\n\n"
                                  f"⚠️ Isso também pode afetar vendas antigas registradas com ele.",
                                  parent=janela):
                self.db.excluir_produto(prod_id)
                messagebox.showinfo("✅ Sucesso", "Produto excluído!", parent=janela)
                atualizar_lista()
                self.mostrar_view_categorias()

        # Duplo clique carrega para edição
        tree.bind('<Double-1>', lambda e: carregar_para_edicao())

        # ==== BOTÕES DE AÇÃO DA LISTA ====
        frame_btns = tk.Frame(frame, bg='white')
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="✏️ Editar Selecionado",
                 command=carregar_para_edicao, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="🔄 Ativar/Desativar",
                 command=alternar_status, bg='#f39c12', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="🗑️ Excluir",
                 command=excluir, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="✖️ Fechar",
                 command=janela.destroy, bg='#95a5a6', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=10).pack(side=tk.LEFT, padx=5)

        carregar_categorias_combo()
        atualizar_lista()

    def gerenciar_usuarios(self):
        """Janela de gerenciamento de usuários (CRUD completo)"""

        # 🔒 Verificação de segurança extra (defesa em profundidade)
        if self.perfil not in ['administrador', 'desenvolvedor']:
            messagebox.showerror("🔒 Acesso Negado",
                                "Apenas administradores e desenvolvedores\n"
                                "podem gerenciar usuários!")
            return

        janela = tk.Toplevel(self.root)
        janela.title("👥 Gerenciar Usuários")
        janela.geometry("850x650")
        janela.grab_set()

        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 425
        y = (janela.winfo_screenheight() // 2) - 325
        janela.geometry(f'850x650+{x}+{y}')

        header = tk.Frame(janela, bg='#8e44ad', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="👥 Usuários do Sistema",
                font=('Arial', 16, 'bold'), bg='#8e44ad', fg='white').pack(expand=True)

        frame = tk.Frame(janela, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ==== FORMULÁRIO ====
        frame_form = tk.LabelFrame(frame, text="Dados do Usuário",
                                   bg='white', font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame_form.pack(fill=tk.X, pady=(0, 15))

        # Nome
        tk.Label(frame_form, text="Nome:", bg='white').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        entry_nome = ttk.Entry(frame_form, width=25)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)

        # Usuário (login)
        tk.Label(frame_form, text="Usuário (login):", bg='white').grid(row=0, column=2, sticky='e', padx=5, pady=5)
        entry_usuario = ttk.Entry(frame_form, width=20)
        entry_usuario.grid(row=0, column=3, padx=5, pady=5)

        # Senha
        tk.Label(frame_form, text="Senha:", bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        entry_senha = ttk.Entry(frame_form, width=25, show='*')
        entry_senha.grid(row=1, column=1, padx=5, pady=5)

        # Perfil
        tk.Label(frame_form, text="Perfil:", bg='white').grid(row=1, column=2, sticky='e', padx=5, pady=5)
        valores_perfil = ["funcionario", "administrador"]
        # Apenas desenvolvedor pode criar outro administrador com privilégio total
        combo_perfil = ttk.Combobox(frame_form, width=17, state='readonly', values=valores_perfil)
        combo_perfil.grid(row=1, column=3, padx=5, pady=5)
        combo_perfil.set("funcionario")

        # Pergunta de segurança
        tk.Label(frame_form, text="Pergunta Segurança:", bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        entry_pergunta = ttk.Entry(frame_form, width=25)
        entry_pergunta.grid(row=2, column=1, padx=5, pady=5)

        # Resposta de segurança
        tk.Label(frame_form, text="Resposta:", bg='white').grid(row=2, column=2, sticky='e', padx=5, pady=5)
        entry_resposta = ttk.Entry(frame_form, width=20)
        entry_resposta.grid(row=2, column=3, padx=5, pady=5)

        aviso_senha = tk.Label(frame_form,
                              text="💡 Ao editar, deixe a senha em branco para não alterá-la.",
                              bg='white', fg='#888', font=('Arial', 8, 'italic'))
        aviso_senha.grid(row=3, column=0, columnspan=4, pady=(5, 0))

        # Guarda o ID do usuário em edição (None = criando novo)
        usuario_editando = {'id': None}

        def limpar_formulario():
            usuario_editando['id'] = None
            entry_nome.delete(0, tk.END)
            entry_usuario.delete(0, tk.END)
            entry_usuario.config(state='normal')
            entry_senha.delete(0, tk.END)
            combo_perfil.set("funcionario")
            entry_pergunta.delete(0, tk.END)
            entry_resposta.delete(0, tk.END)
            btn_salvar.config(text="➕ Adicionar Usuário", bg='#27ae60')

        def salvar():
            nome = entry_nome.get().strip()
            usuario = entry_usuario.get().strip()
            senha = entry_senha.get().strip()
            perfil = combo_perfil.get()
            pergunta = entry_pergunta.get().strip()
            resposta = entry_resposta.get().strip()

            if not nome or not usuario:
                messagebox.showwarning("⚠️ Aviso", "Preencha nome e usuário!", parent=janela)
                return
            if not perfil:
                messagebox.showwarning("⚠️ Aviso", "Selecione um perfil!", parent=janela)
                return

            if usuario_editando['id'] is None:
                # ===== Criando novo usuário =====
                if not senha:
                    messagebox.showwarning("⚠️ Aviso", "Digite uma senha!", parent=janela)
                    return
                if not pergunta or not resposta:
                    messagebox.showwarning("⚠️ Aviso",
                                          "Preencha a pergunta e resposta de segurança!\n"
                                          "(Necessário para recuperação de senha)",
                                          parent=janela)
                    return

                sucesso, msg = self.db.criar_usuario(nome, usuario, senha, perfil, pergunta, resposta)

                if sucesso:
                    messagebox.showinfo("✅ Sucesso", msg, parent=janela)
                    limpar_formulario()
                    atualizar_lista()
                else:
                    messagebox.showerror("❌ Erro", msg, parent=janela)
            else:
                # ===== Editando usuário existente =====
                sucesso, msg = self.db.atualizar_usuario(usuario_editando['id'], nome, perfil)

                # Se digitou uma nova senha, atualiza também
                if senha:
                    self.db.redefinir_senha_id(usuario_editando['id'], senha)
                    msg += " Senha também foi redefinida."

                messagebox.showinfo("✅ Sucesso", msg, parent=janela)
                limpar_formulario()
                atualizar_lista()

        btn_salvar = tk.Button(frame_form, text="➕ Adicionar Usuário",
                 command=salvar, bg='#27ae60', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=15, pady=8)
        btn_salvar.grid(row=0, column=4, rowspan=2, padx=10)

        tk.Button(frame_form, text="🗑️ Limpar",
                 command=limpar_formulario, bg='#95a5a6', fg='white',
                 font=('Arial', 9, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=10, pady=8).grid(row=2, column=4, padx=10)

        # ==== LISTA DE USUÁRIOS ====
        tk.Label(frame, text="Usuários Cadastrados:",
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(5, 5))

        tree_frame = tk.Frame(frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame,
                           columns=('ID', 'Nome', 'Usuário', 'Perfil', 'Criado em', 'Status'),
                           show='headings', yscrollcommand=scroll.set)
        tree.heading('ID', text='ID')
        tree.heading('Nome', text='Nome')
        tree.heading('Usuário', text='Usuário')
        tree.heading('Perfil', text='Perfil')
        tree.heading('Criado em', text='Criado em')
        tree.heading('Status', text='Status')

        tree.column('ID', width=40, anchor='center')
        tree.column('Nome', width=160)
        tree.column('Usuário', width=120)
        tree.column('Perfil', width=110, anchor='center')
        tree.column('Criado em', width=140, anchor='center')
        tree.column('Status', width=80, anchor='center')

        tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=tree.yview)

        def atualizar_lista():
            tree.delete(*tree.get_children())
            usuarios = self.db.listar_usuarios()  # já exclui perfil 'desenvolvedor'
            for usr in usuarios:
                usr_id, nome, usuario, perfil, data_criacao, ativo = usr
                status_texto = '✅ Ativo' if ativo else '❌ Inativo'
                tree.insert('', tk.END, values=(
                    usr_id, nome, usuario, perfil.title(), data_criacao, status_texto
                ))

        def carregar_para_edicao():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um usuário!", parent=janela)
                return
            item = tree.item(sel[0])
            usr_id = item['values'][0]

            usuario_db = self.db.obter_usuario(usr_id)
            if not usuario_db:
                return

            _, nome, usuario, perfil, ativo = usuario_db

            entry_nome.delete(0, tk.END)
            entry_nome.insert(0, nome)

            entry_usuario.delete(0, tk.END)
            entry_usuario.insert(0, usuario)
            entry_usuario.config(state='disabled')  # não permite trocar o login

            entry_senha.delete(0, tk.END)  # fica em branco (só altera se digitar)

            combo_perfil.set(perfil)

            entry_pergunta.delete(0, tk.END)
            entry_resposta.delete(0, tk.END)

            usuario_editando['id'] = usr_id
            btn_salvar.config(text="💾 Salvar Alterações", bg='#3498db')

        def alternar_status():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um usuário!", parent=janela)
                return
            item = tree.item(sel[0])
            usr_id = item['values'][0]

            if usr_id == self.usuario_id:
                messagebox.showwarning("⚠️ Aviso",
                                      "Você não pode desativar seu próprio usuário!",
                                      parent=janela)
                return

            usuario_db = self.db.obter_usuario(usr_id)
            if not usuario_db:
                return

            _, nome, usuario, perfil, ativo = usuario_db
            novo_status = 0 if ativo else 1

            self.db.atualizar_status_usuario(usr_id, novo_status)
            atualizar_lista()

            texto = "ativado" if novo_status else "desativado"
            messagebox.showinfo("✅ Sucesso", f"Usuário {texto}!", parent=janela)

        def redefinir_senha_rapido():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um usuário!", parent=janela)
                return
            item = tree.item(sel[0])
            usr_id = item['values'][0]
            usr_nome = item['values'][1]

            nova_senha = simpledialog.askstring(
                "🔑 Redefinir Senha",
                f"Digite a nova senha para '{usr_nome}':",
                parent=janela, show='*'
            )
            if nova_senha:
                self.db.redefinir_senha_id(usr_id, nova_senha)
                messagebox.showinfo("✅ Sucesso", "Senha redefinida com sucesso!", parent=janela)

        def excluir():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecione um usuário!", parent=janela)
                return
            item = tree.item(sel[0])
            usr_id = item['values'][0]
            usr_nome = item['values'][1]

            if usr_id == self.usuario_id:
                messagebox.showwarning("⚠️ Aviso",
                                      "Você não pode excluir seu próprio usuário!",
                                      parent=janela)
                return

            if messagebox.askyesno("Confirmar",
                                  f"Deseja excluir o usuário '{usr_nome}'?\n\n"
                                  f"⚠️ Essa ação não pode ser desfeita!",
                                  parent=janela):
                self.db.excluir_usuario(usr_id)
                messagebox.showinfo("✅ Sucesso", "Usuário excluído!", parent=janela)
                atualizar_lista()

        # Duplo clique carrega para edição
        tree.bind('<Double-1>', lambda e: carregar_para_edicao())

        # ==== BOTÕES DE AÇÃO DA LISTA ====
        frame_btns = tk.Frame(frame, bg='white')
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="✏️ Editar",
                 command=carregar_para_edicao, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=12, pady=10).pack(side=tk.LEFT, padx=4)

        tk.Button(frame_btns, text="🔄 Ativar/Desativar",
                 command=alternar_status, bg='#f39c12', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=12, pady=10).pack(side=tk.LEFT, padx=4)

        tk.Button(frame_btns, text="🔑 Redefinir Senha",
                 command=redefinir_senha_rapido, bg='#9b59b6', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=12, pady=10).pack(side=tk.LEFT, padx=4)

        tk.Button(frame_btns, text="🗑️ Excluir",
                 command=excluir, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=12, pady=10).pack(side=tk.LEFT, padx=4)

        tk.Button(frame_btns, text="✖️ Fechar",
                 command=janela.destroy, bg='#95a5a6', fg='white',
                 font=('Arial', 10, 'bold'), cursor='hand2',
                 relief=tk.FLAT, padx=12, pady=10).pack(side=tk.LEFT, padx=4)

        atualizar_lista()

    def sair_sistema(self):
        if messagebox.askyesno("❓ Confirmar", "Deseja realmente sair do sistema?"):
            print("👋 Usuário saiu do sistema")
            self.db.fechar()
            self.root.destroy()