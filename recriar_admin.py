import sqlite3
from datetime import datetime
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Conectar ao banco
conn = sqlite3.connect('sorveteria.db')
cursor = conn.cursor()

print("🔧 Recriando usuário admin...")

# Deletar admin antigo (se existir)
try:
    cursor.execute("DELETE FROM usuarios WHERE usuario = 'admin'")
    print("🗑️ Admin antigo removido")
except:
    pass

# Criar novo admin
try:
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
    conn.commit()
    print("✅ Novo admin criado com sucesso!")
    print("📝 Usuário: admin")
    print("📝 Senha: admin123")
except Exception as e:
    print(f"❌ Erro ao criar admin: {e}")

conn.close()