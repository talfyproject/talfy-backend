from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Connessione al database (Render Postgres)
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# ✅ CREA LA TABELLA USERS SE NON ESISTE
def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_company BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabella 'users' creata o già esistente.")

# REGISTRA UN UTENTE
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_company = data.get('is_company', False)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing = cur.fetchone()

    if existing:
        return jsonify({'success': False, 'message': 'Email already registered.'}), 409

    cur.execute("INSERT INTO users (email, password, is_company) VALUES (%s, %s, %s)", 
                (email, password, is_company))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True})

# OTTIENI IL NUMERO DI CANDIDATI E AZIENDE
@app.route('/api/counts', methods=['GET'])
def get_counts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE is_company = FALSE")
    candidates = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_company = TRUE")
    companies = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({'candidates': candidates, 'companies': companies})

# AVVIA L'APP
if __name__ == '__main__':
    create_users_table()  # ✅ CREA LA TABELLA ALL'AVVIO
    app.run(debug=True)
