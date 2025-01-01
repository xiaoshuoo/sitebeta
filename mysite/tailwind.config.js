/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './blog/templates/**/*.html',
  ],
  darkMode: 'class',
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
      animation: {
        'float': 'float 15s infinite linear',
        'twinkle': 'twinkle 5s infinite',
        'pulse-slow': 'pulse 4s infinite',
        'bounce-slow': 'bounce 3s infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0) translateX(0)' },
          '25%': { transform: 'translateY(-30vh) translateX(20vw)' },
          '50%': { transform: 'translateY(-10vh) translateX(-20vw)' },
          '75%': { transform: 'translateY(-25vh) translateX(10vw)' },
        },
        twinkle: {
          '0%, 100%': { opacity: '0' },
          '50%': { opacity: '1' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}