from database import Database

db = Database()
db.criar_usuario(
    nome="Marbo Cristian",
    usuario="marbosantos",
    senha="Crispa74",
    perfil="desenvolvedor",
    pergunta="Qual meu cargo?",
    resposta="desenvolvedor"
)
print("✅ Usuário desenvolvedor criado: dev/marbocristian")