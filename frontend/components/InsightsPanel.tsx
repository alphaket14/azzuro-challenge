"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getTopicInsights } from "@/lib/api";
import type { InsightsTopicsResponse } from "@/lib/types";

export function InsightsPanel() {
  const [insights, setInsights] = useState<InsightsTopicsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTopicInsights()
      .then(setInsights)
      .catch(() => setError("Could not load insights — check that the backend is running."));
  }, []);

  if (error) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>;
  }

  if (!insights) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm text-sm text-gray-400">
        Loading insights…
      </div>
    );
  }

  const chartData = insights.overall.map((t) => ({
    topic: t.topic.replace(/_/g, " "),
    pct_of_negative: t.pct_of_negative,
  }));

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold text-gray-700">Operational insights (this week)</h2>

      {insights.headline_callouts.length > 0 ? (
        <ul className="mb-4 space-y-1.5 text-sm text-gray-800">
          {insights.headline_callouts.map((callout, i) => (
            <li key={i} className="flex gap-2">
              <span aria-hidden className="text-amber-500">
                ●
              </span>
              <span>{callout}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mb-4 text-sm text-gray-400">
          No topic crossed the reporting threshold this week — no major recurring issues detected.
        </p>
      )}

      {chartData.length > 0 && (
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ left: -10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="topic" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={50} />
              <YAxis tick={{ fontSize: 11 }} unit="%" />
              <Tooltip formatter={(value: number) => [`${value}%`, "% of negative reviews"]} />
              <Bar dataKey="pct_of_negative" fill="#dc2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
