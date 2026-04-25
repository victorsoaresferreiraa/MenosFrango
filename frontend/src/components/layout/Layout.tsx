/**
 * Layout principal MENOSFRANGO — sidebar com identidade visual completa.
 */

import { ReactNode, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { href: "/dashboard",    label: "Dashboard",    emoji: "📊", tip: "Visão geral" },
  { href: "/workouts",     label: "Treinos",      emoji: "🏋️", tip: "Seus treinos" },
  { href: "/nutrition",    label: "Nutrição",     emoji: "🥗", tip: "O que comeu" },
  { href: "/photos",       label: "Progresso",    emoji: "📸", tip: "Fotos" },
  { href: "/ai",           label: "IA Frango",    emoji: "🤖", tip: "Planos com IA" },
  { href: "/reports",      label: "Relatórios",   emoji: "📄", tip: "PDF mensal" },
  { href: "/my-personals", label: "Meu Personal", emoji: "👨‍🏫", tip: "Personal trainer" },
  { href: "/profile",      label: "Meu Perfil",   emoji: "👤", tip: "Configurações" },
];

const MOTIVATIONAL = [
  "Bora, sem desculpa! 💪",
  "Frango é quem não treina! 🐔",
  "Hoje é dia de ser menos frango!",
  "A IA tá do seu lado! 🤖",
  "Consistência vence talento! 🔥",
  "Menos conversa, mais treino!",
];

export default function Layout({ children, title }: { children: ReactNode; title?: string }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();
  const phrase = MOTIVATIONAL[Math.floor(Math.random() * MOTIVATIONAL.length)];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 w-64 bg-blue-900 z-30 flex flex-col transform transition-transform duration-300 lg:translate-x-0 lg:static ${
        sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>

        {/* Logo */}
        <div className="p-5 border-b border-blue-800">
          <div className="flex items-center gap-3">
            <img src="/mascote.svg" alt="mascote" className="w-12 h-auto" />
            <div>
              <p className="font-black text-white text-lg leading-none">
                MENOS<span className="text-orange-400">FRANGO</span>
              </p>
              <p className="text-blue-300 text-xs mt-0.5">Treino com tecnologia</p>
            </div>
          </div>
        </div>

        {/* Info usuário */}
        <div className="p-4 border-b border-blue-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-blue-700 flex items-center justify-center text-white font-bold text-sm">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-white text-sm truncate">{user?.name}</p>
              <span className="text-xs text-blue-300 capitalize">{user?.role || "aluno"}</span>
            </div>
          </div>
          <p className="text-blue-400 text-xs mt-2 italic">{phrase}</p>
        </div>

        {/* Nav */}
        <nav className="p-3 space-y-0.5 flex-1 overflow-y-auto">
          {NAV_ITEMS.map(({ href, label, emoji }) => {
            const isActive = router.pathname === href || (href !== "/" && router.pathname.startsWith(href));
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-150 ${
                  isActive
                    ? "bg-orange-500 text-white font-bold"
                    : "text-blue-200 hover:bg-blue-800 hover:text-white"
                }`}
                onClick={() => setSidebarOpen(false)}>
                <span className="text-base">{emoji}</span>
                <span className="text-sm font-medium">{label}</span>
                {isActive && <span className="ml-auto text-xs">←</span>}
              </Link>
            );
          })}
        </nav>

        {/* Streak motivacional */}
        <div className="mx-3 mb-3 p-3 bg-blue-800 rounded-xl text-center">
          <p className="text-2xl">🔥</p>
          <p className="text-white text-xs font-bold mt-1">Continue treinando!</p>
          <p className="text-blue-300 text-xs">Todo dia conta.</p>
        </div>

        {/* Logout */}
        <div className="p-3 border-t border-blue-800">
          <button onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-2.5 text-blue-300 hover:bg-blue-800 hover:text-red-400 rounded-xl transition-all">
            <span>🚪</span>
            <span className="text-sm font-medium">Sair</span>
          </button>
        </div>
      </aside>

      {/* Conteúdo */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header mobile */}
        <header className="lg:hidden sticky top-0 z-10 bg-blue-900 px-4 py-3 flex items-center gap-4">
          <button onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg text-white text-xl">
            {sidebarOpen ? "✕" : "☰"}
          </button>
          <div className="flex items-center gap-2">
            <img src="/mascote.svg" alt="" className="w-8 h-auto" />
            <span className="font-black text-white text-base">
              MENOS<span className="text-orange-400">FRANGO</span>
            </span>
          </div>
        </header>

        <main className="flex-1 p-5 lg:p-8 overflow-auto">
          {title && (
            <h1 className="text-2xl font-black text-gray-900 mb-6 hidden lg:block">{title}</h1>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
