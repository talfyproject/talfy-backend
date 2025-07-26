from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime
import os
import hashlib
import re

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
        
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect('voting.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    if len(password) < 8:
        return False, "Password deve essere di almeno 8 caratteri"
    if not re.search(r'[A-Z]', password):
        return False, "Password deve contenere almeno una maiuscola"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password deve contenere almeno un simbolo"
    return True, "Password valida"

# Template HTML per registrazione utenti
USER_REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrazione - Sistema Votazioni</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 450px;
            text-align: center;
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2.2em;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
            font-size: 14px;
        }

        input[type="text"],
        input[type="email"],
        input[type="password"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }

        input[type="text"]:focus,
        input[type="email"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .password-requirements {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            font-size: 13px;
            color: #666;
        }

        .requirement {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }

        .requirement.valid {
            color: #28a745;
        }

        .requirement.invalid {
            color: #dc3545;
        }

        .requirement::before {
            content: "✗";
            margin-right: 8px;
            font-weight: bold;
        }

        .requirement.valid::before {
            content: "✓";
            color: #28a745;
        }

        .requirement.invalid::before {
            color: #dc3545;
        }

        .password-match {
            margin-top: 10px;
            font-size: 13px;
            font-weight: 500;
        }

        .password-match.match {
            color: #28a745;
        }

        .password-match.no-match {
            color: #dc3545;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .back-link:hover {
            color: #764ba2;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }

        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }

        @media (max-width: 480px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗳️ Registrazione</h1>
        
        {% if error %}
            <div class="error-message">{{ error }}</div>
        {% endif %}
        
        {% if success %}
            <div class="success-message">{{ success }}</div>
        {% endif %}
        
        <form method="POST" id="registrationForm">
            <div class="form-group">
                <label for="username">Nome Utente</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
                
                <div class="password-requirements">
                    <div class="requirement" id="length">Almeno 8 caratteri</div>
                    <div class="requirement" id="uppercase">Almeno una lettera maiuscola</div>
                    <div class="requirement" id="symbol">Almeno un simbolo (!@#$%^&*)</div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="confirmPassword">Conferma Password</label>
                <input type="password" id="confirmPassword" name="confirmPassword" required>
                <div class="password-match" id="passwordMatch"></div>
            </div>
            
            <button type="submit" class="btn" id="submitBtn" disabled>Registrati</button>
        </form>
        
        <a href="/" class="back-link">← Torna alla Homepage</a>
    </div>

    <script>
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        const submitBtn = document.getElementById('submitBtn');

        const requirements = {
            length: { element: document.getElementById('length'), regex: /.{8,}/ },
            uppercase: { element: document.getElementById('uppercase'), regex: /[A-Z]/ },
            symbol: { element: document.getElementById('symbol'), regex: /[!@#$%^&*(),.?":{}|<>]/ }
        };

        function validatePassword() {
            const password = passwordInput.value;
            let allValid = true;

            Object.keys(requirements).forEach(key => {
                const req = requirements[key];
                const isValid = req.regex.test(password);
                
                req.element.classList.toggle('valid', isValid);
                req.element.classList.toggle('invalid', !isValid);
                
                if (!isValid) allValid = false;
            });

            return allValid;
        }

        function validatePasswordMatch() {
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            const matchElement = document.getElementById('passwordMatch');

            if (confirmPassword === '') {
                matchElement.textContent = '';
                return false;
            }

            if (password === confirmPassword) {
                matchElement.textContent = '✓ Le password corrispondono';
                matchElement.className = 'password-match match';
                return true;
            } else {
                matchElement.textContent = '✗ Le password non corrispondono';
                matchElement.className = 'password-match no-match';
                return false;
            }
        }

        function updateSubmitButton() {
            const passwordValid = validatePassword();
            const passwordsMatch = validatePasswordMatch();
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();

            const canSubmit = passwordValid && passwordsMatch && username && email;
            submitBtn.disabled = !canSubmit;
        }

        passwordInput.addEventListener('input', updateSubmitButton);
        confirmPasswordInput.addEventListener('input', updateSubmitButton);
        document.getElementById('username').addEventListener('input', updateSubmitButton);
        document.getElementById('email').addEventListener('input', updateSubmitButton);

        updateSubmitButton();
    </script>
</body>
</html>
'''

# Template HTML per register candidati
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
        <p><a href="/user-register">Registrazione Utenti</a></p>
        <p><a href="/register">Registra Candidato</a></p>
        <p><a href="/api/candidates">Vedi Candidati</a></p>
        <p><a href="/api/users">Vedi Utenti</a></p>
    </body>
    </html>
    '''

@app.route('/user-register', methods=['GET', 'POST'])
def user_register():
    error = None
    success = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')
        
        # Validazioni
        if not username or not email or not password:
            error = "Tutti i campi sono obbligatori"
        elif password != confirm_password:
            error = "Le password non corrispondono"
        else:
            is_valid, message = validate_password(password)
            if not is_valid:
                error = message
            else:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Controlla se username o email esistono già
                    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
                    if cursor.fetchone():
                        error = "Username o email già esistenti"
                    else:
                        # Inserisci nuovo utente
                        password_hash = hash_password(password)
                        cursor.execute(
                            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                            (username, email, password_hash)
                        )
                        conn.commit()
                        success = f"✅ Utente '{username}' registrato con successo!"
                    
                    conn.close()
                except Exception as e:
                    error = f"Errore database: {str(e)}"
    
    return render_template_string(USER_REGISTER_TEMPLATE, error=error, success=success)

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

@app.route('/api/users')
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            })
        
        return jsonify({
            'users': users_list,
            'total': len(users_list),
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'users': [],
            'total': 0,
            'message': f'Errore database: {str(e)}'
        })

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

@app.route('/reset-db')
def reset_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM votes')
        cursor.execute('DELETE FROM candidates')
        cursor.execute('DELETE FROM users')
        conn.commit()
        conn.close()
        return "✅ Database azzerato completamente!"
    except Exception as e:
        return f"❌ Errore: {str(e)}"

if __name__ == '__main__':
    init_db()  # Crea database se non esiste
    app.run(debug=True)
    init_db()  # Crea database se non esiste
    app.run(debug=True)
