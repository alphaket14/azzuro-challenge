"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getTrends } from "@/lib/api";
import { useFilters } from "@/lib/filterStore";
import type { TrendsResponse } from "@/lib/types";

export function TrendChart() {
  const { filters } = useFilters();
  const [trends, setTrends] = useState<TrendsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    getTrends(filters.propertyIds, filters.dateFrom, filters.dateTo)
      .then(setTrends)
      .catch(() => setError("Could not load trends — check that the backend is running."));
  }, [filters.propertyIds, filters.dateFrom, filters.dateTo]);

  if (error) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>;
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold text-gray-700">Positive vs negative review trend</h2>

      {!trends ? (
        <p className="text-sm text-gray-400">Loading…</p>
      ) : trends.buckets.length === 0 ? (
        <p className="text-sm text-gray-400">No reviews in the selected date range.</p>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trends.buckets}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="period_start" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="positive" stackId="1" stroke="#16a34a" fill="#86efac" name="Positive" />
              <Area type="monotone" dataKey="neutral" stackId="1" stroke="#9ca3af" fill="#e5e7eb" name="Neutral" />
              <Area type="monotone" dataKey="negative" stackId="1" stroke="#dc2626" fill="#fca5a5" name="Negative" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
