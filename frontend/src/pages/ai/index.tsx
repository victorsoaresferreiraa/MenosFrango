/**
 * Página de IA — versão melhorada com resultado formatado visualmente.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useMutation, useQuery } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { aiApi } from "@/lib/api";

type Tab = "workout" | "nutrition" | "progress" | "history";

export default function AIPage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<Tab>("workout");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, isLoading, router]);

  const [wForm, setWForm] = useState({
    goal: user?.goal || "manutencao",
    weekly_frequency: 4,
    level: user?.level || "iniciante",
    limitations: "",
  });

  const [nForm, setNForm] = useState({
    weight_kg: user?.weight_kg || 75,
    height_cm: user?.height_cm || 175,
    age: user?.age || 25,
    goal: user?.goal || "manutencao",
    activity_level: "moderado",
  });

  const workoutMutation = useMutation({
    mutationFn: (data: any) => aiApi.workoutPlan(data).then((r) => r.data),
    onSuccess: (data) => setResult({ type: "workout", data }),
  });

  const nutritionMutation = useMutation({
    mutationFn: (data: any) => aiApi.nutritionPlan(data).then((r) => r.data),
    onSuccess: (data) => setResult({ type: "nutrition", data }),
  });

  const progressMutation = useMutation({
    mutationFn: () => aiApi.analyzeProgress({ days: 30 }).then((r) => r.data),
    onSuccess: (data) => setResult({ type: "progress", data }),
  });

  const { data: history } = useQuery({
    queryKey: ["ai-history"],
    queryFn: () => aiApi.history().then((r) => r.data),
    enabled: isAuthenticated && activeTab === "history",
  });

  const isPending = workoutMutation.isPending || nutritionMutation.isPending || progressMutation.isPending;

  if (isLoading) return null;

  const TABS = [
    { key: "workout",   label: "🏋️ Treino" },
    { key: "nutrition", label: "🥗 Nutrição" },
    { key: "progress",  label: "📊 Progresso" },
    { key: "history",   label: "📋 Histórico" },
  ];

  return (
    <Layout title="IA Frango 🤖🐔">
      <div className="max-w-3xl">
        {/* Badge modo IA */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center gap-3">
          <span className="text-2xl">🤖</span>
          <div>
            <p className="text-blue-800 font-semibold">Modo A — Offline (Frango Sábio) 🐔🧠</p>
            <p className="text-blue-600 text-sm">Ciência do esporte + frango computacional. Zero custo, zero desculpa!. Zero custo, zero internet.</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {TABS.map(({ key, label }) => (
            <button key={key}
              onClick={() => { setActiveTab(key as Tab); setResult(null); }}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                activeTab === key ? "bg-blue-600 text-white" : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
              }`}>
              {label}
            </button>
          ))}
        </div>

        {/* Plano de Treino */}
        {activeTab === "workout" && (
          <div className="card mb-6">
            <h3 className="font-semibold mb-4">Parâmetros do Plano de Treino</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo</label>
                <select value={wForm.goal} onChange={(e) => setWForm({ ...wForm, goal: e.target.value })} className="input-field">
                  <option value="bulking">Bulking (ganho de massa)</option>
                  <option value="cutting">Cutting (perda de gordura)</option>
                  <option value="manutencao">Manutenção</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nível</label>
                <select value={wForm.level} onChange={(e) => setWForm({ ...wForm, level: e.target.value })} className="input-field">
                  <option value="iniciante">Iniciante</option>
                  <option value="intermediario">Intermediário</option>
                  <option value="avancado">Avançado</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dias por semana</label>
                <input type="number" min={2} max={7} value={wForm.weekly_frequency}
                  onChange={(e) => setWForm({ ...wForm, weekly_frequency: Number(e.target.value) })} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Limitações (opcional)</label>
                <input type="text" value={wForm.limitations}
                  onChange={(e) => setWForm({ ...wForm, limitations: e.target.value })}
                  className="input-field" placeholder="ex: lesão no joelho" />
              </div>
            </div>
            <button onClick={() => workoutMutation.mutate(wForm)} disabled={isPending} className="btn-primary mt-4 w-full py-3">
              {isPending ? "Gerando plano... 🤖🐔" : "🤖 GERAR PLANO DE TREINO 💪"}
            </button>
          </div>
        )}

        {/* Plano Nutricional */}
        {activeTab === "nutrition" && (
          <div className="card mb-6">
            <h3 className="font-semibold mb-4">Parâmetros do Plano Nutricional</h3>
            <div className="grid grid-cols-2 gap-4">
              {[
                { key: "weight_kg", label: "Peso (kg)", min: 30, max: 300 },
                { key: "height_cm", label: "Altura (cm)", min: 100, max: 250 },
                { key: "age", label: "Idade", min: 10, max: 100 },
              ].map(({ key, label, min, max }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input type="number" min={min} max={max} value={(nForm as any)[key]}
                    onChange={(e) => setNForm({ ...nForm, [key]: Number(e.target.value) })} className="input-field" />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo</label>
                <select value={nForm.goal} onChange={(e) => setNForm({ ...nForm, goal: e.target.value })} className="input-field">
                  <option value="bulking">Bulking</option>
                  <option value="cutting">Cutting</option>
                  <option value="manutencao">Manutenção</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Nível de Atividade</label>
                <select value={nForm.activity_level} onChange={(e) => setNForm({ ...nForm, activity_level: e.target.value })} className="input-field">
                  <option value="sedentario">Sedentário</option>
                  <option value="leve">Leve (1-3x/semana)</option>
                  <option value="moderado">Moderado (3-5x/semana)</option>
                  <option value="ativo">Ativo (6-7x/semana)</option>
                  <option value="muito_ativo">Muito Ativo (2x/dia)</option>
                </select>
              </div>
            </div>
            <button onClick={() => nutritionMutation.mutate(nForm)} disabled={isPending} className="btn-primary mt-4 w-full py-3">
              {isPending ? "Calculando... 🤖🐔" : "🤖 Gerar Plano Nutricional"}
            </button>
          </div>
        )}

        {/* Análise de Progresso */}
        {activeTab === "progress" && (
          <div className="card mb-6 text-center py-8">
            <p className="text-5xl mb-4">📊</p>
            <p className="text-gray-600 mb-2 font-medium">Análise dos últimos 30 dias</p>
            <p className="text-gray-400 text-sm mb-6">A IA analisa sua evolução de peso e volume de treino e retorna tendências e recomendações.</p>
            <button onClick={() => progressMutation.mutate()} disabled={isPending} className="btn-primary px-8 py-3">
              {isPending ? "Analisando..." : "📊 Analisar Meu Progresso"}
            </button>
          </div>
        )}

        {/* Histórico */}
        {activeTab === "history" && (
          <div className="space-y-3">
            {(history || []).length === 0 ? (
              <div className="card text-center py-8 text-gray-400">
                <p className="text-3xl mb-2">📋</p>
                <p>Nenhuma recomendação ainda.</p>
              </div>
            ) : (history || []).map((rec: any) => (
              <div key={rec.id} className="card">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 capitalize">
                    {rec.type === "workout_plan" ? "🏋️ Plano de Treino" :
                     rec.type === "nutrition_plan" ? "🥗 Plano Nutricional" : "📊 Análise de Progresso"}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(rec.created_at).toLocaleDateString("pt-BR")}
                    {rec.payload?.generated_by_personal && (
                      <span className="ml-2 bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                        por {rec.payload.personal_name}
                      </span>
                    )}
                  </span>
                </div>
                {rec.type === "workout_plan" && rec.payload?.split && (
                  <p className="text-sm text-gray-600">Split: <strong>{rec.payload.split}</strong> · {rec.payload.frequencia_semanal}x/semana</p>
                )}
                {rec.type === "nutrition_plan" && rec.payload?.calorias_alvo && (
                  <p className="text-sm text-gray-600">Meta: <strong>{rec.payload.calorias_alvo} kcal</strong> · P:{rec.payload.macros?.proteinas_g}g C:{rec.payload.macros?.carboidratos_g}g G:{rec.payload.macros?.gorduras_g}g</p>
                )}
                {rec.type === "progress_analysis" && rec.payload?.recomendacoes && (
                  <p className="text-sm text-gray-600">{rec.payload.recomendacoes[0]}</p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Resultado formatado */}
        {result && (
          <div className="card mt-4">
            <p className="font-semibold text-green-700 mb-4">✅ Plano gerado com sucesso!</p>

            {/* Resultado de treino */}
            {result.type === "workout" && result.data?.payload && (
              <div className="space-y-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="font-medium text-blue-800">Split: {result.data.payload.split}</p>
                  <p className="text-sm text-blue-600">{result.data.payload.frequencia_semanal}x por semana · Nível: {result.data.payload.nivel}</p>
                </div>
                {(result.data.payload.dias || []).map((dia: any) => (
                  <div key={dia.dia} className="border border-gray-100 rounded-lg p-4">
                    <p className="font-semibold text-gray-800 mb-2">Dia {dia.dia} — {dia.foco}</p>
                    <div className="space-y-1">
                      {dia.exercicios.map((ex: any, i: number) => (
                        <div key={i} className="flex items-center justify-between text-sm">
                          <span className="text-gray-700">{ex.exercicio}</span>
                          <span className="text-gray-400">{ex.series}×{ex.reps} · {ex.descanso_seg}s</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                {result.data.payload.observacoes?.map((obs: string, i: number) => (
                  <p key={i} className="text-sm text-gray-500 italic">💡 {obs}</p>
                ))}
              </div>
            )}

            {/* Resultado de nutrição */}
            {result.type === "nutrition" && result.data?.payload && (
              <div className="space-y-4">
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="font-medium text-green-800">{result.data.payload.descricao_objetivo}</p>
                  <p className="text-2xl font-bold text-green-700 mt-1">{result.data.payload.calorias_alvo} kcal/dia</p>
                  <p className="text-sm text-green-600">TDEE base: {result.data.payload.tdee} kcal</p>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  {[
                    { label: "Proteína", value: result.data.payload.macros?.proteinas_g, unit: "g", pct: result.data.payload.macros?.proteinas_pct, color: "text-red-600" },
                    { label: "Carboidratos", value: result.data.payload.macros?.carboidratos_g, unit: "g", pct: result.data.payload.macros?.carboidratos_pct, color: "text-yellow-600" },
                    { label: "Gordura", value: result.data.payload.macros?.gorduras_g, unit: "g", pct: result.data.payload.macros?.gorduras_pct, color: "text-blue-600" },
                  ].map(({ label, value, unit, pct, color }) => (
                    <div key={label} className="bg-gray-50 rounded-lg p-3">
                      <p className={`text-xl font-bold ${color}`}>{value}{unit}</p>
                      <p className="text-xs text-gray-500">{label}</p>
                      <p className="text-xs text-gray-400">{pct}%</p>
                    </div>
                  ))}
                </div>
                <div className="space-y-1">
                  {result.data.payload.dicas?.map((dica: string, i: number) => (
                    <p key={i} className="text-sm text-gray-600">💡 {dica}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Resultado de progresso */}
            {result.type === "progress" && result.data?.payload && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-gray-500">Tendência de peso</p>
                    <p className="font-semibold text-gray-800 capitalize">{result.data.payload.tendencia_peso}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-gray-500">Tendência de volume</p>
                    <p className="font-semibold text-gray-800 capitalize">{result.data.payload.tendencia_volume}</p>
                  </div>
                </div>
                {result.data.payload.recomendacoes?.map((rec: string, i: number) => (
                  <div key={i} className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-500 mt-0.5">→</span>
                    <p className="text-sm text-blue-800">{rec}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
