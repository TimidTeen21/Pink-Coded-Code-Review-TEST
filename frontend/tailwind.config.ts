import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'pink-flamingo': '#FF66B3',
        'dark-triangle': '#1A1A1A',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
      },
    },
  },
  plugins: [],
}

export default config