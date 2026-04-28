/**
 * Perfil do Personal Trainer
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useMutation } from "@tanstack/react-query";
import PersonalLayout from "@/components/layout/PersonalLayout";
import { useAuth } from "@/hooks/useAuth";
import { usersApi } from "@/lib/api";

export default function PersonalProfilePage() {
  const { isAuthenticated, isLoading, user, setUser } = useAuth();
  const router = useRouter();
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({ name: "", bio: "" });

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) router.replace("/login");
      else if (user?.role !== "personal") router.replace("/dashboard");
    }
    if (user) setForm({ name: user.name || "", bio: user.bio || "" });
  }, [isAuthenticated, isLoading, user, router]);

  const mutation = useMutation({
    mutationFn: (data: any) => usersApi.updateMe(data),
    onSuccess: (res) => {
      setUser(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    },
  });

  if (isLoading || !user) return null;

  return (
    <PersonalLayout title="Meu Perfil">
      <div className="max-w-lg">
        {saved && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            ✅ Perfil atualizado!
          </div>
        )}
        <form onSubmit={(e) => { e.preventDefault(); mutation.mutate(form); }} className="space-y-4">
          <div className="card">
            <h3 className="font-semibold mb-4">Dados do Personal</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required minLength={2} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bio profissional</label>
                <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  rows={4} maxLength={500} className="input-field resize-none"
                  placeholder="Especialidades, certificações, metodologia de trabalho..." />
                <p className="text-xs text-gray-400 mt-1">{form.bio.length}/500</p>
              </div>
            </div>
          </div>
          <div className="card bg-gray-50">
            <p className="text-sm text-gray-600"><span className="font-medium">E-mail:</span> {user.email}</p>
            <p className="text-sm text-gray-600 mt-1"><span className="font-medium">Conta:</span> Personal Trainer</p>
          </div>
          <button type="submit" disabled={mutation.isPending} className="btn-primary w-full py-3">
            {mutation.isPending ? "Salvando..." : "Salvar Perfil"}
          </button>
        </form>
      </div>
    </PersonalLayout>
  );
}
