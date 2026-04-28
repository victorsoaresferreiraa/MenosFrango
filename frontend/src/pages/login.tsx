/**
 * Página de Login — MENOSFRANGO
 */

import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import FrangoLogo from "@/components/FrangoLogo"
import { useAuth } from "@/hooks/useAuth";
import { AxiosError } from "axios";
import { Particles } from "@/components/ui/particles";

export default function LoginPage() {
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const { login } = useAuth();
  const router    = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail: string }>;
      setError(axiosErr.response?.data?.detail || "E-mail ou senha inválidos. Tenta de novo! 🐔");
    } finally {
      setLoading(false);
    }
  };

 return (
    // 1. FUNDO GERAL: Adicionado bg-slate-900 para o texto branco aparecer, e overflow-hidden para a partícula não criar barra de rolagem
    <div className="min-h-screen flex items-center justify-center p-4 relative bg-slate-900 overflow-hidden">

      <div className="absolute inset-0 z-0 pointer-events-none">
        <Particles className="w-full h-full" />
      </div>

      <div className="w-full max-w-md relative z-10">
        

        <div className="text-center mb-8">
          <FrangoLogo  className="w-32 h-auto mx-auto mb-4 drop-shadow-xl" />
          <h1 className="text-4xl font-black text-white tracking-tight">
            MENOS<span className="text-orange-400">FRANGO</span>
          </h1>
          <p className="text-blue-200 mt-2 text-sm font-medium">
            Treino inteligente, resultado de verdade 
          </p>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h2 className="text-xl font-bold text-orange-400 mb-1">BORA ENTRAR?</h2>
          <p className="text-gray-400 text-sm mb-6">Que bom te ver de volta </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">E-mail</label>
              <input type="email" value={email}
                onChange={(e) => setEmail(e.target.value)}
                required className="input-field focus:ring-orange-400" placeholder="seu@email.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Senha</label>
              <input type="password" value={password}
                onChange={(e) => setPassword(e.target.value)}
                required className="input-field focus:ring-orange-400" placeholder="••••••••" />
            </div>
            <button type="submit" disabled={loading} className="w-full py-3 bg-orange-400 text-white font-black rounded-xl hover:bg-orange-600 active:scale-95 transition-all text-base disabled:opacity-50">
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>

          <div className="mt-6 p-4 bg-slate-50 rounded-xl text-xs text-gray-500">
            <p className="flex text-orange-400 font-bold mb-2">Usuários demo:</p>
            <p>Aluno: <strong>demo@menosfrango.ai</strong> / 12345678</p>
            <p>Personal: <strong>personal@menosfrango.ai</strong> / 12345678</p>
          </div>

          <p className="mt-5 text-center text-sm text-gray-500">
            Ainda é um frango sem conta?{" "}
            <Link href="/register" className="text-orange-400 font-bold hover:underline">
              Cria agora
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}