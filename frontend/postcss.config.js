// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},    // ← This is the correct plugin for v4
    autoprefixer: {},
  },
}
