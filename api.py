from flask import Flask, request, render_template_string
import sqlite3
import time
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

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

# Instagram kullanıcı bilgilerini alma
def get_instagram_info(username):
    try:
        url = f'https://www.instagram.com/{username}/'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', text=lambda t: 'window._sharedData' in t)
            if script_tag:
                json_data = script_tag.string.partition('=')[-1].strip()
                profile_data = json.loads(json_data[:-1])
                user_info = profile_data['entry_data']['ProfilePage'][0]['graphql']['user']
                followers = user_info['edge_followed_by']['count']
                following = user_info['edge_follow']['count']
                posts = user_info['edge_owner_to_timeline_media']['count']
                return followers, following, posts
    except Exception as e:
        print(f'Hata oluştu: {e}')
    return None, None, None

# Kullanıcı aramasını kaydetme
def log_search(username, followers, following, posts):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    cursor.execute('INSERT INTO instagram_logs (username, followers, following, posts, timestamp) VALUES (?, ?, ?, ?, ?)', (username, followers, following, posts, timestamp))
    conn.commit()
    conn.close()

# Ana sayfa
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        followers, following, posts = get_instagram_info(username)
        if followers is not None and following is not None and posts is not None:
            log_search(username, followers, following, posts)
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, followers, following, posts, timestamp FROM instagram_logs')
    logs = cursor.fetchall()
    conn.close()

    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Logs</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1>Instagram Logs</h1>
        <form method="post">
            <label for="username">Instagram Kullanıcı Adı:</label>
            <input type="text" id="username" name="username" required>
            <button type="submit">Ara</button>
        </form>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Kullanıcı Adı</th>
                    <th>Takipçi Sayısı</th>
                    <th>Takip Edilen Sayısı</th>
                    <th>Gönderi Sayısı</th>
                    <th>Zaman Damgası</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td>{{ log[0] }}</td>
                    <td>{{ log[1] }}</td>
                    <td>{{ log[2] }}</td>
                    <td>{{ log[3] }}</td>
                    <td>{{ log[4] }}</td>
                    <td>{{ log[5] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    '''
    return render_template_string(html, logs=logs)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
