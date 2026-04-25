/**
 * Página de Fotos de Progresso — versão melhorada com galeria.
 */

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/hooks/useAuth";
import { photosApi } from "@/lib/api";

export default function PhotosPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [weight, setWeight] = useState("");
  const [notes, setNotes] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [enlarged, setEnlarged] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, isLoading, router]);

  const { data, isLoading: loadingPhotos } = useQuery({
    queryKey: ["photos"],
    queryFn: () => photosApi.list().then((r) => r.data),
    enabled: isAuthenticated,
  });

  const uploadMutation = useMutation({
    mutationFn: (fd: FormData) => photosApi.upload(fd),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["photos"] });
      setFile(null); setPreview(null); setWeight(""); setNotes("");
      setShowForm(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => photosApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["photos"] }),
  });

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = (ev) => setPreview(ev.target?.result as string);
    reader.readAsDataURL(f);
  };

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    if (weight) fd.append("weight_kg", weight);
    if (notes) fd.append("notes", notes);
    uploadMutation.mutate(fd);
  };

  const photos = data?.items || [];

  if (isLoading) return null;

  return (
    <Layout title="Fotos de Progresso">
      {/* Modal de imagem ampliada */}
      {enlarged && (
        <div
          className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4"
          onClick={() => setEnlarged(null)}
        >
          <img src={enlarged} alt="Foto ampliada" className="max-w-full max-h-full rounded-lg" />
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-gray-500">{photos.length} foto{photos.length !== 1 ? "s" : ""} registrada{photos.length !== 1 ? "s" : ""}</p>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? "Cancelar" : "📸 Adicionar Foto"}
        </button>
      </div>

      {/* Formulário de upload */}
      {showForm && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Nova Foto de Progresso</h3>
          <form onSubmit={handleUpload} className="space-y-4">
            <div
              className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
              onClick={() => fileRef.current?.click()}
            >
              {preview ? (
                <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded-lg" />
              ) : (
                <>
                  <p className="text-4xl mb-2">📸</p>
                  <p className="text-gray-500 text-sm">Clique para selecionar uma foto</p>
                  <p className="text-gray-400 text-xs mt-1">JPEG, PNG ou WebP · máx. 10MB</p>
                </>
              )}
              <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} className="hidden" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Peso atual (kg)</label>
                <input type="number" min={0} step={0.1} value={weight}
                  onChange={(e) => setWeight(e.target.value)} className="input-field" placeholder="ex: 80.5" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
                <input type="text" value={notes}
                  onChange={(e) => setNotes(e.target.value)} className="input-field" placeholder="ex: 8 semanas de treino" />
              </div>
            </div>
            <button type="submit" disabled={!file || uploadMutation.isPending} className="btn-primary w-full py-3">
              {uploadMutation.isPending ? "Enviando..." : "Salvar Foto"}
            </button>
          </form>
        </div>
      )}

      {/* Galeria */}
      {loadingPhotos ? (
        <div className="text-center py-12 text-gray-400">Carregando fotos...</div>
      ) : photos.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-5xl mb-3">📸</p>
          <p className="text-gray-500">Nenhuma foto ainda.</p>
          <p className="text-sm text-gray-400 mt-1">Registre sua evolução com fotos periódicas.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {photos.map((p: any) => (
            <div key={p.id} className="relative group">
              <img
                src={p.url}
                alt={`Foto ${new Date(p.taken_at).toLocaleDateString("pt-BR")}`}
                className="w-full aspect-square object-cover rounded-xl cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => setEnlarged(p.url)}
              />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent rounded-b-xl p-3">
                <p className="text-white text-xs font-medium">
                  {new Date(p.taken_at).toLocaleDateString("pt-BR")}
                </p>
                {p.weight_kg && <p className="text-white text-xs opacity-80">{p.weight_kg} kg</p>}
              </div>
              <button
                onClick={() => { if (confirm("Remover foto?")) deleteMutation.mutate(p.id); }}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-7 h-7 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
              >✕</button>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
