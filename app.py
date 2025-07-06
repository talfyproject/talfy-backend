from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'candidate' or 'company'

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    current_job = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    salary_range = db.Column(db.String(50))
    sector = db.Column(db.String(100))
    tools = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255))

# ROUTES
@app.route("/")
def home():
    return "Talfy Backend Running!"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user_type = data.get("user_type")

    if not all([email, password, user_type]):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(email=email, password=password, user_type=user_type)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201

@app.route("/api/counts", methods=["GET"])
def get_counts():
    candidate_count = User.query.filter_by(user_type="candidate").count()
    company_count = User.query.filter_by(user_type="company").count()
    return jsonify({
        "candidates": candidate_count,
        "companies": company_count
    })

@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    candidates = Candidate.query.all()
    result = []

    for c in candidates:
        display_name = f"{c.first_name} {c.last_name[0]}." if c.last_name else c.first_name
        result.append({
            "display_name": display_name,
            "current_job": c.current_job,
            "experience_years": c.experience_years,
            "salary_range": c.salary_range,
            "sector": c.sector,
            "tools": c.tools,
            "avatar": c.avatar_url or "/img/avatar-male.png"
        })

    return jsonify(result)

# TEMPORARY: Initialize DB (run once)
@app.route("/init-db")
def init_db():
    try:
        db.create_all()
        return "Database initialized with all tables.", 200
    except Exception as e:
        return f"Error: {e}", 500

# MAIN
if __name__ == "__main__":
    app.run(debug=True)
