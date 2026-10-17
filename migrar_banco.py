import sqlite3

def migrar_banco():
    """Adiciona colunas de perfil aos usuários existentes"""
    conn = sqlite3.connect('sorveteria.db')
    cursor = conn.cursor()
    
    try:
        # Adicionar coluna perfil (se não existir)
        cursor.execute('''
            ALTER TABLE usuarios 
            ADD COLUMN perfil TEXT DEFAULT 'funcionario'
        ''')
        print("✅ Coluna 'perfil' adicionada")
    except sqlite3.OperationalError:
        print("⚠️ Coluna 'perfil' já existe")
    
    try:
        # Adicionar coluna ativo
        cursor.execute('''
            ALTER TABLE usuarios 
            ADD COLUMN ativo INTEGER DEFAULT 1
        ''')
        print("✅ Coluna 'ativo' adicionada")
    except sqlite3.OperationalError:
        print("⚠️ Coluna 'ativo' já existe")
    
    # Tornar primeiro usuário admin
    cursor.execute('''
        UPDATE usuarios 
        SET perfil = 'administrador' 
        WHERE id = (SELECT MIN(id) FROM usuarios)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Migração concluída!")

if __name__ == "__main__":
    migrar_banco()