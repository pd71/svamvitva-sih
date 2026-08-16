/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  async rewrites() {
    const rawUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'https://nerdvana-sih-backend.onrender.com';
    let backendUrl = rawUrl.replace(/\/+$/, '');
    if (backendUrl.endsWith('/api')) {
      backendUrl = backendUrl.slice(0, -4);
    }
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/static/:path*',
        destination: `${backendUrl}/static/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

