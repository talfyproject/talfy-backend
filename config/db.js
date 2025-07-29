const { Sequelize } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(process.env.DB_URL, {
  dialect: 'postgres',
  logging: false
});

(async () => {
  try {
    await sequelize.authenticate();
    console.log('✅ PostgreSQL connected successfully!');
  } catch (error) {
    console.error('❌ DB connection failed:', error);
  }
})();

module.exports = sequelize;
