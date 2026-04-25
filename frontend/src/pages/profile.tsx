/**
 * Página de Perfil do Usuário
 * Permite editar dados pessoais: nome, peso, altura, idade, objetivo, nível e bio.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { usersApi } from "@/lib/api";
import { AxiosError } from "axios";

export default function ProfilePage() {
  const { isAuthenticated, isLoading, user, setUser } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "", height_cm: "", weight_kg: "", age: "",
    goal: "manutencao", level: "iniciante", bio: "",
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
    if (user) {
      setForm({
        name: user.name || "",
        height_cm: user.height_cm?.toString() || "",
        weight_kg: user.weight_kg?.toString() || "",
        age: user.age?.toString() || "",
        goal: user.goal || "manutencao",
        level: user.level || "iniciante",
        bio: user.bio || "",
      });
    }
  }, [isAuthenticated, isLoading, user, router]);

  const mutation = useMutation({
    mutationFn: (data: any) => usersApi.updateMe(data),
    onSuccess: (res) => {
      setUser(res.data);
      setSaved(true);
      qc.invalidateQueries({ queryKey: ["macro-goals"] });
      setTimeout(() => setSaved(false), 3000);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Erro ao salvar.");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    mutation.mutate({
      name: form.name,
      height_cm: form.height_cm ? Number(form.height_cm) : undefined,
      weight_kg: form.weight_kg ? Number(form.weight_kg) : undefined,
      age: form.age ? Number(form.age) : undefined,
      goal: form.goal,
      level: form.level,
      bio: form.bio || undefined,
    });
  };

  if (isLoading) return null;

  return (
    <Layout title="Meu Perfil 🐔">
      <div className="max-w-2xl">
        {saved && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            ✅ Perfil atualizado! Menos frango que antes. ✅
          </div>
        )}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dados pessoais */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">👤 Dados Pessoais</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome completo</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required minLength={2} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Peso (kg)</label>
                <input type="number" min={30} max={300} step={0.1} value={form.weight_kg}
                  onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Altura (cm)</label>
                <input type="number" min={100} max={250} value={form.height_cm}
                  onChange={(e) => setForm({ ...form, height_cm: e.target.value })} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Idade</label>
                <input type="number" min={10} max={100} value={form.age}
                  onChange={(e) => setForm({ ...form, age: e.target.value })} className="input-field" />
              </div>
            </div>
          </div>

          {/* Objetivo e nível */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">🎯 Objetivo e Nível</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo</label>
                <select value={form.goal} onChange={(e) => setForm({ ...form, goal: e.target.value })} className="input-field">
                  <option value="cutting">Cutting — perder gordura</option>
                  <option value="bulking">Bulking — ganhar massa</option>
                  <option value="manutencao">Manutenção</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nível</label>
                <select value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })} className="input-field">
                  <option value="iniciante">Iniciante</option>
                  <option value="intermediario">Intermediário</option>
                  <option value="avancado">Avançado</option>
                </select>
              </div>
            </div>
          </div>

          {/* Bio */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">📝 Bio (visível para seu personal)</h3>
            <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })}
              rows={3} maxLength={500} className="input-field resize-none"
              placeholder="Conte um pouco sobre você, seus objetivos, limitações..." />
            <p className="text-xs text-gray-400 mt-1">{form.bio.length}/500 caracteres</p>
          </div>

          {/* Info da conta */}
          <div className="card bg-gray-50">
            <h3 className="font-semibold text-gray-700 mb-3">ℹ️ Informações da Conta</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium">E-mail:</span> {user?.email}</p>
              <p><span className="font-medium">Tipo de conta:</span> {user?.role === "personal" ? "Personal Trainer" : "Aluno"}</p>
            </div>
          </div>

          <button type="submit" disabled={mutation.isPending} className="btn-primary w-full py-3 text-base">
            {mutation.isPending ? "Salvando..." : "SALVAR PERFIL 💾"}
          </button>
        </form>
      </div>
    </Layout>
  );
}
