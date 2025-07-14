from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["https://www.talfy.eu"]}})

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

db = SQLAlchemy(app)

# MODELS
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'candidate' or 'company'

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profile'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    current_job = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    salary_range = db.Column(db.String(50))
    sector = db.Column(db.String(255))  # multiple values separated by comma
    tools = db.Column(db.String(255))   # multiple values separated by comma
    avatar = db.Column(db.String(255))

    # New fields
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    native_language = db.Column(db.String(100))
    other_languages = db.Column(db.String(255))  # comma-separated list
    job_title = db.Column(db.String(255))        # comma-separated list
    education_area = db.Column(db.String(255))   # comma-separated list
    birth_day = db.Column(db.Integer)
    birth_month = db.Column(db.Integer)
    birth_year = db.Column(db.Integer)

class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100))
    num_employees = db.Column(db.Integer)
    headquarters = db.Column(db.String(100))
    logo = db.Column(db.String(255))

# ROUTES
@app.route("/")
def home():
    return "✅ Talfy Backend Running!"

@app.route("/register", methods=["POST"])
def register():
    try:
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

        return jsonify({"message": "Registration successful", "user_id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/update-candidate/<int:user_id>", methods=["POST"])
def update_candidate(user_id):
    try:
        data = request.get_json()
        profile = CandidateProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            profile = CandidateProfile(user_id=user_id)

        profile.first_name = data.get("first_name")
        profile.last_name = data.get("last_name")
        profile.display_name = data.get("display_name")
        profile.current_job = data.get("current_job")
        profile.experience_years = data.get("experience_years")
        profile.salary_range = data.get("salary_range")
        profile.native_language = data.get("native_language")
        profile.birth_day = data.get("birth_day")
        profile.birth_month = data.get("birth_month")
        profile.birth_year = data.get("birth_year")
        profile.avatar = data.get("avatar")

        # Join array fields with comma
        profile.sector = ",".join(data.get("sector", []))
        profile.tools = ",".join(data.get("tools", []))
        profile.other_languages = ",".join(data.get("other_languages", []))
        profile.job_title = ",".join(data.get("job_title", []))
        profile.education_area = ",".join(data.get("education_area", []))

        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "user_type": user.user_type
        }), 200

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route("/api/counts", methods=["GET"])
def get_counts():
    try:
        candidate_count = db.session.query(CandidateProfile).count()
        company_count = db.session.query(CompanyProfile).count()

        return jsonify({
            "candidates": candidate_count,
            "companies": company_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-candidate-profile", methods=["POST"])
def save_candidate_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        display_name = data.get("display_name")
        current_job = data.get("current_job")
        experience_years = data.get("experience_years")
        salary_range = data.get("salary_range")
        sector = data.get("sector")
        tools = data.get("tools")
        avatar = data.get("avatar")

        if not user_id or not display_name:
            return jsonify({"error": "Missing user_id or display_name"}), 400

        existing_profile = CandidateProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({"error": "Profile already exists"}), 409

        profile = CandidateProfile(
            user_id=user_id,
            display_name=display_name,
            current_job=current_job,
            experience_years=experience_years,
            salary_range=salary_range,
            sector=sector,
            tools=tools,
            avatar=avatar
        )
        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Candidate profile saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-company-profile", methods=["POST"])
def save_company_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        company_name = data.get("company_name")
        sector = data.get("sector")
        num_employees = data.get("num_employees")
        headquarters = data.get("headquarters")
        logo = data.get("logo")

        if not user_id or not company_name:
            return jsonify({"error": "Missing user_id or company_name"}), 400

        existing_profile = CompanyProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({"error": "Company profile already exists"}), 409

        profile = CompanyProfile(
            user_id=user_id,
            company_name=company_name,
            sector=sector,
            num_employees=num_employees,
            headquarters=headquarters,
            logo=logo
        )
        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Company profile saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    try:
        candidates = CandidateProfile.query.all()
        result = []
        for c in candidates:
            result.append({
                "id": c.id,
                "display_name": c.display_name,
                "current_job": c.current_job,
                "experience_years": c.experience_years,
                "salary_range": c.salary_range,
                "sector": c.sector,
                "tools": c.tools,
                "avatar": c.avatar
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error loading candidates: {str(e)}"}), 500

@app.route("/api/companies", methods=["GET"])
def get_companies():
    try:
        companies = CompanyProfile.query.all()
        result = []
        for c in companies:
            result.append({
                "id": c.id,
                "company_name": c.company_name,
                "sector": c.sector,
                "num_employees": c.num_employees,
                "headquarters": c.headquarters,
                "logo": c.logo
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error loading companies: {str(e)}"}), 500

@app.route("/api/candidate/<int:user_id>", methods=["GET"])
def get_candidate(user_id):
    try:
        profile = CandidateProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"error": "Candidate not found"}), 404

        return jsonify({
            "id": profile.id,
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "current_job": profile.current_job,
            "experience_years": profile.experience_years,
            "salary_range": profile.salary_range,
            "sector": profile.sector,
            "tools": profile.tools,
            "avatar": profile.avatar
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/init-db")
def init_db():
    try:
        db.create_all()
        return "✅ Database initialized successfully", 200
    except Exception as e:
        return f"❌ Error initializing DB: {e}", 500

@app.route("/admin-data")
def admin_data():
    try:
        users = User.query.all()
        candidates = CandidateProfile.query.all()
        companies = CompanyProfile.query.all()

        users_data = []
        for u in users:
            users_data.append({
                "id": u.id,
                "email": u.email,
                "user_type": u.user_type
            })

        candidate_data = []
        for c in candidates:
            candidate_data.append({
                "id": c.id,
                "display_name": c.display_name,
                "current_job": c.current_job,
                "experience_years": c.experience_years,
                "sector": c.sector,
                "tools": c.tools
            })

        company_data = []
        for c in companies:
            company_data.append({
                "id": c.id,
                "company_name": c.company_name,
                "sector": c.sector,
                "num_employees": c.num_employees,
                "headquarters": c.headquarters
            })

        return jsonify({
            "users": users_data,
            "candidates": candidate_data,
            "companies": company_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# MAIN
if __name__ == "__main__":
    app.run(debug=True)
