from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_company = data.get('is_company', False)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM myschema.users WHERE email = %s", (email,))
    existing = cur.fetchone()

    if existing:
        return jsonify({'success': False, 'message': 'Email already registered.'}), 409

    cur.execute("INSERT INTO myschema.users (email, password, is_company) VALUES (%s, %s, %s)", 
                (email, password, is_company))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/counts', methods=['GET'])
def get_counts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM myschema.users WHERE is_company = FALSE")
    candidates = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM myschema.users WHERE is_company = TRUE")
    companies = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({'candidates': candidates, 'companies': companies})

if __name__ == '__main__':
    app.run(debug=True)
