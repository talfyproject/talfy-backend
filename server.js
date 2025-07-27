// server.js - Backend Talfy con Node.js + Express + PostgreSQL
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { Pool } from 'pg';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Percorso statico
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, 'public')));

// ✅ Connessione DB PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

pool.connect()
  .then(() => console.log('✅ Connesso al database PostgreSQL'))
  .catch(err => console.error('❌ Errore connessione DB:', err));

/* ==============================
   AUTENTICAZIONE
============================== */

// ✅ Registrazione
app.post('/api/auth/register', async (req, res) => {
  const { email, password, accountType, company } = req.body;
  try {
    const userExists = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: 'Email già registrata' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await pool.query(
      `INSERT INTO users (email, password, account_type, company_name) 
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [email, hashedPassword, accountType, company || null]
    );

    const userId = result.rows[0].id;
    res.json({ status: "success", id: userId });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Errore interno server' });
  }
});

// ✅ Login
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (result.rows.length === 0) return res.status(400).json({ message: 'Utente non trovato' });

    const user = result.rows[0];
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) return res.status(400).json({ message: 'Password errata' });

    const token = jwt.sign(
      { id: user.id, accountType: user.account_type },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({ status: "success", token, userId: user.id, accountType: user.account_type });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Errore interno server' });
  }
});

/* ==============================
   STATS
============================== */
app.get('/api/stats', async (req, res) => {
  try {
    const candidatesCount = await pool.query("SELECT COUNT(*) FROM users WHERE account_type = 'candidate'");
    const companiesCount = await pool.query("SELECT COUNT(*) FROM users WHERE account_type = 'company'");
    res.json({ candidates: candidatesCount.rows[0].count, companies: companiesCount.rows[0].count });
  } catch (error) {
    res.status(500).json({ message: 'Errore recupero statistiche' });
  }
});

/* ==============================
   PROFILI (CANDIDATI)
============================== */
app.get('/api/profile/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const result = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Profilo non trovato' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Errore nel recupero del profilo' });
  }
});

app.post('/api/profile/update', async (req, res) => {
  const { userId, first_name, last_name, job_title, sector, tools, education_area } = req.body;
  try {
    await pool.query(
      `UPDATE users 
       SET first_name=$1, last_name=$2, job_title=$3, sector=$4, tools=$5, education_area=$6
       WHERE id=$7`,
      [first_name, last_name, job_title, sector, tools, education_area, userId]
    );
    res.json({ status: "success", message: "Profilo aggiornato" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Errore aggiornamento profilo' });
  }
});

/* ==============================
   PROFILI (AZIENDE)
============================== */

// ✅ GET Profilo azienda
app.get('/api/company/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const result = await pool.query('SELECT * FROM users WHERE id = $1 AND account_type = $2', [id, 'company']);
    if (result.rows.length === 0) return res.status(404).json({ message: 'Azienda non trovata' });

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Errore nel recupero del profilo azienda' });
  }
});

// ✅ PUT Aggiorna profilo azienda
app.put('/api/company/:id', async (req, res) => {
  const { id } = req.params;
  const {
    company_name, website, vat_number, country, industry,
    company_size, city, email, company_description, work_culture,
    linkedin, facebook, twitter, instagram
  } = req.body;

  try {
    const query = `
      UPDATE users
      SET company_name=$1, website=$2, vat_number=$3, country=$4, industry=$5,
          company_size=$6, city=$7, email=$8, company_description=$9, work_culture=$10,
          linkedin=$11, facebook=$12, twitter=$13, instagram=$14
      WHERE id=$15 AND account_type='company'
      RETURNING *;
    `;
    const values = [
      company_name, website, vat_number, country, industry,
      company_size, city, email, company_description, work_culture,
      linkedin, facebook, twitter, instagram, id
    ];

    const result = await pool.query(query, values);
    if (result.rows.length === 0) return res.status(404).json({ message: 'Azienda non trovata' });

    res.json({ status: "success", company: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Errore aggiornamento profilo azienda' });
  }
});

/* ==============================
   AVVIO SERVER
============================== */
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server avviato su http://localhost:${PORT}`));
