'use client'

import { createContext, useContext, useEffect, useState } from 'react'

const I18nContext = createContext({ lang: 'en', t: (k) => k, setLang: () => {} })

export const useI18n = () => useContext(I18nContext)

export const INDIAN_LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  { code: 'gu', label: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'Malayalam', native: 'മലയാളം' },
  { code: 'pa', label: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'or', label: 'Odia', native: 'ଓଡ଼ିଆ' },
]

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
  mr: {
    'nav.home': 'मुख्यपृष्ठ',
    'nav.scan': 'स्कॅन',
    'nav.history': 'इतिहास',
    'nav.admin': 'अॅडमिन',
    'nav.profile': 'प्रोफाइल',
    'nav.faq': 'प्रश्न',
    'nav.contact': 'संपर्क',
    'nav.tips': 'शेती सल्ला',
    'nav.signOut': 'साइन आउट',
    'nav.lightMode': 'लाइट मोड',
    'nav.darkMode': 'डार्क मोड',
    'nav.changePassword': 'पासवर्ड बदला',
    'hero.title1': 'पिकांनावरील रोग ओळखा',
    'hero.title2': 'पसरण्यापूर्वी',
    'scan.title': 'पिकाचे आरोग्य तपासा',
    'scan.upload': 'फोटो अपलोड करा किंवा ड्रॅग करा',
    'scan.analyze': 'पिकांच्या आरोग्याचे विश्लेषण करा',
    'dashboard.welcome': 'पुन्हा स्वागत आहे',
    'dashboard.subtitle': 'पिकाच्या आरोग्यावर लक्ष ठेवा',
    'chat.title': 'AgriBot सहाय्यक',
    'chat.placeholder': 'पिके, रोग किंवा उपचारांबद्दल विचारा...',
    'chat.unavailable': 'चॅट उपलब्ध नाही.',
  },
  te: {
    'nav.home': 'హోమ్',
    'nav.scan': 'స్కాన్',
    'nav.history': 'చరిత్ర',
    'nav.admin': 'అడ్మిన్',
    'nav.profile': 'ప్రొఫైల్',
    'nav.faq': 'సందేహాలు',
    'nav.contact': 'సంప్రదించండి',
    'nav.tips': 'వ్యవసాయ సూచనలు',
    'nav.signOut': 'సైన్ అవుట్',
    'nav.lightMode': 'లైట్ మోడ్',
    'nav.darkMode': 'డార్క్ మోడ్',
    'nav.changePassword': 'పాస్‌వర్డ్ మార్చండి',
    'hero.title1': 'పంట వ్యాధులను గుర్తించండి',
    'hero.title2': 'వ్యాపించక ముందే',
    'scan.title': 'మొక్కల ఆరోగ్యాన్ని స్కాన్ చేయండి',
    'scan.upload': 'చిత్రాలను అప్‌లోడ్ చేయడానికి క్లిక్ చేయండి',
    'scan.analyze': 'విశ్లేషించండి',
    'dashboard.welcome': 'స్వాగతం',
    'dashboard.subtitle': 'మీ పంట ఆరోగ్యాన్ని పర్యవేక్షించండి',
    'chat.title': 'AgriBot సహాయకుడు',
    'chat.placeholder': 'పంటలు, వ్యాధుల గురించి అడగండి...',
    'chat.unavailable': 'చాట్ అందుబాటులో లేదు.',
  },
  ta: {
    'nav.home': 'முகப்பு',
    'nav.scan': 'ஸ்கேன்',
    'nav.history': 'வரலாறு',
    'nav.admin': 'நிர்வாகி',
    'nav.profile': 'சுயவிவரம்',
    'nav.faq': 'கேள்விகள்',
    'nav.contact': 'தொடர்பு',
    'nav.tips': 'விவசாய குறிப்புகள்',
    'nav.signOut': 'வெளியேறு',
    'nav.lightMode': 'லைட் மோட்',
    'nav.darkMode': 'டார்க் மோட்',
    'nav.changePassword': 'கடவுச்சொல்லை மாற்றவும்',
    'hero.title1': 'பயிர் நோய்களை கண்டறியவும்',
    'hero.title2': 'பரவுவதற்கு முன்',
    'scan.title': 'தாவர ஆரோக்கியத்தை ஸ்கேன் செய்க',
    'scan.upload': 'படங்களை பதிவேற்ற கிளிக் செய்யவும்',
    'scan.analyze': 'ஆராய்ச்சி செய்க',
    'dashboard.welcome': 'நல்வரவு',
    'dashboard.subtitle': 'பயிர் ஆரோக்கியத்தை கண்காணிக்கவும்',
    'chat.title': 'AgriBot உதவியாளர்',
    'chat.placeholder': 'பயிர்கள், நோய்கள் பற்றி கேட்கவும்...',
    'chat.unavailable': 'சாட் வசதி இல்லை.',
  },
  bn: {
    'nav.home': 'হোম',
    'nav.scan': 'স্ক্যান',
    'nav.history': 'ইতিহাস',
    'nav.admin': 'এডমিন',
    'nav.profile': 'প্রোফাইল',
    'nav.faq': 'প্রশ্নাবলী',
    'nav.contact': 'যোগাযোগ',
    'nav.tips': 'কৃষি পরামর্শ',
    'nav.signOut': 'সাইন আউট',
    'nav.lightMode': 'লাইট মোড',
    'nav.darkMode': 'ডার্ক মোড',
    'nav.changePassword': 'পাসওয়ার্ড পরিবর্তন',
    'hero.title1': 'ফসলের রোগ সনাক্ত করুন',
    'hero.title2': 'ছড়িয়ে পড়ার আগেই',
    'scan.title': 'গাছের স্বাস্থ্য স্ক্যান করুন',
    'scan.upload': 'ছবি আপলোড করতে ক্লিক করুন',
    'scan.analyze': 'বিশ্লেষণ করুন',
    'dashboard.welcome': 'স্বাগতম',
    'dashboard.subtitle': 'আপনার ফসলের স্বাস্থ্য পর্যবেক্ষণ করুন',
    'chat.title': 'AgriBot সহকারী',
    'chat.placeholder': 'ফসল, রোগ বা চিকিৎসা সম্পর্কে জিজ্ঞাসা করুন...',
    'chat.unavailable': 'চ্যাট উপলব্ধ নেই।',
  },
  gu: {
    'nav.home': 'હોમ',
    'nav.scan': 'સ્કેન',
    'nav.history': 'ઇતિહાસ',
    'nav.admin': 'એડમિન',
    'nav.profile': 'પ્રોફાઇલ',
    'nav.faq': 'પ્રશ્નો',
    'nav.contact': 'સંપર્ક',
    'nav.tips': 'ખેતી સલાહ',
    'nav.signOut': 'સાઇન આઉટ',
    'nav.lightMode': 'લાઇટ મોડ',
    'nav.darkMode': 'ડાર્ક મોડ',
    'nav.changePassword': 'પાસવર્ડ બદલો',
    'hero.title1': 'પાકના રોગો શોધો',
    'hero.title2': 'ફેલાય તે પહેલાં',
    'scan.title': 'છોડનું આરોગ્ય સ્કેન કરો',
    'scan.upload': 'અપલોડ કરવા માટે ક્લિક કરો',
    'scan.analyze': 'વિશ્લેષણ કરો',
    'dashboard.welcome': 'સ્વાગત છે',
    'dashboard.subtitle': 'તમારા પાકના આરોગ્યનું નિરીક્ષણ કરો',
    'chat.title': 'AgriBot સહાયક',
    'chat.placeholder': 'પાક, રોગો અથવા સારવાર વિશે પૂછો...',
    'chat.unavailable': 'ચેટ ઉપલબ્ધ નથી.',
  },
  kn: {
    'nav.home': 'ಮುಖ್ಯಪುಟ',
    'nav.scan': 'ಸ್ಕ್ಯಾನ್',
    'nav.history': 'ಇತಿಹಾಸ',
    'nav.admin': 'ಅಡ್ಮಿನ್',
    'nav.profile': 'ಪ್ರೊಫೈಲ್',
    'nav.faq': 'ಪ್ರಶ್ನೋತ್ತರ',
    'nav.contact': 'ಸಂಪರ್ಕಿಸಿ',
    'nav.tips': 'ಕೃಷಿ ಸಲಹೆಗಳು',
    'nav.signOut': 'ಸೈನ್ ಔಟ್',
    'nav.lightMode': 'ಲೈಟ್ ಮೋಡ್',
    'nav.darkMode': 'ಡಾರ್ಕ್ ಮೋಡ್',
    'nav.changePassword': 'ಪಾಸ್‌ವರ್ಡ್ ಬದಲಾಯಿಸಿ',
    'hero.title1': 'ಬೆಳೆ ರೋಗಗಳನ್ನು ಪತ್ತೆ ಮಾಡಿ',
    'hero.title2': 'ಹರಡುವ ಮೊದಲು',
    'scan.title': 'ಸಸ್ಯದ ಆರೋಗ್ಯ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ',
    'scan.upload': 'ಚಿತ್ರಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ',
    'scan.analyze': 'ವಿಶ್ಲೇಷಿಸಿ',
    'dashboard.welcome': 'ಸ್ವಾಗತ',
    'dashboard.subtitle': 'ನಿಮ್ಮ ಬೆಳೆಯ ಆರೋಗ್ಯವನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ',
    'chat.title': 'AgriBot ಸಹಾಯಕ',
    'chat.placeholder': 'ಬೆಳೆಗಳು, ರೋಗಗಳು ಅಥವಾ ಚಿಕಿತ್ಸೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ...',
    'chat.unavailable': 'ಚಾಟ್ ಲಭ್ಯವಿಲ್ಲ.',
  },
  ml: {
    'nav.home': 'ഹോം',
    'nav.scan': 'സ്കാൻ',
    'nav.history': 'ചരിത്രം',
    'nav.admin': 'അഡ്മിൻ',
    'nav.profile': 'പ്രൊഫൈൽ',
    'nav.faq': 'ചോദ്യങ്ങൾ',
    'nav.contact': 'ബന്ധപ്പെടുക',
    'nav.tips': 'കാർഷിക നിർദ്ദേശങ്ങൾ',
    'nav.signOut': 'സൈൻ ഔട്ട്',
    'nav.lightMode': 'ലൈറ്റ് മോഡ്',
    'nav.darkMode': 'ഡാർക്ക് മോഡ്',
    'nav.changePassword': 'പാസ്‌വേഡ് മാറ്റുക',
    'hero.title1': 'വിള രോഗങ്ങൾ കണ്ടെത്തുക',
    'hero.title2': 'പടരുന്നതിന് മുമ്പ്',
    'scan.title': 'ചെടിയുടെ ആരോഗ്യം പരിശോധിക്കുക',
    'scan.upload': 'ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യാൻ ക്ലിക്ക് ചെയ്യുക',
    'scan.analyze': 'വിശകലനം ചെയ്യുക',
    'dashboard.welcome': 'സ്വാഗതം',
    'dashboard.subtitle': 'വിളകളുടെ ആരോഗ്യം നിരീക്ഷിക്കുക',
    'chat.title': 'AgriBot സഹായി',
    'chat.placeholder': 'വിളകൾ, രോഗങ്ങൾ അല്ലെങ്കിൽ ചികിത്സകൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കുക...',
    'chat.unavailable': 'ചാറ്റ് ലഭ്യമല്ല.',
  },
  pa: {
    'nav.home': 'ਹੋਮ',
    'nav.scan': 'ਸਕੈਨ',
    'nav.history': 'ਇਤਿਹਾਸ',
    'nav.admin': 'ਐਡਮਿਨ',
    'nav.profile': 'ਪ੍ਰੋਫਾਈਲ',
    'nav.faq': 'ਸਵਾਲ',
    'nav.contact': 'ਸੰਪਰਕ',
    'nav.tips': 'ਖੇਤੀ ਸੁਝਾਅ',
    'nav.signOut': 'ਸਾਈਨ ਆਊਟ',
    'nav.lightMode': 'ਲਾਈਟ ਮੋਡ',
    'nav.darkMode': 'ਡਾਰਕ ਮੋਡ',
    'nav.changePassword': 'ਪਾਸਵਰਡ ਬਦਲੋ',
    'hero.title1': 'ਫ਼ਸਲ ਦੀਆਂ ਬੀਮਾਰੀਆਂ ਪਛਾਣੋ',
    'hero.title2': 'ਫੈਲਣ ਤੋਂ ਪਹਿਲਾਂ',
    'scan.title': 'ਪੌਦੇ ਦੀ ਸਿਹਤ ਸਕੈਨ ਕਰੋ',
    'scan.upload': 'ਤਸਵੀਰਾਂ ਅੱਪਲੋਡ ਕਰਨ ਲਈ ਕਲਿੱਕ ਕਰੋ',
    'scan.analyze': 'ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ',
    'dashboard.welcome': 'ਜੀ ਆਇਆਂ ਨੂੰ',
    'dashboard.subtitle': 'ਆਪਣੀ ਫ਼ਸਲ ਦੀ ਸਿਹਤ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ',
    'chat.title': 'AgriBot ਸਹਾਇਕ',
    'chat.placeholder': 'ਫ਼ਸਲਾਂ, ਬੀਮਾਰੀਆਂ ਜਾਂ ਇਲਾਜ ਬਾਰੇ ਪੁੱਛੋ...',
    'chat.unavailable': 'ਚੈਟ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।',
  },
  or: {
    'nav.home': 'ହୋମ୍',
    'nav.scan': 'ସ୍କାନ୍',
    'nav.history': 'ଇତିହାସ',
    'nav.admin': 'ଆଡମିନ୍',
    'nav.profile': 'ପ୍ରୋଫାଇଲ୍',
    'nav.faq': 'ପ୍ରଶ୍ନୋତ୍ତର',
    'nav.contact': 'ସମ୍ପର୍କ',
    'nav.tips': 'କୃଷି ପରାମର୍ଶ',
    'nav.signOut': 'ସାଇନ୍ ଆଉଟ୍',
    'nav.lightMode': 'ଲାଇଟ୍ ମୋଡ୍',
    'nav.darkMode': 'ଡାର୍କ ମୋଡ୍',
    'nav.changePassword': 'ପାସୱାର୍ଡ ବଦଳାନ୍ତୁ',
    'hero.title1': 'ଫସଲ ରୋଗ ଚିହ୍ନଟ କରନ୍ତୁ',
    'hero.title2': 'ବ୍ୟାପିବା ପୂର୍ବରୁ',
    'scan.title': 'ଗଛର ସ୍ୱାସ୍ଥ୍ୟ ସ୍କାନ୍ କରନ୍ତୁ',
    'scan.upload': 'ଫଟୋ ଅପଲୋଡ୍ କରିବାକୁ କ୍ଲିକ୍ କରନ୍ତୁ',
    'scan.analyze': 'ବିଶ୍ଳେଷଣ କରନ୍ତୁ',
    'dashboard.welcome': 'ସ୍ୱାଗତ',
    'dashboard.subtitle': 'ଫସଲ ସ୍ୱାସ୍ଥ୍ୟ ଉପରେ ନଜର ରଖନ୍ତୁ',
    'chat.title': 'AgriBot ସହାୟକ',
    'chat.placeholder': 'ଫସଲ, ରୋଗ କିମ୍ବା ଚିକିତ୍ସା ବିଷୟରେ ପଚାରନ୍ତୁ...',
    'chat.unavailable': 'ଚାଟ୍ ଉପଲବ୍ଧ ନାହିଁ।',
  },
}

