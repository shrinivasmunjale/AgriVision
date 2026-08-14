'use client'

import { createContext, useContext, useEffect, useState } from 'react'

const I18nContext = createContext({ lang: 'en', t: (k) => k, setLang: () => {} })

export const useI18n = () => useContext(I18nContext)

const translations = {
  en: {
    'nav.home': 'Home',
    'nav.scan': 'Scan',
    'nav.history': 'History',
    'nav.admin': 'Admin',
    'nav.profile': 'Profile',
    'nav.faq': 'FAQ',
    'nav.contact': 'Contact',
    'nav.tips': 'Farming Tips',
    'nav.signOut': 'Sign Out',
    'nav.lightMode': 'Light Mode',
    'nav.darkMode': 'Dark Mode',
    'nav.changePassword': 'Change Password',
    'hero.title1': 'Detect crop diseases',
    'hero.title2': 'before they spread',
    'scan.title': 'Scan Plant Health',
    'scan.upload': 'Drag & drop images or click to upload',
    'scan.analyze': 'Analyze Plant Health',
    'dashboard.welcome': 'Welcome back',
    'dashboard.subtitle': 'Monitor your crop health and get AI-powered insights',
    'chat.title': 'AgriBot Assistant',
    'chat.placeholder': 'Ask about crops, diseases or treatments...',
    'chat.unavailable': 'Chat is not configured. Add AI_API_KEY to enable.',
  },
  hi: {
    'nav.home': 'होम',
    'nav.scan': 'स्कैन',
    'nav.history': 'इतिहास',
    'nav.admin': 'एडमिन',
    'nav.profile': 'प्रोफ़ाइल',
    'nav.faq': 'FAQ',
    'nav.contact': 'संपर्क',
    'nav.tips': 'कृषि सुझाव',
    'nav.signOut': 'साइन आउट',
    'nav.lightMode': 'लाइट मोड',
    'nav.darkMode': 'डार्क मोड',
    'nav.changePassword': 'पासवर्ड बदलें',
    'hero.title1': 'फसल रोगों का पता लगाएं',
    'hero.title2': 'फैलने से पहले',
    'scan.title': 'पौधों के स्वास्थ्य की जांच',
    'scan.upload': 'इमेज खींचें और ड्रॉप करें या अपलोड करने के लिए क्लिक करें',
    'scan.analyze': 'पौधों के स्वास्थ्य का विश्लेषण करें',
    'dashboard.welcome': 'वापसी पर स्वागत है',
    'dashboard.subtitle': 'अपनी फसल के स्वास्थ्य की निगरानी करें',
    'chat.title': 'AgriBot सहायक',
    'chat.placeholder': 'फसल, रोग या उपचार के बारे में पूछें...',
    'chat.unavailable': 'चैट कॉन्फ़िगर नहीं है। AI_API_KEY जोड़ें।',
  },
  es: {
    'nav.home': 'Inicio',
    'nav.scan': 'Escanear',
    'nav.history': 'Historial',
    'nav.admin': 'Admin',
    'nav.profile': 'Perfil',
    'nav.faq': 'FAQ',
    'nav.contact': 'Contacto',
    'nav.tips': 'Consejos',
    'nav.signOut': 'Cerrar sesión',
    'nav.lightMode': 'Modo claro',
    'nav.darkMode': 'Modo oscuro',
    'nav.changePassword': 'Cambiar contraseña',
    'hero.title1': 'Detecta enfermedades',
    'hero.title2': 'antes de que se propaguen',
    'scan.title': 'Escanear salud de la planta',
    'scan.upload': 'Arrastra imágenes o haz clic para subir',
    'scan.analyze': 'Analizar salud de la planta',
    'dashboard.welcome': 'Bienvenido de nuevo',
    'dashboard.subtitle': 'Monitorea la salud de tus cultivos',
    'chat.title': 'AgriBot Asistente',
    'chat.placeholder': 'Pregunta sobre cultivos, enfermedades o tratamientos...',
    'chat.unavailable': 'El chat no está configurado. Agrega AI_API_KEY.',
  },
}

export const I18nProvider = ({ children }) => {
  const [lang, setLangState] = useState('en')

  useEffect(() => {
    const stored = localStorage.getItem('agrivision_lang')
    if (stored && translations[stored]) setLangState(stored)
  }, [])

  useEffect(() => {
    localStorage.setItem('agrivision_lang', lang)
  }, [lang])

  const setLang = (l) => {
    if (translations[l]) setLangState(l)
  }

  const t = (key) => (translations[lang] && translations[lang][key]) || key

  return (
    <I18nContext.Provider value={{ lang, t, setLang }}>
      {children}
    </I18nContext.Provider>
  )
}