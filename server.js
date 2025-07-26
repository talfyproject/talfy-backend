const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// DB Pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Utils
const generateToken = (id, email) => {
  return jwt.sign({ id, email }, process.env.JWT_SECRET, { expiresIn: '7d' });
};

// ✅ ROUTE: Test
app.get('/', (req, res) => {
  res.json({ message: 'Talfy API is live!' });
});

// ✅ REGISTRAZIONE
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, accountType, company } = req.body;

    if (!email || !password || !accountType) {
      return res.status(400).json({ message: 'Missing required fields' });
    }

    // Check esistenza
    const existing = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (existing.rows.length > 0) {
      return res.status(400).json({ message: 'Email already registered' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await pool.query(
      'INSERT INTO users (email, password, account_type, company_name) VALUES ($1,$2,$3,$4) RETURNING id',
      [email, hashedPassword, accountType, company || null]
    );

    const userId = result.rows[0].id;
    const token = generateToken(userId, email);

    res.json({
      status: 'success',
      id: userId,
      token,
      next: accountType === 'candidate' ? `/edit-profile-candidate.html?id=${userId}` : `/edit-profile-company.html?id=${userId}`
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// ✅ LOGIN
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await pool.query('SELECT * FROM users WHERE email = $1', [email]);

    if (user.rows.length === 0) return res.status(400).json({ message: 'Invalid credentials' });

    const valid = await bcrypt.compare(password, user.rows[0].password);
    if (!valid) return res.status(400).json({ message: 'Invalid credentials' });

    const token = generateToken(user.rows[0].id, user.rows[0].email);
    res.json({ status: 'success', token, id: user.rows[0].id, accountType: user.rows[0].account_type });
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
});

// ✅ UPDATE CANDIDATE PROFILE
app.post('/api/profile/candidate', async (req, res) => {
  try {
    const { userId, firstName, lastName, jobTitles, tools, educationArea, salaryRange, experienceYears } = req.body;

    const result = await pool.query(
      `INSERT INTO candidates (user_id, first_name, last_name, job_titles, tools, education_area, salary_range, experience_years)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id`,
      [userId, firstName, lastName, jobTitles, tools, educationArea, salaryRange, experienceYears]
    );

    res.json({ status: 'success', candidateId: result.rows[0].id });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// ✅ STATS
app.get('/api/stats', async (req, res) => {
  try {
    const candidatesCount = await pool.query('SELECT COUNT(*) FROM candidates');
    const companiesCount = await pool.query('SELECT COUNT(*) FROM companies');

    res.json({
      candidates: parseInt(candidatesCount.rows[0].count),
      companies: parseInt(companiesCount.rows[0].count)
    });
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
});

app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
