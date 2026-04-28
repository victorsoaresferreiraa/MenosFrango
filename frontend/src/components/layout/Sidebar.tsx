/**
 * Sidebar MENOSFRANGO — Identidade visual e navegação.
 */

import Link from "next/link";
import { useRouter } from "next/router";
import { DoorClosed, DoorClosedFill, ForkKnife, GraphUp, Paperclip, PersonCircle, PersonRaisedHand, Robot } from 'react-bootstrap-icons'
import { Camera, DumbbellIcon } from 'lucide-react';
import FrangoLogo from "@/components/FrangoLogo";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { href: "/dashboard",    label: "Dashboard",    emoji: <GraphUp size={20}/>, tip: "Visão geral" },
  { href: "/workouts",     label: "Treinos",      emoji: <DumbbellIcon size={20}/>, className: "text-xs", tip: "Seus treinos" },
  { href: "/nutrition",    label: "Nutrição",     emoji: <ForkKnife size={20}/>, tip: "O que comeu" },
  { href: "/photos",       label: "Progresso",    emoji: <Camera size={20}/>, tip: "Fotos" },
  { href: "/ai",           label: "IA Frango",    emoji: <Robot size={20}/>, tip: "Planos com IA" },
  { href: "/reports",      label: "Relatórios",   emoji: <Paperclip size={20}/>, tip: "PDF mensal" },
  { href: "/my-personals", label: "Meu Personal", emoji: <PersonRaisedHand size={20}/>, tip: "Personal trainer" },
  { href: "/profile",      label: "Meu Perfil",   emoji: <PersonCircle size={20}/>, tip: "Configurações" },
];

const MOTIVATIONAL = [
  "Bora, sem desculpa! 💪",
  "Frango é quem não treina! 🐔",
  "Hoje é dia de ser menos frango!",
  "A IA tá do seu lado! 🤖",
  "Consistência vence talento! 🔥",
  "Menos conversa, mais treino!",
];

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export default function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const phrase = MOTIVATIONAL[Math.floor(Math.random() * MOTIVATIONAL.length)];

  return (
    <>
      {/* Overlay para Mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-frango-base bg-opacity-60 z-20 lg:hidden"
          onClick={() => setIsOpen(false)} 
        />
      )}

      {/* Navegação Lateral */}
      <aside className={`fixed inset-y-0 left-0 w-64 bg-principal-cinzaClaro dark:bg-principal-cinza z-30 flex flex-col transform transition-transform duration-300 lg:translate-x-0 lg:static ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}>
        {/* Logo */}
        <div className="p-5">
          <div className="flex items-center gap-3">
            <FrangoLogo className="w-16 h-16 drop-shadow-xl hidden sm:block hover:scale-110 transition-transform" />
            <div>
              <p className="font-black text-principal-cinza dark:text-white text-lg leading-none">
                MENOS<span className="text-orange-400">FRANGO</span>
              </p>
              <p className="text-principal-cinza dark:text-white text-xs mt-0.5">Treino com tecnologia</p>
            </div>
          </div>
        </div>


        {/* Nav */}
        <nav className="p-3 space-y-0.5 flex-1 overflow-y-auto">
          {NAV_ITEMS.map(({ href, label, emoji }) => {
            const isActive = router.pathname === href || (href !== "/" && router.pathname.startsWith(href));
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-150 ${
                  isActive
                    ? "bg-frango-base text-principal-cinza dark:text-white font-bold"
                    : "text-principal-cinza dark:text-white  hover:bg-frango-base hover:text-white"
                }`}
                onClick={() => setIsOpen(false)}>
                <span className="text-base">{emoji}</span>
                <span className="text-sm font-medium">{label}</span>
                {isActive && <span className="ml-auto text-xs">←</span>}
              </Link>
            );
          })}
        </nav>

        {/* Info usuário */}
        <div className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-frango-base flex items-center justify-center text-white font-bold text-sm">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-principal-cinza dark:text-white text-sm truncate">{user?.name}</p>
              <span className="text-xs text-frango-base capitalize">{user?.role || "aluno"}</span>
            </div>
          </div>
          <p className="text-frango-escuro text-xs mt-2 italic">{phrase}</p>
        </div>
        {/* Logout */}
        <div className="p-3">
          <button onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-2.5 text-principal-vermelho hover:bg-principal-vermelhoHover hover:text-white rounded-xl transition-all">
            <span><DoorClosedFill/></span>
            <span className="text-sm font-medium">Sair</span>
          </button>
        </div>
      </aside>
    </>
  );
}