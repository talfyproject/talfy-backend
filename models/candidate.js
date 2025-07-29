const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const User = require('./User');

const Candidate = sequelize.define('Candidate', {
  firstName: DataTypes.STRING,
  lastName: DataTypes.STRING,
  location: DataTypes.STRING,
  phone: DataTypes.STRING,
  birthDate: DataTypes.DATEONLY,
  jobRole: DataTypes.STRING,
  experience: DataTypes.STRING,
  education: DataTypes.STRING,
  languages: DataTypes.JSON,
  salaryMin: DataTypes.INTEGER,
  salaryMax: DataTypes.INTEGER,
  availability: DataTypes.STRING,
  remoteWork: DataTypes.STRING,
  relocation: DataTypes.STRING,
  summary: DataTypes.TEXT,
  sectors: DataTypes.ARRAY(DataTypes.STRING),
  software: DataTypes.ARRAY(DataTypes.STRING),
  avatar: DataTypes.STRING,
  photo: DataTypes.STRING,
  cv: DataTypes.STRING
});

Candidate.belongsTo(User, { foreignKey: 'userId' });
module.exports = Candidate;

