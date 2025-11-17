// theme/static_src/tailwind.config.js
module.exports = {
  content: [
    // template ของ theme เอง (theme/templates)
    '../templates/**/*.html',

    // template กลางของโปรเจกต์ (ถ้ามีโฟลเดอร์ templates ที่ root เดียวกับ theme)
    '../../templates/**/*.html',

    // template ของทุก app ในโปรเจกต์ (trainmydog, course ฯลฯ)
    '../../**/templates/**/*.html',

    // ถ้าเขียน class tailwind ในไฟล์ .py ด้วย เช่น render_to_string
    '../../**/*.py',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
