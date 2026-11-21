"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getPropertyBreakdown } from "@/lib/api";
import type { PropertyBreakdown } from "@/lib/types";

export function PropertyBreakdownTable() {
  const [rows, setRows] = useState<PropertyBreakdown[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPropertyBreakdown()
      .then(setRows)
      .catch(() => setError("Could not load property breakdown — check that the backend is running."));
  }, []);

  if (error) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>;
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-sm font-semibold text-gray-700">Property breakdown (this week)</h2>

      {rows.length === 0 ? (
        <p className="text-sm text-gray-400">Loading…</p>
      ) : (
        <>
          <div className="mb-4 h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rows} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" domain={[0, 10]} hide />
                <YAxis type="category" dataKey="property_name" width={110} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="avg_rating" fill="#2563eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-gray-500">
                <th className="py-1">Property</th>
                <th className="py-1 text-right">Avg rating</th>
                <th className="py-1 text-right">Reviews</th>
                <th className="py-1 text-right">vs last week</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.property_id} className="border-t border-gray-100">
                  <td className="py-2 font-medium text-gray-800">{row.property_name}</td>
                  <td className="py-2 text-right">{row.avg_rating ?? "—"}</td>
                  <td className="py-2 text-right">{row.review_count}</td>
                  <td
                    className={`py-2 text-right font-medium ${
                      row.delta === null ? "text-gray-400" : row.delta >= 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {row.delta === null ? "—" : row.delta >= 0 ? `+${row.delta}` : row.delta}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
