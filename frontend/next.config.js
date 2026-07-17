/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['images.unsplash.com', 'mock-storage.agrivision.ai', 'localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.r2.cloudflarestorage.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
  // Ensure proper module resolution for Vercel
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/contexts': path.resolve(__dirname, 'src/contexts'),
      '@/lib': path.resolve(__dirname, 'src/lib'),
      '@/app': path.resolve(__dirname, 'src/app'),
    }
    
    // Ensure proper module resolution
    config.resolve.extensions = ['.js', '.jsx', '.json']
    
    return config
  },
}

module.exports = nextConfig
