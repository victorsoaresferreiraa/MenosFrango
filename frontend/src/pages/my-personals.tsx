/**
 * Página "Meu Personal Trainer 👨‍🏫" — vista pelo Aluno
 *
 * O aluno vê aqui:
 * - Lista de personais que o acompanham
 * - Convites pendentes para aceitar
 * - Status de cada vínculo
 *
 * Acessada em: /my-personals
 */

import { useEffect } from "react";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { personalApi } from "@/lib/api";

export default function MyPersonalsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, isLoading, router]);

  // Lista de personais/convites
  const { data: personals, isLoading: loadingPersonals } = useQuery({
    queryKey: ["my-personals"],
    queryFn: () => personalApi.getMyPersonals().then((r) => r.data),
    enabled: isAuthenticated,
  });

  // Aceitar convite
  const acceptMutation = useMutation({
    mutationFn: (linkId: string) => personalApi.acceptInvite(linkId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["my-personals"] });
    },
  });

  if (isLoading) return null;

  const pending = (personals || []).filter((p: any) => p.status === "pendente");
  const active  = (personals || []).filter((p: any) => p.status === "ativo");

  return (
    <Layout title="Meu Personal Trainer 👨‍🏫">

      {/* Convites pendentes */}
      {pending.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            📬 Convites Pendentes ({pending.length})
          </h2>
          <div className="space-y-3">
            {pending.map((p: any) => (
              <div
                key={p.id}
                className="card flex items-center justify-between gap-4 border-2 border-yellow-200"
              >
                <div>
                  <p className="font-semibold text-gray-900">{p.personal_name}</p>
                  <p className="text-sm text-yellow-600">
                    Quer te destrangalhar como personal! 💪
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Convidado em {new Date(p.invited_at).toLocaleDateString("pt-BR")}
                  </p>
                </div>
                <button
                  onClick={() => acceptMutation.mutate(p.id)}
                  disabled={acceptMutation.isPending}
                  className="btn-primary text-sm"
                >
                  {acceptMutation.isPending ? "Aceitando..." : "✅ Aceitar"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Personais ativos */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          👨‍🏫 Meu Personal Trainer 👨‍🏫 ({active.length})
        </h2>

        {loadingPersonals ? (
          <div className="text-center py-8 text-gray-400">Carregando...</div>
        ) : active.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-4xl mb-3">👨‍🏫</p>
            <p className="text-gray-500">Ainda sem personal? Pede pro seu treinador te convidar pelo e-mail! 🐔</p>
            <p className="text-sm text-gray-400 mt-1">
              Peça para seu personal te enviar um convite pelo e-mail.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {active.map((p: any) => (
              <div key={p.id} className="card flex items-center gap-4">
                <div className="w-11 h-11 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold text-lg">
                  {p.personal_name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{p.personal_name}</p>
                  <p className="text-sm text-green-600">✓ Ativo desde {" "}
                    {new Date(p.invited_at).toLocaleDateString("pt-BR")}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
