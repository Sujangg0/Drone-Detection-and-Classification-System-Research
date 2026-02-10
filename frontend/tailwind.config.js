/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        primary: '#1E3A8A',     // dark blue for buttons/headers
        critical: '#EF4444',    // red for critical alerts
        warning: '#F59E0B',     // amber for warnings
        normal: '#10B981',      // green for normal/clear status
      },
    },
  },
  plugins: [],
}
