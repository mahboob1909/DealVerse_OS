/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
      fontSize: {
        'h1': ['2rem', { lineHeight: '2.5rem', fontWeight: '700' }],     // 32px
        'h2': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],     // 24px
        'h3': ['1.125rem', { lineHeight: '1.75rem', fontWeight: '600' }], // 18px
        'body': ['0.875rem', { lineHeight: '1.25rem', fontWeight: '400' }], // 14px
        'caption': ['0.75rem', { lineHeight: '1rem', fontWeight: '400' }], // 12px
      },
      spacing: {
        'unit-1': '0.5rem',   /* 8px */
        'unit-2': '1rem',     /* 16px */
        'unit-3': '1.5rem',   /* 24px */
        'unit-4': '2rem',     /* 32px */
        'unit-5': '2.5rem',   /* 40px */
        'unit-6': '3rem',     /* 48px */
        'unit-8': '4rem',     /* 64px */
      },
      gridTemplateColumns: {
        // DealVerse OS 12-column grid system
        '12': 'repeat(12, minmax(0, 1fr))',
        'dealverse': 'repeat(12, minmax(0, 1fr))',
      },
      gridColumn: {
        'span-1': 'span 1 / span 1',
        'span-2': 'span 2 / span 2',
        'span-3': 'span 3 / span 3',
        'span-4': 'span 4 / span 4',
        'span-5': 'span 5 / span 5',
        'span-6': 'span 6 / span 6',
        'span-7': 'span 7 / span 7',
        'span-8': 'span 8 / span 8',
        'span-9': 'span 9 / span 9',
        'span-10': 'span 10 / span 10',
        'span-11': 'span 11 / span 11',
        'span-12': 'span 12 / span 12',
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // DealVerse OS Investment Banking Color Palette
        'dealverse': {
          'navy': '#1a2332',      // Primary: Deep Navy Blue
          'blue': '#0066ff',      // Secondary: Electric Blue
          'green': '#00c896',     // Accent: Emerald Green
          'amber': '#ff9500',     // Warning: Amber
          'coral': '#ff4757',     // Error: Coral Red
          'light-gray': '#f8f9fa', // Neutral: Light Gray
          'medium-gray': '#6c757d', // Neutral: Medium Gray
          'dark-gray': '#343a40',  // Neutral: Dark Gray
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}