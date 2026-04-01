/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f7fa',
          100: '#eaeef4',
          200: '#d0dae7',
          300: '#a7bbd3',
          400: '#7694b8',
          500: '#53749d',
          600: '#415b84',
          700: '#354a6c',
          800: '#2f3f5a',
          900: '#2a374d',
          950: '#1c2433', // Deep luxury blue-slate
        },
        accent: {
          50: '#fbf8f1',
          100: '#f4ecd9',
          200: '#e9d6b5',
          300: '#d9b886',
          400: '#ca9a5d',
          500: '#b67a42',
          600: '#a66738',
          700: '#8a5131',
          800: '#70432c',
          900: '#5b3827',
          950: '#301c13', // Warm golden-earth tones
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
    },
  },
  plugins: [],
}
