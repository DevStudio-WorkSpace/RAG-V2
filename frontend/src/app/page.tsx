"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";

type Result = {
  id: string;
  nombre: string;
  imagen: string;
  url: string;
  score: number;
  score_reranking?: number;
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  const [excludeIds, setExcludeIds] = useState<string[]>([]);
  
  // Nuevos estados para UX
  const [isDragging, setIsDragging] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const processFile = (selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError("Por favor, sube un archivo de imagen válido.");
      return;
    }
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setResults([]);
    setFeedback({});
    setExcludeIds([]);
    setError(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleSearch = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResults([]);
    setExcludeIds([]);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("modo", "auto");

    try {
      const response = await fetch("http://localhost:8000/search/image", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error en la API: ${response.status}`);
      }

      const data = await response.json();
      const docs = data.resultados || data;
      setResults(docs);
      showToast("Búsqueda completada con éxito");
    } catch (err: any) {
      setError(err.message || "Ocurrió un error al buscar");
      showToast("Error en la búsqueda");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (resultId: string, choice: string) => {
    setFeedback((prev) => ({ ...prev, [resultId]: choice }));

    const newExcludeIds = [...excludeIds, resultId];
    setExcludeIds(newExcludeIds);

    const updatedResults = results.filter((r) => r.id !== resultId);
    setResults(updatedResults);

    if (!file) {
      showToast(`Feedback registrado: ${choice}`);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("modo", "auto");
      // exclude_ids como cadena CSV (la API espera Form field único)
      formData.append("exclude_ids", newExcludeIds.join(","));

      const response = await fetch("http://localhost:8000/search/image", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      const docs: Result[] = data.resultados || data;

      const currentIds = new Set([...updatedResults.map((r) => r.id), ...newExcludeIds]);
      const replacement = docs.find((doc) => !currentIds.has(doc.id)) ?? null;

      if (replacement) {
        setResults([...updatedResults, { ...replacement, _isNew: true } as any]);
        showToast(`✨ Nuevo candidato: ${replacement.nombre}`);
      } else {
        showToast(`Feedback registrado: ${choice}`);
      }
    } catch (err: any) {
      console.error("Error al obtener reemplazo:", err);
      showToast(`Feedback registrado: ${choice}`);
    }
  };

  const renderSkeletons = () => {
    return Array(5).fill(0).map((_, i) => (
      <div key={i} className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex flex-col sm:flex-row gap-6 animate-pulse">
        <div className="w-40 h-40 bg-gray-200 rounded-lg flex-shrink-0"></div>
        <div className="flex-1 flex flex-col justify-center w-full">
          <div className="h-6 bg-gray-200 rounded-md w-1/3 mb-3"></div>
          <div className="h-4 bg-gray-200 rounded-md w-1/5 mb-8"></div>
          <div className="h-4 bg-gray-200 rounded-md w-1/4 mb-3"></div>
          <div className="flex gap-3">
            <div className="h-10 bg-gray-200 rounded-lg w-24"></div>
            <div className="h-10 bg-gray-200 rounded-lg w-24"></div>
            <div className="h-10 bg-gray-200 rounded-lg w-24"></div>
          </div>
        </div>
      </div>
    ));
  };

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans pb-20 overflow-x-hidden">
      
      {/* Toast Notification */}
      <div className={`fixed bottom-6 right-6 bg-gray-900 text-white px-6 py-3 rounded-xl shadow-2xl transition-all duration-300 z-50 flex items-center gap-3 ${toastMessage ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0 pointer-events-none'}`}>
        <span className="text-xl">✨</span> 
        <span className="font-medium">{toastMessage}</span>
      </div>

      <header className="bg-white shadow-sm py-6 border-b border-gray-100 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              RAG Visual Search
            </h1>
            <p className="text-sm text-gray-500 font-medium">Buscador Inteligente de Diseños</p>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 mt-8 flex flex-col items-center">
        
        {/* Zona de Drag & Drop */}
        <section 
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`w-full p-8 rounded-3xl transition-all duration-300 flex flex-col items-center mb-8 border-2 border-dashed ${
            isDragging 
              ? "bg-blue-50 border-blue-400 shadow-inner scale-[1.02]" 
              : "bg-white border-gray-200 shadow-sm"
          }`}
        >
          <h2 className="text-xl font-bold mb-2 text-gray-800">
            {isDragging ? "Suelta la imagen aquí..." : "Sube o arrastra una imagen de consulta"}
          </h2>
          <p className="text-gray-500 text-sm mb-6">Formatos soportados: JPG, PNG, WEBP</p>
          
          <div className="flex flex-col items-center gap-6 w-full">
            {!previewUrl && (
              <label className="cursor-pointer bg-gray-50 hover:bg-gray-100 text-gray-700 font-semibold py-4 px-8 rounded-2xl transition-colors border border-gray-200 flex items-center gap-2 group">
                <span className="text-2xl group-hover:-translate-y-1 transition-transform">📸</span>
                <span>Explorar archivos</span>
                <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
              </label>
            )}
            
            {previewUrl && (
              <div className="relative w-72 h-72 rounded-2xl overflow-hidden shadow-lg border border-gray-100 group">
                <Image src={previewUrl} alt="Preview" fill className="object-cover transition-transform duration-500 group-hover:scale-105" />
                
                {/* Botón cambiar imagen superpuesto */}
                <label className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-xl text-sm font-bold shadow-sm cursor-pointer hover:bg-white transition-colors">
                  Cambiar
                  <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                </label>
              </div>
            )}

            {file && (
              <button
                onClick={handleSearch}
                disabled={loading}
                className="mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-10 rounded-2xl shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 hover:shadow-2xl active:scale-95 flex items-center gap-2 text-lg"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Buscando...
                  </>
                ) : "Buscar Similares"}
              </button>
            )}

            {error && (
              <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl border border-red-100 font-medium w-full max-w-md text-center">
                {error}
              </div>
            )}
          </div>
        </section>

        {/* Sección de Resultados */}
        <section className="w-full">
          {(loading || results.length > 0) && (
            <h2 className="text-2xl font-black mb-6 text-gray-800 flex items-center gap-3">
              Resultados Similares
              {results.length > 0 && <span className="bg-blue-100 text-blue-700 text-sm py-1 px-3 rounded-full">{results.length} encontrados</span>}
              {excludeIds.length > 0 && (
                <span className="bg-gray-100 text-gray-500 text-xs py-1 px-3 rounded-full font-medium">
                  {excludeIds.length} evaluado{excludeIds.length !== 1 ? "s" : ""}
                </span>
              )}
            </h2>
          )}

          {/* Alerta de score bajo */}
          {!loading && results.length > 0 && (() => {
            const bestScore = results[0].score_reranking ?? results[0].score ?? 0;
            if (bestScore < 0.65) {
              return (
                <div className="mb-6 p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-4 shadow-sm animate-[fadeIn_0.5s_ease-out]">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <h3 className="font-bold text-lg">No se encontró un diseño exacto</h3>
                    <p className="text-sm mt-1 opacity-80">El nivel de similitud es bajo ({(bestScore * 100).toFixed(1)}%). Te mostramos los más cercanos, pero te recomendamos intentar con otra imagen.</p>
                  </div>
                </div>
              );
            }
            return null;
          })()}

          <div className="flex flex-col gap-6">
            {loading ? renderSkeletons() : results.slice(0, 5).map((result, index) => {
              const scoreValue = result.score_reranking ?? result.score ?? 0;
              const activeFeedback = feedback[result.id];
              const isNew = (result as any)._isNew === true;
              // Retraso escalonado para la animación (staggered animation)
              const animationDelay = isNew ? "0ms" : `${index * 100}ms`;

              return (
                <div 
                  key={result.id || index} 
                  className={`bg-white p-5 rounded-2xl shadow-sm border flex flex-col sm:flex-row gap-6 items-center sm:items-start transition-all hover:shadow-lg ${
                    isNew
                      ? "border-blue-200 shadow-md animate-[newCardIn_0.5s_ease-out_forwards]"
                      : "border-gray-100 hover:border-blue-100 translate-y-4 opacity-0 animate-[fadeInUp_0.5s_ease-out_forwards]"
                  }`}
                  style={{ animationDelay }}
                >
                  
                  {/* Imagen del resultado */}
                  <div className="relative w-40 h-40 flex-shrink-0 rounded-xl overflow-hidden bg-gray-50 border border-gray-100">
                    {result.imagen ? (
                      <img 
                        src={`/api/images/${result.imagen}`} 
                        alt={result.nombre}
                        className="w-full h-full object-cover transition-transform duration-700 hover:scale-110"
                        onError={(e) => { e.currentTarget.src = result.url || 'https://via.placeholder.com/160?text=Sin+Imagen' }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">Sin Imagen</div>
                    )}
                    {isNew && (
                      <div className="absolute top-2 left-2 bg-blue-500 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow">
                        Nuevo
                      </div>
                    )}
                  </div>

                  {/* Información del resultado */}
                  <div className="flex-1 flex flex-col justify-center">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{result.nombre}</h3>
                        <p className="text-sm text-gray-400 font-mono mt-1">ID: {result.id}</p>
                      </div>
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 text-indigo-700 px-4 py-2 rounded-xl font-black text-lg border border-indigo-100/50 shadow-sm">
                        {(scoreValue * 100).toFixed(1)}%
                      </div>
                    </div>
                    
                    {/* 3 Botones de juicio */}
                    <div className="mt-6 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                      <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Evaluación de Resultados</p>
                      <div className="flex flex-wrap gap-3">
                        <button 
                          onClick={() => handleFeedback(result.id, "Acierto")}
                          disabled={!!activeFeedback}
                          className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all flex-1 sm:flex-none disabled:opacity-50 disabled:cursor-not-allowed ${
                            activeFeedback === "Acierto" 
                              ? "bg-emerald-500 text-white shadow-md shadow-emerald-200 scale-105" 
                              : "bg-white text-emerald-700 hover:bg-emerald-50 border border-emerald-200"
                          }`}
                        >
                          Acierto
                        </button>
                        <button 
                          onClick={() => handleFeedback(result.id, "Sirve")}
                          disabled={!!activeFeedback}
                          className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all flex-1 sm:flex-none disabled:opacity-50 disabled:cursor-not-allowed ${
                            activeFeedback === "Sirve" 
                              ? "bg-amber-500 text-white shadow-md shadow-amber-200 scale-105" 
                              : "bg-white text-amber-700 hover:bg-amber-50 border border-amber-200"
                          }`}
                        >
                          Sirve
                        </button>
                        <button 
                          onClick={() => handleFeedback(result.id, "No sirve")}
                          disabled={!!activeFeedback}
                          className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all flex-1 sm:flex-none disabled:opacity-50 disabled:cursor-not-allowed ${
                            activeFeedback === "No sirve" 
                              ? "bg-rose-500 text-white shadow-md shadow-rose-200 scale-105" 
                              : "bg-white text-rose-700 hover:bg-rose-50 border border-rose-200"
                          }`}
                        >
                          No sirve
                        </button>
                      </div>
                    </div>
                    
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {/* Estilos CSS en línea para las animaciones personalizadas sin tocar tailwind.config */}
      <style jsx global>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes newCardIn {
          from {
            opacity: 0;
            transform: translateY(16px) scale(0.97);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
}
