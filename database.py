import sqlite3
from datetime import datetime
import hashlib

class Database:
    """Classe para gerenciar o banco de dados da sorveteria"""
    
    def __init__(self):
        """Inicializa a conexão com o banco de dados"""
        self.conn = sqlite3.connect('sorveteria.db')
        self.criar_tabelas()
    
    def criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados"""
        cursor = self.conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                pergunta_seguranca TEXT,
                resposta_seguranca TEXT,
                data_criacao TEXT
            )
        ''')
        
        # Tabela de vendas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peso REAL NOT NULL,
                valor_kg REAL NOT NULL,
                valor_total REAL NOT NULL,
                data_hora TEXT NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabela de configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
        print("✅ Banco de dados inicializado com sucesso!")
    
    def hash_senha(self, senha):
        """Criptografa a senha usando SHA-256"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def criar_usuario(self, nome, usuario, senha, pergunta, resposta):
        """
        Cria um novo usuário no sistema
        
        Args:
            nome: Nome completo do usuário
            usuario: Nome de usuário (login)
            senha: Senha do usuário
            pergunta: Pergunta de segurança
            resposta: Resposta da pergunta de segurança
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios (nome, usuario, senha, pergunta_seguranca, 
                                    resposta_seguranca, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nome, usuario, self.hash_senha(senha), pergunta, 
                  self.hash_senha(resposta.lower().strip()), 
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
            print(f"✅ Usuário '{usuario}' criado com sucesso!")
            return True, "Usuário criado com sucesso!"
        except sqlite3.IntegrityError:
            print(f"❌ Erro: Usuário '{usuario}' já existe!")
            return False, "Nome de usuário já existe!"
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return False, f"Erro ao criar usuário: {e}"
    
    def verificar_login(self, usuario, senha):
        """
        Verifica se o login é válido
        
        Returns:
            Tupla (id, nome) se válido, None se inválido
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, nome FROM usuarios WHERE usuario = ? AND senha = ?',
                      (usuario, self.hash_senha(senha)))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"✅ Login bem-sucedido: {resultado[1]}")
        else:
            print("❌ Login falhou: usuário ou senha incorretos")
            
        return resultado
    
    def recuperar_senha(self, usuario, resposta):
        """Verifica se a resposta de segurança está correta"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE usuario = ? AND resposta_seguranca = ?',
                      (usuario, self.hash_senha(resposta.lower().strip())))
        return cursor.fetchone() is not None
    
    def alterar_senha(self, usuario, nova_senha):
        """Altera a senha de um usuário"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE usuarios SET senha = ? WHERE usuario = ?',
                      (self.hash_senha(nova_senha), usuario))
        self.conn.commit()
        print(f"✅ Senha alterada para o usuário '{usuario}'")
    
    def obter_pergunta_seguranca(self, usuario):
        """Retorna a pergunta de segurança de um usuário"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT pergunta_seguranca FROM usuarios WHERE usuario = ?', (usuario,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    
    def registrar_venda(self, peso, valor_kg, usuario_id):
        """
        Registra uma nova venda
        
        Returns:
            Valor total da venda
        """
        cursor = self.conn.cursor()
        valor_total = peso * valor_kg
        cursor.execute('''
            INSERT INTO vendas (peso, valor_kg, valor_total, data_hora, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (peso, valor_kg, valor_total, 
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'), usuario_id))
        self.conn.commit()
        print(f"✅ Venda registrada: {peso}kg x R${valor_kg} = R${valor_total:.2f}")
        return valor_total
    
    def obter_relatorio(self, periodo='dia'):
        """
        Gera relatório de vendas por período
        
        Args:
            periodo: 'dia', 'mes' ou 'ano'
            
        Returns:
            Dicionário com dados do relatório
        """
        cursor = self.conn.cursor()
        
        if periodo == 'dia':
            data_filtro = datetime.now().strftime('%Y-%m-%d')
            query = "SELECT * FROM vendas WHERE date(data_hora) = ?"
        elif periodo == 'mes':
            data_filtro = datetime.now().strftime('%Y-%m')
            query = "SELECT * FROM vendas WHERE strftime('%Y-%m', data_hora) = ?"
        else:  # ano
            data_filtro = datetime.now().strftime('%Y')
            query = "SELECT * FROM vendas WHERE strftime('%Y', data_hora) = ?"
        
        cursor.execute(query, (data_filtro,))
        vendas = cursor.fetchall()
        
        total_vendas = len(vendas)
        total_kg = sum(v[1] for v in vendas) if vendas else 0
        total_valor = sum(v[3] for v in vendas) if vendas else 0
        
        print(f"📊 Relatório do {periodo}: {total_vendas} vendas, {total_kg:.2f}kg, R${total_valor:.2f}")
        
        return {
            'vendas': vendas,
            'total_vendas': total_vendas,
            'total_kg': total_kg,
            'total_valor': total_valor
        }
    
    def obter_valor_kg_padrao(self):
        """Retorna o valor por kg configurado"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'valor_kg'")
        resultado = cursor.fetchone()
        return float(resultado[0]) if resultado else 45.00
    
    def salvar_valor_kg_padrao(self, valor):
        """Salva o valor por kg padrão"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('valor_kg', ?)
        ''', (str(valor),))
        self.conn.commit()
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        self.conn.close()
        print("🔌 Conexão com banco de dados fechada")