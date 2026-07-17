/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,jsx}',
    './src/components/**/*.{js,jsx}',
    './src/app/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0B2B1E',
          600: '#1B4332',
          500: '#297B5C',
          400: '#34A65F',
          100: '#A2F4C8',
        },
        accent: {
          DEFAULT: '#DDA15E',
          600: '#8A5A2A',
        },
        surface: {
          canvas: '#1E1F22',
          base: '#202124',
          card: '#2A2E2B',
          light: '#F8F9FA',
        },
        border: {
          subtle: '#3A3F3C',
          light: '#E1E3E1',
        },
        text: {
          primary: '#F5F7F6',
          secondary: '#9AA39D',
          inverse: '#14171A',
        },
        status: {
          successBg: '#A2F4C8',
          successText: '#0B3D24',
          dangerBg: '#FFDAD6',
          dangerText: '#7A1F17',
          warningBg: '#FBD2CE',
          warningText: '#7A3A17',
        },
      },
      borderRadius: {
        xl: '16px',
        '2xl': '20px',
        pill: '999px',
      },
      fontFamily: {
        heading: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
