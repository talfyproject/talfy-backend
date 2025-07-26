from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Inizializza database
def init_db():
    if not os.path.exists('voting.db'):
        conn = sqlite3.connect('voting.db')
        cursor = conn.cursor()
        
        # Crea tabelle
        cursor.execute('''
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            party TEXT,
            description TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY,
            candidate_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
        ''')
        
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect('voting.db')
    conn.row_factory = sqlite3.Row
    return conn

# Template HTML per register
REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Registra Candidato</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 50px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 500px; 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; text-align: center; }
        input, textarea { 
            width: 100%; 
            margin: 10px 0; 
            padding: 12px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            box-sizing: border-box;
        }
        button { 
            background: #007bff; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            width: 100%;
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
        .message { 
            color: green; 
            text-align: center; 
            margin-top: 20px; 
            font-weight: bold;
        }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗳️ Registra Nuovo Candidato</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="Nome completo candidato" required>
            <input type="text" name="party" placeholder="Partito politico" required>
            <textarea name="description" placeholder="Descrizione del candidato" rows="4"></textarea>
            <button type="submit">Registra Candidato</button>
        </form>
        
        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/api/candidates" style="color: #007bff;">Vedi tutti i candidati</a>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    return '''
    <html>
    <head><title>Sistema Votazioni</title></head>
    <body style="font-family: Arial; text-align: center; margin: 100px;">
        <h1>🗳️ Sistema di Votazioni</h1>
        <p><a href="/register">Registra Candidato</a></p>
        <p><a href="/api/candidates">Vedi Candidati</a></p>
    </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        description = request.form.get('description')
        
        if name and party:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO candidates (name, party, description) VALUES (?, ?, ?)',
                    (name, party, description)
                )
                conn.commit()
                conn.close()
                message = f"✅ Candidato '{name}' registrato con successo!"
            except Exception as e:
                message = f"❌ Errore: {str(e)}"
        else:
            message = "❌ Nome e partito sono obbligatori!"
    
    return render_template_string(REGISTER_TEMPLATE, message=message)

@app.route('/api/candidates')
def get_candidates():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidates')
        candidates = cursor.fetchall()
        conn.close()
        
        candidates_list = []
        for candidate in candidates:
            candidates_list.append({
                'id': candidate['id'],
                'name': candidate['name'],
                'party': candidate['party'],
                'description': candidate['description']
            })
        
        return jsonify({
            'candidates': candidates_list,
            'total': len(candidates_list),
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'candidates': [],
            'total': 0,
            'message': f'Errore database: {str(e)}'
        })

@app.route('/api/votes')
def get_votes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM votes')
        votes = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'votes': len(votes),
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'votes': 0,
            'message': f'Errore: {str(e)}'
        })

@app.route('/api/results')
def get_results():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.name, c.party, COUNT(v.id) as votes
            FROM candidates c
            LEFT JOIN votes v ON c.id = v.candidate_id
            GROUP BY c.id, c.name, c.party
            ORDER BY votes DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        
        results_list = []
        for result in results:
            results_list.append({
                'name': result[0],
                'party': result[1],
                'votes': result[2]
            })
        
        return jsonify({
            'results': results_list,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'results': [],
            'message': f'Errore: {str(e)}'
        })

if __name__ == '__main__':
    init_db()  # Crea database se non esiste
    app.run(debug=True)
