import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vip_stock.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas e popula com dados de teste realistas do VIP."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de lojas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lojas (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT,
            horario TEXT
        )
    """)

    # Tabela de produtos + stock
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT,
            unidade TEXT,
            preco REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            loja_id INTEGER DEFAULT 1,
            promocao TEXT,
            FOREIGN KEY (loja_id) REFERENCES lojas(id)
        )
    """)

    # Limpar dados antigos para recriar limpo
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM lojas")

    # Lojas VIP (dados reais aproximados)
    lojas = [
        (1, "VIP Maputo", "Maputo", "Maputo Centro", "+258 84 123 4533", "08h-21h"),
        (2, "VIP Nampula", "Nampula", "Av. Eduardo Mondlane, Edifício Millennium Center", "+258 84 575 5555", "08h-21h"),
        (3, "VIP Beira", "Beira", "Av. General Vieira Da Rocha", "+258 84 590 9999", "08h-21h"),
        (4, "VIP Zimpeto", "Maputo", "Av. de Moçambique, Rotunda Missão Roque", "+258 84 631 6058", "08h-21h"),
        (5, "VIP Pemba", "Pemba", "Av. 25 de Setembro", "+258 84 279 9999", "08h-21h"),
        (6, "VIP Chimoio", "Chimoio", "Rua dos Operários N12", "+258 84 152 2222", "08h-21h"),
        (7, "VIP Tete", "Tete", "Av. Julius Nyerere", "+258 84 946 1192", "08h-21h"),
        (8, "VIP Nacala", "Nacala", "Estrada Principal N12, Nacala City Center", "+258 84 888 8863", "08h-21h"),
    ]
    cursor.executemany(
        "INSERT INTO lojas (id, nome, cidade, endereco, telefone, horario) VALUES (?, ?, ?, ?, ?, ?)",
        lojas
    )

    # Produtos de teste (baseados em produtos reais do VIP + staples moçambicanos)
    produtos = [
        # Mercearia
        ("Arroz 5kg", "Mercearia", "saco", 320.0, 45, 1, "15% off até domingo"),
        ("Arroz 1kg", "Mercearia", "kg", 70.0, 120, 1, None),
        ("Óleo de Cozinha 1L", "Mercearia", "litro", 95.0, 80, 1, None),
        ("Açúcar 1kg", "Mercearia", "kg", 55.0, 90, 1, None),
        ("Farinha de Trigo 1kg", "Mercearia", "kg", 48.0, 60, 1, None),
        ("Farinha Integral Nacional 1kg", "Mercearia", "kg", 145.0, 35, 1, "POUPA 130MT"),
        ("Leite UHT Gordo 1L", "Mercearia", "litro", 110.0, 70, 1, "POUPA 35MT"),
        ("Leite Nido 400g", "Mercearia", "lata", 280.0, 25, 1, None),
        ("Ovos (1.5 dúzia)", "Mercearia", "caixa", 215.0, 40, 1, "POUPA 60MT"),
        ("Pão Forma Integral 700g", "Mercearia", "unidade", 105.0, 30, 1, None),
        ("Água Mineral 5L", "Mercearia", "garrafa", 80.0, 100, 1, "POUPA 5MT"),
        ("Água Mineral 500ml", "Mercearia", "garrafa", 24.0, 200, 1, None),

        # Bebé
        ("Huggies Toalhitas Pure 56", "Bebé", "pacote", 120.0, 45, 1, None),
        ("Pampers Baby Wipes 64", "Bebé", "pacote", 220.0, 30, 1, "POUPA 10MT"),
        ("Fraldas Pampers M 40un", "Bebé", "pacote", 450.0, 20, 1, None),

        # Limpeza
        ("Detergente Louça 500ml", "Limpeza", "unidade", 65.0, 55, 1, None),
        ("Água Sanitária 1L", "Limpeza", "unidade", 40.0, 70, 1, None),
        ("Inseticida Eléctrico", "Limpeza", "unidade", 320.0, 15, 1, "POUPA 5MT"),

        # Snacks / Outros
        ("Cornetto Morango 6x90ml", "Gelados", "caixa", 510.0, 18, 1, "POUPA 85MT"),
        ("Nescafé Dolce Gusto 8s", "Café", "caixa", 650.0, 12, 1, "POUPA 100MT"),
        ("Biscoitos Chocolate 125g", "Snacks", "pacote", 45.0, 80, 1, "POUPA 5MT"),
    ]

    cursor.executemany(
        """INSERT INTO produtos (nome, categoria, unidade, preco, stock, loja_id, promocao)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        produtos
    )

    conn.commit()
    conn.close()
    print("✅ Base de dados criada e populada com sucesso!")


def buscar_produtos(termo: str, limite: int = 5):
    """Busca produtos por nome (fuzzy simples)."""
    conn = get_connection()
    cursor = conn.cursor()
    termo = f"%{termo.lower()}%"
    cursor.execute("""
        SELECT p.nome, p.categoria, p.unidade, p.preco, p.stock, p.promocao, l.nome as loja
        FROM produtos p
        JOIN lojas l ON p.loja_id = l.id
        WHERE LOWER(p.nome) LIKE ?
        ORDER BY p.stock DESC
        LIMIT ?
    """, (termo, limite))
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados


def listar_lojas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, cidade, endereco, telefone, horario FROM lojas ORDER BY cidade")
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados


def get_produto_exato(nome: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nome, p.preco, p.stock, p.unidade, p.promocao
        FROM produtos p
        WHERE LOWER(p.nome) = LOWER(?)
        LIMIT 1
    """, (nome,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    init_db()
    print("\nExemplos de busca:")
    print(buscar_produtos("arroz"))
    print(buscar_produtos("leite"))
    print("\nLojas:")
    for loja in listar_lojas():
        print(f"- {loja['nome']} ({loja['cidade']})")