/**
 * Layout do Personal Trainer — MENOSFRANGO (verde para diferenciar)
 */

import { ReactNode, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { href: "/personal/dashboard", label: "Meus Alunos",  emoji: "👥" },
  { href: "/personal/profile",   label: "Meu Perfil",   emoji: "👤" },
];

export default function PersonalLayout({ children, title }: { children: ReactNode; title?: string }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)} />
      )}

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
              <span className="text-xs bg-orange-500 text-white px-2 py-0.5 rounded-full font-bold mt-1 inline-block">
                👨‍🏫 PERSONAL
              </span>
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="p-4 border-b border-blue-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold text-sm">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="font-semibold text-white text-sm">{user?.name}</p>
              <p className="text-orange-300 text-xs">Personal Trainer</p>
            </div>
          </div>
        </div>

        <nav className="p-3 space-y-0.5 flex-1">
          {NAV_ITEMS.map(({ href, label, emoji }) => {
            const isActive = router.pathname.startsWith(href);
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all ${
                  isActive ? "bg-orange-500 text-white font-bold" : "text-blue-200 hover:bg-blue-800 hover:text-white"
                }`}
                onClick={() => setSidebarOpen(false)}>
                <span>{emoji}</span>
                <span className="text-sm font-medium">{label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mx-3 mb-3 p-3 bg-blue-800 rounded-xl text-center">
          <p className="text-xl">💪</p>
          <p className="text-white text-xs font-bold mt-1">Destrangalhe seus alunos!</p>
        </div>

        <div className="p-3 border-t border-blue-800">
          <button onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-2.5 text-blue-300 hover:bg-blue-800 hover:text-red-400 rounded-xl transition-all">
            <span>🚪</span>
            <span className="text-sm font-medium">Sair</span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="lg:hidden sticky top-0 z-10 bg-blue-900 px-4 py-3 flex items-center gap-4">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-white text-xl">
            {sidebarOpen ? "✕" : "☰"}
          </button>
          <span className="font-black text-white">MENOS<span className="text-orange-400">FRANGO</span></span>
          <span className="text-xs bg-orange-500 text-white px-2 py-0.5 rounded-full">Personal</span>
        </header>
        <main className="flex-1 p-5 lg:p-8 overflow-auto">
          {title && <h1 className="text-2xl font-black text-gray-900 mb-6 hidden lg:block">{title}</h1>}
          {children}
        </main>
      </div>
    </div>
  );
}
