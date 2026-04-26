"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API ?? "http://localhost:8000";

type RoleGap = {
  role: string;
  n_m: number;
  n_f: number;
  raw_gap: number;
  explained: number;
  unexplained: number;
  interaction: number;
};

type Audit = {
  raw_gap: number;
  explained: number;
  unexplained: number;
  interaction: number;
  unexplained_ci_low: number;
  unexplained_ci_high: number;
  by_role: RoleGap[];
  recommendations: string[];
  decision_aid_disclaimer: string;
};

const fmtPct = (x: number) => (x * 100).toFixed(2) + " log-pts";

export default function Home() {
  const [audit, setAudit] = useState<Audit | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch(`${API}/equity_audit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    setAudit(await res.json());
    setLoading(false);
  }

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold">Compensation Equity Analyzer</h1>
      <p className="opacity-70 mb-6">
        Blinder-Oaxaca decomposition: how much of the pay gap is explained — and how much isn&apos;t.
      </p>

      <button
        onClick={run}
        disabled={loading}
        className="rounded-xl px-4 py-2 bg-black text-white disabled:opacity-50"
      >
        {loading ? "Auditing..." : "Run equity audit"}
      </button>

      {audit && (
        <>
          <div className="mt-8 grid grid-cols-3 gap-4">
            <Stat label="Raw gap" value={fmtPct(audit.raw_gap)} />
            <Stat label="Explained" value={fmtPct(audit.explained)} />
            <Stat
              label="Unexplained"
              value={fmtPct(audit.unexplained)}
              sub={`95% CI [${fmtPct(audit.unexplained_ci_low)}, ${fmtPct(
                audit.unexplained_ci_high,
              )}]`}
            />
          </div>

          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-2">Pay-gap waterfall</h2>
            <Waterfall
              raw={audit.raw_gap}
              explained={audit.explained}
              unexplained={audit.unexplained}
              interaction={audit.interaction}
            />
          </div>

          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-2">By role</h2>
            <div className="overflow-x-auto rounded-2xl border">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left p-3">Role</th>
                    <th className="text-right p-3">n (M / F)</th>
                    <th className="text-right p-3">Raw</th>
                    <th className="text-right p-3">Explained</th>
                    <th className="text-right p-3">Unexplained</th>
                    <th className="text-right p-3">Interaction</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.by_role.map((r) => (
                    <tr key={r.role} className="border-t">
                      <td className="p-3">{r.role}</td>
                      <td className="p-3 text-right">{r.n_m} / {r.n_f}</td>
                      <td className="p-3 text-right">{fmtPct(r.raw_gap)}</td>
                      <td className="p-3 text-right">{fmtPct(r.explained)}</td>
                      <td className="p-3 text-right font-semibold">
                        {fmtPct(r.unexplained)}
                      </td>
                      <td className="p-3 text-right">{fmtPct(r.interaction)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-8 rounded-2xl border p-4">
            <div className="text-xs uppercase opacity-60">Recommendations</div>
            <ul className="mt-2 list-disc list-inside">
              {audit.recommendations.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>

          <p className="mt-6 text-xs opacity-60 italic">
            {audit.decision_aid_disclaimer}
          </p>
        </>
      )}
    </main>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-2xl border p-4">
      <div className="text-xs uppercase tracking-wide opacity-60">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
      {sub && <div className="text-xs opacity-60 mt-1">{sub}</div>}
    </div>
  );
}

function Waterfall({
  raw, explained, unexplained, interaction,
}: { raw: number; explained: number; unexplained: number; interaction: number }) {
  const series = [
    { label: "Raw gap", v: raw, color: "bg-slate-700" },
    { label: "Explained", v: explained, color: "bg-emerald-500" },
    { label: "Unexplained", v: unexplained, color: "bg-rose-500" },
    { label: "Interaction", v: interaction, color: "bg-amber-500" },
  ];
  const max = Math.max(...series.map((s) => Math.abs(s.v)));
  return (
    <div className="rounded-2xl border p-4 space-y-2">
      {series.map((s) => (
        <div key={s.label} className="flex items-center gap-3">
          <div className="w-24 text-xs opacity-70">{s.label}</div>
          <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full ${s.color}`}
              style={{ width: `${(Math.abs(s.v) / Math.max(max, 1e-9)) * 100}%` }}
            />
          </div>
          <div className="w-28 text-right text-xs">{fmtPct(s.v)}</div>
        </div>
      ))}
    </div>
  );
}
