"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { ArrowLeft, LockKeyhole, Mail, Phone, User } from "lucide-react";

type FormValues = {
  full_name: string;
  email: string;
  phone_number: string;
  password: string;
};

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit } = useForm<FormValues>({
    defaultValues: { full_name: "", email: "", phone_number: "", password: "" },
  });

  async function onSubmit(values: FormValues) {
    setError(null);
    setLoading(true);
    try {
      const res = await api.post("auth/register/", {
        full_name: values.full_name.trim(),
        email: values.email.trim(),
        phone_number: values.phone_number.trim(),
        password: values.password,
      });
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      router.push("/dashboard");
    } catch (err: any) {
      const detail = err?.response?.data;
      if (typeof detail?.detail === "string") {
        setError(detail.detail);
      } else if (detail && typeof detail === "object") {
        const first = Object.values(detail)[0] as any;
        setError(Array.isArray(first) ? String(first[0]) : "Could not create account.");
      } else {
        setError("Could not create account.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-transparent">
      <div className="mx-auto grid min-h-screen max-w-6xl gap-10 px-6 py-10 lg:grid-cols-[1fr_1fr] lg:items-center">
        <section className="space-y-8">
          <div className="inline-flex items-center gap-3 rounded-full border border-[var(--line-strong)] bg-[var(--teal-soft)] px-4 py-2 text-sm text-[var(--text-muted)]">
            <LockKeyhole size={16} className="text-[var(--teal)]" />
            Create your account
          </div>
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.45em] text-[var(--text-muted)]">Door App</p>
            <h1 className="mt-4 text-5xl font-semibold leading-tight md:text-6xl">Profile first. Doors next.</h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-[var(--text-muted)]">
              Set up your account so the admin dashboard can load organizations, QR doors, queues, and live alerts.
            </p>
          </div>
          <Link
            href="/auth/login"
            className="inline-flex items-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 text-sm text-[var(--text-muted)] transition hover:border-[var(--line-strong)] hover:text-[var(--text)]"
          >
            <ArrowLeft size={16} /> Back to sign in
          </Link>
        </section>

        <section className="rounded-[32px] border border-[var(--line)] bg-[var(--bg-panel)] p-6 shadow-[var(--shadow)] backdrop-blur md:p-8">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.35em] text-[var(--text-muted)]">Account</p>
            <h2 className="mt-3 text-3xl font-semibold">Register</h2>
          </div>

          {error ? (
            <div className="mb-5 rounded-[18px] border border-[rgba(255,109,109,0.25)] bg-[rgba(255,109,109,0.10)] px-4 py-3 text-sm text-[var(--text-soft)]">
              {error}
            </div>
          ) : null}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <label className="block text-sm text-[var(--text-muted)]">Full name</label>
            <div className="flex items-center gap-3 rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4">
              <User size={18} className="text-[var(--amber)]" />
              <input
                {...register("full_name", { required: true })}
                placeholder="Full name"
                className="w-full bg-transparent text-[var(--text)] outline-none placeholder:text-[var(--text-muted)]"
              />
            </div>

            <label className="block text-sm text-[var(--text-muted)]">Email</label>
            <div className="flex items-center gap-3 rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4">
              <Mail size={18} className="text-[var(--teal)]" />
              <input
                {...register("email", { required: true })}
                placeholder="you@example.com"
                className="w-full bg-transparent text-[var(--text)] outline-none placeholder:text-[var(--text-muted)]"
              />
            </div>

            <label className="block text-sm text-[var(--text-muted)]">Phone number</label>
            <div className="flex items-center gap-3 rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4">
              <Phone size={18} className="text-[var(--amber)]" />
              <input
                {...register("phone_number", { required: true })}
                placeholder="+92 300 0000000"
                className="w-full bg-transparent text-[var(--text)] outline-none placeholder:text-[var(--text-muted)]"
              />
            </div>

            <label className="block text-sm text-[var(--text-muted)]">Password</label>
            <input
              type="password"
              {...register("password", { required: true, minLength: 8 })}
              placeholder="Minimum 8 characters"
              className="w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)] focus:ring-2 focus:ring-[var(--amber-soft)]"
            />

            <button
              disabled={loading}
              className="w-full rounded-[18px] bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-4 py-4 font-semibold text-[#1a1204] transition hover:brightness-105 disabled:opacity-70"
            >
              {loading ? "Creating…" : "Create account"}
            </button>

            <div className="pt-2 text-center text-sm text-[var(--text-muted)]">
              Already have an account?{" "}
              <Link href="/auth/login" className="font-semibold text-[var(--teal)]">
                Sign in
              </Link>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}
