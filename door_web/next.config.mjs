/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: { allowedOrigins: ["*"] },
  },
  images: {
    remotePatterns: [{ hostname: "localhost" }],
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8010/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
