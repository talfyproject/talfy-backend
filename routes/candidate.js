const express = require('express');
const Candidate = require('../models/Candidate');
const authMiddleware = require('../middleware/authMiddleware');
const multer = require('multer');
const path = require('path');

const router = express.Router();

// File upload config
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const folder = file.fieldname === 'photo' ? 'uploads/photos' : 'uploads/cvs';
    cb(null, folder);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});
const upload = multer({ storage });

// Save candidate profile
router.post('/complete-profile', authMiddleware, upload.fields([{ name: 'photo' }, { name: 'cv' }]), async (req, res) => {
  try {
    const userId = req.user.userId;
    const data = req.body;
    const photo = req.files['photo'] ? req.files['photo'][0].filename : null;
    const cv = req.files['cv'] ? req.files['cv'][0].filename : null;

    const candidate = await Candidate.create({ ...data, userId, photo, cv });
    res.json({ message: 'Profile completed', candidate });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
