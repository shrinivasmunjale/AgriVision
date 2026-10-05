import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  metadataBase: new URL('https://www.agrivisioncare.tech'),
  title: {
    default: 'AgriVision AI - Crop Disease Detection',
    template: '%s | AgriVision AI',
  },
  description: 'AI-powered tomato leaf disease detection and treatment recommendations. Accurate diagnosis with evidence-based treatment from ICAR, PPQS, and Agricultural Universities.',
  keywords: ['tomato disease detection', 'crop disease AI', 'agricultural technology', 'plant disease diagnosis', 'smart farming', 'precision agriculture', 'tomato farming', 'disease management'],
  authors: [{ name: 'AgriVision AI' }],
  creator: 'AgriVision AI',
  publisher: 'AgriVision AI',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://www.agrivisioncare.tech',
    title: 'AgriVision AI - Crop Disease Detection',
    description: 'AI-powered tomato leaf disease detection and treatment recommendations. Accurate diagnosis with evidence-based treatment from ICAR, PPQS, and Agricultural Universities.',
    siteName: 'AgriVision AI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AgriVision AI - Crop Disease Detection',
    description: 'AI-powered tomato leaf disease detection and treatment recommendations',
    creator: '@agrivisionai',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code-here',
    yandex: 'your-yandex-verification-code-here',
  },
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
