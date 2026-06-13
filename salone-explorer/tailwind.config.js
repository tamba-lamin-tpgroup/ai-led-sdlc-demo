// Tailwind config — reads FambulTik tokens from CSS variables.
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "var(--color-brand-primary)",
          secondary: "var(--color-brand-secondary)",
          accent: "var(--color-brand-accent)",
          sand: "var(--color-brand-sand)",
        },
        tpgroup: {
          primary: "var(--color-tpgroup-primary)",
        },
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        text: {
          DEFAULT: "var(--color-text)",
          muted: "var(--color-text-muted)",
        },
        border: "var(--color-border)",
        "focus-ring": "var(--color-focus-ring)",
        success: "var(--color-success)",
        warning: "var(--color-warning)",
        danger: "var(--color-danger)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
        display: ["Lora", "Georgia", "serif"],
      },
      fontSize: {
        "fs-12": "var(--fs-12)",
        "fs-14": "var(--fs-14)",
        "fs-16": "var(--fs-16)",
        "fs-18": "var(--fs-18)",
        "fs-20": "var(--fs-20)",
        "fs-24": "var(--fs-24)",
        "fs-30": "var(--fs-30)",
        "fs-36": "var(--fs-36)",
        "fs-48": "var(--fs-48)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
      },
      borderRadius: {
        sm: "var(--r-sm)",
        md: "var(--r-md)",
        lg: "var(--r-lg)",
        xl: "var(--r-xl)",
        full: "var(--r-full)",
      },
    },
  },
  plugins: [],
};
