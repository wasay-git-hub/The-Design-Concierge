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
        luxury: {
          charcoal: "#121212",
          brass: "#C5A880",
          cream: "#FAF8F5",
          sage: "#A3B19B",
          darkGray: "#1E1E1E",
          lightGray: "#F5F3EF",
          border: "#EAE7E2"
        }
      },
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "serif"],
        sans: ["Outfit", "Inter", "sans-serif"]
      }
    },
  },
  plugins: [],
}
