from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
CORS(app)

# Configurazione DB
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modello utente
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'candidate' o 'company'

# Route: Contatori per homepage
@app.route("/api/counts")
def get_counts():
    candidates = User.query.filter_by(user_type="candidate").count()
    companies = User.query.filter_by(user_type="company").count()
    return jsonify({"candidates": candidates, "companies": companies})

# Route: Registrazione
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user_type = data.get("user_type")

    if not email or not password or user_type not in ["candidate", "company"]:
        return jsonify({"error": "Missing or invalid fields."}), 400

    # Check esistenza utente
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered."}), 409

    hashed_pw = generate_password_hash(password)

    new_user = User(email=email, password=hashed_pw, user_type=user_type)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201

# Esegui server in locale
if __name__ == "__main__":
    app.run(debug=True)
