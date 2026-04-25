/**
 * Dashboard MENOSFRANGO — com linguagem brasileirada e motivacional.
 */

import { useEffect } from "react";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { dashboardApi } from "@/lib/api";

export default function DashboardPage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) router.replace("/login");
      else if (user?.role === "personal") router.replace("/personal/dashboard");
    }
  }, [isAuthenticated, isLoading, user, router]);

  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => dashboardApi.getSummary().then((r) => r.data),
    enabled: isAuthenticated,
  });

  const { data: graphs, isLoading: loadingGraphs } = useQuery({
    queryKey: ["dashboard-graphs"],
    queryFn: () => dashboardApi.getGraphs(30).then((r) => r.data),
    enabled: isAuthenticated,
  });

  if (isLoading || !user) return null;

  const kpis           = summary?.kpis || {};
  const recentWorkouts = summary?.recent_workouts || [];
  const volumeByGroup  = graphs?.volume_by_muscle_group || [];
  const weeklyVolume   = graphs?.weekly_volume || [];
  const maxVolume      = Math.max(...volumeByGroup.map((g: any) => g.volume), 1);
  const maxWeekly      = Math.max(...weeklyVolume.map((w: any) => w.volume), 1);

  const goalMsg: Record<string, string> = {
    cutting:    "🔥 Secando o frango!",
    bulking:    "💪 Enchendo o papo!",
    manutencao: "⚖️ Segurando a onda!",
  };

  const lvlEmoji: Record<string, string> = {
    iniciante: "🐣", intermediario: "🐔", avancado: "🦅",
  };

  return (
    <Layout title="Dashboard">

      {/* Banner de boas-vindas */}
      <div className="rounded-3xl bg-gradient-to-r from-blue-700 to-blue-900 text-white p-6 mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black">
            Eaí, {user.name?.split(" ")[0]}! {lvlEmoji[user.level || "iniciante"] || "🐔"}
          </h2>
          <p className="text-blue-200 text-sm mt-1">
            {user.goal ? goalMsg[user.goal] : "Configure seu objetivo no perfil"} · {user.level || "configure seu nível"}
          </p>
          <p className="text-blue-300 text-xs mt-2 italic">
            "Cada série te deixa menos frango." 💪
          </p>
        </div>
        <img src="/mascote.svg" alt="" className="w-20 h-auto opacity-90 hidden sm:block" />
      </div>

      {/* Aviso perfil incompleto */}
      {(!user.weight_kg || !user.height_cm || !user.age) && (
        <div className="mb-6 p-4 bg-orange-50 border-2 border-orange-200 rounded-2xl flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🐔</span>
            <div>
              <p className="font-bold text-orange-800">Ei, seu perfil tá incompleto!</p>
              <p className="text-sm text-orange-600">Complete pra ativar os cálculos de macros e a IA completa.</p>
            </div>
          </div>
          <a href="/profile" className="btn-orange whitespace-nowrap">Completar →</a>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Treinos esta semana", value: kpis.workouts_last_7d ?? "—", emoji: "📅", color: "blue" },
          { label: "Treinos este mês", value: kpis.workouts_last_30d ?? "—", emoji: "🗓️", color: "blue" },
          { label: "Volume total (30d)", value: kpis.total_volume_last_30d_kg ? `${kpis.total_volume_last_30d_kg.toLocaleString()}kg` : "—", emoji: "⚡", color: "orange" },
          { label: "Média kcal (7d)", value: kpis.avg_daily_calories_7d ? `${kpis.avg_daily_calories_7d}kcal` : "—", emoji: "🥗", color: "green" },
        ].map(({ label, value, emoji }) => (
          <div key={label} className="card text-center">
            <p className="text-3xl mb-1">{emoji}</p>
            <p className="text-2xl font-black text-gray-900">{loadingSummary ? "..." : value}</p>
            <p className="text-xs text-gray-400 mt-1 leading-tight">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

        {/* Volume por grupo muscular */}
        <div className="card">
          <h3 className="font-black text-gray-900 mb-4">💪 Qual parte você mais treinou?</h3>
          {loadingGraphs ? (
            <div className="text-center py-8 text-gray-400">Calculando... 🤖</div>
          ) : volumeByGroup.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-4xl mb-2">🐔</p>
              <p className="text-gray-500 text-sm">Registra um treino pra ver o gráfico!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {volumeByGroup.slice(0, 8).map((g: any) => (
                <div key={g.group}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-700 capitalize font-semibold">{g.group}</span>
                    <span className="text-gray-400 text-xs">{g.volume.toLocaleString()}kg · {g.count}x</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2.5">
                    <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-700"
                      style={{ width: `${(g.volume / maxVolume) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Evolução semanal */}
        <div className="card">
          <h3 className="font-black text-gray-900 mb-4">📈 Evolução semanal de volume</h3>
          {loadingGraphs ? (
            <div className="text-center py-8 text-gray-400">Carregando... 🤖</div>
          ) : weeklyVolume.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-4xl mb-2">📈</p>
              <p className="text-gray-500 text-sm">Treina mais semanas pra ver a evolução!</p>
            </div>
          ) : (
            <>
              <div className="flex items-end gap-2 h-36">
                {weeklyVolume.map((w: any) => (
                  <div key={w.week} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full flex flex-col justify-end" style={{ height: "110px" }}>
                      <div className="w-full bg-blue-600 hover:bg-orange-500 rounded-t-lg transition-colors cursor-default"
                        style={{ height: `${Math.max((w.volume / maxWeekly) * 100, 5)}%` }}
                        title={`${w.volume.toLocaleString()}kg · ${w.workouts} treinos`} />
                    </div>
                    <span className="text-xs text-gray-400">{w.week}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-400 text-center mt-2">Passe o mouse em cada barra para ver o volume</p>
            </>
          )}
        </div>
      </div>

      {/* Treinos recentes */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-black text-gray-900">🏋️ Últimos treinos</h3>
          <a href="/workouts" className="text-sm text-blue-700 font-bold hover:underline">Ver todos →</a>
        </div>
        {recentWorkouts.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-5xl mb-3">🐔</p>
            <p className="text-gray-500 font-medium">Ainda sem treinos. Que frango! 😄</p>
            <a href="/workouts" className="btn-primary mt-4 inline-block">Registrar primeiro treino →</a>
          </div>
        ) : (
          <div className="space-y-2">
            {recentWorkouts.map((w: any) => (
              <div key={w.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <div>
                  <p className="font-bold text-gray-900 text-sm">{w.exercise}</p>
                  <p className="text-xs text-gray-400 capitalize">{w.muscle_group}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-black text-blue-700">{w.weight_kg}kg</p>
                  <p className="text-xs text-gray-400">{w.sets}×{w.reps} · {new Date(w.workout_date).toLocaleDateString("pt-BR")}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
