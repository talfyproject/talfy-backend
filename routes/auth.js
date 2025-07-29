const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
require('dotenv').config();

const router = express.Router();

// Registrazione
router.post('/register', async (req, res) => {
  const { email, password, userType } = req.body;
  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await User.create({ email, password: hashedPassword, userType });
    res.json({ message: 'User registered', userId: user.id });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ where: { email } });
    if (!user) return res.status(404).json({ error: 'User not found' });

    const match = await bcrypt.compare(password, user.password);
    if (!match) return res.status(401).json({ error: 'Invalid credentials' });

    const token = jwt.sign({ userId: user.id, userType: user.userType }, process.env.JWT_SECRET, { expiresIn: '1d' });
    res.json({ token, userType: user.userType });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;