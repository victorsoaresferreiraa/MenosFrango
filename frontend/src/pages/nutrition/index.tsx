/**
 * Página de Nutrição — versão completa com metas de macros.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { nutritionApi } from "@/lib/api";

const defaultForm = {
  food_name: "", quantity_g: 100, calories: 0,
  protein_g: 0, carbs_g: 0, fat_g: 0,
};

export default function NutritionPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();

  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(defaultForm);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, isLoading, router]);

  const { data: dayData, isLoading: loadingDay } = useQuery({
    queryKey: ["nutrition-day", selectedDate],
    queryFn: () => nutritionApi.getDay(selectedDate).then((r) => r.data),
    enabled: isAuthenticated,
  });

  const { data: goals } = useQuery({
    queryKey: ["macro-goals"],
    queryFn: () => nutritionApi.getMacroGoals().then((r) => r.data),
    enabled: isAuthenticated,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => nutritionApi.create({ ...data, log_date: selectedDate }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["nutrition-day", selectedDate] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
      setShowForm(false);
      setForm(defaultForm);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => nutritionApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["nutrition-day", selectedDate] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const totals = dayData?.totals || {};
  const items = dayData?.items || [];

  const pct = (val: number, goal: number) =>
    goal > 0 ? Math.min(Math.round((val / goal) * 100), 100) : 0;

  if (isLoading) return null;

  return (
    <Layout title="Nutrição">
      {/* Seletor de data + botão */}
      <div className="flex items-center justify-between mb-6 gap-3">
        <input
          type="date"
          value={selectedDate}
          max={new Date().toISOString().slice(0, 10)}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="input-field w-auto"
        />
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? "Cancelar" : "+ Adicionar Alimento"}
        </button>
      </div>

      {/* Formulário */}
      {showForm && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Registrar Alimento</h3>
          <form
            onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form); }}
            className="grid grid-cols-2 md:grid-cols-3 gap-4"
          >
            <div className="col-span-2 md:col-span-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">Alimento *</label>
              <input type="text" required value={form.food_name}
                onChange={(e) => setForm({ ...form, food_name: e.target.value })}
                className="input-field" placeholder="ex: Frango grelhado" />
            </div>
            {[
              { key: "quantity_g", label: "Quantidade (g) *", min: 0.1, step: 0.1 },
              { key: "calories",   label: "Calorias (kcal) *", min: 0 },
              { key: "protein_g",  label: "Proteína (g)", min: 0, step: 0.1 },
              { key: "carbs_g",    label: "Carboidratos (g)", min: 0, step: 0.1 },
              { key: "fat_g",      label: "Gordura (g)", min: 0, step: 0.1 },
            ].map(({ key, label, min, step }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input type="number" min={min} step={step || 1}
                  value={(form as any)[key]}
                  onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}
                  className="input-field" required={label.includes("*")} />
              </div>
            ))}
            <div className="col-span-2 md:col-span-3 flex justify-end gap-3">
              <button type="button" onClick={() => { setShowForm(false); setForm(defaultForm); }} className="btn-secondary">Cancelar</button>
              <button type="submit" disabled={createMutation.isPending} className="btn-primary">
                {createMutation.isPending ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Resumo do dia */}
      <div className="card mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">
          📊 Resumo de {new Date(selectedDate + "T12:00:00").toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" })}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {[
            { label: "Calorias", value: Math.round(totals.calories || 0), goal: goals?.calorias_alvo, unit: "kcal", color: "blue" },
            { label: "Proteína", value: Math.round(totals.protein_g || 0), goal: goals?.macros?.proteinas_g, unit: "g", color: "red" },
            { label: "Carboidratos", value: Math.round(totals.carbs_g || 0), goal: goals?.macros?.carboidratos_g, unit: "g", color: "yellow" },
            { label: "Gordura", value: Math.round(totals.fat_g || 0), goal: goals?.macros?.gorduras_g, unit: "g", color: "purple" },
          ].map(({ label, value, goal, unit, color }) => (
            <div key={label}>
              <div className="flex items-end justify-between mb-1">
                <span className="text-xs text-gray-500">{label}</span>
                <span className="text-sm font-bold text-gray-900">{value}{unit}</span>
              </div>
              {goal && (
                <>
                  <div className="w-full bg-gray-100 rounded-full h-2 mb-1">
                    <div
                      className={`h-2 rounded-full bg-${color}-500`}
                      style={{ width: `${pct(value, goal)}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400">Meta: {goal}{unit} ({pct(value, goal)}%)</p>
                </>
              )}
              {!goal && (
                <p className="text-xs text-gray-400">Complete o perfil para ver metas</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Lista de alimentos */}
      {loadingDay ? (
        <div className="text-center py-8 text-gray-400">Carregando...</div>
      ) : items.length === 0 ? (
        <div className="card text-center py-10">
          <p className="text-4xl mb-3">🥗</p>
          <p className="text-gray-500">Nenhum alimento registrado neste dia.</p>
          <button onClick={() => setShowForm(true)} className="btn-primary mt-3">+ Adicionar Alimento</button>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item: any) => (
            <div key={item.id} className="card flex items-center justify-between gap-3">
              <div className="flex-1">
                <p className="font-medium text-gray-900">{item.food_name}</p>
                <p className="text-xs text-gray-500">
                  {item.quantity_g}g · {Math.round(item.calories)} kcal · P:{Math.round(item.protein_g)}g C:{Math.round(item.carbs_g)}g G:{Math.round(item.fat_g)}g
                </p>
              </div>
              <button
                onClick={() => { if (confirm("Remover?")) deleteMutation.mutate(item.id); }}
                className="text-red-400 hover:text-red-600 px-2 py-1 hover:bg-red-50 rounded transition-colors"
              >🗑️</button>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
