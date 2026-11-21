"use client";

import { useEffect, useState } from "react";
import { getWeeklySummary } from "@/lib/api";
import type { WeeklySummaryResponse } from "@/lib/types";

export function KpiCards() {
  const [summary, setSummary] = useState<WeeklySummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getWeeklySummary()
      .then(setSummary)
      .catch(() => setError("Could not load this week's summary — check that the backend is running."));
  }, []);

  if (error) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>;
  }

  if (!summary) {
    return <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-400">Loading…</div>;
  }

  const delta = summary.delta;
  const deltaLabel =
    delta === null
      ? "No comparison available"
      : delta >= 0
        ? `▲ up ${delta.toFixed(1)} vs last week`
        : `▼ down ${Math.abs(delta).toFixed(1)} vs last week`;
  const deltaColor = delta === null ? "text-gray-400" : delta >= 0 ? "text-green-600" : "text-red-600";

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-xs font-medium uppercase tracking-wide text-gray-500">This week&apos;s avg rating</div>
        <div className="mt-2 text-3xl font-semibold text-gray-900">
          {summary.current_week.avg_rating ?? "—"}
          <span className="text-base font-normal text-gray-400"> / 10</span>
        </div>
        <div className={`mt-1 text-sm font-medium ${deltaColor}`}>{deltaLabel}</div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-xs font-medium uppercase tracking-wide text-gray-500">Last week&apos;s avg rating</div>
        <div className="mt-2 text-3xl font-semibold text-gray-900">
          {summary.previous_week.avg_rating ?? "—"}
          <span className="text-base font-normal text-gray-400"> / 10</span>
        </div>
        <div className="mt-1 text-sm text-gray-400">{summary.previous_week.review_count} reviews</div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-xs font-medium uppercase tracking-wide text-gray-500">Reviews this week</div>
        <div className="mt-2 text-3xl font-semibold text-gray-900">{summary.current_week.review_count}</div>
        <div className="mt-1 text-sm text-gray-400">
          {summary.current_week.start} – {summary.current_week.end}
        </div>
      </div>
    </div>
  );
}
