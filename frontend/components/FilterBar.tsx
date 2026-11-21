"use client";

import { useEffect, useState } from "react";
import { getProperties } from "@/lib/api";
import { useFilters } from "@/lib/filterStore";
import type { Property } from "@/lib/types";

export function FilterBar() {
  const { filters, setPropertyIds, setDateFrom, setDateTo } = useFilters();
  const [properties, setProperties] = useState<Property[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProperties()
      .then(setProperties)
      .catch(() => setError("Could not load properties — check that the backend is running."));
  }, []);

  function togglePropertyId(id: string) {
    if (filters.propertyIds.includes(id)) {
      setPropertyIds(filters.propertyIds.filter((p) => p !== id));
    } else {
      setPropertyIds([...filters.propertyIds, id]);
    }
  }

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-500">Properties</label>
        <div className="flex flex-wrap gap-2">
          {properties.map((p) => {
            const active = filters.propertyIds.includes(p.id);
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => togglePropertyId(p.id)}
                className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                  active
                    ? "border-blue-600 bg-blue-600 text-white"
                    : "border-gray-300 bg-white text-gray-700 hover:border-blue-400"
                }`}
              >
                {p.name}
              </button>
            );
          })}
          {properties.length === 0 && !error && (
            <span className="text-sm text-gray-400">Loading properties…</span>
          )}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="date-from" className="text-xs font-medium text-gray-500">
          From
        </label>
        <input
          id="date-from"
          type="date"
          value={filters.dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="rounded-md border border-gray-300 px-2 py-1 text-sm"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="date-to" className="text-xs font-medium text-gray-500">
          To
        </label>
        <input
          id="date-to"
          type="date"
          value={filters.dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="rounded-md border border-gray-300 px-2 py-1 text-sm"
        />
      </div>

      {error && <span className="text-sm text-red-600">{error}</span>}
    </div>
  );
}
