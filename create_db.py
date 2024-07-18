import sqlite3

# Veritabanı ve tablo oluşturma
def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instagram_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        followers INTEGER,
        following INTEGER,
        posts INTEGER,
        timestamp TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# init_db() fonksiyonunu uygulamanın başında çağırın
if __name__ == '__main__':
    init_db()
