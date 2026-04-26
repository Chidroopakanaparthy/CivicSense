/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use static export for Firebase Hosting to avoid SSR timeouts
  output: 'export',
  reactStrictMode: true,
}

module.exports = nextConfig