export const I18nProvider = ({ children }) => {
  const [lang, setLangState] = useState('en')

  useEffect(() => {
    const stored = localStorage.getItem('agrivision_lang')
    if (stored) {
      setLangState(stored)
      applyGoogleTranslateCookie(stored)
    }
    loadGoogleTranslateScript()
  }, [])

  const applyGoogleTranslateCookie = (l) => {
    if (typeof window === 'undefined') return
    try {
      const targetLang = l === 'en' ? '' : l
      const cookieValue = targetLang ? `/en/${targetLang}` : '/en/en'
      
      // Set cookie for current domain and paths
      document.cookie = `googtrans=${cookieValue}; path=/`
      document.cookie = `googtrans=${cookieValue}; domain=.${window.location.hostname}; path=/`
      document.cookie = `googtrans=${cookieValue}; domain=${window.location.hostname}; path=/`
      
      // Dispatch change event to trigger Google Translate widget if loaded
      const select = document.querySelector('.goog-te-combo')
      if (select) {
        select.value = l
        select.dispatchEvent(new Event('change'))
        select.dispatchEvent(new Event('input'))
      }
    } catch (e) {
      console.warn('Google Translate Cookie error:', e)
    }
  }

  const loadGoogleTranslateScript = () => {
    if (typeof window === 'undefined') return
    if (document.getElementById('google-translate-script')) return

    // Inject CSS to force-hide top bar
    const style = document.createElement('style')
    style.innerHTML = `
      .goog-te-banner-frame, iframe.goog-te-banner-frame, .skiptranslate.goog-te-banner-frame, body > .skiptranslate, #goog-gt-tt {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
      }
      body { top: 0px !important; position: static !important; }
    `
    document.head.appendChild(style)

    window.googleTranslateElementInit = () => {
      new window.google.translate.TranslateElement(
        {
          pageLanguage: 'en',
          includedLanguages: 'hi,mr,te,ta,bn,gu,kn,ml,pa,or,en',
          autoDisplay: false,
          layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE
        },
        'google_translate_element'
      )
    }

    const script = document.createElement('script')
    script.id = 'google-translate-script'
    script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'
    script.async = true
    document.body.appendChild(script)
  }

  const setLang = (l) => {
    if (l === lang) return
    setLangState(l)
    localStorage.setItem('agrivision_lang', l)
    applyGoogleTranslateCookie(l)
    
    // Auto reload location so Google Translate translates the entire page instantly
    setTimeout(() => {
      window.location.reload()
    }, 50)
  }

  const t = (key) => {
    const currentDict = translations[lang] || translations.en
    return currentDict[key] || translations.en[key] || key
  }

  return (
    <I18nContext.Provider value={{ lang, t, setLang, languages: INDIAN_LANGUAGES }}>
      <div id="google_translate_element" style={{ display: 'none' }} />
      {children}
    </I18nContext.Provider>
  )
}