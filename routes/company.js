const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Company = require('../models/company');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

// ✅ Register Company
router.post('/register', async (req, res) => {
  const { name, email, password, vat_number, description } = req.body;

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const company = await Company.create({
      name,
      email,
      password: hashedPassword,
      vat_number,
      description
    });

    res.status(201).json({ message: 'Company registered successfully', company });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

// ✅ Login Company
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const company = await Company.findOne({ where: { email } });
    if (!company) return res.status(404).json({ error: 'Company not found' });

    const isPasswordValid = await bcrypt.compare(password, company.password);
    if (!isPasswordValid) return res.status(401).json({ error: 'Invalid credentials' });

    const token = jwt.sign({ id: company.id, email: company.email, type: 'company' }, process.env.JWT_SECRET, {
      expiresIn: '1d'
    });

    res.json({ token });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// ✅ Get Company Profile (Protected)
router.get('/profile', authMiddleware, async (req, res) => {
  try {
    const company = await Company.findByPk(req.user.id);
    if (!company) return res.status(404).json({ error: 'Company not found' });

    res.json(company);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to fetch company profile' });
  }
});

module.exports = router;
