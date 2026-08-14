import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AgriVision AI - Crop Disease Detection',
  description: 'AI-powered tomato leaf disease detection and treatment recommendations',
}

// Set the persisted theme before paint to avoid a flash of the wrong theme
const themeScript = `(function(){try{var t=localStorage.getItem('agrivision_theme')||'dark';document.documentElement.setAttribute('data-theme',t==='light'?'light':'dark');}catch(e){document.documentElement.setAttribute('data-theme','dark');}})();`

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
