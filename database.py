import sqlite3

# Database initialize pannumbothu 'password' column-ah add pannittaen
def init_db():
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    # Table structure: Added 'password' field
    cursor.execute('''CREATE TABLE IF NOT EXISTS session_stock 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       session_text TEXT, 
                       phone TEXT, 
                       password TEXT, 
                       status INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Stock add pannumbothu password-aiyum save panna logic
def add_stock(session, phone, password):
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO session_stock (session_text, phone, password, status) VALUES (?, ?, ?, 0)", 
        (session, phone, password)
    )
    conn.commit()
    conn.close()

# User-ku send panna password-aiyum fetch panrom
def get_available_account():
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    # Query-la password column-ah add pannittaen
    cursor.execute("SELECT id, session_text, phone, password FROM session_stock WHERE status = 0 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

# Account sold aanadhukapparam status update panna
def mark_as_sold(acc_id):
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE session_stock SET status = 1 WHERE id = ?", (acc_id,))
    conn.commit()
    conn.close()

# Admin check panna total stock count
def get_stock_count():
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM session_stock WHERE status = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count
