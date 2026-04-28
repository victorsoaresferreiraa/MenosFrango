/**
 * Página inicial — redireciona conforme o tipo de conta.
 *
 * - Aluno    → /dashboard
 * - Personal → /personal/dashboard
 * - Não logado → /login
 *
 * INSTRUÇÕES:
 * Substitua frontend/src/pages/index.tsx por este.
 */

import { useEffect } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/hooks/useAuth";
import FrangoLogo from "@/components/FrangoLogo";

export default function Home() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    // Redireciona conforme o tipo de conta
    if (user?.role === "personal") {
      router.replace("/personal/dashboard");
    } else {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, user, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-principal-cinza">
      <div className="text-center">
        <div className="text-4xl mb-4 justify-center"><FrangoLogo/></div>
        <p className="text-white">Carregando MENOSFRANGO...</p>
      </div>
    </div>
  );
}
