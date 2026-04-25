/**
 * Relatórios — MENOSFRANGO
 * Gera um PDF mensal com o resumo de treinos e nutrição.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useMutation } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { reportsApi } from "@/lib/api";

export default function ReportsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const now = new Date();
  const [year, setYear]   = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [msg, setMsg]     = useState("");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, isLoading, router]);

  const mutation = useMutation({
    mutationFn: () => reportsApi.generateMonthly({ year, month }),
    onSuccess: () => {
      setMsg("🤖 Relatório na fila! O franguinho está gerando seu PDF. Você vai receber por e-mail em instantes.");
    },
    onError: () => {
      setMsg("❌ Deu ruim! Tenta de novo.");
    },
  });

  const MONTHS = [
    "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
  ];

  if (isLoading) return null;

  return (
    <Layout title="Relatórios 📄">
      <div className="max-w-lg">

        {/* Explicação */}
        <div className="card mb-6 border-2 border-blue-100">
          <div className="flex items-start gap-4">
            <img src="/mascote.svg" alt="" className="w-20 h-auto flex-shrink-0" />
            <div>
              <h3 className="font-black text-gray-900 text-lg">PDF Mensal do Frango</h3>
              <p className="text-gray-500 text-sm mt-1">
                O MENOSFRANGO gera um relatório completo em PDF com seus treinos, nutrição, volume acumulado e recomendações da IA.
              </p>
              <p className="text-gray-400 text-xs mt-2">
                📩 Enviado por e-mail assim que ficar pronto (pode levar alguns minutinhos).
              </p>
            </div>
          </div>
        </div>

        {/* Seletor */}
        <div className="card mb-6">
          <h3 className="font-black text-gray-900 mb-4">Escolha o mês 📅</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Mês</label>
              <select value={month} onChange={(e) => setMonth(Number(e.target.value))} className="input-field">
                {MONTHS.map((m, i) => (
                  <option key={i + 1} value={i + 1}>{m}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Ano</label>
              <select value={year} onChange={(e) => setYear(Number(e.target.value))} className="input-field">
                {[2024, 2025, 2026].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>

          {msg && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-xl text-blue-700 text-sm">
              {msg}
            </div>
          )}

          <button
            onClick={() => { setMsg(""); mutation.mutate(); }}
            disabled={mutation.isPending}
            className="btn-primary w-full py-3 font-black mt-4"
          >
            {mutation.isPending
              ? "🤖 Gerando PDF..."
              : `📄 Gerar Relatório de ${MONTHS[month - 1]} ${year}`}
          </button>
        </div>

        {/* O que tem no relatório */}
        <div className="card">
          <h3 className="font-black text-gray-900 mb-4">📋 O que tem no relatório?</h3>
          <div className="space-y-3">
            {[
              { emoji: "👤", title: "Perfil completo", desc: "Seus dados, objetivo e nível" },
              { emoji: "🏋️", title: "Treinos do mês", desc: "Total de sessões, volume acumulado e exercícios" },
              { emoji: "🥗", title: "Nutrição", desc: "Médias diárias de calorias e macros" },
              { emoji: "🤖", title: "Recomendações da IA", desc: "Planos e análises gerados no período" },
              { emoji: "📊", title: "Gráficos", desc: "Volume por grupo muscular e evolução semanal" },
            ].map(({ emoji, title, desc }) => (
              <div key={title} className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <span className="text-2xl">{emoji}</span>
                <div>
                  <p className="font-bold text-gray-800 text-sm">{title}</p>
                  <p className="text-xs text-gray-500">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
