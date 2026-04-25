/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_APP_NAME: 'MENOSFRANGO',
    NEXT_PUBLIC_APP_TAGLINE: 'Treino inteligente, resultado de verdade',
  },
  images: {
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost', port: '9000' },
      { protocol: 'https', hostname: '**.menosfrango.ai' },
    ],
  },
};

module.exports = nextConfig;
