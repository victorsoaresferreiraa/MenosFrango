/**
 * Página de Login — MENOSFRANGO
 */

import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/hooks/useAuth";
import { AxiosError } from "axios";

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
    <div className="min-h-screen bg-gradient-to-br from-blue-700 via-blue-800 to-blue-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Mascote + nome */}
        <div className="text-center mb-8">
          <img src="/mascote.svg" alt="MENOSFRANGO mascote" className="w-32 h-auto mx-auto mb-4 drop-shadow-xl" />
          <h1 className="text-4xl font-black text-white tracking-tight">
            MENOS<span className="text-orange-400">FRANGO</span>
          </h1>
          <p className="text-blue-200 mt-2 text-sm font-medium">
            Treino inteligente, resultado de verdade 🤖💪
          </p>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Bora entrar!</h2>
          <p className="text-gray-400 text-sm mb-6">Que bom te ver de volta 🐔</p>

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
                required className="input-field" placeholder="seu@email.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Senha</label>
              <input type="password" value={password}
                onChange={(e) => setPassword(e.target.value)}
                required className="input-field" placeholder="••••••••" />
            </div>
            <button type="submit" disabled={loading} className="w-full py-3 bg-blue-700 text-white font-black rounded-xl hover:bg-blue-800 active:scale-95 transition-all text-base disabled:opacity-50">
              {loading ? "Entrando..." : "ENTRAR 🚀"}
            </button>
          </form>

          <div className="mt-6 p-4 bg-slate-50 rounded-xl text-xs text-gray-500">
            <p className="font-bold mb-2">🐔 Usuários demo:</p>
            <p>Aluno: <strong>demo@menosfrango.ai</strong> / 12345678</p>
            <p>Personal: <strong>personal@menosfrango.ai</strong> / 12345678</p>
          </div>

          <p className="mt-5 text-center text-sm text-gray-500">
            Ainda é um frango sem conta?{" "}
            <Link href="/register" className="text-blue-700 font-bold hover:underline">
              Cria agora
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
