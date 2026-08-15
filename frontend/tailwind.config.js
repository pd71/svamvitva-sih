/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        gis: {
          bg: "#0B1120",
          card: "#161F33",
          border: "#2A3854",
          accent: "#0EA5E9",
          hover: "#1E293B",
          rcc: "#F59E0B",
          tiled: "#EF4444",
          tin: "#06B6D4",
          other: "#64748B",
          success: "#10B981"
        }
      }
    },
  },
  plugins: [],
}
