import sqlite3
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Conectar ao banco
conn = sqlite3.connect('sorveteria.db')
cursor = conn.cursor()

print("="*60)
print("🔍 VERIFICANDO BANCO DE DADOS")
print("="*60)

# Verificar se a tabela existe
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
    if cursor.fetchone():
        print("✅ Tabela 'usuarios' existe")
    else:
        print("❌ Tabela 'usuarios' NÃO existe!")
except Exception as e:
    print(f"❌ Erro ao verificar tabela: {e}")

# Listar todos os usuários
print("\n📋 USUÁRIOS NO BANCO:")
print("-"*60)
try:
    cursor.execute("SELECT id, nome, usuario, perfil, ativo FROM usuarios")
    usuarios = cursor.fetchall()
    
    if usuarios:
        for user in usuarios:
            print(f"ID: {user[0]} | Nome: {user[1]} | Usuario: {user[2]} | Perfil: {user[3]} | Ativo: {user[4]}")
    else:
        print("⚠️ Nenhum usuário encontrado!")
except Exception as e:
    print(f"❌ Erro ao listar usuários: {e}")

# Testar login do admin
print("\n🔐 TESTANDO LOGIN DO ADMIN:")
print("-"*60)
usuario = "admin"
senha = "admin123"
senha_hash = hash_senha(senha)

print(f"Usuário: {usuario}")
print(f"Senha: {senha}")
print(f"Senha Hash: {senha_hash}")

try:
    cursor.execute('''
        SELECT id, nome, perfil FROM usuarios 
        WHERE usuario = ? AND senha = ? AND ativo = 1
    ''', (usuario, senha_hash))
    
    resultado = cursor.fetchone()
    
    if resultado:
        print(f"\n✅ LOGIN FUNCIONOU!")
        print(f"   ID: {resultado[0]}")
        print(f"   Nome: {resultado[1]}")
        print(f"   Perfil: {resultado[2]}")
    else:
        print("\n❌ LOGIN FALHOU!")
        
        # Verificar se existe mas com senha errada
        cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
        senha_db = cursor.fetchone()
        if senha_db:
            print(f"   Senha no banco: {senha_db[0]}")
            print(f"   Senha tentada:  {senha_hash}")
            if senha_db[0] == senha_hash:
                print("   ✅ Senhas coincidem")
            else:
                print("   ❌ Senhas NÃO coincidem")
        else:
            print("   ⚠️ Usuário não encontrado!")
            
except Exception as e:
    print(f"❌ Erro ao testar login: {e}")

conn.close()
print("\n" + "="*60)