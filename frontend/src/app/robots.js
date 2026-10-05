export default function robots() {
  const baseUrl = 'https://www.agrivisioncare.tech'
  
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: [
          '/api/',
          '/admin/',
          '/profile/',
          '/dashboard/',
          '/history/',
        ],
      },
      {
        userAgent: 'Googlebot',
        allow: '/',
        disallow: [
          '/api/',
          '/admin/',
          '/profile/',
          '/dashboard/',
          '/history/',
        ],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  }
}
