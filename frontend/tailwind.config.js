/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                brand: {
                    DEFAULT: '#00ccb4', // Primary Teal
                    light: '#5eead4',
                    dark: '#0f766e',
                    glow: '#00ffda',
                },
                accent: {
                    teal: '#00f5e1',
                    cyan: '#06b6d4',
                    lime: '#a3e635',
                },
                pixora: {
                    bg: '#020606', // Deep background
                    card: 'rgba(10, 25, 25, 0.7)', // Glass card
                    border: 'rgba(20, 50, 50, 0.4)',
                    'darker-green': '#051414',
                    'lighter-green': '#0d2d2d',
                }
            },
            backgroundImage: {
                'pixora-gradient': 'radial-gradient(circle at top right, #052020 0%, #020606 100%)',
                'glow-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow-spin': 'spin 10s linear infinite',
            },
            backdropBlur: {
                'xs': '2px',
            },
            boxShadow: {
                'brand-glow': '0 0 20px rgba(0, 204, 180, 0.3)',
                'brand-glow-strong': '0 0 30px rgba(0, 204, 180, 0.5)',
            }
        },
    },
    plugins: [],
}
