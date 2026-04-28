/**
 * Layout principal MENOSFRANGO — Com Dark Mode Toggle e Fundo Animado! 🚀
 */

import { ReactNode, useState, useEffect } from "react";
import FrangoLogo from "@/components/FrangoLogo";
import Sidebar from "./Sidebar"; 
import { Particles } from "@/components/ui/particles";
import { Sun, Moon } from "react-bootstrap-icons"; // 🌟 ÍCONES IMPORTADOS AQUI

export default function Layout({ children, title }: { children: ReactNode; title?: string }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // 🌟 LÓGICA DO DARK MODE: Checa o tema salvo ao carregar a página
  useEffect(() => {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  // 🌟 FUNÇÃO DE ALTERNÂNCIA (TOGGLE)
  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.theme = 'light';
      setIsDarkMode(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.theme = 'dark';
      setIsDarkMode(true);
    }
  };

  return (
    // 'transition-colors' adicionado para suavizar a troca entre claro e escuro
    <div className="relative h-screen w-screen bg-slate-50 dark:bg-slate-900 flex overflow-hidden transition-colors duration-300">
      
      {/* PARTÍCULAS GLOBAIS */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40">
        <Particles className="w-full h-full" color="#f97316" quantity={60} />
      </div>

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      {/* CONTEÚDO */}
      <div className="relative z-10 flex-1 flex flex-col min-w-0 overflow-hidden">
        
        {/* Header mobile (visível apenas em telas pequenas) */}
        <header className="lg:hidden sticky top-0 z-20 bg-[#000080] px-4 py-3 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg text-white text-xl">
              {sidebarOpen ? "✕" : "☰"}
            </button>
            <div className="flex items-center gap-2">
              <FrangoLogo className="w-8 h-8 drop-shadow-xl" />
            </div>
          </div>
          
          {/* Botão Tema - Mobile */}
          <button onClick={toggleTheme} className="text-white p-2 hover:scale-110 transition-transform">
            {isDarkMode ? <Sun size={24} className="text-yellow-400" /> : <Moon size={24} />}
          </button>
        </header>

        {/* MAIN (Área principal) */}
        <main className="flex-1 p-5 lg:p-8 overflow-y-auto relative">
          
          {/* Header Desktop (Título à esquerda, Botão Tema à direita) */}
          <div className="flex items-center justify-between mb-6 hidden lg:flex">
            {title ? (
              <h1 className="text-2xl font-black text-frango-base ">{title}</h1>
            ) : <div />}
            
            {/* Botão Tema - Desktop */}
            <button 
              onClick={toggleTheme} 
              className="p-2.5 rounded-full bg-white dark:bg-slate-800 text-slate-800 dark:text-yellow-400 shadow-sm border border-slate-200 dark:border-slate-700 hover:scale-110 hover:shadow-md transition-all duration-200"
              title={isDarkMode ? "Mudar para modo claro" : "Mudar para modo escuro"}
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>

          <div className="h-full w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}