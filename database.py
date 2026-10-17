import sqlite3
from datetime import datetime
import hashlib

class Database:
    """Classe para gerenciar o banco de dados da sorveteria"""

    def __init__(self, modo_teste=False):
        if modo_teste:
            self.conn = sqlite3.connect(':memory:')
            print("⚠️ MODO TESTE DESENVOLVEDOR - Dados não serão salvos!")
        else:
            self.conn = sqlite3.connect('sorveteria.db')

        self.modo_teste = modo_teste
        self.criar_tabelas()
        self.criar_usuario_padrao()

    # ==================== TABELAS ====================

    def criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados"""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'funcionario'
                    CHECK(perfil IN ('funcionario', 'administrador', 'desenvolvedor')),
                pergunta_seguranca TEXT,
                resposta_seguranca TEXT,
                data_criacao TEXT,
                ativo INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                data_criacao TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria_id INTEGER,
                tipo_venda TEXT CHECK(tipo_venda IN ('peso', 'unidade')),
                valor REAL NOT NULL,
                ativo INTEGER DEFAULT 1,
                data_criacao TEXT,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id)
            )
        ''')

        # NOVA: Tabela de pedidos (cabeçalho da venda - pode ter vários itens)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL,
                valor_total REAL NOT NULL,
                forma_pagamento TEXT,
                detalhes_pagamento TEXT,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')

        # ATUALIZADA: vendas agora são ITENS de um pedido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                produto_id INTEGER,
                peso REAL,
                quantidade INTEGER,
                valor_unitario REAL NOT NULL,
                valor_total REAL NOT NULL,
                data_hora TEXT NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL
            )
        ''')

        self.conn.commit()
        print("✅ Banco de dados inicializado com sucesso!")

    def criar_usuario_padrao(self):
        """Cria usuário administrador padrão se não existir"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM usuarios WHERE perfil = "administrador"')
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute('''
                    INSERT INTO usuarios (nome, usuario, senha, perfil,
                                        pergunta_seguranca, resposta_seguranca,
                                        data_criacao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    "Administrador",
                    "admin",
                    self.hash_senha("admin123"),
                    "administrador",
                    "Qual o nome do sistema?",
                    self.hash_senha("sorveteria"),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                self.conn.commit()
                print("👤 Usuário administrador padrão criado: admin/admin123")
        except Exception as e:
            print(f"⚠️ Aviso ao criar usuário padrão: {e}")

    def hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    # ==================== USUÁRIOS ====================

    def criar_usuario(self, nome, usuario, senha, perfil, pergunta, resposta):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios (nome, usuario, senha, perfil, pergunta_seguranca,
                                    resposta_seguranca, data_criacao, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (nome, usuario, self.hash_senha(senha), perfil, pergunta,
                  self.hash_senha(resposta.lower().strip()),
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
            print(f"✅ Usuário '{usuario}' ({perfil}) criado com sucesso!")
            return True, "Usuário criado com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Nome de usuário já existe!"
        except Exception as e:
            return False, f"Erro ao criar usuário: {e}"

    def verificar_login(self, usuario, senha):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, nome, perfil FROM usuarios
            WHERE usuario = ? AND senha = ? AND ativo = 1
        ''', (usuario, self.hash_senha(senha)))
        resultado = cursor.fetchone()
        if resultado:
            print(f"✅ Login bem-sucedido: {resultado[1]} ({resultado[2]})")
        else:
            print("❌ Login falhou: usuário ou senha incorretos")
        return resultado

    def recuperar_senha(self, usuario, resposta):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE usuario = ? AND resposta_seguranca = ?',
                      (usuario, self.hash_senha(resposta.lower().strip())))
        return cursor.fetchone() is not None

    def alterar_senha(self, usuario, nova_senha):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE usuarios SET senha = ? WHERE usuario = ?',
                      (self.hash_senha(nova_senha), usuario))
        self.conn.commit()

    def obter_pergunta_seguranca(self, usuario):
        cursor = self.conn.cursor()
        cursor.execute('SELECT pergunta_seguranca FROM usuarios WHERE usuario = ?', (usuario,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

    def listar_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, nome, usuario, perfil, data_criacao, ativo
            FROM usuarios WHERE perfil != 'desenvolvedor' ORDER BY nome
        ''')
        return cursor.fetchall()

    def atualizar_status_usuario(self, usuario_id, ativo):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE usuarios SET ativo = ? WHERE id = ?', (ativo, usuario_id))
        self.conn.commit()
        return True, "Status atualizado!"

    def excluir_usuario(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
        self.conn.commit()
        return True, "Usuário excluído!"
    def atualizar_usuario(self, usuario_id, nome, perfil):
        """Atualiza nome e perfil de um usuário"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE usuarios SET nome = ?, perfil = ? WHERE id = ?',
                      (nome, perfil, usuario_id))
        self.conn.commit()
        return True, "Usuário atualizado com sucesso!"

    def redefinir_senha_id(self, usuario_id, nova_senha):
        """Redefine a senha de um usuário pelo ID"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE usuarios SET senha = ? WHERE id = ?',
                      (self.hash_senha(nova_senha), usuario_id))
        self.conn.commit()
        return True, "Senha redefinida com sucesso!"

    def obter_usuario(self, usuario_id):
        """Busca dados de um usuário específico pelo ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, nome, usuario, perfil, ativo FROM usuarios WHERE id = ?',
                      (usuario_id,))
        return cursor.fetchone()
    # ==================== CATEGORIAS ====================

    def criar_categoria(self, nome, descricao=""):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO categorias (nome, descricao, data_criacao)
                VALUES (?, ?, ?)
            ''', (nome, descricao, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
            return True, "Categoria criada com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Categoria já existe!"

    def listar_categorias(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, nome, descricao FROM categorias ORDER BY nome')
        return cursor.fetchall()

    def excluir_categoria(self, categoria_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM categorias WHERE id = ?', (categoria_id,))
        self.conn.commit()
        return True, "Categoria excluída!"

    # ==================== PRODUTOS ====================

    def criar_produto(self, nome, categoria_id, tipo_venda, valor):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (nome, categoria_id, tipo_venda, valor, data_criacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, categoria_id, tipo_venda, valor,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()
        return True, "Produto criado com sucesso!"

    def listar_produtos(self, categoria_id=None, ativos_apenas=True):
        cursor = self.conn.cursor()
        query = '''
            SELECT p.id, p.nome, c.nome, p.tipo_venda, p.valor, p.ativo
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
        '''
        params = []
        conditions = []
        if categoria_id:
            conditions.append('p.categoria_id = ?')
            params.append(categoria_id)
        if ativos_apenas:
            conditions.append('p.ativo = 1')
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY c.nome, p.nome'
        cursor.execute(query, params)
        return cursor.fetchall()

    def atualizar_produto(self, produto_id, nome, valor, ativo):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE produtos SET nome = ?, valor = ?, ativo = ? WHERE id = ?
        ''', (nome, valor, ativo, produto_id))
        self.conn.commit()
        return True, "Produto atualizado!"

    def excluir_produto(self, produto_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        self.conn.commit()
        return True, "Produto excluído!"

    def obter_produto(self, produto_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, nome, categoria_id, tipo_venda, valor, ativo
            FROM produtos WHERE id = ?
        ''', (produto_id,))
        return cursor.fetchone()

    # ==================== PEDIDOS / VENDAS ====================

    def registrar_pedido(self, itens, forma_pagamento, detalhes_pagamento, usuario_id):
        """
        Registra um pedido completo (pode conter vários produtos/itens)

        Args:
            itens: lista de dicts com produto_id, peso, quantidade,
                   valor_unitario, valor_total
            forma_pagamento: 'dinheiro', 'cartao', 'pix'
            detalhes_pagamento: string com detalhes extras (troco, crédito/débito)
            usuario_id: quem registrou a venda

        Returns:
            (pedido_id, valor_total_pedido)
        """
        cursor = self.conn.cursor()
        valor_total_pedido = sum(item['valor_total'] for item in itens)
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO pedidos (data_hora, valor_total, forma_pagamento,
                                detalhes_pagamento, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (data_hora, valor_total_pedido, forma_pagamento, detalhes_pagamento, usuario_id))

        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute('''
                INSERT INTO vendas (pedido_id, produto_id, peso, quantidade,
                                   valor_unitario, valor_total, data_hora, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pedido_id, item['produto_id'], item.get('peso'), item.get('quantidade'),
                  item['valor_unitario'], item['valor_total'], data_hora, usuario_id))

        self.conn.commit()
        print(f"✅ Pedido #{pedido_id} registrado: {len(itens)} item(ns), "
              f"Total R${valor_total_pedido:.2f}, Pagamento: {forma_pagamento}")
        return pedido_id, valor_total_pedido

    def obter_relatorio(self, periodo='dia'):
        """
        Gera relatório de vendas por período

        Args:
            periodo: 'dia', 'mes' ou 'ano'

        Returns:
            Dicionário com 'pedidos', 'itens', 'total_vendas', 'total_kg', 'total_valor'
        """
        cursor = self.conn.cursor()

        if periodo == 'dia':
            data_filtro = datetime.now().strftime('%Y-%m-%d')
            condicao_pedido = "date(data_hora) = ?"
            condicao_item = "date(pe.data_hora) = ?"
        elif periodo == 'mes':
            data_filtro = datetime.now().strftime('%Y-%m')
            condicao_pedido = "strftime('%Y-%m', data_hora) = ?"
            condicao_item = "strftime('%Y-%m', pe.data_hora) = ?"
        else:  # ano
            data_filtro = datetime.now().strftime('%Y')
            condicao_pedido = "strftime('%Y', data_hora) = ?"
            condicao_item = "strftime('%Y', pe.data_hora) = ?"

        cursor.execute(f'''
            SELECT id, data_hora, valor_total, forma_pagamento, detalhes_pagamento, usuario_id
            FROM pedidos WHERE {condicao_pedido} ORDER BY data_hora
        ''', (data_filtro,))
        pedidos = cursor.fetchall()

        cursor.execute(f'''
            SELECT v.id, v.pedido_id, p.nome, v.peso, v.quantidade, v.valor_total,
                   pe.data_hora, pe.forma_pagamento
            FROM vendas v
            JOIN pedidos pe ON v.pedido_id = pe.id
            LEFT JOIN produtos p ON v.produto_id = p.id
            WHERE {condicao_item}
            ORDER BY pe.data_hora
        ''', (data_filtro,))
        itens = cursor.fetchall()

        total_vendas = len(pedidos)
        total_valor = sum(p[2] for p in pedidos) if pedidos else 0
        total_kg = sum(i[3] for i in itens if i[3] is not None) if itens else 0

        print(f"📊 Relatório do {periodo}: {total_vendas} pedido(s), "
              f"{total_kg:.2f}kg, R${total_valor:.2f}")

        return {
            'pedidos': pedidos,
            'itens': itens,
            'total_vendas': total_vendas,
            'total_kg': total_kg,
            'total_valor': total_valor
        }
    def obter_resumo_pagamentos(self, periodo='dia'):
        """Retorna totais agrupados por forma de pagamento"""
        cursor = self.conn.cursor()

        if periodo == 'dia':
            data_filtro = datetime.now().strftime('%Y-%m-%d')
            condicao = "date(data_hora) = ?"
        elif periodo == 'mes':
            data_filtro = datetime.now().strftime('%Y-%m')
            condicao = "strftime('%Y-%m', data_hora) = ?"
        else:  # ano
            data_filtro = datetime.now().strftime('%Y')
            condicao = "strftime('%Y', data_hora) = ?"

        cursor.execute(f'''
            SELECT forma_pagamento, COUNT(*), SUM(valor_total)
            FROM pedidos
            WHERE {condicao}
            GROUP BY forma_pagamento
            ORDER BY SUM(valor_total) DESC
        ''', (data_filtro,))
        return cursor.fetchall()

    def obter_ranking_produtos(self, periodo='dia'):
        """Retorna produtos mais vendidos no período, ordenados por faturamento"""
        cursor = self.conn.cursor()

        if periodo == 'dia':
            data_filtro = datetime.now().strftime('%Y-%m-%d')
            condicao = "date(pe.data_hora) = ?"
        elif periodo == 'mes':
            data_filtro = datetime.now().strftime('%Y-%m')
            condicao = "strftime('%Y-%m', pe.data_hora) = ?"
        else:  # ano
            data_filtro = datetime.now().strftime('%Y')
            condicao = "strftime('%Y', pe.data_hora) = ?"

        cursor.execute(f'''
            SELECT p.nome,
                   COUNT(v.id) as vezes_vendido,
                   SUM(COALESCE(v.quantidade, 0)) as total_unidades,
                   SUM(COALESCE(v.peso, 0)) as total_peso,
                   SUM(v.valor_total) as total_valor
            FROM vendas v
            JOIN pedidos pe ON v.pedido_id = pe.id
            LEFT JOIN produtos p ON v.produto_id = p.id
            WHERE {condicao}
            GROUP BY v.produto_id
            ORDER BY total_valor DESC
        ''', (data_filtro,))
        return cursor.fetchall()
    # ==================== CONFIGURAÇÕES ====================

    def obter_valor_kg_padrao(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'valor_kg'")
        resultado = cursor.fetchone()
        return float(resultado[0]) if resultado else 45.00

    def salvar_valor_kg_padrao(self, valor):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('valor_kg', ?)
        ''', (str(valor),))
        self.conn.commit()

    def fechar(self):
        self.conn.close()
        print("🔌 Conexão com banco de dados fechada")