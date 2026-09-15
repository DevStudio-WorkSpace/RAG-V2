"use client";

type ModeloInfo = {
  value: "clip" | "openclip" | "fusion";
  label: string;
  detail: string;
  best?: boolean;
};

export const MODELOS: readonly ModeloInfo[] = [
  {
    value: "fusion",
    label: "Fusión (CLIP + OpenCLIP + SigLIP)",
    detail: "ganador en la evaluación · 84% Top1 / 90% Top5",
    best: true,
  },
  {
    value: "openclip",
    label: "OpenCLIP",
    detail: "laion/CLIP-ViT-B-32",
  },
  {
    value: "clip",
    label: "CLIP",
    detail: "openai/clip-vit-base-patch32",
  },
] as const satisfies readonly ModeloInfo[];

export type ModelKey = (typeof MODELOS)[number]["value"];

export const MODELO_DEFAULT: ModelKey = "fusion";

export function modeloDetalle(modelo: string): { label: string; detail: string } {
  const clave = MODELOS.find((x) => x.value === modelo)?.value
    ? modelo
    : modelo.startsWith("fusion")
      ? "fusion"
      : modelo.startsWith("laion")
        ? "openclip"
        : "clip";
  const m = MODELOS.find((x) => x.value === clave);
  return m ? { label: m.label, detail: m.detail } : { label: modelo || "clip", detail: "" };
}

export default function ModelSelect({
  value,
  onChange,
  id,
}: {
  value: ModelKey;
  onChange: (v: ModelKey) => void;
  id?: string;
}) {
  return (
    <label className="model-select">
      <span>Modelo</span>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value as ModelKey)}
      >
        {MODELOS.map((m) => (
          <option key={m.value} value={m.value}>
            {m.label}
            {m.best ? " · (mejor)" : ""}
          </option>
        ))}
      </select>
    </label>
  );
}