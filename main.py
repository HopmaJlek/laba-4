from flask import Flask, request, jsonify 
import psycopg2 
import os 
from urllib.parse import urlparse 
 
 
app = Flask(__name__) 
 
DATABASE_URL = os.environ.get("DB_URL") 
 
if DATABASE_URL: 
    url = urlparse(DATABASE_URL) 
    conn = psycopg2.connect( 
        database=url.path[1:], 
        user=url.username, 
        password=url.password, 
        host=url.hostname, 
        port=url.port 
    ) 
else: 
    conn = None 
 
if conn: 
    with conn.cursor() as cur: 
        cur.execute(""" 
            create table if not exists messages( 
                id serial primary key, 
                content text not null, 
                created_at timestamp default now() 
            ) 
        """) 
        conn.commit() 
 
 
@app.route("/save", methods=["POST"]) 
def save_message(): 
    if not conn: 
        return jsonify({"error": "Database not connected"}), 500 
 
    data = request.get_json()  
    message = data.get("message", "") 
    if data else "" 
 
    with conn.cursor() as cur: 
        cur.execute(""" 
            insert into messages(content) values (%s) 
        """, (message,)) 
        conn.commit() 
 
    return jsonify({ 
        "status": "saved", 
        "message": message 
    }) 
 
 
@app.route("/messages", methods=["GET"]) 
def get_messages(): 
    if not conn: 
        return jsonify({"error": "Database not connected"}), 500 
 
    with conn.cursor() as cur: 
        cur.execute(""" 
            select 
                id, 
                content, 
                created_at 
            from messages 
            order by id desc limit 10 
        """) 
        db_response_rows = cur.fetchall() 
 
    messages = [{ 
        "id": row[0], 
        "text": row[1], 
        "time": row[2].isoformat() 
    } for row in db_response_rows] 
 
    return jsonify(messages) 
 
 
@app.route("/", methods=["GET"]) 
def hello(): 
    return "Hello, Serverless!        \n", 200, {"Content-Type": "text/plain"} 

@app.route("/echo", methods=["POST"]) 
def echo(): 
data = request.get_json() 
return jsonify({ 
"status": "received", 
"you_data": data, 
"length": len(str(data)) if data else 0 
}) 
if __name__ == "__main__": 
app.run(host="0.0.0.0", port=5000) 
