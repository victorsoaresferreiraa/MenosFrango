/**
 * Dashboard MENOSFRANGO — com linguagem brasileirada e motivacional.
 * Agora com Dark Mode ativado! 🌙
 */

import { useEffect } from "react";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { dashboardApi } from "@/lib/api";

// 🌟 IMPORTAÇÃO DO FUNDO ANIMADO AQUI
import { Particles } from "@/components/ui/particles"; 
import { Calendar, Calendar2, Calendar2Day, Calendar2DayFill, CalendarCheck, CalendarFill, ForkKnife, Lightning, Thunderbolt, ThunderboltFill } from "react-bootstrap-icons";

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
    cutting:    "Secando o frango!",
    bulking:    "Enchendo o papo!",
    manutencao: "Segurando a onda!",
  };

  const lvlEmoji: Record<string, string> = {
    iniciante: "🐣", intermediario: "🐔", avancado: "🦅",
  };

  return (
    <Layout title="Dashboard">
      
      {/* ========================================== */}
      {/* 1. FUNDO ANIMADO: Preso atrás de tudo (z-0) */}
      {/* ========================================== */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40">
        <Particles className="w-full h-full" />
      </div>

      {/* ========================================== */}
      {/* 2. CONTEÚDO DO DASHBOARD: Na frente (z-10) */}
      {/* ========================================== */}
      <div className="relative z-10 w-full h-full pb-10">
        
        {/* Banner de boas-vindas */}
        <div className="rounded-3xl bg-principal-cinzaclaro dark:bg-principal-cinza border border-frango-base text-white p-6 mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-black">
              Eaí, {user.name?.split(" ")[0]}! {lvlEmoji[user.level || "iniciante"] || ""}
            </h2>
            <p className="text-blue-200 dark:text-gray-300 text-sm mt-1">
              {user.goal ? goalMsg[user.goal] : "Configure seu objetivo no perfil"} · {user.level || "configure seu nível"}
            </p>
            <p className="text-black dark:text-gray-400 text-xs mt-2 italic">
              "Cada série te deixa menos frango." 💪
            </p>
          </div>
          <img src="/workinout.gif" alt="" className="w-20 h-auto opacity-90 hidden sm:block" />
        </div>

        {/* Aviso perfil incompleto */}
        {(!user.weight_kg || !user.height_cm || !user.age) && (
          <div className="mb-6 p-4 bg-principal-cinzaclaro dark:bg-principal-cinza rounded-2xl flex items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🐔 </span>
              <div>
                <p className="font-bold text-orange-800 dark:text-orange-300">Ei, seu perfil tá incompleto!</p>
                <p className="text-sm text-orange-600 dark:text-orange-400">Complete pra ativar os cálculos de macros e a IA completa.</p>
              </div>
            </div>
            <a href="/profile" className="btn-orange whitespace-nowrap">Completar →</a>
          </div>
        )}

        {/* KPIs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[
            { label: "Treinos esta semana", value: kpis.workouts_last_7d ?? "—", emoji: <CalendarCheck/>, color: "blue" },
            { label: "Treinos este mês", value: kpis.workouts_last_30d ?? "—", emoji: <Calendar2Day/>, color: "blue" },
            { label: "Volume total (30d)", value: kpis.total_volume_last_30d_kg ? `${kpis.total_volume_last_30d_kg.toLocaleString()}kg` : "—", emoji: <Lightning/>, color: "orange" },
            { label: "Média kcal (7d)", value: kpis.avg_daily_calories_7d ? `${kpis.avg_daily_calories_7d}kcal` : "—", emoji: <ForkKnife/>, color: "green" },
          ].map(({ label, value, emoji }) => (
            <div key={label} className="card text-center bg-principal-cinzaclaro dark:bg-principal-cinza shadow-sm border border-frango-base">
              <p className="text-4xl flex text-frango-base justify-center mb-3">{emoji}</p>
              <p className="text-2xl font-black text-gray-900 dark:text-white">{loadingSummary ? "..." : value}</p>
              <p className="text-xs text-principal-cinzaescuro dark:text-principal-cinzaClaro mt-1 leading-tight">{label}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

          {/* Volume por grupo muscular */}
          <div className="card bg-principal-cinzaclaro dark:bg-principal-cinza shadow-sm border border-frango-base">
            <h3 className="font-black text-frango-base mb-4">Qual parte você mais treinou?</h3>
            {loadingGraphs ? (
              <div className="text-center py-8 text-gray-400 dark:text-gray-500">Calculando... 🤖</div>
            ) : volumeByGroup.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-4xl mb-2">🐔</p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Registra um treino pra ver o gráfico!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {volumeByGroup.slice(0, 8).map((g: any) => (
                  <div key={g.group}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-black dark:text-white capitalize font-semibold">{g.group}</span>
                      <span className="text-black dark:text-white text-xs">{g.volume.toLocaleString()}kg · {g.count}x</span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-gray-700 rounded-full h-2.5">
                      <div className="bg-frango-base hover:bg-frango-escuro h-2.5 rounded-full transition-all duration-700"
                        style={{ width: `${(g.volume / maxVolume) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Evolução semanal */}
          <div className="card bg-principal-cinzaclaro dark:bg-principal-cinza shadow-sm border border-frango-base">
            <h3 className="font-black text-frango-base mb-4">Evolução semanal de volume</h3>
            {loadingGraphs ? (
              <div className="text-center py-8 text-gray-400 dark:text-gray-500">Carregando... 🤖</div>
            ) : weeklyVolume.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-4xl mb-2">📈</p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Treina mais semanas pra ver a evolução!</p>
              </div>
            ) : (
              <>
                <div className="flex items-end gap-2 h-36">
                  {weeklyVolume.map((w: any) => (
                    <div key={w.week} className="flex-1 flex flex-col items-center gap-1">
                      <div className="w-full flex flex-col justify-end" style={{ height: "110px" }}>
                        <div className="w-full bg-blue-600 bg-frango-base hover:bg-frango-escuro rounded-t-lg transition-colors cursor-default"
                          style={{ height: `${Math.max((w.volume / maxWeekly) * 100, 5)}%` }}
                          title={`${w.volume.toLocaleString()}kg · ${w.workouts} treinos`} />
                      </div>
                      <span className="text-xs font-bold text-principal-pretoClaro dark:text-principal-cinza2">{w.week}</span>
                    </div>
                  ))}
                </div>
                <p className="text-xs dark:text-white text-black text-center mt-2">Passe o mouse em cada barra para ver o volume</p>
              </>
            )}
          </div>
        </div>

        {/* Treinos recentes */}
        <div className="card bg-principal-cinzaclaro dark:bg-principal-cinza shadow-sm border border-frango-base">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-black text-gray-900 dark:text-white">Últimos treinos</h3>
            <a href="/workouts" className="text-sm text-frango-base font-bold hover:underline">Ver todos →</a>
          </div>
          {recentWorkouts.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-5xl mb-3">🐔</p>
              <p className="text-gray-500 dark:text-gray-400 font-medium">Ainda sem treinos. Que frango! 😄</p>
              <a href="/workouts" className="btn-primary mt-4 inline-block">Registrar primeiro treino →</a>
            </div>
          ) : (
            <div className="space-y-2">
              {recentWorkouts.map((w: any) => (
                <div key={w.id} className="flex items-center justify-between p-3 bg-principal-cinza2 dark:bg-principal-cinza3 rounded-xl">
                  <div>
                    <p className="text-black dark:text-white text-sm">{w.exercise}</p>
                    <p className="text-xs text-principal-pretoClaro dark:text-principal-cinza2 capitalize">{w.muscle_group}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-black text-frango-base">{w.weight_kg}kg</p>
                    <p className="text-xs ttext-principal-pretoClaro dark:text-principal-cinza2">{w.sets}×{w.reps} · {new Date(w.workout_date).toLocaleDateString("pt-BR")}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </Layout>
  );
}