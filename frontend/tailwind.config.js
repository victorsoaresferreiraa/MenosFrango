/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/features/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-montserrat)', 'sans-serif'],
      },
      colors: {
        // JEITO 1: Cor única direta
        // Vai gerar classes como: bg-principal, text-principal
        principal: { 
          preto: "#000000", 
          pretoClaro: "#252525", 
          cinza: "#2b2b2b", 
          cinzaEscuro: "#4d4d4d",
          cinzaClaro: "#f7f7f7",
          cinza2: "#cecece",
          cinza3: "#4d4d4d",
          vermelhoHover: "#640000",
          vermelho: "#db0000",
        },
        frango: {
          claro: "#ffedd5",   // Laranja bem clarinho para fundos
          base: "#f97316",    // O laranja padrão dos botões
          escuro: "#c2410c",  // Laranja mais escuro para o hover
        },

        // Você também pode mapear as cores do Shadcn UI aqui, caso volte a usar!
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
};