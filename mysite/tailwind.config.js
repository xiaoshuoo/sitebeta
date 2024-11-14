/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './blog/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'background': '#1A1625',
        'surface': '#2D2A3D',
        'primary': {
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
        },
      },
    },
  },
  plugins: [],
}