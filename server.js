import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import pkg from "pg";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import multer from "multer";
import path from "path";
import fs from "fs";

dotenv.config();
const { Pool } = pkg;

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors({ origin: "*", methods: ["GET", "POST"], allowedHeaders: ["Content-Type", "Authorization"] }));
app.use(express.json());
app.use(express.static("public"));

// ✅ Upload folder
const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}
app.use("/uploads", express.static(uploadDir));

// ✅ Multer config
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname)
});
const upload = multer({ storage });

// ✅ PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

pool.connect()
  .then(() => console.log("✅ Connected to PostgreSQL"))
  .catch((err) => console.error("❌ DB connection error:", err));

const JWT_SECRET = process.env.JWT_SECRET || "supersecretkey";

// ✅ JWT Middleware
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ success: false, error: "Unauthorized" });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ success: false, error: "Invalid token" });
  }
};

// ✅ ROUTES

// Test route
app.get("/", (req, res) => res.json({ message: "✅ Talfy Backend is running" }));

// REGISTER
app.post("/api/register", async (req, res) => {
  const { email, password, user_type } = req.body;
  if (!email || !password || !user_type) {
    return res.status(400).json({ success: false, error: "Missing required fields" });
  }

  try {
    const existingUser = await pool.query("SELECT id FROM users WHERE email = $1", [email]);
    if (existingUser.rows.length > 0) {
      return res.status(400).json({ success: false, error: "Email already registered" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await pool.query(
      "INSERT INTO users (email, password, user_type) VALUES ($1, $2, $3) RETURNING id",
      [email, hashedPassword, user_type]
    );

    res.json({ success: true, userId: result.rows[0].id, userType: user_type });
  } catch (err) {
    console.error("❌ Registration error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// LOGIN
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ success: false, error: "Email and password required" });
  }

  try {
    const userResult = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userResult.rows.length === 0) return res.status(400).json({ success: false, error: "Invalid credentials" });

    const user = userResult.rows[0];
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) return res.status(400).json({ success: false, error: "Invalid credentials" });

    const token = jwt.sign({ id: user.id, email: user.email, user_type: user.user_type }, JWT_SECRET, { expiresIn: "2h" });

    res.json({ success: true, token, userId: user.id, userType: user.user_type });
  } catch (err) {
    console.error("❌ Login error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ✅ COMPLETE PROFILE (with upload)
app.post("/api/candidate-profile", authMiddleware, upload.fields([
  { name: "photo", maxCount: 1 },
  { name: "cv", maxCount: 1 }
]), async (req, res) => {
  try {
    const userId = req.user.id;

    const profileData = {
      firstName: req.body.firstName,
      lastName: req.body.lastName/*,
      phone: req.body.phone,
      location: req.body.location,
      birthDate: `${req.body.birthDay}-${req.body.birthMonth}-${req.body.birthYear}`,
      jobRole: req.body.jobRole,
      avatar: req.body.avatar || null,
      experience: req.body.experience,
      education: req.body.education,
      salaryRange: { min: req.body.salaryMin, max: req.body.salaryMax },
      languages: {
        native: req.body.nativeLanguage,
        second: { lang: req.body.secondLanguage, level: req.body.secondLanguageLevel },
        third: { lang: req.body.thirdLanguage, level: req.body.thirdLanguageLevel }
      },
      availability: req.body.availability,
      remoteWork: req.body.remoteWork,
      relocation: req.body.relocation,
      summary: req.body.summary,
      sectors: JSON.parse(req.body.sectors || "[]"),
      software: JSON.parse(req.body.software || "[]"),
      photo: req.files["photo"] ? `/uploads/${req.files["photo"][0].filename}` : null,
      cv: req.files["cv"] ? `/uploads/${req.files["cv"][0].filename}` : null*/
    };

    await pool.query("UPDATE users SET profile = $1 WHERE id = $2", [JSON.stringify(profileData), userId]);

    res.json({ success: true, message: "Profile saved", profile: profileData });
  } catch (err) {
    console.error("❌ Profile error:", err);
    res.status(500).json({ success: false, error: "Error saving profile" });
  }
});

// ✅ GET USER PROFILE
app.get("/api/user/:id", async (req, res) => {
  try {
    const result = await pool.query("SELECT id, email, user_type, profile FROM users WHERE id = $1", [req.params.id]);
    if (result.rows.length === 0) return res.status(404).json({ success: false, error: "User not found" });
    res.json({ success: true, user: result.rows[0] });
  } catch (err) {
    console.error("❌ Get user error:", err);
    res.status(500).json({ success: false, error: "Error fetching user" });
  }
});

// ✅ COUNTERS
app.get("/api/counters", async (req, res) => {
  try {
    const candidates = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'candidate'");
    const companies = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'company'");
    res.json({ success: true, candidates: parseInt(candidates.rows[0].count), companies: parseInt(companies.rows[0].count) });
  } catch (err) {
    console.error("❌ Counters error:", err);
    res.status(500).json({ success: false, error: "Error fetching counters" });
  }
});

// ✅ Start Server
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));

