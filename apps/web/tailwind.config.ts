import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      borderRadius: {
        'none': '0px',
        'sm': '2px',
        DEFAULT: '4px',
        'md': '4px',
        'lg': '4px',
        'xl': '4px',
        '2xl': '4px',
        '3xl': '4px',
        'full': '4px', // Hard-overrides rounded-full to prevent pill shapes entirely
      },
      colors: {
        foreground: "var(--foreground)",
        background: "var(--background)",
        // Strict neutral palette; explicitly avoiding vibrant purples
        brand: {
          neutral: '#171717',
          surface: '#fafafa',
          border: '#e5e5e5',
        }
      },
      backgroundImage: {
        'none': 'none', // Disables default gradient utilities
      }
    },
  },
  plugins: [],
};
export default config;
