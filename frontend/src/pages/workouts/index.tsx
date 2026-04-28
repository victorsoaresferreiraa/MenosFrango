/**
 * Página de Treinos — MENOSFRANGO
 * CRUD completo com linguagem brasileirada.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { workoutsApi } from "@/lib/api";
import { Pen, Trash } from "react-bootstrap-icons";

const MUSCLE_GROUPS = [
  "peito","costas","ombros","biceps","triceps",
  "quadriceps","posterior","gluteos","abdomen","panturrilha",
];

const defaultForm = {
  exercise: "", muscle_group: "peito", sets: 4, reps: 10,
  weight_kg: 0, rpe: 7, notes: "",
  workout_date: new Date().toISOString().slice(0, 16),
};

const RPE_LABELS: Record<number, string> = {
  1:"Moleza total 😴", 2:"Fácil demais 😌", 3:"Tranquilo 🙂",
  4:"Ok 😐", 5:"Moderado 😤", 6:"Puxado 💪",
  7:"Pesado 🔥", 8:"Muito pesado 😰", 9:"Quase falha 😱", 10:"Falha total 💀",
};

export default function WorkoutsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();

  const [showForm, setShowForm]           = useState(false);
  const [form, setForm]                   = useState(defaultForm);
  const [filterGroup, setFilterGroup]     = useState("");
  const [page, setPage]                   = useState(1);
  const [editingWorkout, setEditingWorkout] = useState<any>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, isLoading, router]);

  const { data, isLoading: loadingWorkouts } = useQuery({
    queryKey: ["workouts", page, filterGroup],
    queryFn: () =>
      workoutsApi.list({ page, page_size: 20, muscle_group: filterGroup || undefined })
        .then((r) => r.data),
    enabled: isAuthenticated,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => workoutsApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workouts"] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
      qc.invalidateQueries({ queryKey: ["dashboard-graphs"] });
      handleCloseForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => workoutsApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workouts"] });
      qc.invalidateQueries({ queryKey: ["dashboard-graphs"] });
      handleCloseForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => workoutsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workouts"] });
      qc.invalidateQueries({ queryKey: ["dashboard-graphs"] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { ...form, workout_date: new Date(form.workout_date).toISOString() };
    if (editingWorkout) {
      updateMutation.mutate({ id: editingWorkout.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleEdit = (w: any) => {
    setEditingWorkout(w);
    setForm({
      exercise: w.exercise, muscle_group: w.muscle_group,
      sets: w.sets, reps: w.reps, weight_kg: w.weight_kg,
      rpe: w.rpe || 7, notes: w.notes || "",
      workout_date: new Date(w.workout_date).toISOString().slice(0, 16),
    });
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingWorkout(null);
    setForm(defaultForm);
  };

  const volume = (w: any) => Math.round(w.sets * w.reps * w.weight_kg);

  if (isLoading) return null;

  return (
    <Layout title="TREINOS">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 gap-3 flex-wrap">
        <select value={filterGroup}
          onChange={(e) => { setFilterGroup(e.target.value); setPage(1); }}
          className="input-field w-auto bg-principal-white dark:bg-principal-cinza3 dark:text-white">
          <option value="">Todos os grupos</option>
          {MUSCLE_GROUPS.map((g) => (
            <option key={g} value={g} className="capitalize">{g}</option>
          ))}
        </select>
        <button onClick={() => showForm ? handleCloseForm() : setShowForm(true)} className="btn-primary bg-frango-base hover:bg-frango-escuro">
          {showForm ? "Cancelar" : "+ Registrar Treino"}
        </button>
      </div>

      {/* Formulário */}
      {showForm && (
        <div className="card mb-6 bg-principal-cinzaClaro dark:bg-principal-cinza dark:text-white">
          <h3 className="text-black dark:text-white">
            {editingWorkout ? "Editar Treino" : "Novo Treino"}
          </h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Exercício *</label>
              <input type="text" required value={form.exercise}
                onChange={(e) => setForm({ ...form, exercise: e.target.value })}
                className="input-field bg-principal-white dark:bg-principal-cinza3" placeholder="ex: Supino Reto" />
            </div>
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Grupo Muscular *</label>
              <select value={form.muscle_group}
                onChange={(e) => setForm({ ...form, muscle_group: e.target.value })}
                className="input-field bg-principal-white dark:bg-principal-cinza3">
                {MUSCLE_GROUPS.map((g) => (
                  <option key={g} value={g} className="capitalize">{g}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Data/Hora *</label>
              <input type="datetime-local" required value={form.workout_date}
                onChange={(e) => setForm({ ...form, workout_date: e.target.value })}
                className="input-field bg-principal-white dark:bg-principal-cinza3" />
            </div>
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Séries *</label>
              <input type="number" required min={1} max={100} value={form.sets}
                onChange={(e) => setForm({ ...form, sets: Number(e.target.value) })}
                className="input-field bg-principal-white dark:bg-principal-cinza3" />
            </div>
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Repetições *</label>
              <input type="number" required min={1} max={1000} value={form.reps}
                onChange={(e) => setForm({ ...form, reps: Number(e.target.value) })}
                className="input-field bg-principal-white dark:bg-principal-cinza3" />
            </div>
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Carga (kg)</label>
              <input type="number" min={0} step={0.5} value={form.weight_kg}
                onChange={(e) => setForm({ ...form, weight_kg: Number(e.target.value) })}
                className="input-field bg-principal-white dark:bg-principal-cinza3" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-black dark:text-white mb-1">
                RPE — Esforço: {form.rpe}/10 · {RPE_LABELS[form.rpe]}
              </label>
              <input type="range" min={1} max={10} value={form.rpe}
                onChange={(e) => setForm({ ...form, rpe: Number(e.target.value) })}
                className="w-full accent-frango-base" />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Moleza</span><span>Médio</span><span>💀 Falha</span>
              </div>
            </div>
            <div>
              <label className="block text-sm text-black dark:text-white mb-1">Observações</label>
              <input type="text" value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                className="input-field bg-principal-white dark:bg-principal-cinza3" placeholder="ex: bateu um cansaço no final..." />
            </div>
            <div className="md:col-span-3 flex justify-end gap-3">
              <button type="button" onClick={handleCloseForm} className="btn-secondary  bg-principal-white dark:bg-principal-cinza3 dark:text-white">Cancelar</button>
              <button type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="btn-primary bg-frango-base hover:bg-frango-escuro">
                {createMutation.isPending || updateMutation.isPending
                  ? "Salvando... 🤖"
                  : editingWorkout ? "💾 Salvar Edição" : "Registrar Treino"}
              </button>
            </div>
          </form>
          {(createMutation.isError || updateMutation.isError) && (
            <p className="mt-2 text-red-600 text-sm">❌ Erro ao salvar. Verifica os dados!</p>
          )}
        </div>
      )}

      {/* Lista */}
      {loadingWorkouts ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-4xl mb-2">🤖</p>
          <p>Carregando seus treinos...</p>
        </div>
      ) : (data?.items || []).length === 0 ? (
        <div className="card text-center py-14">
          <p className="text-5xl mb-3">🐔</p>
          <p className="text-gray-600 font-bold text-lg">Nenhum treino ainda!</p>
          <p className="text-sm text-gray-400 mt-1">Vai ser eterno frango? Clica em "+ Registrar Treino"!</p>
        </div>
      ) : (
        <>
          <div className="space-y-3 ">
            {(data?.items || []).map((w: any) => (
              <div key={w.id} className="card flex items-start justify-between gap-4 border border-frango-base hover:border-frango-escuro bg-principal-white dark:bg-principal-cinza3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap mb-1 ">
                    <h4 className="text-black dark:text-white">{w.exercise}</h4>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold capitalize">
                      {w.muscle_group}
                    </span>
                    {w.rpe && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                        w.rpe >= 9 ? "bg-red-100 text-red-700" :
                        w.rpe >= 7 ? "bg-orange-100 text-orange-700" :
                        "bg-green-100 text-green-700"
                      }`}>
                        RPE {w.rpe} {w.rpe >= 9 ? "💀" : w.rpe >= 7 ? "🔥" : "💪"}
                      </span>
                    )}
                  </div>
                  <p className="text-black dark:text-white">
                    {w.sets} séries × {w.reps} reps @ <strong className="text-frango-base">{w.weight_kg}kg</strong>
                    {w.weight_kg > 0 && (
                      <span className="text-gray-400 text-sm ml-2">· {volume(w).toLocaleString()}kg vol</span>
                    )}
                  </p>
                  {w.notes && <p className="text-sm text-gray-400 mt-1 italic">"{w.notes}"</p>}
                  <p className="text-xs text-gray-300 mt-1">
                    {new Date(w.workout_date).toLocaleString("pt-BR")}
                  </p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => handleEdit(w)}
                    className="text-black dark:text-white hover:bg-frango-base px-2 py-1 rounded-lg transition-colors text-lg">
                    <Pen size={20}/>
                  </button>
                  <button
                    onClick={() => { if (confirm("Deletar esse treino? 🐔")) deleteMutation.mutate(w.id); }}
                    className="text-[#FF0000] hover:bg-[#880808] px-2 py-1 rounded-lg transition-colors text-lg">
                    <Trash size={20}/>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Paginação */}
          {(data?.pages || 1) > 1 && (
            <div className="flex justify-center items-center gap-4 mt-6">
              <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn-secondary disabled:opacity-40">
                ← Anterior
              </button>
              <span className="text-gray-600 font-bold">{page} / {data?.pages}</span>
              <button disabled={page >= (data?.pages || 1)} onClick={() => setPage(page + 1)} className="btn-secondary disabled:opacity-40">
                Próxima →
              </button>
            </div>
          )}
        </>
      )}
    </Layout>
  );
}
