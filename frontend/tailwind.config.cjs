/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'velo-green': {
          DEFAULT: '#2d5f4d',
          50: '#f0f5f3',
          100: '#dde9e4',
          200: '#c3d8cf',
          300: '#9dbfad',
          400: '#72a088',
          500: '#52826b',
          600: '#3f6756',
          700: '#345447',
          800: '#2d5f4d',
          900: '#234335',
        },
        'velo-beige': {
          DEFAULT: '#f5f3f0',
          50: '#faf9f7',
          100: '#f5f3f0',
          200: '#ebe7e1',
          300: '#ddd6cc',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
