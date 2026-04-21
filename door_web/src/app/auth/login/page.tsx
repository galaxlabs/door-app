"use client";
import { useForm } from "react-hook-form";
import { useState } from "react";
import api from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { LockKeyhole, QrCode, RadioTower, Ticket } from "lucide-react";

type AuthMode = "password" | "otp";
type OtpStep = "phone" | "otp";

export default function LoginPage() {
  const router = useRouter();
  const [authMode, setAuthMode] = useState<AuthMode>("password");
  const [otpStep, setOtpStep] = useState<OtpStep>("phone");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit } = useForm<{ phone?: string; otp?: string; identifier?: string; password?: string }>();

  function resolveNextPath() {
    if (typeof window === "undefined") return "/dashboard";
    const requested = new URLSearchParams(window.location.search).get("next");
    return requested && requested.startsWith("/dashboard") ? requested : "/dashboard";
  }

  async function onSubmitPhone(data: { phone?: string }) {
    setError(null);
    const value = (data.phone ?? "").trim();
    if (!value) {
      setError("Phone number is required.");
      return;
    }
    await api.post("auth/otp/request/", { phone: value });
    setPhone(value);
    setOtpStep("otp");
  }

  async function onSubmitOtp(data: { otp?: string }) {
    setError(null);
    const code = (data.otp ?? "").trim();
    if (!code) {
      setError("OTP code is required.");
      return;
    }
    try {
      const res = await api.post("auth/otp/verify/", { phone, code });
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      router.push(resolveNextPath());
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not verify OTP.");
    }
  }

  async function onSubmitPassword(data: { identifier?: string; password?: string }) {
    setError(null);
    const identifier = (data.identifier ?? "").trim();
    const password = data.password ?? "";
    if (!identifier) {
      setError("Email or phone number is required.");
      return;
    }
    if (!password) {
      setError("Password is required.");
      return;
    }
    try {
      const res = await api.post("auth/login/", { identifier, password });
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      router.push(resolveNextPath());
    } catch (err: any) {
      const detail = err?.response?.data;
      if (typeof detail?.detail === "string") {
        setError(detail.detail);
      } else if (detail && typeof detail === "object") {
        const first = Object.values(detail)[0] as any;
        setError(Array.isArray(first) ? String(first[0]) : "Could not sign in.");
      } else {
        setError("Could not sign in.");
      }
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-transparent">
      <div className="mx-auto grid min-h-screen max-w-7xl gap-10 px-6 py-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <section className="space-y-8">
          <div className="inline-flex items-center gap-3 rounded-full border border-[var(--line-strong)] bg-[var(--amber-soft)] px-4 py-2 text-sm text-[var(--text-muted)]">
            <LockKeyhole size={16} className="text-[var(--amber)]" />
            Production-oriented Phase 1 admin access
          </div>
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.45em] text-[var(--text-muted)]">Door App</p>
            <h1 className="mt-4 text-5xl font-semibold leading-tight md:text-6xl">
              One QR. Multiple real-world coordination flows.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-[var(--text-muted)]">
              Doorbell communication, queue control, visitor interactions, chat, and broadcast
              messaging from a single offline-first platform.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { icon: QrCode, title: "Mode-driven QR", text: "Door, queue, event, group, and future actions." },
              { icon: Ticket, title: "Queue engine", text: "Live serving state, token issuance, and admin actions." },
              { icon: RadioTower, title: "Broadcast", text: "Keep one-way urgent communication separate from chat." },
            ].map(({ icon: Icon, title, text }) => (
              <div
                key={title}
                className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-panel)] p-5 shadow-[var(--shadow)] backdrop-blur"
              >
                <Icon size={18} className="text-[var(--teal)]" />
                <h2 className="mt-4 text-lg font-medium">{title}</h2>
                <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">{text}</p>
              </div>
            ))}
          </div>
        </section>
        <section className="rounded-[32px] border border-[var(--line)] bg-[var(--bg-panel)] p-6 shadow-[var(--shadow)] backdrop-blur md:p-8">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.35em] text-[var(--text-muted)]">Secure Entry</p>
            <h2 className="mt-3 text-3xl font-semibold">Admin sign in</h2>
          </div>
          {error ? (
            <div className="mb-5 rounded-[18px] border border-[rgba(255,109,109,0.25)] bg-[rgba(255,109,109,0.10)] px-4 py-3 text-sm text-[var(--text-soft)]">
              {error}{" "}
              {String(error).toLowerCase().includes("register") ? (
                <Link
                  href="/auth/register"
                  className="font-semibold text-[var(--amber)] underline decoration-[rgba(246,185,74,0.35)]"
                >
                  Create account
                </Link>
              ) : null}
            </div>
          ) : null}
          <div className="mb-5 flex gap-2">
            {[
              { key: "password" as const, label: "Password" },
              { key: "otp" as const, label: "OTP" },
            ].map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => {
                  setError(null);
                  setAuthMode(tab.key);
                  if (tab.key === "otp") {
                    setOtpStep("phone");
                    setPhone("");
                  }
                }}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  authMode === tab.key
                    ? "border border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]"
                    : "border border-[var(--line)] bg-[rgba(255,255,255,0.02)] text-[var(--text-muted)] hover:text-[var(--text)]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {authMode === "password" ? (
            <form onSubmit={handleSubmit(onSubmitPassword)} className="space-y-4">
              <label className="block text-sm text-[var(--text-muted)]">Email or phone number</label>
              <input
                {...register("identifier")}
                placeholder="you@example.com or +92 300 0000000"
                className="w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)] focus:ring-2 focus:ring-[var(--amber-soft)]"
              />
              <label className="block text-sm text-[var(--text-muted)]">Password</label>
              <input
                {...register("password")}
                type="password"
                placeholder="Password"
                className="w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)] focus:ring-2 focus:ring-[var(--amber-soft)]"
              />
              <button className="w-full rounded-[18px] bg-[linear-gradient(135deg,#37d6c5,#239e91)] px-4 py-4 font-semibold text-[#041412] transition hover:brightness-105">
                Sign in
              </button>
              <div className="pt-2 text-center text-sm text-[var(--text-muted)]">
                New here?{" "}
                <Link href="/auth/register" className="font-semibold text-[var(--teal)]">
                  Create an account
                </Link>
              </div>
            </form>
          ) : otpStep === "phone" ? (
            <form onSubmit={handleSubmit(onSubmitPhone)} className="space-y-4">
              <label className="block text-sm text-[var(--text-muted)]">Phone number</label>
              <input
                {...register("phone")}
                placeholder="+92 300 0000000"
                className="w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)] focus:ring-2 focus:ring-[var(--amber-soft)]"
              />
              <button className="w-full rounded-[18px] bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-4 py-4 font-semibold text-[#1a1204] transition hover:brightness-105">
                Send OTP
              </button>
              <div className="pt-2 text-center text-sm text-[var(--text-muted)]">
                New here?{" "}
                <Link href="/auth/register" className="font-semibold text-[var(--teal)]">
                  Create an account
                </Link>
              </div>
            </form>
          ) : (
            <form onSubmit={handleSubmit(onSubmitOtp)} className="space-y-4">
              <p className="text-sm leading-6 text-[var(--text-muted)]">Enter the code sent to {phone}</p>
              <input
                {...register("otp")}
                placeholder="6-digit code"
                className="w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-center text-2xl tracking-[0.4em] text-[var(--text)] outline-none transition focus:border-[var(--line-strong)] focus:ring-2 focus:ring-[var(--amber-soft)]"
              />
              <button className="w-full rounded-[18px] bg-[linear-gradient(135deg,#37d6c5,#239e91)] px-4 py-4 font-semibold text-[#041412] transition hover:brightness-105">
                Verify & Enter
              </button>
              <div className="flex items-center justify-between pt-2 text-sm text-[var(--text-muted)]">
                <button type="button" onClick={() => setOtpStep("phone")} className="text-[var(--teal)]">
                  Change number
                </button>
                <Link href="/auth/register" className="text-[var(--text-muted)] hover:text-[var(--text)]">
                  Create account
                </Link>
              </div>
            </form>
          )}
        </section>
      </div>
    </main>
  );
}
