/**
 * Dashboard do Personal Trainer — MENOSFRANGO
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import PersonalLayout from "@/components/layout/PersonalLayout";
import { useAuth } from "@/hooks/useAuth";
import { personalApi } from "@/lib/api";

export default function PersonalDashboardPage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();

  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteNotes, setInviteNotes] = useState("");
  const [inviteMsg, setInviteMsg]     = useState("");

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) router.replace("/login");
      else if (user?.role !== "personal") router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, user, router]);

  const { data, isLoading: loadingData } = useQuery({
    queryKey: ["personal-dashboard"],
    queryFn: () => personalApi.getDashboard().then((r) => r.data),
    enabled: isAuthenticated && user?.role === "personal",
  });

  const inviteMutation = useMutation({
    mutationFn: (payload: { client_email: string; notes?: string }) =>
      personalApi.inviteClient(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["personal-dashboard"] });
      setInviteMsg("✅ Convite enviado! O aluno vai aparecer aqui quando aceitar.");
      setInviteEmail(""); setInviteNotes("");
      setTimeout(() => { setShowInvite(false); setInviteMsg(""); }, 3000);
    },
    onError: (err: any) => {
      setInviteMsg(`❌ ${err.response?.data?.detail || "Deu ruim! Tenta de novo."}`);
    },
  });

  if (isLoading || !user) return null;

  const clients = data?.clients || [];
  const statusStyle: Record<string, string> = {
    ativo:    "bg-green-100 text-green-700",
    pendente: "bg-yellow-100 text-yellow-700",
    inativo:  "bg-gray-100 text-gray-500",
  };
  const statusLabel: Record<string, string> = {
    ativo: "✅ Ativo", pendente: "⏳ Pendente", inativo: "❌ Inativo",
  };

  return (
    <PersonalLayout title="Meus Alunos">

      {/* KPIs */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card text-center">
          <p className="text-3xl font-black text-gray-900">{data?.total_clients ?? "—"}</p>
          <p className="text-sm text-gray-500 mt-1">Total de alunos</p>
        </div>
        <div className="card text-center border-2 border-green-200">
          <p className="text-3xl font-black text-green-600">{data?.active_clients ?? "—"}</p>
          <p className="text-sm text-gray-500 mt-1">Ativos 💪</p>
        </div>
        <div className="card text-center border-2 border-yellow-200">
          <p className="text-3xl font-black text-yellow-500">{data?.pending_clients ?? "—"}</p>
          <p className="text-sm text-gray-500 mt-1">Aguardando 📩</p>
        </div>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-black text-gray-900 text-lg">Sua galera 👥</h2>
        <button onClick={() => setShowInvite(!showInvite)} className="btn-orange">
          {showInvite ? "Cancelar" : "📩 Convidar Aluno"}
        </button>
      </div>

      {/* Formulário convite */}
      {showInvite && (
        <div className="card mb-6 border-2 border-orange-200">
          <h3 className="font-black text-gray-900 mb-1">📩 Convidar novo aluno</h3>
          <p className="text-sm text-gray-500 mb-4">O aluno precisa ter uma conta no MENOSFRANGO como "Aluno".</p>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">E-mail do aluno *</label>
              <input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)}
                className="input-field" placeholder="frango@email.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Anotação inicial (opcional)</label>
              <input type="text" value={inviteNotes} onChange={(e) => setInviteNotes(e.target.value)}
                className="input-field" placeholder="ex: foco em emagrecimento, iniciante..." />
            </div>
            {inviteMsg && <p className="text-sm font-medium">{inviteMsg}</p>}
            <button disabled={!inviteEmail || inviteMutation.isPending}
              onClick={() => inviteMutation.mutate({ client_email: inviteEmail, notes: inviteNotes || undefined })}
              className="btn-orange w-full py-3 font-black">
              {inviteMutation.isPending ? "Enviando..." : "ENVIAR CONVITE 📩"}
            </button>
          </div>
        </div>
      )}

      {/* Lista de alunos */}
      {loadingData ? (
        <div className="text-center py-12 text-gray-400">Carregando seus frangos... 🐔</div>
      ) : clients.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-5xl mb-3">🐔</p>
          <p className="text-gray-500 font-bold">Você ainda não tem alunos!</p>
          <p className="text-sm text-gray-400 mt-1">Clique em "Convidar Aluno" pra começar a destrangalhar alguém.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {clients.map((c: any) => (
            <div key={c.id} className="card flex items-center justify-between gap-4 hover:border-blue-200 transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-100 flex items-center justify-center text-blue-700 font-black text-xl">
                  {c.client.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-bold text-gray-900">{c.client.name}</p>
                  <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${statusStyle[c.status]}`}>
                      {statusLabel[c.status]}
                    </span>
                    {c.client.goal && (
                      <span className="text-xs text-gray-400 capitalize">{c.client.goal}</span>
                    )}
                    {c.client.level && (
                      <span className="text-xs text-gray-400 capitalize">· {c.client.level}</span>
                    )}
                  </div>
                </div>
              </div>
              {c.status === "ativo" ? (
                <Link href={`/personal/clients/${c.client.id}`} className="btn-primary text-sm">
                  Ver aluno →
                </Link>
              ) : (
                <span className="text-xs text-gray-400 italic">Aguardando aceite...</span>
              )}
            </div>
          ))}
        </div>
      )}
    </PersonalLayout>
  );
}
