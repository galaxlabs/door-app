import { ReactNode } from "react";

type Stat = {
  label: string;
  value: string;
  tone?: "amber" | "teal" | "neutral";
};

type AdminPageProps = {
  eyebrow: string;
  title: string;
  description: string;
  stats?: Stat[];
  children?: ReactNode;
};

const toneClass: Record<NonNullable<Stat["tone"]>, string> = {
  amber: "border-[var(--line-strong)] bg-[var(--amber-soft)]",
  teal: "border-[rgba(55,214,197,0.22)] bg-[var(--teal-soft)]",
  neutral: "border-[var(--line)] bg-[var(--bg-card)]",
};

export function AdminPage({ eyebrow, title, description, stats = [], children }: AdminPageProps) {
  return (
    <div className="space-y-6">
      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-6">
          <p className="text-xs uppercase tracking-[0.35em] text-[var(--text-muted)]">{eyebrow}</p>
          <h2 className="mt-3 text-3xl font-semibold">{title}</h2>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-[var(--text-muted)]">{description}</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className={`rounded-[var(--radius-lg)] border p-5 ${toneClass[stat.tone ?? "neutral"]}`}
            >
              <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">{stat.label}</p>
              <p className="mt-3 text-3xl font-semibold">{stat.value}</p>
            </div>
          ))}
        </div>
      </section>
      {children}
    </div>
  );
}
