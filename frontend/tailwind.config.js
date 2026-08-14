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
          canvas: 'var(--surface-canvas)',
          base: 'var(--surface-base)',
          card: 'var(--surface-card)',
          light: 'var(--surface-light)',
        },
        border: {
          subtle: 'var(--border-subtle)',
          light: 'var(--border-light)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          inverse: 'var(--text-inverse)',
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
