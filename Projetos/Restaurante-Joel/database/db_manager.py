# database/db_manager.py
import sqlite3
import os

# Define o caminho do arquivo do banco de dados na mesma pasta do projeto
DB_FOLDER = "database"
DB_NAME = "estoque_restaurante.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def init_db():
    """Cria o arquivo do banco de dados e a estrutura das tabelas se não existirem."""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # --- Estrutura das Tabelas ---
    
    # Tabela de Usuários (para o Login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    
    # Tabela de Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            unidade TEXT,
            estoque_minimo REAL DEFAULT 0
        )
    """)

    # Tabela de Movimentações (Lote, Validade, Entradas/Saídas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, -- 'ENTRADA', 'SAIDA_USO', 'SAIDA_PERDA'
            quantidade REAL NOT NULL,
            lote TEXT,
            data_fabricacao DATE,
            data_validade DATE,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    # Cria um usuário padrão se não existir (admin/admin)
    cursor.execute("SELECT count(*) FROM usuarios WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password) VALUES ('admin', 'admin')")
        print("Usuário padrão 'admin' criado com sucesso.")

    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado em: {DB_PATH}")

def connect_db():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DB_PATH)

if __name__ == "__main__":
    init_db() # Rode este script uma vez para criar o .db
