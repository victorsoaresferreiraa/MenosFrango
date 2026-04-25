/**
 * Página de Detalhe do Aluno — vista pelo Personal
 *
 * O personal vê aqui:
 * - Dados pessoais do aluno (nome, objetivo, nível, peso)
 * - KPIs de treino dos últimos 30 dias
 * - Resumo nutricional dos últimos 7 dias
 * - Histórico de treinos
 * - Botão para gerar plano de treino via IA
 * - Botão para gerar plano nutricional via IA
 * - Campo de anotações do personal
 */

import { useState } from "react";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/layout/PersonalLayout";
import { personalApi } from "@/lib/api";

export default function ClientDetailPage() {
  const router = useRouter();
  const { id } = router.query as { id: string };
  const qc = useQueryClient();

  const [notes,       setNotes]       = useState("");
  const [editingNotes, setEditingNotes] = useState(false);
  const [aiMsg,       setAiMsg]       = useState("");

  // Dados do aluno
  const { data: client, isLoading } = useQuery({
    queryKey: ["personal-client", id],
    queryFn: () => personalApi.getClient(id).then((r) => r.data),
    enabled: !!id,
    onSuccess: (data: any) => setNotes(data.notes || ""),
  });

  // Treinos do aluno
  const { data: workouts } = useQuery({
    queryKey: ["personal-client-workouts", id],
    queryFn: () => personalApi.getClientWorkouts(id).then((r) => r.data),
    enabled: !!id,
  });

  // Nutrição do aluno
  const { data: nutrition } = useQuery({
    queryKey: ["personal-client-nutrition", id],
    queryFn: () => personalApi.getClientNutrition(id).then((r) => r.data),
    enabled: !!id,
  });

  // Salvar notas
  const notesMutation = useMutation({
    mutationFn: () => personalApi.updateClientNotes(id, notes),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["personal-client", id] });
      setEditingNotes(false);
    },
  });

  // Gerar plano de treino via IA
  const workoutPlanMutation = useMutation({
    mutationFn: () =>
      personalApi.generateWorkoutPlan(id, {
        goal: client?.client?.goal || "manutencao",
        weekly_frequency: 4,
        level: client?.client?.level || "iniciante",
      }),
    onSuccess: (data: any) => {
      setAiMsg(`✅ Plano de treino gerado! Split: ${data.plan?.split}`);
      setTimeout(() => setAiMsg(""), 4000);
    },
  });

  // Gerar plano nutricional via IA
  const nutritionPlanMutation = useMutation({
    mutationFn: () =>
      personalApi.generateNutritionPlan(id, {
        weight_kg:  client?.client?.weight_kg || 70,
        height_cm:  client?.client?.height_cm || 170,
        age:        client?.client?.age || 25,
        goal:       client?.client?.goal || "manutencao",
        activity_level: "moderado",
      }),
    onSuccess: (data: any) => {
      setAiMsg(`✅ Plano nutricional gerado! Meta: ${data.plan?.calorias_alvo} kcal/dia`);
      setTimeout(() => setAiMsg(""), 4000);
    },
  });

  if (isLoading || !client) {
    return (
      <Layout title="Carregando...">
        <div className="text-center py-12 text-gray-400">Carregando dados do aluno...</div>
      </Layout>
    );
  }

  const info = client.client;
  const kpis = client.kpis || {};
  const workoutList = workouts?.items || [];

  return (
    <Layout title={info.name}>

      {/* Botão voltar */}
      <button
        onClick={() => router.push("/personal/dashboard")}
        className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 text-sm"
      >
        ← Voltar para meus alunos
      </button>

      {/* Cabeçalho do aluno */}
      <div className="card mb-6">
        <div className="flex items-start gap-5">
          {/* Avatar */}
          <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-2xl flex-shrink-0">
            {info.name.charAt(0).toUpperCase()}
          </div>

          {/* Dados */}
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">{info.name}</h2>
            <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-600">
              {info.goal && (
                <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full capitalize">
                  🎯 {info.goal}
                </span>
              )}
              {info.level && (
                <span className="bg-purple-50 text-purple-700 px-3 py-1 rounded-full capitalize">
                  📊 {info.level}
                </span>
              )}
              {info.weight_kg && (
                <span className="bg-gray-50 text-gray-700 px-3 py-1 rounded-full">
                  ⚖️ {info.weight_kg} kg
                </span>
              )}
            </div>
            {info.bio && (
              <p className="text-sm text-gray-500 mt-2 italic">"{info.bio}"</p>
            )}
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="card text-center">
          <p className="text-2xl font-bold text-gray-900">{kpis.workouts_last_30d ?? "—"}</p>
          <p className="text-sm text-gray-500">Treinos (30 dias)</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-bold text-gray-900">
            {kpis.total_volume_kg ? `${kpis.total_volume_kg.toLocaleString()} kg` : "—"}
          </p>
          <p className="text-sm text-gray-500">Volume total</p>
        </div>
      </div>

      {/* Nutrição */}
      {nutrition && (
        <div className="card mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">🥗 Nutrição (últimos 7 dias)</h3>
          <div className="grid grid-cols-3 gap-3 text-center">
            <div>
              <p className="text-lg font-bold text-gray-900">
                {nutrition.avg_daily_calories ?? "—"}
              </p>
              <p className="text-xs text-gray-500">kcal/dia (média)</p>
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">
                {nutrition.total_calories ?? "—"}
              </p>
              <p className="text-xs text-gray-500">kcal total</p>
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">
                {nutrition.total_protein_g ?? "—"}g
              </p>
              <p className="text-xs text-gray-500">proteína total</p>
            </div>
          </div>
        </div>
      )}

      {/* Ações de IA */}
      <div className="card mb-6">
        <h3 className="font-semibold text-gray-900 mb-3">🤖 Gerar com IA</h3>
        {aiMsg && (
          <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            {aiMsg}
          </div>
        )}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => workoutPlanMutation.mutate()}
            disabled={workoutPlanMutation.isPending}
            className="btn-primary text-sm"
          >
            {workoutPlanMutation.isPending ? "Gerando..." : "🏋️ Plano de Treino"}
          </button>
          <button
            onClick={() => nutritionPlanMutation.mutate()}
            disabled={nutritionPlanMutation.isPending}
            className="btn-secondary text-sm"
          >
            {nutritionPlanMutation.isPending ? "Gerando..." : "🥗 Plano Nutricional"}
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          O plano gerado aparece automaticamente na tela do aluno.
        </p>
      </div>

      {/* Anotações do personal */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">📝 Minhas anotações</h3>
          {!editingNotes ? (
            <button
              onClick={() => setEditingNotes(true)}
              className="text-sm text-blue-600 hover:underline"
            >
              Editar
            </button>
          ) : (
            <button
              onClick={() => notesMutation.mutate()}
              disabled={notesMutation.isPending}
              className="text-sm text-green-600 hover:underline"
            >
              {notesMutation.isPending ? "Salvando..." : "Salvar"}
            </button>
          )}
        </div>

        {editingNotes ? (
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={4}
            className="input-field resize-none"
            placeholder="Anote objetivos, limitações, progressão, observações..."
          />
        ) : (
          <p className="text-sm text-gray-600">
            {notes || (
              <span className="italic text-gray-400">
                Nenhuma anotação ainda. Clique em Editar.
              </span>
            )}
          </p>
        )}
      </div>

      {/* Histórico de treinos */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">
          🏋️ Últimos treinos ({workoutList.length})
        </h3>
        {workoutList.length === 0 ? (
          <p className="text-center text-gray-400 py-6">
            O aluno ainda não registrou treinos.
          </p>
        ) : (
          <div className="space-y-3">
            {workoutList.slice(0, 10).map((w: any) => (
              <div
                key={w.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900 text-sm">{w.exercise}</p>
                  <p className="text-xs text-gray-500 capitalize">{w.muscle_group}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{w.weight_kg} kg</p>
                  <p className="text-xs text-gray-500">
                    {w.sets}×{w.reps} · {new Date(w.workout_date).toLocaleDateString("pt-BR")}
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
