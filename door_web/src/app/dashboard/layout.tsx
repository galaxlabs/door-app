"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import clsx from "clsx";
import {
  BellRing,
  DoorOpen,
  LayoutDashboard,
  QrCode,
  User,
} from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/dashboard/doors", label: "Doors", icon: DoorOpen },
  { href: "/dashboard/qr", label: "QR", icon: QrCode },
  { href: "/dashboard/profile", label: "Profile", icon: User },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const [authState, setAuthState] = useState<"checking" | "authorized" | "unauthorized">("checking");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setAuthState("unauthorized");
      const next = encodeURIComponent(path || "/dashboard");
      router.replace(`/auth/login?next=${next}`);
      return;
    }
    setAuthState("authorized");
  }, [path, router]);

  if (authState !== "authorized") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-transparent px-6 text-[var(--text)]">
        <div className="max-w-md rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-6 text-center shadow-[var(--shadow)]">
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Security Check</p>
          <h2 className="mt-3 text-xl font-semibold">Sign in required</h2>
          <p className="mt-2 text-sm text-[var(--text-muted)]">Redirecting to login so protected dashboard APIs do not fail with unauthorized errors.</p>
        </div>
      </div>
    );
  }

  const isActive = (href: string) => {
    if (!path) return false;
    if (href === "/dashboard") return path === href;
    return path === href || path.startsWith(`${href}/`);
  };

  return (
    <div className="min-h-screen bg-transparent text-[var(--text)]">
      <div className="mx-auto flex min-h-screen w-full max-w-[1600px] gap-6 px-4 py-4 md:px-6">
        <aside className="hidden w-72 shrink-0 flex-col rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-5 shadow-[var(--shadow)] backdrop-blur md:flex">
          <div className="mb-8 rounded-[var(--radius-lg)] border border-[var(--line-strong)] bg-[linear-gradient(145deg,rgba(246,185,74,0.16),rgba(55,214,197,0.08))] p-5">
            <p className="text-xs uppercase tracking-[0.35em] text-[var(--text-muted)]">Door App</p>
            <h2 className="mt-3 text-2xl font-semibold">Simple smart door system</h2>
            <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
              The web shell now stays focused on four core areas: Home, Doors, QR, and Profile.
            </p>
          </div>
          <nav className="flex flex-1 flex-col gap-2">
            {NAV.map((n) => {
              const Icon = n.icon;
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={clsx(
                    "flex items-center gap-3 rounded-[18px] border px-4 py-3 text-sm font-medium transition",
                    isActive(n.href)
                      ? "border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]"
                      : "border-transparent text-[var(--text-muted)] hover:border-[var(--line)] hover:bg-[rgba(255,255,255,0.03)] hover:text-[var(--text)]"
                  )}
                >
                  <Icon size={18} />
                  <span>{n.label}</span>
                </Link>
              );
            })}
          </nav>
          <div className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Live queue updates</p>
                <p className="text-xs text-[var(--text-muted)]">Serving now, tokens, appointments</p>
              </div>
              <BellRing size={18} className="text-[var(--teal)]" />
            </div>
          </div>
        </aside>
        <div className="flex min-h-screen flex-1 flex-col gap-4">
          <header className="flex flex-wrap items-center justify-between gap-3 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] px-5 py-4 shadow-[var(--shadow)] backdrop-blur">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Web Layout</p>
              <h1 className="text-xl font-semibold">Door App control center</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-full border border-[var(--line)] bg-[var(--bg-card)] px-4 py-2 text-sm text-[var(--text-muted)]">
                QR, queues, appointments, visitor flow
              </div>
            </div>
          </header>
          <div className="flex gap-3 overflow-x-auto rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-3 shadow-[var(--shadow)] backdrop-blur md:hidden">
            {NAV.map((n) => {
              const Icon = n.icon;
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={clsx(
                    "flex min-w-fit items-center gap-2 rounded-[16px] border px-4 py-3 text-sm font-medium transition",
                    isActive(n.href)
                      ? "border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]"
                      : "border-[var(--line)] bg-[var(--bg-card)] text-[var(--text-muted)]"
                  )}
                >
                  <Icon size={16} />
                  <span>{n.label}</span>
                </Link>
              );
            })}
          </div>
          <main className="flex-1 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-5 shadow-[var(--shadow)] backdrop-blur md:p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
