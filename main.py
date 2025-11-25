from flask import Flask, request, jsonify
import psycopg
from psycopg import sql
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Подключаемся к БД один раз при старте приложения
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # psycopg3 сам умеет парсить DATABASE_URL!
    conn = psycopg.connect(DATABASE_URL, sslmode="require")
    
    # Создаём таблицу при старте (один раз)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("Подключились к БД и создали таблицу")
else:
    conn = None
    print("Переменная DATABASE_URL не найдена — работаем без БД")


@app.route('/save', methods=['POST'])
def save_message():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500
    
    data = request.get_json()
    message = data.get('message', '') if data else ''
    
    with conn.cursor() as cur:
        cur.execute("INSERT INTO messages (content) VALUES (%s) RETURNING id", (message,))
        new_id = cur.fetchone()[0]
        conn.commit()
    
    return jsonify({"status": "saved", "id": new_id, "message": message})


@app.route('/messages')
def get_messages():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, content, created_at 
            FROM messages 
            ORDER BY id DESC 
            LIMIT 10
        """)
        rows = cur.fetchall()
    
    messages = [
        {"id": row[0], "text": row[1], "time": row[2].isoformat()}
        for row in rows
    ]
    return jsonify(messages)


@app.route('/')
def hello():
    return "Server is running! POST /save и GET /messages работают!"


# Render требует именно так (без if __name__ == '__main__')
# app.run() не нужен и даже вреден
