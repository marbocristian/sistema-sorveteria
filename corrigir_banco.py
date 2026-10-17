import sqlite3
from datetime import datetime
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def corrigir_banco():
    """Corrige o banco de dados adicionando as colunas faltantes"""
    conn = sqlite3.connect('sorveteria.db')
    cursor = conn.cursor()
    
    print("🔧 Verificando e corrigindo banco de dados...")
    
    # Verificar se a coluna perfil existe
    try:
        cursor.execute("SELECT perfil FROM usuarios LIMIT 1")
        print("✅ Coluna 'perfil' já existe")
    except sqlite3.OperationalError:
        print("⚠️ Coluna 'perfil' não existe. Adicionando...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN perfil TEXT DEFAULT 'funcionario'")
        print("✅ Coluna 'perfil' adicionada")
    
    # Verificar se a coluna ativo existe
    try:
        cursor.execute("SELECT ativo FROM usuarios LIMIT 1")
        print("✅ Coluna 'ativo' já existe")
    except sqlite3.OperationalError:
        print("⚠️ Coluna 'ativo' não existe. Adicionando...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN ativo INTEGER DEFAULT 1")
        print("✅ Coluna 'ativo' adicionada")
    
    # Verificar se existe admin
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'administrador'")
    if cursor.fetchone()[0] == 0:
        print("⚠️ Nenhum administrador encontrado. Criando...")
        
        cursor.execute('''
            INSERT INTO usuarios (nome, usuario, senha, perfil, 
                                pergunta_seguranca, resposta_seguranca, 
                                data_criacao, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            "Administrador",
            "admin",
            hash_senha("admin123"),
            "administrador",
            "Qual o nome do sistema?",
            hash_senha("sorveteria"),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        print("✅ Usuário admin criado (admin/admin123)")
    else:
        print("✅ Administrador já existe")
    
    # Atualizar usuários sem perfil
    cursor.execute("UPDATE usuarios SET perfil = 'funcionario' WHERE perfil IS NULL OR perfil = ''")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados corrigido com sucesso!")
    print("📝 Você pode fazer login com: admin / admin123")

if __name__ == "__main__":
    corrigir_banco()