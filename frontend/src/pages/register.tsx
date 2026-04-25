/**
 * Página de Cadastro — MENOSFRANGO
 */

import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { AxiosError } from "axios";

type Role = "aluno" | "personal";

export default function RegisterPage() {
  const [name,     setName]     = useState("");
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [role,     setRole]     = useState<Role>("aluno");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(name, email, password, role);
      router.push(role === "personal" ? "/personal/dashboard" : "/dashboard");
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail: string }>;
      setError(axiosErr.response?.data?.detail || "Deu ruim! Tenta de novo 🐔");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 via-blue-800 to-blue-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <img src="/mascote.svg" alt="MENOSFRANGO" className="w-28 h-auto mx-auto mb-4 drop-shadow-xl" />
          <h1 className="text-4xl font-black text-white tracking-tight">
            MENOS<span className="text-orange-400">FRANGO</span>
          </h1>
          <p className="text-blue-200 mt-2 text-sm">Chega de ser frango. Começa agora! 💪</p>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Criar conta gratuita</h2>
          <p className="text-gray-400 text-sm mb-6">Zero desculpa. Zero frango. 🐔🤖</p>

          {/* Escolha do tipo */}
          <div className="mb-6">
            <p className="text-sm font-bold text-gray-700 mb-3">Eu sou...</p>
            <div className="grid grid-cols-2 gap-3">
              <button type="button" onClick={() => setRole("aluno")}
                className={`p-4 rounded-2xl border-2 text-left transition-all ${
                  role === "aluno" ? "border-blue-600 bg-blue-50" : "border-slate-200 hover:border-slate-300"
                }`}>
                <div className="text-2xl mb-1">🏃</div>
                <div className="font-bold text-gray-900 text-sm">Aluno</div>
                <div className="text-xs text-gray-500 mt-1">Quero parar de ser frango</div>
              </button>
              <button type="button" onClick={() => setRole("personal")}
                className={`p-4 rounded-2xl border-2 text-left transition-all ${
                  role === "personal" ? "border-orange-500 bg-orange-50" : "border-slate-200 hover:border-slate-300"
                }`}>
                <div className="text-2xl mb-1">👨‍🏫</div>
                <div className="font-bold text-gray-900 text-sm">Personal</div>
                <div className="text-xs text-gray-500 mt-1">Quero destrangalhar meus alunos</div>
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Seu nome</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                required minLength={2} className="input-field" placeholder="Como te chamam na academia?" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">E-mail</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                required className="input-field" placeholder="seu@email.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Senha</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                required minLength={8} className="input-field" placeholder="Mínimo 8 caracteres" />
            </div>
            <button type="submit" disabled={loading}
              className={`w-full py-3 text-white font-black rounded-xl text-base active:scale-95 transition-all disabled:opacity-50 ${
                role === "personal" ? "bg-orange-500 hover:bg-orange-600" : "bg-blue-700 hover:bg-blue-800"
              }`}>
              {loading ? "Criando..." : `CRIAR CONTA COMO ${role === "personal" ? "PERSONAL 👨‍🏫" : "ALUNO 🏃"}`}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-gray-500">
            Já tem conta?{" "}
            <Link href="/login" className="text-blue-700 font-bold hover:underline">Entrar</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
