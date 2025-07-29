import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import pkg from "pg";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

dotenv.config();
const { Pool } = pkg;

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors({
  origin: "*",
  methods: ["GET", "POST", "PUT", "DELETE"],
  allowedHeaders: ["Content-Type", "Authorization"]
}));
app.use(express.json());
app.use(express.static("public"));

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

pool.connect()
  .then(() => console.log("✅ Connected to PostgreSQL"))
  .catch((err) => console.error("❌ Database connection error:", err));

const JWT_SECRET = process.env.JWT_SECRET || "supersecretkey";

// ✅ Test Route
app.get("/", (req, res) => {
  res.json({ message: "✅ Talfy Backend is running" });
});

// ✅ Middleware JWT
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

// ✅ REGISTER
app.post("/api/register", async (req, res) => {
  const { email, password, user_type, userType } = req.body;
  const type = user_type || userType;

  if (!email || !password || !type) {
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
      [email, hashedPassword, type]
    );

    return res.json({ success: true, userType: type, userId: result.rows[0].id });
  } catch (err) {
    console.error("❌ Registration error:", err);
    return res.status(500).json({ success: false, error: "Server error during registration" });
  }
});

// ✅ LOGIN
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ success: false, error: "Email and password are required" });
  }

  try {
    const userResult = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userResult.rows.length === 0) {
      return res.status(400).json({ success: false, error: "Invalid email or password" });
    }

    const user = userResult.rows[0];
    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return res.status(400).json({ success: false, error: "Invalid email or password" });
    }

    const token = jwt.sign({ id: user.id, email: user.email, user_type: user.user_type }, JWT_SECRET, { expiresIn: "2h" });

    return res.json({ success: true, message: "Login successful", token, userId: user.id, userType: user.user_type });
  } catch (err) {
    console.error("❌ Login error:", err);
    return res.status(500).json({ success: false, error: "Server error during login" });
  }
});

// ✅ UPDATE PROFILE
app.post("/api/update-profile", authMiddleware, async (req, res) => {
  const { profileData } = req.body;
  const userId = req.user.id;

  if (!profileData) {
    return res.status(400).json({ success: false, error: "Missing profile data" });
  }

  try {
    await pool.query("UPDATE users SET profile = $1 WHERE id = $2", [profileData, userId]);
    return res.json({ success: true, message: "Profile updated successfully" });
  } catch (err) {
    console.error("❌ Profile update error:", err);
    return res.status(500).json({ success: false, error: "Error updating profile" });
  }
});

// ✅ COUNTERS
app.get("/api/counters", async (req, res) => {
  try {
    const candidates = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'candidate'");
    const companies = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'company'");

    return res.json({
      success: true,
      candidates: parseInt(candidates.rows[0].count, 10),
      companies: parseInt(companies.rows[0].count, 10)
    });
  } catch (err) {
    console.error("❌ Counters error:", err);
    return res.status(500).json({ success: false, error: "Error fetching counters" });
  }
});

// ✅ Start Server
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
