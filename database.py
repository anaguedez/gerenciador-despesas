import sqlite3

conexao = sqlite3.connect("despesas.db")

cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS despesas(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    categoria TEXT,
    valor REAL,
    data TEXT DEFAULT CURRENT_DATE

)
""")

colunas = [linha[1] for linha in cursor.execute("PRAGMA table_info(despesas)").fetchall()]

if "data" not in colunas:
    cursor.execute("ALTER TABLE despesas ADD COLUMN data TEXT")
    cursor.execute("UPDATE despesas SET data = date('now') WHERE data IS NULL")

conexao.commit()
conexao.close()

print("Banco criado/atualizado com sucesso!")