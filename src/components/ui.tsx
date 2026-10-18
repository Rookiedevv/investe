import type { ComponentProps } from "react";

export function Card({ className = "", ...rest }: ComponentProps<"section">) {
  return <section className={`rounded-2xl border border-line bg-card p-4 ${className}`} {...rest} />;
}

export function H1({ children }: { children: React.ReactNode }) {
  return <h1 className="mb-4 text-2xl font-bold tracking-tight">{children}</h1>;
}

export function H2({ children }: { children: React.ReactNode }) {
  return <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-soft">{children}</h2>;
}

export function Button({ variant = "primary", className = "", ...rest }: ComponentProps<"button"> & { variant?: "primary" | "quiet" }) {
  const look =
    variant === "primary"
      ? "bg-accent text-on-accent border-accent hover:opacity-90"
      : "border-line hover:bg-paper";
  return <button className={`min-h-11 rounded-xl border-2 px-4 font-semibold ${look} ${className}`} {...rest} />;
}

const field = "mt-1 block min-h-11 w-full rounded-xl border-2 border-line bg-card px-3";

export function Field({ label, ...rest }: ComponentProps<"input"> & { label: string }) {
  return (
    <label className="block text-sm font-medium">
      {label}
      <input className={field} {...rest} />
    </label>
  );
}

export function Select({ label, children, ...rest }: ComponentProps<"select"> & { label: string }) {
  return (
    <label className="block text-sm font-medium">
      {label}
      <select className={field} {...rest}>
        {children}
      </select>
    </label>
  );
}

export function ErrorNote({ show, text }: { show: boolean; text: string }) {
  if (!show) return null;
  return <p className="mb-4 rounded-xl bg-warn-bg px-4 py-3 text-sm font-semibold">{text}</p>;
}

/** Signed money value: green for gains, orange-red for losses. */
export function Signed({ value, children }: { value: number; children: React.ReactNode }) {
  return <span className={`num font-semibold ${value > 0 ? "text-up" : value < 0 ? "text-down" : ""}`}>{children}</span>;
}
